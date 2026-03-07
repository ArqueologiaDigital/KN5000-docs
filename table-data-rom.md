---
layout: page
title: Table Data ROM
permalink: /table-data-rom/
---

# Table Data ROM Structure

The Table Data ROM is a 2MB flash ROM mapped at **0x800000-0x9FFFFF** after boot-time memory reconfiguration. At power-on, the CPU sees it at 0xE00000-0xFFFFFF (overlapping the Program ROM), and the first-stage bootloader at the end of this ROM handles initial hardware setup before remapping.

This ROM contains factory preset data, waveform samples, fonts, UI icons, wallpapers, demo songs, and the first-stage bootloader code.

## ROM Layout

| Address Range | Size | Contents |
|:---|:---|:---|
| `0x800000-0x800087` | 136B | Section Directory Table (33 pointers) |
| `0x800088-0x87FFEF` | 512KB | Preset Data Banks |
| `0x87FFF0-0x8CFFFF` | 320KB | Feature Demo Data |
| `0x8D0000-0x8DFFFF` | 64KB | Unused (0xFF fill) |
| `0x8E0000-0x8ECFFF` | 52KB | LZSS Compressed Presets |
| `0x8ED000-0x937FFF` | 300KB | Wallpapers + gap data |
| `0x938000-0x944D77` | 51KB | UI Icons |
| `0x944D78-0x9F9FFF` | 753KB | Mixed Data Tables |
| `0x9FA000-0x9FA14F` | 336B | File Identifier Strings |
| `0x9FA150-0x9FB4D1` | ~5KB | Boot Screen Bitmaps |
| `0x9FB4D2-0x9FB4E7` | 22B | Boot Data Tables |
| `0x9FB4E8-0x9FFFFF` | 19KB | First-Stage Bootloader + IVT |

## Section Directory Table (0x800000)

The ROM begins with a directory of 33 four-byte little-endian pointers, terminated by a null entry. Each pointer addresses a preset data bank within the ROM. These sections are read/written during floppy disk save/load operations (`FDC_WriteSectors`).

Factory-default fill patterns indicate the initialization state of each bank:
- **0xF7**: Erased flash (unprogrammed)
- **0x07**: Default parameter values
- **0x00**: Zeroed slots
- **0xFF**: Empty/unwritten

Notable section groupings:
- **Entries 12-24**: 13 identical 3,016-byte slots (zero-filled) -- user registration memory
- **Entries 25-27**: 3 identical 31,968-byte slots (0xFF-filled) -- large user data banks
- **Entry 7**: 983KB -- largest section, mostly erased flash

## Font System (0x945C00)

The font descriptor table contains **10 font entries**, each 16 bytes:

| Offset | Size | Field |
|:---|:---|:---|
| +0x00 | word | Width (pixels, 0 = proportional) |
| +0x02 | word | Height (pixels) |
| +0x04 | word | Descent |
| +0x06 | word | Ascent |
| +0x08 | long | Pointer to glyph bitmap data |
| +0x0C | long | Pointer to kerning table (0 = fixed-width) |

Font glyphs are stored as **1bpp bitmaps** (8 pixels per byte, MSB first), located at 0x945CB0-0x94FFFF. The `DrawString` routine at 0xFA7E7C in the Main CPU ROM renders text using these fonts.

## Waveform Sample Table (0x9C4000)

A pointer table of **19 entries** (4-byte LE pointers), terminated by a null entry. The first 18 entries point to variable-length PCM waveform samples in the 0x9C4050-0x9F9FFF range. Entry 18 points to 0x8E0000 (the LZSS compressed preset area).

Access pattern in main CPU code:
```
extz wa          ; zero-extend sample index
sla wa, 2        ; multiply by 4 (pointer size)
extz xwa
add xwa, 0x9C4000  ; add table base
ld xwa, (xwa)      ; load sample pointer
```

## Model-Specific Preset Tables (0x986000/0x987000)

Two pointer tables are selected based on the keyboard model code stored in RAM:
- **0x986000**: Used when model = 0xC2 (KN3000) or 0xC5 (KN5000)
- **0x987000**: Used for other model variants

Each table contains 4-byte LE pointers to 198-byte preset records in the 0x951000 region. These records contain sound program names (e.g., "Easy Listening", "German Schlager") and associated parameters.

## Demo Song System (0x988000)

The demo song index table at 0x988000 contains **12 entries** of 4-byte LE pointers to demo song data in the 0x988030-0x9963FA range.

Demo category names at 0x99EC00 include:
- "Tour Of The 5000"
- "Accordion", "Piano Styles", "Jazz&Rock Organ"
- "Church & Theatre", "Light Orchestra"
- "Split Sounds", "Layer Production"
- "Special DSP FX", "World", "xPiano Atmosphere"

## UI Icons (0x938000)

**176 icons**, all 24x24 pixels at 4bpp (16 colors), 288 bytes each. The icon table (8 bytes per entry) precedes the pixel data:

| Offset | Size | Field |
|:---|:---|:---|
| +0x00 | word | Bounding box width (for UI hit-testing) |
| +0x02 | word | Bounding box height |
| +0x04 | long | Pointer to pixel data |

Icons use a 16-color CGA/EGA-style palette. The color lookup table at 0xEAABF2 expands 4-bit nibbles to 8-bit palette indices.

## Wallpapers (0x8ED000)

Two preset wallpaper images for the LCD background:
- **Wallpaper 0** (0x8ED000): Blue textured pattern, 320x240 @ 8bpp = 76,800 bytes
- **Wallpaper 1** (0x900000): Technics branded texture, same format

Referenced by `SetWallPaper` via the wallpaper table at 0xEAAE62 in the Main CPU ROM.

## LZSS Compressed Presets (0x8E0000)

Factory preset data compressed using **SLIDE4K** algorithm. The section begins with an ASCII "SLIDE4K" marker followed by compression parameters and the compressed data stream (~28KB).

Decompresses to ~33KB of parameter data (MIDI-range values 0-127). Referenced by `SubCPU_Send_Payload` during boot. If decompression fails, firmware falls back to data at 0x830000.

## First-Stage Bootloader (0x9FB4E8)

The bootloader code runs at power-on when the CPU sees this ROM at 0xFFxxxx. It:

1. Initializes CPU registers and memory controller
2. Sets up stack pointer at 0x00987E
3. Clears RAM (35KB at 0x104E, 1KB at 0x0C00)
4. Copies boot data tables to RAM
5. Detects region code and boot mode
6. Checks for floppy disk firmware update
7. Validates flash integrity
8. Reconfigures CS2 to remap ROM to 0x800000
9. Jumps to main Program ROM entry point at 0xFFFEDC

## File Identifier Strings (0x9FA000)

Format identification strings used to detect floppy disk file types:
- `Technics KN5000 Program  DATA FILE 1/2`
- `Technics KN5000 Program  DATA FILE 2/2`
- `Technics KN5000 Program  DATA FILE PCK`
- `Technics KN5000 Table    DATA FILE 1/2`
- `Technics KN5000 Table    DATA FILE 2/2`
- `Technics KN5000 Table    DATA FILE PCK`
- `Technics KN5000 CMPCUSTOMDATA FILE`
- `Technics KN5000 HD-AEPRG DATA FILE`

## Boot Screen Bitmaps (0x9FA150)

1bpp bitmaps displayed during firmware update:
- "Flash Memory Update"
- "Now Erasing"
- "FD to Flash Memory"
- "Completed"
- "Please Wait"
- "Change FD 2 of 2"
- "Illegal Disk"
- "Turn On AGAIN"
