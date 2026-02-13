---
layout: page
title: Feature Demo & Presentation System
permalink: /feature-demo/
---

# Feature Demo & Presentation System

The KN5000 firmware contains a **full XML-based presentation scripting system** used for the built-in Feature Demo. This system is significantly more sophisticated than a simple slideshow — it includes an XML parser, an event-driven presentation controller, and a rich tag vocabulary suggesting it was designed for general-purpose use.

## SSF Presentation Format

### Files in Table Data ROM

Two SSF (presumably "Show/Script/Sequence File") files are embedded in the Table Data ROM:

| File | ROM Address | Purpose |
|------|-------------|---------|
| `hkst_55.ssf` | 0x87FFF0 (metadata), 0x88000E (XML data) | Feature Demo presentation script |
| `hkt_87.ssf` | Near boot vectors (table_data.asm line 3855) | Unknown — possibly a second presentation |

**Source file:** `../../kn5000-roms-disasm/table_data/includes/hkst_55.ssf`

### XML Format

The Feature Demo script is real XML with a defined structure:

```xml
<ACTION>
  <ACT NO=1><SHOW OBJ="ftdemo01"></ACT>
  <ACT NO=2><SHOW OBJ="ftdemo04"></ACT>
  <ACT NO=3><SHOW OBJ="ftdemo05"></ACT>
  ...
  <ACT NO=27><SHOW OBJ="ftdemo48"></ACT>
</ACTION>
```

The script defines 27 sequential actions, each referencing a named UI object. Objects include `ftdemo01`–`ftdemo48` plus instrument-specific displays like `Accordion`, `Drawbar`, and `Sdmixer`.

---

## XML Tag Vocabulary

The firmware contains a complete XML tag name table at approximately line 87475 of the Program ROM disassembly (`kn5000_v10_program.asm`):

### Structure Tags

| Tag | Close Tag | Purpose |
|-----|-----------|---------|
| `PRESENTATION` | `/PRESENTATION` | Top-level presentation wrapper |
| `ACTION` | `/ACTION` | Action sequence container |
| `ACT` | `/ACT` | Individual action step (with `NO=` attribute) |

### Content Tags

| Tag | Close Tag | Purpose |
|-----|-----------|---------|
| `SHOW` | — | Show/display a named UI object |
| `IMG` | — | Display an image |
| `SONG` | — | Play a song or MIDI sequence |
| `FONT` | `/FONT` | Font selection for text rendering |
| `CENTER` | `/CENTER` | Text centering |
| `BR` | — | Line break |

### Attribute Tags

| Tag | Purpose |
|-----|---------|
| `SRC` | Source reference (file/resource) |
| `NAME` | Name identifier |

### Command Tags

| Tag | Purpose |
|-----|---------|
| **`EXEC`** | **Execute a command or routine** |

The `EXEC` tag is particularly notable — it strongly suggests the presentation format was designed to support executing code or commands as part of scripted presentations, going beyond simple display and playback.

---

## Presentation Handler Functions

The firmware implements a full event-driven presentation controller:

### Core Handlers

| Function | ROM Address | Line | Purpose |
|----------|-------------|------|---------|
| `AcFdemoScreenProc` | 0xF84149 | 308910 | Feature Demo screen handler |
| `AcPresentationBoxProc` | 0xF842B4 | 309070 | Presentation display widget |
| `AcPresentationControlProc` | 0xF8450B | 309287 | Main presentation controller |
| `IvDemofeature1Proc` | — | ~310702 | Feature Demo event handler 1 |
| `IvDemofeature2Proc` | — | ~310736 | Feature Demo event handler 2 |

`AcPresentationControlProc` is the main dispatch routine. It uses a jump table at `0xE9F9B2` to handle different presentation states/events.

### Event System

The firmware defines dedicated events for presentation processing:

