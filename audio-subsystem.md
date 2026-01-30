---
layout: page
title: Audio Subsystem
permalink: /audio-subsystem/
---

# Audio Subsystem

> **Documentation Status: Placeholder**
>
> This page is a placeholder for future documentation. The audio subsystem has been
> identified but not yet fully reverse-engineered.

## Overview

The KN5000 audio subsystem handles all sound generation, processing, and output. It is controlled by the Sub CPU (TMP94C241F) which receives commands from the Main CPU.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SUB CPU (TMP94C241F)                    │
│                                                              │
│  Boot ROM: 128KB @ 0xFE0000 (internal)                       │
│  Payload: 192KB (loaded from Main CPU at boot)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    DSP / TONE GENERATOR                      │
│                                                              │
│  Waveform ROM: Multiple MB of PCM samples                   │
│  Polyphony: 64 voices                                        │
│  Effects: Reverb, Chorus, etc.                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         DAC OUTPUT                           │
│                                                              │
│  Memory-mapped at: 0x100000                                 │
│  Channels: Stereo L/R                                        │
│  Sample Rate: 44.1kHz (presumed)                            │
└─────────────────────────────────────────────────────────────┘
```

## Known Information

### Hardware Components

| Component | Address | Description |
|-----------|---------|-------------|
| DAC Interface | 0x100000 | Digital-to-Analog converter control |
| Sub CPU Latch | 0x120000 | Communication with Main CPU |

### Sub CPU Firmware

The Sub CPU runs dedicated audio firmware:

- **Boot ROM**: 128KB internal ROM at 0xFE0000
- **Payload**: 192KB loaded from Main CPU during boot via DMA
- **Status**: Both ROMs 100% reconstructed

### Waveform Data

The waveform ROMs contain:
- Piano samples
- Orchestral instruments
- Synthesizer waveforms
- Drum kits
- GM/GS sound set

**Note**: Waveform ROM contents not yet analyzed in detail.

## Communication Protocol

The Main CPU sends note and control data to the Sub CPU via the latch at 0x120000:

```
Main CPU                    Sub CPU
    │                          │
    │── Note On (ch, note, vel) ──►│
    │                          │
    │── Program Change ────────►│
    │                          │
    │── Control Change ────────►│
    │                          │
    │◄── Status/Acknowledge ───│
```

## Related Pages

- [CPU Subsystem]({{ site.baseurl }}/cpu-subsystem/) - Main and Sub CPU details
- [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) - Communication latch protocol
- [MIDI Subsystem]({{ site.baseurl }}/midi-subsystem/) - External MIDI handling
- [System Overview]({{ site.baseurl }}/system-overview/) - Overall architecture

## Research Needed

- [ ] Document DAC register interface at 0x100000
- [ ] Analyze Sub CPU payload command handlers
- [ ] Identify waveform ROM format and sample layout
- [ ] Document DSP effects processing
- [ ] Map voice allocation algorithm
- [ ] Understand polyphony management

## How to Contribute

See [Help Wanted]({{ site.baseurl }}/help-wanted/) for contribution guidelines.

The Sub CPU payload is fully disassembled at `subcpu/kn5000_subprogram_v142.asm` - analysis of audio-related routines would be valuable.
