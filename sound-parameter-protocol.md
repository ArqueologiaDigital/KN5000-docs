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

### Phase 2: Lsw\* function analysis

For each of the 32 Lsw\* functions, identify:
- Which command code it sends (e.g., 0x63 for reverb)
- Which Sub CPU CC handler receives it
- Which offset in the 287-byte voice structure it writes to
- The valid value range

**Status:** Partially complete — see Phase 2 Results below

### Phase 3: Preset tables

Decode the preset data tables at 0xEDB36C (reverb presets) and 0xEDB394 (EQ presets) — 13 reverb types × 24 channels of parameter data.

**Status:** In progress

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

---

## Phase 2 Results: Lsw\* Function Architecture

### Key Finding: Data-Driven Widget System

The 32 Lsw\* functions are **generic widget callbacks**, not per-parameter command generators. The actual CC/command identity comes from the **NAKA widget configuration data**, not from the Lsw function code.

Each Lsw function handles a specific widget TYPE (slider, on/off toggle, etc.):
- **LswVolume, LswExpression** → numeric slider with mute state (bit 15 check)
- **LswPan** → center-left-right slider (3-way display: "CTR", "L%2d", "R%2d")
- **LswReverb, LswDSPEffect** → numeric slider ("%3d" format)
- **LswSustain, LswDigitalEffect** → on/off toggle ("ON ", "OFF")
- **LswKeyShift** → signed slider ("%+3d")
- **LswTuning** → signed fine-tune ("%+4d")

### Command Flow

```
NAKA Widget Config Data
  (contains: CC number, value range, channel)
    │
    ▼
Lsw* Function (generic handler for widget type)
  handles event 0x1E00042 (value changed)
    │
    ├─ bit 13 set? → LABEL_FF0A72 (send command to Sub CPU)
    │                  │
    │                  ├─ st32_24 0x03c21c, widget_data  (buffer the widget config)
    │                  ├─ LABEL_FF1048 (command encoder, reads template at 0x0AD8)
    │                  └─ AssswbWr → ring buffer → sendCOMM → DMA → Sub CPU
    │
    └─ bit 13 clear? → Strcpy (format display string only, no sound command)
```

The per-channel configuration table at **0xE952AA** contains 4-byte flag words. The bit tested by each Lsw function determines whether the parameter is "active" for that channel:

| Lsw Function | Bit Tested | Display Format | Send Command? |
|-------------|-----------|---------------|---------------|
| LswVolume | bit 15 | `"%4d"` / `"MUTE"` | Yes |
| LswMute | bit 15 | `"%4d"` / `"MUTE"` | Yes |
| LswPan | bit 14 | `"CTR"` / `"L%2d"` / `"R%2d"` | Yes |
| LswReverb | bit 13 | `"%3d"` | Yes |
| LswDSPEffect | bit 12 | `"%3d"` | Yes |
| LswSustain | bit 11 | `"ON "` / `"OFF"` | No (Strcpy only) |
| LswSustainLength | bit 10 | `"%2d"` | Yes |
| LswDigitalEffect | bit 3 | `"ON "` / `"OFF"` | No (Strcpy only) |
| LswKeyShift | - | `"%+3d"` | Yes |
| LswTuning | - | `"%+4d"` | Yes |
| LswBendRange | - | `"%3d"` | Yes |
| LswSound | - | `" ------"` | No (Strcpy only) |
| LswGlidePedal | - | `"ON "` / `"OFF"` | No (Strcpy only) |
| LswSustainPedal | - | `"ON "` / `"OFF"` | No (Strcpy only) |
| LswAfterTouch | - | `"ON "` / `"OFF"` | No (Strcpy only) |
| LswKeyScaling | - | `"ON "` / `"OFF"` | No (Strcpy only) |
| LswOrchestrator | - | various | No (Strcpy only) |
| LswLocalControl | - | various | No (special) |
| LswMidiChannel | - | `"CH%2d"` / `"OFF"` | Yes (3 variants) |
| LswMasterTuning | - | `"%+4d"` | Yes (loop-based) |
| LswLeftHold | - | (format at E952A6) | Yes |

