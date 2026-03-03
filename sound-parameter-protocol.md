---
layout: page
title: Sound Parameter Protocol
permalink: /sound-parameter-protocol/
---

# Sound Parameter Protocol

This page documents the protocol used by the KN5000 Main CPU to send sound parameter changes to the Sub CPU, traced from the UI widgets all the way to the DSP hardware. The investigation starts with the Reverb settings as a proof of concept, then systematically maps all parameters.

## Architecture (3 layers)

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: UI (Main CPU — NAKA Widget System)            │
│                                                         │
│  Widget event (e.g. slider changed)                     │
│    → Lsw* handler function (e.g. LswReverb at F7CFA5)  │
│    → AssswbWr (ring buffer write at FDB1F3)             │
└──────────────────────┬──────────────────────────────────┘
                       │ 4-byte command packets
                       │ via ring buffer at RAM 0xBD3C
                       ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: Inter-CPU Transport                           │
│                                                         │
│  sendCOMM (EF32F4) → DMA latch at 0x140000             │
│  Command byte: bits 7-5 = handler, bits 4-0 = count    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: Sub CPU (Sound Processing)                    │
│                                                         │
│  INT0 ISR → ring buffer 0x2B0D                          │
│  CC dispatch → Voice_CC_91 (reverb depth, at 0x02A46C) │
│    → LABEL_028A44: store at voice[ch × 0x11F + 0x7F]   │
│  Voice param structure: 287 bytes/voice at 0x041300     │
└─────────────────────────────────────────────────────────┘
```

## Concrete trace: Reverb Depth (CC#91)

**Sub CPU side (already decoded):**
- `Voice_CC_91` loads channel from `(xiz+1)`, value from `(xiz+3)`
- Calls `LABEL_028A44`: computes `wa × 0x11F`, points to `0x04137F` (= base 0x041300 + offset 0x7F)
- Stores reverb depth in the per-voice parameter structure

**For comparison, other CC handlers at nearby offsets:**

| CC | Handler | Sub CPU function | Voice offset | Meaning |
|----|---------|-----------------|-------------|---------|
| 0x91 | Voice_CC_91 | LABEL_028A44 | +0x7F | Reverb depth |
| 0x95 | Voice_CC_95 | LABEL_028A55 | +0x72 | Chorus depth |
| (sustain) | Voice_CC_Sostenuto | LABEL_028A04 | +0x7E | Sostenuto |

## Reverb preset loading path

When a reverb preset is selected on the REVERB & EQ PRESETS screen:
1. `MainRevEqPresetLoad` (at F746F4) dispatches on preset type (reverb-only / EQ-only / combined)
2. Calls `LABEL_FC9F81` which loads preset data from ROM at **0xEDB36C**
3. A loop sends **24 commands** (code 0x63) via `AssswbWr`, one per MIDI channel
4. Each command carries a parameter value from the preset data table

## What we have to work with

**32 Lsw\* functions** — each is a per-parameter widget handler:
- LswReverb, LswDSPEffect, LswDigitalEffect
- LswVolume, LswPan, LswMute
- LswSustain, LswSustainLength, LswSustainPedal
- LswKeyShift, LswTuning, LswBendRange
- LswGlidePedal, LswAfterTouch, LswPartExp
- LswLocalControl, LswMidiChannel, LswOrchestrator
- LswMasterTuning, LswKeyScaling, LswSound
- LswLeftHold, LswEditCheck
- LswPercDecay, LswPercLevel, LswDrawAttack, LswDrawRelease
- LswScalingType/Shift/Shift2/Mode/KeyX

All reference the same parameter table at **0xE952AA** (per-channel config) and **0xE953CE** (value lookup). They all follow the same pattern — they share the exit code at LABEL_F7D0A6.

## Investigation plan

### Phase 1: Proof of concept — Reverb Depth end-to-end trace

Fully trace LswReverb end-to-end — from the event `0x1E00042` through `LABEL_FF0A72` → `LABEL_FF1048` → `AssswbWr` → `sendCOMM` → Sub CPU `Voice_CC_91` → voice param offset 0x7F. Verify the command byte encoding.

**Status:** Complete

### Phase 2: Systematic mapping of all 32 Lsw\* functions

For each of the 32 Lsw\* functions, identify:
- Which command code it sends (e.g., 0x63 for reverb)
- Which Sub CPU CC handler receives it
- Which offset in the 287-byte voice structure it writes to
- The valid value range

**Status:** Not started

### Phase 3: Preset tables

Decode the preset data tables at 0xEDB36C (reverb presets) and 0xEDB394 (EQ presets) — 13 reverb types × 24 channels of parameter data.

**Status:** Not started

### Phase 4: DSP commands

Trace the DSP configuration path (0x130000 interface, command 0x30 for parameter update) to understand how reverb type changes reprogram the actual DSP chips.

**Status:** Not started

---

## Phase 1 Results: Sub CPU Voice Parameter Structure

### Voice_CtrlChange Dispatcher (Sub CPU 0x02A46C)

The Sub CPU function `Voice_CtrlChange` receives 4-byte command packets via the inter-CPU ring buffer and dispatches them to per-CC handler functions. The packet format is:

```
Byte 0: Command type (determines dispatch to Voice_CtrlChange vs other handlers)
Byte 1: Channel number (0x00-0x19, 26 channels total)
Byte 2: CC number (MIDI Control Change number)
Byte 3: CC value (0x00-0x7F typically)
```

The channel number is validated: `cp (xiz + 1), 0x1A` — any channel >= 26 is rejected.

### Per-Voice Parameter Structure

Each voice has a **287-byte (0x11F)** parameter block, with 26 voices starting at base address **0x041300** in Sub CPU DRAM.

**Address formula:** `0x041300 + (channel × 0x11F) + offset`

### Complete CC → Voice Offset Mapping

| MIDI CC | Name | Handler | Voice Offset | Size | Operation | Default |
|---------|------|---------|-------------|------|-----------|---------|
| 0x01 | Mod Wheel | Voice_ModWheel_Apply | (complex) | - | Multi-register update | - |
| 0x07 | Volume | LABEL_028839 | +0x74 | 2 | Lookup table at 0x011D16 | 0xFE00 |
| 0x0A | Pan | LABEL_0288C5 | +0x76 | 2 | Store direct | - |
| 0x0B | Expression | LABEL_0288D6 | +0x78 | 2 | Lookup table at 0x011D16 | 0xFE00 |
| 0x40 | Sustain | LABEL_028962 | +0x72 | bit 0 | Set/clear bit 0 | 0 |
| 0x5B | Sostenuto | LABEL_02898C | +0x77 | 2 | Store direct | - |
| 0x5D | Soft Pedal | LABEL_02899D | +0x7A | 2 | Store direct | - |
| 0x5E | Portamento | LABEL_02A0E9 | (complex) | - | Multi-function chain | - |
| 0x78-0x82 | (Extended) | Jump table at 0x00F739 | various | - | See extended table | - |
| 0x91 | **Reverb Depth** | **LABEL_028A44** | **+0x7F** | **2** | **Store direct** | **0x00** |
| 0x95 | Chorus Enable | LABEL_028A55 | +0x72 | bit 2 | Set/clear bit 2 | 0 |
| 0x97 | Unknown | LABEL_028A7F | +0x80 | 2 | Store direct | 0x06 |
| 0x9B | Unknown | LABEL_028A90 | +0x8D | 2 | Store direct | 0x01 |
| 0x9C | Pedal Control | LABEL_028AA1 | +0x6A | bit 8 | Set/clear bit 8 | 0x00 |
| 0x9D | Unknown | LABEL_028ACB | +0x8E | 2 | Store direct | 0x00 |

### Extended CC Table (0x78-0x82)

CCs 0x78-0x82 are dispatched via a jump table at Sub CPU ROM 0x00F739 (11 word entries) with base 0x02A306. These include:

| CC | Target | Voice Offset | Purpose |
|----|--------|-------------|---------|
| 0x7B | LABEL_0289D8 | +0x7B | Portamento amount |
| 0x7C | LABEL_0289E9 | +0x7C | Pitch bend (stores `(value - 0x80) × 2`) |
| 0x7D | LABEL_028A04 | +0x7E | Sostenuto depth (stores `value - 0x40`) |

### Flags Word at Offset +0x72

The 16-bit word at offset +0x72 is a bitfield shared by multiple CC handlers:

| Bit | CC | Meaning | Set mask | Clear mask |
|-----|-----|---------|----------|------------|
| 0 | 0x40 | Sustain pedal on | 0x0001 | 0xFFFE |
| 2 | 0x95 | Chorus enable | 0x0004 | 0xFFFB |
| 14 | (0x5E chain) | Alt sustain mode | 0x4000 | 0xBFFF |

### Volume and Expression: Lookup Table

CC 0x07 (Volume) and CC 0x0B (Expression) don't store the raw CC value — they use a **lookup table at ROM 0x011D16** to translate the 7-bit CC value into a 16-bit hardware value. This implements a non-linear response curve (likely logarithmic for perceived loudness).

When CC value is 0, a special "mute" value 0xFE00 is stored instead.

### Reverb Depth Trace (CC 0x91) — Complete Path

```
Main CPU UI:
  LswReverb (F7CFA5) handles event 0x1E00042 (value changed)
    → LABEL_FF0A72: acquires audio lock #7, formats command
      → LABEL_FF1048: command encoding engine (parses format string)
        → AssswbWr (FDB1F3): writes 4-byte packet to ring buffer at 0xBD3C
          Ring buffer: max 127 entries (508 bytes), 4 bytes each

