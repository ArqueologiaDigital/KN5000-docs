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

## How to Contribute

See [Help Wanted]({{ site.baseurl }}/help-wanted/) for contribution guidelines.

The Table Data ROM at 0x800000 contains factory styles - analyzing this would help understand the format.
