---
layout: page
title: Display Subsystem
permalink: /display-subsystem/
---

# Display Subsystem

> **Documentation Status: Placeholder**
>
> This page is a placeholder for future documentation. The display subsystem hardware
> is documented but the firmware graphics routines need analysis.

## Overview

The KN5000 uses a 320x240 color LCD driven by an MN89304 VGA-compatible controller. The display shows menus, parameters, song information, and graphical elements.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        MAIN CPU                              │
│                                                              │
│  Graphics routines in Main ROM                              │
│  UI framework manages pages and widgets                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              v
┌─────────────────────────────────────────────────────────────┐
│                    MN89304 VGA CONTROLLER                    │
│                                                              │
│  Memory-mapped at: 0x170000                                 │
│  Resolution: 320 x 240 pixels                                │
│  Color depth: 8-bit indexed (256 colors)                    │
│  DAC ports: 0x3C8 (index), 0x3C9 (RGB data)                 │
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

## Known Information

### Hardware Components

| Component | Address | Description |
|-----------|---------|-------------|
| VGA Base | 0x170000 | VGA controller registers |
| Palette Index | 0x1703C8 | Write palette entry index |
| Palette Data | 0x1703C9 | Write R, G, B values |
| HDAE5000 Palettes | 0x2E5DCE, 0x2E61CE | Palette data in expansion ROM |

### VGA Register Access

VGA I/O ports are memory-mapped to 0x170000 + port number:

```c
// Write palette entry
*(uint8_t*)0x1703C8 = palette_index;  // Select entry
*(uint8_t*)0x1703C9 = red >> 2;       // 6-bit R
*(uint8_t*)0x1703C9 = green >> 2;     // 6-bit G
*(uint8_t*)0x1703C9 = blue >> 2;      // 6-bit B
```

### Embedded Images

Images extracted from firmware ROMs:

| Source | Count | Description |
|--------|-------|-------------|
| Main CPU ROM | 42 | UI elements, logos, demo graphics |
| HDAE5000 ROM | 4 | Product logo, file panel graphics |

See [Image Gallery]({{ site.baseurl }}/image-gallery/) for all extracted images.

## Display Modes

The KN5000 appears to use a single 320x240x8 display mode:

| Property | Value |
|----------|-------|
| Width | 320 pixels |
| Height | 240 pixels |
| Color Depth | 8-bit (256 color palette) |
| Palette | Software-defined, 6-bit per channel |

## Related Pages

- [Image Gallery]({{ site.baseurl }}/image-gallery/) - Extracted firmware graphics
- [UI Framework]({{ site.baseurl }}/ui-framework/) - Menu and widget system
- [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) - Physical components
- [System Overview]({{ site.baseurl }}/system-overview/) - Overall architecture

## Research Needed

- [ ] Document complete VGA register set at 0x170000
- [ ] Analyze framebuffer memory layout
- [ ] Identify font rendering routines
- [ ] Document text drawing functions
- [ ] Map UI widget drawing primitives
- [ ] Understand page transition effects

## How to Contribute

See [Help Wanted]({{ site.baseurl }}/help-wanted/) for contribution guidelines.

The HDAE5000 ROM has documented VGA palette setup at `0x28F8E0` which can serve as a reference for understanding the display interface.