Inter-CPU Transport:
  sendCOMM (EF32F4): reads from ring buffer, acquires audio lock #2
    → InterCPU_Send_Data_Block (EF3345): encodes command byte
      Command byte = (handler_id << 5) | (byte_count - 1)
    → Audio_DMA_Transfer (EF341B): writes payload to DMA latch at 0x140000
      Handshake: wait SSTAT1 high → write → wait SSTAT1 low → DMA

Sub CPU:
  INT0 ISR: receives from latch, HDMA transfers payload to ring buffer 0x2B0D
  Main loop: reads 4-byte packet [type, channel, cc#, value]
    → Voice_CtrlChange (02A46C):
      channel = (xiz+1) = 0x00-0x19
      cc# = (xiz+2) = 0x91
      value = (xiz+3) = 0x00-0x7F
    → LABEL_028A44:
      extz wa                      ; wa = channel
      muls wa, 0x11F               ; wa = channel × 287
      lda_24 xde, 0x04137f         ; de = base + 0x7F
      lda_dri3 XHL, 0x07, 0xE8, 0xE0  ; store value at [de + wa]
      ret
    → Reverb depth stored at: 0x041300 + (channel × 0x11F) + 0x7F
```

### Reverb Preset Loading Path — Complete

When the user selects a reverb preset on the REVERB & EQ PRESETS screen:

```
Main CPU:
  NAKA widget generates event 0x1E3000A/B/C (preset type: reverb/EQ/combined)
    → MainRevEqPresetLoad (F746F4): dispatches on event
      → LABEL_FC9F81: selects preset handler by type
        type 0 (reverb): preset data from ROM 0xEDB36C
        type 1 (EQ):     preset data from ROM 0xEDB394
        type 2 (combined): calls LABEL_FCA04E

  For type 0 (reverb preset):
    → 0xFF0D99: unpacks preset data (24 bytes) from ROM table
    → Loop 24 times (iz = 0..23, one per MIDI channel):
        pushw 0xFF          ; target specifier
        ldw wa, 0x63        ; command code 0x63
        call AssswbWr       ; write to ring buffer
    → LABEL_FCD201: refresh UI display (event 0x4002, widget 0x7F)
```

### Key Addresses Summary

| Address | CPU | Purpose |
|---------|-----|---------|
| 0xBD3C | Main (internal RAM) | Command ring buffer (127 × 4 bytes) |
| 0x140000 | Shared (latch) | Inter-CPU DMA communication port |
| 0x041300 | Sub (DRAM) | Voice parameter structure base |
| 0x011D16 | Sub (ROM) | Volume/Expression lookup table |
| 0x00F739 | Sub (ROM) | CC 0x78-0x82 jump table |
| 0xE952AA | Main (ROM) | Per-channel config table (Lsw functions) |
| 0xE953CE | Main (ROM) | Per-channel value lookup table |
| 0xEDB36C | Main (ROM) | Reverb preset data table |
| 0xEDB394 | Main (ROM) | EQ preset data table |
