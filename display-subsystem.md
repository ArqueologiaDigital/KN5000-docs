---
layout: page
title: Display Subsystem
permalink: /display-subsystem/
---

# Display Subsystem

## Overview

The KN5000 uses a 320x240 color LCD driven by an MN89304 VGA-compatible controller. The display shows menus, parameters, song information, and graphical elements. Display updates are driven by the firmware's main event loop (not by a vertical blank interrupt).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        MAIN CPU                              │
│                                                              │
│  Graphics routines in Main ROM                              │
│  UI framework manages pages and widgets                     │
│  Display updates in main event loop (not VBI)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────┐
│                    MN89304 VGA CONTROLLER                    │
│                                                              │
│  Memory-mapped I/O: 0x1703B0-0x1703DF                       │
│  Resolution: 320 x 240 pixels                                │
│  Color depth: 8-bit indexed (256 colors)                    │
│  RAMDAC: 4-bit per channel (12-bit RGB)                     │
│  Row offset: svga_device::offset() << 3 (8x multiplier)    │
└─────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────┐
│                 VIDEO RAM (0x1A0000-0x1DFFFF)               │
│                                                              │
│  256KB linear framebuffer                                    │
│  Active area: 76,800 bytes (320 x 240 x 1 byte/pixel)      │
│  Row stride: 320 bytes                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────┐
│                      LCD PANEL                               │
│                                                              │
│  320 x 240 color TFT LCD                                    │
│  Backlit display                                             │
└─────────────────────────────────────────────────────────────┘
```

## MN89304 VGA Controller

The MN89304 is a VGA-compatible LCD controller with some important differences from standard VGA:

### Key Differences from Standard VGA

| Property | Standard VGA | MN89304 (KN5000) |
|----------|-------------|-------------------|
| DAC resolution | 6-bit per channel (0-63) | **4-bit per channel (0-15)** |
| Palette color depth | 18-bit RGB | **12-bit RGB** |
| Row pitch calculation | `offset` register value | `offset << 3` (8x multiplier) |
| I/O base | CPU port space | Memory-mapped at 0x170000 |

### VGA Register Map

VGA I/O ports are memory-mapped to CPU address `0x170000 + port_number`:

| VGA Port | CPU Address | Register | Access | Description |
|----------|-------------|----------|--------|-------------|
| 0x3C6 | 0x1703C6 | DAC Mask | R/W | Palette mask (typically 0xFF) |
| 0x3C7 | 0x1703C7 | DAC Read Index | W | Select palette entry for reading |
| 0x3C8 | 0x1703C8 | DAC Write Index | W | Select palette entry for writing |
| 0x3C9 | 0x1703C9 | DAC Data | R/W | RGB data (3 sequential bytes per entry) |
| 0x3D4 | 0x1703D4 | CRTC Index | W | Select CRTC register |
| 0x3D5 | 0x1703D5 | CRTC Data | R/W | CRTC register data |

### Palette Programming

The MN89304 uses a **4-bit RAMDAC** (implemented as `pal4bit()` in MAME). Only the lower 4 bits of each color component value are significant:

```c
// Writing a 256-color palette
for (int i = 0; i < 256; i++) {
    *(volatile uint8_t*)0x1703C8 = i;            // Select entry
    *(volatile uint8_t*)0x1703C9 = red[i] >> 4;  // 4-bit R (from 8-bit)
    *(volatile uint8_t*)0x1703C9 = green[i] >> 4; // 4-bit G
    *(volatile uint8_t*)0x1703C9 = blue[i] >> 4;  // 4-bit B
}
```

**Palette data format notes:**
- The HDAE5000 firmware stores palette data as 8-bit RGB and shifts right by 4 during loading
- If palette data is stored in 6-bit VGA format (0-63), shift right by 2 instead
- Effective color resolution: 4096 colors (16 levels per channel)

### CRTC Start Address

The CRTC start address determines which VRAM byte appears at the top-left pixel:

| CRTC Register | Index | Description |
|---------------|-------|-------------|
| Start Address High | 0x0C | High byte of VRAM start offset |
| Start Address Low | 0x0D | Low byte of VRAM start offset |

The firmware initializes the CRTC start address to `0x0000`, meaning VRAM address `0x1A0000` corresponds to screen pixel (0,0).

```c
// Reading current CRTC start address
*(volatile uint8_t*)0x1703D4 = 0x0C;
uint8_t start_high = *(volatile uint8_t*)0x1703D5;
*(volatile uint8_t*)0x1703D4 = 0x0D;
uint8_t start_low = *(volatile uint8_t*)0x1703D5;
uint16_t crtc_start = (start_high << 8) | start_low;
```

### Row Offset Override

The MN89304 overrides the standard VGA row offset calculation with an 8x multiplier:

```cpp
// In MAME: mn89304::offset()
uint32_t mn89304::offset() {
    return svga_device::offset() << 3;
}
```

This means the CRTC offset register value is multiplied by 8 to get the actual byte offset per row. The default configuration results in a 320-byte row stride (matching the 320-pixel width).

## Video RAM

| Property | Value |
|----------|-------|
| Base address | 0x1A0000 |
| Size | 256KB (0x1A0000-0x1DFFFF) |
| Active display area | 76,800 bytes (320 x 240) |
| Pixel format | 8-bit indexed color (1 byte per pixel) |
| Row stride | 320 bytes |
| Pixel addressing | `VRAM_BASE + y * 320 + x` |

The framebuffer is linear and row-major. The active display occupies the first 76,800 bytes; the remaining ~185KB is unused but accessible.

## Display Update Mechanism

### Main Loop Driven (Not VBI)

The firmware's display updates are **not driven by a vertical blank interrupt**. Instead, they occur as part of the main event loop at `LABEL_EF1245`:

```
Main Event Loop (LABEL_EF1245)
    |
    +-- Control Panel Poll
    +-- Display Update          <-- firmware draws its UI
    +-- MIDI Processing
    +-- FDC Handler
    +-- HDAE5000 Frame_Handler  <-- extension ROM callback
    +-- Audio Sync
    |
    (loop)
