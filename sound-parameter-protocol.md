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

**Status:** In progress

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

## Phase 1 Results: Reverb Depth End-to-End Trace

*(Results will be added here as the investigation progresses)*
