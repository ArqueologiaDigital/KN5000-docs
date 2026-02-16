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
           v                  v                  v
   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
   │ Control Panel │  │ LCD Display   │  │ MIDI Input    │
   │   Buttons     │  │  Rendering    │  │  (external)   │
   └───────────────┘  └───────────────┘  └───────────────┘
```

## Known Information

### Internal Module Names (Developer Code Names)

The firmware contains 11 UI subsystem modules with internal code names, likely named after the original Technics/Matsushita developers. These are initialized during boot via `InitializeObjectTable`:

| Module Name | Init Routine | Address | Purpose (Presumed) |
|-------------|--------------|---------|-------------------|
| **Murai** | `InitializeMurai` | 0xFA9712 | Core UI framework |
| **Toshi** | `InitializeToshi` | 0xFC0969 | Tone/sound selection UI |
| **East** | `InitializeEast` | 0xF63DFC | Eastern region/style UI |
| **Suna** | `InitializeSuna` | 0xF1B134 | Sound parameter UI |
| **Cheap** | `InitializeCheap` | 0xF96F22 | Basic parameter editing |
| **Scoop** | `InitializeScoop` | 0xF00658 | Display update manager |
| **Yoko** | `InitializeYoko` | 0xF2877C | Horizontal layout/scrolling |
| **Kubo** | `InitializeKubo` | 0xF2D2C4 | Grid/table layout |
| **Hama** | `InitializeHama` | 0xF17E34 | List handling |
| **KSS** | `InitializeKSS` | 0xFC09C7 | Keyboard/panel status |
| **Naka** | `InitializeNaka` | 0xF05A7C | Central dispatch |

These modules register "object tables" that define UI component hierarchies. The naming convention suggests this was an internal practice at Matsushita's development team, possibly using staff nicknames or project code names.

**Initialization sequence** (from `InitializeObjectTable` at 0xFA40B3):
```
InitializeMurai  →  InitializeToshi  →  InitializeEast  →
InitializeSuna   →  InitializeCheap  →  InitializeScoop →
InitializeYoko   →  InitializeKubo   →  InitializeHama  →
InitializeKSS    →  InitializeNaka
```

Related macros found in the source:
- `RegObjTableHama` - Register object table (Hama variant)
- `RegTitleHama` - Register title widget (Hama variant)
- `HamaListProc` - List processing procedure

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

## Presentation System (SSF)

The firmware includes a full **XML-based presentation scripting system** used for the built-in Feature Demo. This is a separate subsystem from the general widget framework, with its own XML parser, event handlers (`EV_READPRESENTATION`, `EV_READACTION`, `EV_READSONG`), and tag vocabulary (`PRESENTATION`, `ACTION`, `SHOW`, `IMG`, `SONG`, `EXEC`, etc.).

The presentation controller (`AcPresentationControlProc` at `0xF8450B`) dispatches actions via a jump table, and the Feature Demo script (`hkst_55.ssf`) drives a 27-step automated demonstration with bitmap images and instrument displays.

See [Feature Demo & Presentation System]({{ site.baseurl }}/feature-demo/) for full documentation.

## Related Pages

- [Feature Demo & Presentation System]({{ site.baseurl }}/feature-demo/) - SSF XML scripting system
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