```

This means:
- Display updates happen at the main loop rate (not at a fixed refresh rate)
- The HDAE5000 Frame_Handler runs **after** the firmware's display update
- Any VRAM writes by extension code will be overwritten on the next loop iteration unless the firmware's drawing is disabled

### Display Disable Flag

The firmware checks a flag byte at address `0x0D53` before performing display updates. Setting bit 3 of this byte disables all firmware-driven LCD rendering:

```asm
; At 0xEF77DF (main display update gate):
BIT 3, (0D53h)           ; Check display disable flag
JRL Z, skip              ; If bit 3 CLEAR, skip display entirely
CALL Display_ResetDirtyFlags
; ... dispatches via state byte (0D65h) ...
CALL Display_UpdateDirtyRegions
```

This check occurs at four firmware locations (`0xEF77DF`, `0xEFAA40`, `0xF59C11`, `0xF59D65`), gating all display update code paths. When bit 3 is set, the firmware skips dirty-region tracking, state-based display dispatch, and VRAM writes — allowing an extension ROM to take full control of the framebuffer. See [HDAE5000 Homebrew]({{ site.baseurl }}/hdae5000-homebrew/#display-disable-flag-sfr-0x0d53-bit-3) for usage details.

### Workspace Display Callbacks

The firmware's workspace dispatch system provides display-related callbacks accessible via Handler Table A:

| Offset | Purpose | Notes |
|--------|---------|-------|
| +0x0124 | Display callback | Display state management |
| +0x0278 | Display state | Display mode/state queries |
| +0x0534 | Display update | Trigger display refresh |

These callbacks are used by the original HDAE5000 firmware for integrating its UI with the main firmware's display system. Their exact protocols are under investigation.

## Drawing Primitives

The firmware implements a complete graphics library for rendering to offscreen buffers. All drawing targets `OFFSCREEN_BUFFER_1` (0x43C00) by default, which is then blitted to VRAM (0x1A0000) during the display update cycle.

### Rendering Pipeline

```
Drawing functions write to OFFSCREEN_BUFFER_1 (0x43C00)
     │
     ├── SetChangeRect() expands dirty bounding box
     │
     └── Display update cycle blits changed regions to VRAM (0x1A0000)
