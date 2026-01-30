---
layout: page
title: UI Framework
permalink: /ui-framework/
---

# UI Framework

> **Documentation Status: Placeholder**
>
> This page is a placeholder for future documentation. The UI system has been
> observed but the framework architecture needs detailed analysis.

## Overview

The KN5000 firmware includes a sophisticated UI framework that manages menu pages, parameter editing, and user interaction across the LCD display and control panel.

## Architecture (Presumed)

```
┌─────────────────────────────────────────────────────────────┐
│                      UI FRAMEWORK                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │    Page     │  │    Page     │  │    Page     │   ...    │
│  │   Manager   │  │   Stack     │  │  Renderer   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Widget    │  │    Event    │  │   Focus     │          │
│  │   System    │  │  Dispatch   │  │  Manager    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
   │ Control Panel │  │ LCD Display   │  │ MIDI Input    │
   │   Buttons     │  │  Rendering    │  │  (external)   │
   └───────────────┘  └───────────────┘  └───────────────┘
```

## Known Information

### UI Pages

ROM strings reveal these page identifiers:

| Page ID | Description |
|---------|-------------|
| MAIN_PAGE | Main operating screen |
| SOUND_PAGE | Sound/voice selection |
| STYLE_PAGE | Style selection |
| RECORD_PAGE | Sequencer recording |
| PLAY_PAGE | Playback controls |
| MIDI_PAGE | MIDI settings |
| UTILITY_PAGE | System utilities |
| PC_DATA_LINK_PAGE | PC connection (HDAE5000) |
| HDD_UTIL_PAGE | Hard disk utilities |

### Widget Types (Presumed)

Based on UI observation:

| Widget | Description |
|--------|-------------|
| Button | Pressable UI element |
| Slider | Value selection bar |
| List | Scrollable item list |
| Text | Static or editable text |
| Icon | Graphical indicator |
| Meter | Level/value display |

### Event Handling

The control panel protocol delivers events to the UI:

1. Button press/release
2. Encoder rotation
3. Pitch/mod wheel movement
4. MIDI input events

See [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) for event format.

## Related Pages

- [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) - Input handling
- [Display Subsystem]({{ site.baseurl }}/display-subsystem/) - Screen rendering
- [Image Gallery]({{ site.baseurl }}/image-gallery/) - UI graphics
- [System Overview]({{ site.baseurl }}/system-overview/) - Overall architecture

## Research Needed

- [ ] Identify page management routines
- [ ] Document widget rendering functions
- [ ] Map event dispatch mechanism
- [ ] Analyze focus/navigation system
- [ ] Document parameter editing flow
- [ ] Identify page transition routines

## How to Contribute

See [Help Wanted]({{ site.baseurl }}/help-wanted/) for contribution guidelines.

Search the main ROM disassembly for string references like "PAGE" to locate UI-related code.
