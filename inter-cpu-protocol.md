---
layout: page
title: Inter-CPU Protocol
permalink: /inter-cpu-protocol/
---

# Inter-CPU Protocol

> **Documentation Status: Placeholder**
>
> This page is a placeholder for future documentation. The communication latch
> hardware is known but the protocol details need reverse engineering.

## Overview

The KN5000 uses two TMP94C241F CPUs that communicate via a memory-mapped latch. The Main CPU handles UI and control, while the Sub CPU handles audio generation.

## Architecture

```
┌─────────────────────┐                    ┌─────────────────────┐
│      MAIN CPU       │                    │       SUB CPU       │
│    TMP94C241F       │                    │     TMP94C241F      │
│                     │                    │                     │
│  UI, MIDI, Control  │                    │  Audio, DSP, Synth  │
│                     │                    │                     │
└──────────┬──────────┘                    └──────────┬──────────┘
           │                                          │
           │         ┌──────────────────┐            │
           └────────►│      LATCH       │◄───────────┘
                     │    @ 0x120000    │
                     │                  │
                     │  Bidirectional   │
                     │  Data Register   │
                     └──────────────────┘
```

## Known Information

### Hardware

| Component | Address | Description |
|-----------|---------|-------------|
| Communication Latch | 0x120000 | Bidirectional data register |

### Boot Sequence

During boot, the Main CPU loads the Sub CPU payload:

1. Main CPU writes 192KB payload to latch
2. Sub CPU reads payload into internal RAM
3. Sub CPU executes payload, enters ready state
4. Main CPU begins sending audio commands

### Data Transfer

The latch at 0x120000 supports:
- Byte writes from Main CPU
- Byte reads from Sub CPU
- Handshaking via status bits

## Command Categories (Presumed)

Based on keyboard functionality, the protocol likely includes:

| Category | Commands |
|----------|----------|
| Note Events | Note On, Note Off, Aftertouch |
| Program | Program Change, Bank Select |
| Control | Volume, Pan, Expression, Sustain |
| System | All Notes Off, Reset, Status Query |
| Effects | Reverb, Chorus, DSP settings |

## Related Pages

- [CPU Subsystem]({{ site.baseurl }}/cpu-subsystem/) - Both CPU details
- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) - Sound generation
- [Boot Sequence]({{ site.baseurl }}/boot-sequence/) - Startup process
- [System Overview]({{ site.baseurl }}/system-overview/) - Overall architecture

## Research Needed

- [ ] Document latch register bit layout
- [ ] Identify handshaking mechanism
- [ ] Trace Main CPU command transmission routines
- [ ] Analyze Sub CPU command reception handlers
- [ ] Document complete command set
- [ ] Understand audio parameter formats

## How to Contribute

See [Help Wanted]({{ site.baseurl }}/help-wanted/) for contribution guidelines.

Key areas to analyze:
- Main CPU: Look for writes to 0x120000 in `maincpu/kn5000_v10_program.asm`
- Sub CPU: Analyze command handlers in `subcpu/kn5000_subprogram_v142.asm`
