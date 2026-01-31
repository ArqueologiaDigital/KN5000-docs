---
layout: page
title: Sequencer
permalink: /sequencer/
---

# Sequencer

> **Documentation Status: Placeholder**
>
> This page is a placeholder for future documentation. The sequencer functionality
> is a major feature but needs detailed reverse engineering.

## Overview

The KN5000 includes a full-featured 16-track MIDI sequencer with real-time and step recording, playback, and editing capabilities. It also runs the auto-accompaniment style system.

## Architecture (Presumed)

```
┌─────────────────────────────────────────────────────────────┐
│                      SEQUENCER ENGINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   TRACK MANAGER                      │    │
│  │                                                      │    │
│  │   Track 1   Track 2   Track 3  ...  Track 16        │    │
│  │   [Melody]  [Bass]    [Drums]       [User]          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Recorder   │  │   Player     │  │    Clock     │       │
│  │   (RT/Step)  │  │   (Playback) │  │   (Tempo)    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │    Editor    │  │   Style      │                         │
│  │  (Quantize)  │  │   Engine     │                         │
│  └──────────────┘  └──────────────┘                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Medley Playback System

The KN5000 supports several medley playback modes for playing multiple songs in sequence.

### Medley Types

| Type | Function | Description |
|------|----------|-------------|
| Internal Medley | `FmmIntMedleyFunc` | Plays user-recorded sequences stored in SRAM |
| Disk Medley | `FmmDiskMedleySelectFunc` | Plays sequences from floppy disk |
| SMF Medley | `FmmSmfMedleyFunc` | Plays Standard MIDI Files |
| Performance Data | `FmmPdMedleyFunc` | Plays performance data files |
| Document Medley | `FmmDocMedleyFunc` | Plays document files |

### Internal Medley Memory Layout

Internal medley songs are stored in battery-backed SRAM:

| Address | Size | Description |
|---------|------|-------------|
| `0xAB000` | 20KB | 10 song slots (0x800 bytes each) |
| `0xF180` | 2KB | Current playback buffer |

Each slot is 2048 bytes (0x800) and stores one user-recorded sequence.

### Key Routines

| Routine | Address | Purpose |
|---------|---------|---------|
| `LABEL_F2065A` | 0xF2065A | Check if slot has valid data |
| `LABEL_F20BCE` | 0xF20BCE | Load and play a song from slot |
| `LABEL_F20BFA` | 0xF20BFA | Copy slot to playback buffer (LDIR) |
| `LABEL_F2076D` | 0xF2076D | Get current playback state |

### Medley State Variables

| Address | Name | Description |
|---------|------|-------------|
| `0x84FE` | Play flag | 0=stopped, 1=playing |
| `0x889A` | Song count | Number of songs in playlist |
| `0x889C` | Current index | Currently playing song |
| `0x889E` | Repeat flag | 0=no repeat, 1=repeat |
| `0x8890` | Order array | 10-byte play order (0xFF=unused, 0xFE=marked) |

### Source Code

The medley system is implemented in `maincpu/file_io/medley.asm` with ~4700 lines of disassembled code including:
- Song selection UI handlers
- Playback state machine
- Repeat/shuffle logic
- Multi-format file loading

---

## Known Information

### Features

Based on KN5000 specifications:

| Feature | Description |
|---------|-------------|
| Tracks | 16 MIDI tracks |
| Resolution | 96 PPQ (presumed) |
| Recording | Real-time and step modes |
| Playback | Variable tempo, loop |
| Editing | Quantize, transpose, copy |
| Storage | Save to floppy or HD |

### Style System

The auto-accompaniment styles include:

| Component | Description |
|-----------|-------------|
| Intro | Opening pattern |
| Main A-D | Main variations |
| Fill A-D | Transition fills |
| Ending | Closing pattern |
| Break | Pause pattern |

### File Formats

Sequences and styles can be stored:

| Format | Extension | Description |
|--------|-----------|-------------|
| KN Sequence | .SQT | Native sequencer format |
| Standard MIDI | .MID | Import/export |
| Style | .STY | Auto-accompaniment |

## Related Pages

- [MIDI Subsystem]({{ site.baseurl }}/midi-subsystem/) - MIDI I/O handling
- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) - Sound playback
- [Storage Subsystem]({{ site.baseurl }}/storage-subsystem/) - File save/load
- [System Overview]({{ site.baseurl }}/system-overview/) - Overall architecture

## Research Needed

- [ ] Document sequence data structure
- [ ] Analyze playback timing engine
- [ ] Map recording routines
- [ ] Understand style format
- [ ] Document chord recognition
- [ ] Identify quantization algorithms
- [x] Document medley playback system (see above)

## How to Contribute

See [Help Wanted]({{ site.baseurl }}/help-wanted/) for contribution guidelines.

The Table Data ROM at 0x800000 contains factory styles - analyzing this would help understand the format.
