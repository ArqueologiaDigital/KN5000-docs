---
layout: page
title: MIDI Subsystem
permalink: /midi-subsystem/
---

# MIDI Subsystem

> **Documentation Status: Placeholder**
>
> This page is a placeholder for future documentation. MIDI I/O exists but
> the handler routines need detailed analysis.

## Overview

The KN5000 has full MIDI implementation with In, Out, and Thru ports. It can function as a MIDI controller, sound module, or sequencer recorder/player.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       MAIN CPU                               │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ MIDI Parser  │  │ MIDI Router  │  │ MIDI Output  │       │
│  │              │  │              │  │  Generator   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
   │   MIDI IN     │  │  MIDI THRU    │  │   MIDI OUT    │
   │   (5-pin)     │  │   (5-pin)     │  │   (5-pin)     │
   └───────────────┘  └───────────────┘  └───────────────┘
```

## Known Information

### Hardware

The MIDI interface is handled by the Main CPU's serial ports:

| Function | Description |
|----------|-------------|
| MIDI IN | Receives external MIDI messages |
| MIDI OUT | Transmits generated MIDI messages |
| MIDI THRU | Echoes IN to THRU (hardware or software) |

### MIDI Implementation

Based on KN5000 specifications, supported features include:

| Category | Features |
|----------|----------|
| Channels | 1-16 receive and transmit |
| Notes | Full 128-note range |
| Velocity | Note On/Off velocity |
| Aftertouch | Channel and polyphonic |
| Controllers | Standard CC messages |
| Program Change | Bank select, program |
| System | Clock, Start/Stop/Continue |
| SysEx | Technics-specific messages |

### Control Change Messages

Common MIDI CC values used:

| CC# | Parameter |
|-----|-----------|
| 1 | Modulation Wheel |
| 7 | Main Volume |
| 10 | Pan |
| 11 | Expression |
| 64 | Sustain Pedal |
| 91 | Reverb Send |
| 93 | Chorus Send |

## Related Pages

- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) - Sound generation
- [Sequencer]({{ site.baseurl }}/sequencer/) - MIDI recording/playback
- [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) - Local control
- [System Overview]({{ site.baseurl }}/system-overview/) - Overall architecture

## Research Needed

- [ ] Identify MIDI serial port addresses
- [ ] Document MIDI parser routines
- [ ] Analyze MIDI routing logic
- [ ] Map MIDI output generation
- [ ] Document Technics SysEx format
- [ ] Understand MIDI filter settings

## How to Contribute

See [Help Wanted]({{ site.baseurl }}/help-wanted/) for contribution guidelines.

Search the disassembly for serial port initialization and MIDI-related strings.