### Functions That Send Sub CPU Commands

18 of the 32 Lsw functions call `LABEL_FF0A72` to send commands to the Sub CPU. The remaining 14 only update display strings via `Strcpy` — these handle parameters that are processed locally by the Main CPU (sustain toggle, digital effect on/off, sound name display, etc.).

### Remaining Work

To complete the CC-to-Lsw mapping, the NAKA widget configuration data for each screen needs to be decoded. The widget config contains the actual CC number for each parameter control. This is a data-driven system — the same LswReverb handler is used for ALL reverb depth sliders across all screens.

---

## Phase 3 Results: Preset Tables and DSP Effect Types

### DSP Effect Name Table (ROM 0xE33304)

The firmware maintains a master table of all DSP effect types as 16-character display strings. Each entry is 18 bytes (16 chars + null + pad). The table includes reverbs, delays, modulation effects, and distortion:

| Index | Address | Name | Category |
|-------|---------|------|----------|
| 0 | E33304 | FUZZ | Distortion |
| 1 | E33316 | OVERDRIVE | Distortion |
| 2 | E33328 | DISTORTION | Distortion |
| 3-6 | E3333A | *(unused)* | - |
| 7 | E33382 | WAVE REVERB 2 | Reverb |
| 8 | E33394 | WAVE REVERB 1 | Reverb |
| 9 | E333A6 | BRIGHT REVERB 2 | Reverb |
| 10 | E333B8 | BRIGHT REVERB 1 | Reverb |
| 11 | E333CA | DARK REVERB 2 | Reverb |
| 12 | E333DC | DARK REVERB 1 | Reverb |
| 13 | E333EE | CONCERT REVERB 2 | Reverb |
| 14 | E33400 | CONCERT REVERB 1 | Reverb |
| 15 | E33412 | PLATE REVERB 2 | Reverb |
| 16 | E33424 | PLATE REVERB 1 | Reverb |
| 17 | E33436 | ROOM REVERB 2 | Reverb |
| 18 | E33448 | ROOM REVERB 1 | Reverb |
| 19 | E3345A | ROCK ROTARY | Modulation |
| 20-22 | E3346C | *(unused)* | - |
| 23 | E334A2 | MODULATION DELAY | Delay |
| 24 | E334B4 | MULTI TAP DELAY | Delay |
| 25 | E334C6 | SINGLE DELAY | Delay |
| 26 | E334D8 | GATED REVERB | Reverb |
| 27 | E334EA | *(unused)* | - |
| 28 | E3350E | ENSEMBLE | Modulation |
| 29 | E33520 | PHASER | Modulation |
| 30 | E33532 | FLANGER | Modulation |
| 31 | E33544 | ENHANCER | Dynamics |
| 32 | E33556 | MODULATED CHORUS | Modulation |
| 33 | E33568 | CHORUS | Modulation |
| 34 | E3357A | NO OPERATION | None |

Total: **22 active DSP algorithms** + 12 unused/placeholder slots.

### Reverb Preset Table (ROM 0xEDB36C)

The reverb preset table contains **10 pointer entries** (4 bytes each, little-endian). Each pointer targets a 24-byte preset data block. The presets are loaded by `MainRevEqPresetLoad` → `LABEL_FC9F81` when the user selects from the REVERB & EQ PRESETS screen.