```

### Address Calculation

All drawing functions convert (x, y) pixel coordinates to buffer offsets using:

```
offset = y * 320 + x
```

The multiplication `y * 320` is computed via shifts: `(y << 2 + y) << 6 = y * 5 * 64`. This is implemented in the shared helper `Set_XWA_to_320_times_XDE` at `0xEF5023`.

### Drawing Modes

Several primitives support multiple drawing modes specified by a mode code:

| Mode | Code | Operation | Description |
|------|------|-----------|-------------|
| Write | 0x201 | `pixel = color` | Direct pixel write |
| Clear | 0x202 | `pixel = 0x00` | Clear pixel to zero |
| OR | 0x203 | `pixel |= color` | Bitwise OR with color |
| AND | 0x204 | `pixel &= color` | Bitwise AND with mask |
| XOR | 0x205 | `pixel ^= color` | Bitwise XOR (used for cursors, selection) |

### Special Colors

| Color | Meaning |
|-------|---------|
| 0xF7 | Transparent (pixel skipped, no write) |
| 0xF5 | Read-back: reads pixel from secondary buffer (pattern fill) |

### Memory Operations

| Function | Address | Description |
|----------|---------|-------------|
| `Copy_DE_words_from_XBC_to_XWA` | 0xEF18D7 | Block copy using LDIRW. Blits offscreen → VRAM |
| `Fill_memory_at_XWA_with_DE_words_of_BC_value` | 0xEF18E0 | Fill memory with 16-bit pattern (buffer clear) |

### Pixel Operations

| Function | Address | Description |
|----------|---------|-------------|
| `ReadPixel` | 0xFAA7B4 | Read 8-bit color from offscreen buffer at (x, y) |
| `ModifyPixel` | 0xFAA7E4 | Write single pixel to offscreen buffer |
| `ModifyPixelEx` | 0xFAA84A | Extended pixel op: write/clear/OR/AND/XOR modes |

### Rectangle Operations

| Function | Address | Description |
|----------|---------|-------------|
| `VRAM_FillRect` | 0xEF50DF | Fill 6×12 pixel rect directly in VRAM with solid color |
| `DrawWall` | 0xFABB74 | Fill entire screen from source buffer (wallpaper/splash) |

### Line Drawing

| Function | Address | Description |
|----------|---------|-------------|
| `DrawLine` | 0xFAA98A | Bresenham line from point A to point B |
| `DrawLineEx` | 0xFAAA3E | Extended line with drawing mode (write/XOR/etc.) |

Both use Bresenham's algorithm with optimized fast paths for horizontal lines (`dy = 0`), vertical lines (`dx = 0`), and general diagonal lines. The color 0xF5 triggers pattern-fill mode where each pixel's color is read from a secondary buffer instead of using a fixed color.

### Bitmap/Sprite Drawing

The firmware uses a **bitmap descriptor table** in ROM at `0x913000`. Each entry is 8 bytes:

```
+0x00: word  width (pixels)
+0x02: word  height (rows)
+0x04: long  pixel_data_ptr (24-bit address of pixel data in ROM)
```

Bitmap pixel data is stored as packed 16-bit words (2 pixels per word). Color `0xF7` in bitmap data is treated as transparent (pixel skipped).

| Function | Address | Description |
|----------|---------|-------------|
| `DrawBitmap` | 0xFABC3A | Draw bitmap with transparency (0xF7 = transparent) |
| `DrawBitmapFast` | 0xFABE0E | Draw bitmap without transparency check (opaque only) |
| `MovePixels` | 0xFABA60 | Copy rectangular pixel block within offscreen buffer |
| `Draw_FlashMemUpdate_message_bitmap` | 0xEF5040 | Draw 224×22 monochrome (1bpp) bitmap for firmware update UI |

### Text Rendering

Text is rendered using a **font glyph table** in ROM at `0x945C00`. Each font entry is 16 bytes:

```
+0x00: word  char_width (pixels per character)
+0x02: word  char_height (pixels)
+0x04: word  descent (below baseline)
+0x06: word  ascent (above baseline)
+0x08: long  glyph_bitmap_ptr (1bpp bitmap data, 8 pixels per byte, MSB first)
+0x0C: long  kerning_table_ptr (0 = fixed-width font)
```

Character codes are offset by 0x20 (space) before table lookup. Glyphs are rendered as 1bpp bitmaps decomposed into 8-pixel-wide vertical strips, drawn left-to-right, top-to-bottom. All text rendering clips against a specified rectangle.

| Function | Address | Description |
|----------|---------|-------------|
| `DrawString` | 0xFACACE | Core text renderer: draws null-terminated string |
| `DrawStringCentered` | 0xFACF17 | Center text horizontally and vertically in rect |
| `DrawStringLeftJustify` | 0xFACFBA | Left-align text (x = rect.left + 4), center vertically |
| `DrawStringRightJustify` | 0xFAD004 | Right-align text (x = rect.right - 4 - width) |
| `DrawStringAlignment` | 0xFAD052 | Dispatch by mode: 0=center, 1=left, 2=right |
| `DrawStringReverse` | 0xFAD091 | Draw with swapped fg/bg colors (selection highlight) |

### Font Helper Functions

| Function | Address | Description |
|----------|---------|-------------|
| `GetCharHeight` | 0xFB25ED | Return character height from font table (+0x02) |
| `GetCharDescent` | 0xFB25F9 | Return character descent from font table (+0x04) |
| `CalcTotalWidth` | 0xFB270D | Calculate total pixel width of rendered string |
| `ConvertStrings` | 0xFB264F | Convert control codes to displayable format (0x7E prefix = escape) |
| `WordwrapStrings` | 0xFB26D2 | Word-wrap text for multi-line layout |

### Character Encoding

Characters use ASCII encoding with an offset of `0x20` (space). Before lookup in the font or kerning table, each character code has `0x20` subtracted. Control characters below `0x20` are mapped to space.

**Escape sequences:** The `0x7E` prefix byte introduces a two-digit hex-encoded character code:
```
0x7E 0x33 0x41  →  character 0x3A (colon)
0x7E 0x46 0x37  →  character 0xF7 (special symbol)
```

Hex digits support `0-9`, `a-f`, and `A-F`.

## Screen Layout and Regions

### Region Architecture

The display is divided into 11 independently-tracked dirty regions. Each region has its own redraw function and dirty bit. The regions are not defined by hardcoded pixel coordinates — instead, each redraw function loads **ROM descriptor tables** that define the region geometry, content, and rendering parameters. These descriptors are passed to UI rendering helper functions.

### Region Update Order

`Display_UpdateDirtyRegions` (0xEF5B36) updates regions in a specific order optimized for visual priority:

```
1. Region 0  - Status Bar         (mode indicators, tempo)
2. Region 5  - Menu Area          (menu/list content)
3. Region 7  - Parameter Display  (parameter names)
4. Region 8  - Value Display      (parameter values)
5. Region 9  - Indicator Area     (status indicators)
6. Region 1  - Title Bar          (song/patch name, up to 3 title fields)
7. Region 10 - Footer Area        (status/help text)
8. Region 6  - Button Labels      (soft button labels, 3 rows of 8)
9. Region 3  - Main Content       (primary display area)
10. Region 4 - Side Panel         (side parameters)
11. Region 2 - Selection          (highlight/cursor, drawn last for overlay)
```

### Redraw Functions

Each region has a dedicated redraw function that references ROM descriptor tables:

| Region | Redraw Function | Address | ROM Descriptors (examples) |
|--------|-----------------|---------|---------------------------|
| 0 | `Display_RedrawStatusBar` | 0xF00999 | 0xE0B905, 0xE0B92E, 0xE0B99D |
| 1 | `Display_RedrawTitleBar` | 0xF00C89 | 0xE0BD52-0xE0BD7A (3 title fields) |
| 2 | `Display_RedrawSelection` | 0xF00DA5 | Variable (cursor overlay) |
| 3 | `Display_RedrawMainContent` | 0xF00C33 | 0xE0BD89 |
| 4 | `Display_RedrawSidePanel` | 0xF00E35 | Multiple descriptor sets |
| 5 | `Display_RedrawMenu` | 0xEFF110 | Complex menu rendering |
| 6 | `Display_RedrawButtonLabels` | 0xF00FDC | 0xE0C764, 0xE0C8CC, 0xE0BF6E |
| 7 | `Display_RedrawParameters` | 0xEF6F1A | State-dependent |
| 8 | `Display_RedrawValues` | 0xEF6FA3 | State-dependent |
| 9 | `Display_RedrawIndicators` | 0xEF704B | State-dependent |
| 10 | `Display_RedrawFooter` | 0xF00C4A | 0xE0BDAC, 0xE0BDE8, 0xE0BE06 |

### Display State

The display state byte at address `0x0D65` (SFR 3429) selects the active screen mode:

| Value | Mode |
|-------|------|
| 0 | Default/normal display |
| 2 | Alternative layout (different descriptor sets used) |

The state byte influences which ROM descriptors are selected by redraw functions, allowing the same regions to display different content based on the active screen mode.

### UI Rendering Helpers

The redraw functions delegate to specialized rendering helpers:

| Helper | Address | Purpose |
|--------|---------|---------|
| `LABEL_F0212C` | 0xF0212C | General UI element renderer |
| `LABEL_FB15F6` | 0xFB15F6 | Two-descriptor pair renderer |
| `LABEL_FB1594` | 0xFB1594 | Simple descriptor renderer |
| `LABEL_F01930` | 0xF01930 | Content area renderer |
| `LABEL_F01DAB` | 0xF01DAB | Number/value display renderer |
| `LABEL_F023CF` | 0xF023CF | Dynamic value renderer |
| `LABEL_FB2044` | 0xFB2044 | Parameter display renderer |
| `LABEL_FB24CB` | 0xFB24CB | Status indicator renderer |

### Button Label Organization

Region 6 (button labels) manages three rows of 8 soft-button labels, organized at RAM addresses:
- Row 1: 0x0E55 (8 entries, 4 bytes apart)
- Row 2: 0x0E75 (8 entries, 4 bytes apart)
- Row 3: 0x0E95 (8 entries, 4 bytes apart)

### Dirty Region Tracking

The display update system tracks 11 independent screen regions. Each region has a dirty bit in the bitmap at `DISPLAY_DIRTY_FLAGS` (0x205E4):

| Function | Address | Description |
|----------|---------|-------------|
| `Display_ResetDirtyFlags` | 0xEF5B27 | Clear all dirty flags and enable flag |
| `Display_UpdateDirtyRegions` | 0xEF5B36 | Check all 11 regions, call redraw for dirty ones |
| `Display_UpdateRegion0` | 0xEF5B8B | Status bar |
| `Display_UpdateRegion1` | 0xEF5BE9 | Title bar |
| `Display_UpdateRegion2` | 0xEF5C20 | Selection highlight |
| `Display_UpdateRegion3` | 0xEF5C07 | Main content area |
| `Display_UpdateRegion4` | 0xEF5C39 | Side panel |
| `Display_UpdateRegion5` | 0xEF5C52 | Menu area |
| `Display_UpdateRegion6` | 0xEF5C6B | Button labels |
| `Display_UpdateRegion7` | 0xEF5C84 | Parameter display |
| `Display_UpdateRegion8` | 0xEF5C9D | Value display |
| `Display_UpdateRegion9` | 0xEF5CB6 | Indicator area |
| `Display_UpdateRegion10` | 0xEF5CCF | Footer area |

### Change Tracking

| Function | Address | Description |
|----------|---------|-------------|
| `SetChangeRect` | 0xFAA760 | Expand dirty bounding box to include drawn region |

The bounding box is maintained at:

| Address | Purpose |
|---------|---------|
| 0x030456 | Min X (left edge) |
| 0x030458 | Min Y (top edge) |
| 0x03045A | Max X (right edge) |
| 0x03045C | Max Y (bottom edge) |
| 0x03045E | Update flag (non-zero = needs refresh) |

### Offscreen Buffers

| Buffer | Address | Size | Purpose |
|--------|---------|------|---------|
| OFFSCREEN_BUFFER_1 | 0x043C00 | 76,800 bytes | Primary render target (all drawing goes here) |
| OFFSCREEN_BUFFER_2 | 0x056800 | 76,800 bytes | Secondary buffer (scrolling/animation) |
| OFFSCREEN_BUFFER_3 | 0x05FE00 | 76,800 bytes | Tertiary buffer (compositing) |
| OFFSCREEN_BUFFER_4 | 0x069400 | 76,800 bytes | Quaternary buffer (sprites/overlays) |

## Embedded Images

Images extracted from firmware ROMs:

| Source | Count | Description |
|--------|-------|-------------|
| Main CPU ROM | 42 | UI elements, logos, demo graphics |
| HDAE5000 ROM | 4 | Product logo, file panel graphics |

See [Image Gallery]({{ site.baseurl }}/image-gallery/) for all extracted images.

## Display Modes

The KN5000 uses a single display mode:

| Property | Value |
|----------|-------|
| Width | 320 pixels |
| Height | 240 pixels |
| Color Depth | 8-bit (256 color palette) |
| RAMDAC | 4-bit per channel (12-bit effective RGB) |
| Refresh | Main-loop driven (not fixed rate) |

## Related Pages

- [HDAE5000 Homebrew Development]({{ site.baseurl }}/hdae5000-homebrew/) - Display ownership for custom ROMs
- [Image Gallery]({{ site.baseurl }}/image-gallery/) - Extracted firmware graphics
- [UI Framework]({{ site.baseurl }}/ui-framework/) - Menu and widget system
- [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) - Physical components
- [System Overview]({{ site.baseurl }}/system-overview/) - Overall architecture

## Research Needed

- [x] Document VGA register map at 0x170000
- [x] Analyze framebuffer memory layout
- [x] Understand display update mechanism (main loop, not VBI)
- [x] Document MN89304 differences from standard VGA (4-bit RAMDAC, offset override)
- [x] Identify display disable mechanism (0x0D53 bit 3)
- [x] Identify font rendering routines (DrawString family, font table at 0x945C00)
- [x] Document text drawing functions (DrawString, Centered, Left/Right, Reverse, Alignment)
- [x] Map UI widget drawing primitives (pixel, line, rect, bitmap, text, blit)
- [ ] Understand page transition effects
- [ ] Document workspace display callbacks (0x0124, 0x0278, 0x0534) protocols

## How to Contribute

See [Help Wanted]({{ site.baseurl }}/help-wanted/) for contribution guidelines.

The HDAE5000 ROM has documented VGA palette setup at `0x28F8E0` which can serve as a reference for understanding the display interface.