| Event Constant | Line | Purpose |
|----------------|------|---------|
| `EV_READPRESENTATION` | 78181 | Read and parse a presentation file |
| `EV_READACTION` | 78180 | Read and process an action step |
| `EV_READSONG` | 78178 | Load and play a song reference |

These events integrate with the KN5000's broader UI event system (see [UI Framework]({{ site.baseurl }}/ui-framework/)).

---

## Feature Demo Assets

### Bitmap Images (Table Data ROM)

The Feature Demo includes 6 bitmap images stored in BMP format:

| Asset | ROM Address | Size | Content |
|-------|-------------|------|---------|
| `FTBMP01.BMP` | 0x880418 | ~78 KB | Technics logo with world globe |
| `FTBMP02.BMP` | 0x89344E | ~40 KB | Subwoofers |
| `FTBMP03.BMP` | 0x89DB04 | ~40 KB | Floppy discs |
| `FTBMP04.BMP` | 0x8A753A | ~40 KB | Inserting discs |
| `FTBMP05.BMP` | 0x8B0F70 | ~40 KB | Surround sound arrows |
| `FTBMP06.BMP` | 0x8BAFE6 | ~40 KB | KN5000 name with rainbow comet |

### UI Objects (Program ROM)

48 named UI objects are defined in the Program ROM (lines 36978–42354 of the disassembly):

- `ftdemo01` through `ftdemo48` — presentation step displays
- `Accordion` — accordion instrument display
- `Drawbar` — drawbar organ display
- `Sdmixer` — sound mixer display

Each object defines the visual content shown for its corresponding `<SHOW OBJ="...">` action in the SSF script.

---

## No Floppy Loading Path

Despite the sophisticated XML presentation infrastructure, **the current firmware does NOT load SSF files from floppy disc:**

1. **SSF parser reads from hardcoded ROM addresses.** The `AcPresentationControlProc` and related handlers are wired to data in the Table Data ROM (0x800000+), not to a floppy loading pipeline.

2. **No floppy disc type for presentations.** The [disc type signature table]({{ site.baseurl }}/system-update-discs/#disc-type-detection) has 8 entries covering firmware updates, custom data, and HDAE5000 — none for SSF or presentation files.

3. **Floppy I/O handles only data formats.** Beyond system updates, the floppy subsystem handles: MIDI songs (.MID), sequencer tracks (.SQT), styles (.STY), performance memories (.PMT), rhythm data (.RCM) — but NOT SSF presentations.

---

## Interpretation

The XML presentation system — with its `EXEC` tag, `SONG` playback, `IMG` display, rich tag vocabulary, and event-driven architecture — was almost certainly designed to be more flexible than its single current usage (a hardcoded Feature Demo in ROM).

The most likely explanation: **Technics designed a general-purpose presentation engine**, perhaps intended for:

- **Dealer demonstration discs** — scripted presentations showcasing the keyboard's features at retail stores
- **Educational materials** — step-by-step tutorials loaded from floppy
- **Trade show content** — automated demonstrations for NAMM or music trade events

The infrastructure was built (XML parser, event system, tag vocabulary, `EXEC` command support), but the floppy loading path was either never completed or was removed before release. What shipped was a single ROM-resident Feature Demo using a fraction of the system's capabilities.

The user's memory of "feature presentation discs" may refer to this planned-but-unshipped feature, or to the commercially-sold style/song demo discs that showcased the keyboard's capabilities using standard MIDI file playback.

---

## Related Pages

- [UI Framework]({{ site.baseurl }}/ui-framework/) — Widget system and event handling
- [System Update Discs]({{ site.baseurl }}/system-update-discs/) — Floppy disc format and update process
- [Storage Subsystem]({{ site.baseurl }}/storage-subsystem/) — Storage architecture overview
- [FDC Subsystem]({{ site.baseurl }}/fdc-subsystem/) — Floppy disk controller handlers
- [Image Gallery]({{ site.baseurl }}/image-gallery/) — Extracted graphics including FTBMP images

---

*Last updated: February 2026*