| Preset | Pointer Target | Type ID (byte 0) | Parameters (bytes 1-7) |
|--------|---------------|------------------|----------------------|
| 0 | 0xEDA6EC | 0x11 | 32 00 0C 14 32 5D 00 |
| 1 | 0xEDA704 | 0x10 | 18 00 61 18 63 5E 00 |
| 2 | 0xEDA71C | 0x12 | 02 00 2D 0C 32 50 00 |
| 3 | 0xEDA734 | 0x14 | 2E 00 1D 14 3A 50 00 |
| 4 | 0xEDA74C | 0x15 | 20 00 3C 18 50 4E 00 |
| 5 | 0xEDA764 | 0x16 | 14 00 15 18 34 49 00 |
| 6 | 0xEDA77C | 0x18 | 21 00 02 00 60 4F 00 |
| 7 | 0xEDA794 | 0x19 | 2B 00 1A 00 05 3A 00 |
| 8 | 0xEDA7AC | 0x1A | 0F 00 11 15 17 4F 00 |
| 9 | 0xEDA7C4 | 0x1B | 3C 00 1A 12 32 56 12 |

**Each preset data block is 24 bytes:**
- **Byte 0:** DSP algorithm/type ID (0x10-0x1B)
- **Bytes 1-7:** Parameter values (reverb time, density, diffusion, etc.)
- **Bytes 8-21:** Zero-padded (unused parameter slots, except preset 9)
- **Bytes 22-23:** `0x63 0x00` — command code (0x63) + terminator

The preset loading loop iterates 24 times, sending each byte as a separate command to the Sub CPU with command code `0x63`. A lookup table in DRAM (at runtime address 0xFC8E) maps each byte position to a specific Sub CPU parameter identifier.

### EQ Preset Table (ROM 0xEDB394)

The EQ preset table follows immediately after the reverb table, also with **10 pointer entries**. EQ presets all start with type ID `0x4F` (except preset 9 which appears to be a combined reverb+EQ preset using type `0x14`).

| Preset | Pointer Target | Type ID | Parameters (bytes 1-7) |
|--------|---------------|---------|----------------------|
| 0 | 0xEDA7DC | 0x4F | 02 1C 03 97 04 D5 05 |
| 1 | 0xEDA7F4 | 0x4F | 01 D8 02 84 04 C4 06 |
| 2 | 0xEDA80C | 0x4F | 02 43 03 2A 04 29 04 |
| 3 | 0xEDA824 | 0x4F | 00 CE 03 98 05 18 05 |
| 4 | 0xEDA83C | 0x4F | 00 1C 02 54 03 14 04 |
| 5 | 0xEDA854 | 0x4F | 01 D8 03 98 05 02 05 |
| 6 | 0xEDA86C | 0x4F | 00 12 01 A8 05 18 05 |
| 7 | 0xEDA884 | 0x4F | 01 C0 03 98 05 18 06 |
| 8 | 0xEDA89C | 0x4F | 01 1D 04 EA 05 F0 06 |
| 9 | 0xEDA8B4 | 0x14 | 36 00 0B 14 32 4A 00 |

### DSP Parameter Register Addresses

After the effect name table at 0xE33578, a lookup table maps effect slots to DSP register addresses. The addresses increment by 0x10 per slot:

```
First set:  0x45, 0x55, 0x65, 0x75, 0x85, 0x95, 0xA5, 0xB5
Second set: 0x47, 0x57, 0x67, 0x77, 0x87, 0x97, 0xA7, 0xB7
```

These correspond to the DSP chip's register-indirect access via `0x130000`/`0x130002`, suggesting 8 effect processing slots with parameters addressable in 0x10-byte increments.

### Remaining Questions

1. **Type ID → Name mapping:** The exact correspondence between preset type IDs (0x10-0x1B) and the effect name table indices (0-34) requires tracing the code that selects the display name from the type ID.
2. **Parameter byte meanings:** The 7 non-zero parameter bytes in each preset encode specific DSP parameters (reverb time, pre-delay, density, diffusion, HF damping, wet/dry mix, etc.). Decoding these requires analyzing the Sub CPU's DSP configuration handlers.
3. **Runtime lookup table at 0xFC8E:** This DRAM table maps preset byte positions to Sub CPU parameter identifiers. It's populated at runtime by `0xFF0D99` during preset unpacking.
