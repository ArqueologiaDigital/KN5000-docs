---
layout: page
title: Image Gallery
permalink: /image-gallery/
---

# Embedded Image Gallery

Images extracted from the KN5000 firmware ROMs. These graphics are displayed on the built-in LCD screen (320x240 pixels, controlled by IC206 MN89304).

## Feature Demo Images (Table Data ROM)

These BMP images are used in the keyboard's feature demonstration mode.

### System Update Bitmaps

The Table Data ROM also contains 8 system update message bitmaps at address `0x9FA156`. These are 1-bit monochrome images (224x22 pixels) similar to those in the Main CPU ROM, but stored with different byte ordering due to the 16-bit interleaved ROM bus architecture.

| Address | Image | Purpose |
|---------|-------|---------|
| 0x9FA156 | Flash Memory Update | Update in progress |
| 0x9FA3BE | Now Erasing | Flash erase in progress |
| 0x9FA626 | FD to Flash Memory | Copying from floppy |
| 0x9FA88E | Completed | Operation complete |
| 0x9FAAF6 | Please Wait | Processing |
| 0x9FAD5E | Change FD 2 of 2 | Multi-disk prompt |
| 0x9FAFC6 | Illegal Disk | Invalid disk error |
| 0x9FB22E | Turn On AGAIN | Restart instruction |

**Note:** These bitmaps are NOT byte-identical to the Main CPU versions despite showing the same text messages. The Table Data ROM uses a 16-bit bus with odd/even byte interleaving, which causes a different byte arrangement when the graphics hardware accesses the data. Both sets of images must be maintained separately to achieve byte-accurate ROM reconstruction.

### FTBMP01 - Demo Screen 1

![FTBMP01]({{ "/assets/images/gallery/FTBMP01.png" | relative_url }})

*320x240, 8-bit color*

### FTBMP02 - Demo Screen 2

![FTBMP02]({{ "/assets/images/gallery/FTBMP02.png" | relative_url }})

*320x130, 8-bit color*

### FTBMP03 - Demo Screen 3

![FTBMP03]({{ "/assets/images/gallery/FTBMP03.png" | relative_url }})

*320x120, 8-bit color*

### FTBMP05 - Demo Screen 5

![FTBMP05]({{ "/assets/images/gallery/FTBMP05.png" | relative_url }})

*320x125, 8-bit color*

### FTBMP06 - Demo Screen 6

![FTBMP06]({{ "/assets/images/gallery/FTBMP06.png" | relative_url }})

*320x240, 8-bit color*

**Note:** FTBMP04 has a corrupted header and could not be converted.

---

## Main CPU ROM Images

These images were extracted from raw bitmap data in the main CPU ROM and converted to PNG.

### Status Messages (1-bit bitmaps, 224x22 pixels)

| Image | Filename | Purpose |
|-------|----------|---------|
| ![Flash Memory Update]({{ "/assets/images/gallery/Bitmap_1bit_Flash_Memory_Update.png" | relative_url }}) | `Bitmap_1bit_Flash_Memory_Update.bin` | Flash Memory Update message |
| ![Now Erasing]({{ "/assets/images/gallery/Bitmap_1bit_Now_Erasing.png" | relative_url }}) | `Bitmap_1bit_Now_Erasing.bin` | Now Erasing message |
| ![FD to Flash Memory]({{ "/assets/images/gallery/Bitmap_1bit_FD_to_Flash_Memory.png" | relative_url }}) | `Bitmap_1bit_FD_to_Flash_Memory.bin` | FD to Flash Memory message |
| ![Completed]({{ "/assets/images/gallery/Bitmap_1bit_Completed.png" | relative_url }}) | `Bitmap_1bit_Completed.bin` | Completed message |
| ![Please Wait]({{ "/assets/images/gallery/Bitmap_1bit_Please_Wait.png" | relative_url }}) | `Bitmap_1bit_Please_Wait.bin` | Please Wait message |
| ![Change FD 2 of 2]({{ "/assets/images/gallery/Bitmap_1bit_Change_FD_2_of_2.png" | relative_url }}) | `Bitmap_1bit_Change_FD_2_of_2.bin` | Change FD 2 of 2 message |
| ![Illegal Disk]({{ "/assets/images/gallery/Bitmap_1bit_Illegal_Disk.png" | relative_url }}) | `Bitmap_1bit_Illegal_Disk.bin` | Illegal Disk error |
| ![Turn On AGAIN]({{ "/assets/images/gallery/Bitmap_1bit_Turn_On_AGAIN.png" | relative_url }}) | `Bitmap_1bit_Turn_On_AGAIN.bin` | Turn On AGAIN instruction |

### Logos

| Image | Filename | Dimensions | Description |
|-------|----------|------------|-------------|
| ![Technics Logo]({{ "/assets/images/gallery/BitmapTechnicsLogo.png" | relative_url }}) | `BitmapTechnicsLogo.bin` | 312x45, 8-bit | Technics brand logo |
| ![KN5000 Logo]({{ "/assets/images/gallery/BitmapKN5000Logo.png" | relative_url }}) | `BitmapKN5000Logo.bin` | 200x36, 8-bit | KN5000 model logo |

### Split Point Indicators (58x52 pixels, 8-bit)

These images show keyboard split point notes displayed when configuring the keyboard split.

| Image | Note |
|-------|------|
| ![Split C]({{ "/assets/images/gallery/BitmapSplitPoint_C.png" | relative_url }}) | C |
| ![Split Db]({{ "/assets/images/gallery/BitmapSplitPoint_Db.png" | relative_url }}) | Db |
| ![Split D]({{ "/assets/images/gallery/BitmapSplitPoint_D.png" | relative_url }}) | D |
| ![Split Eb]({{ "/assets/images/gallery/BitmapSplitPoint_Eb.png" | relative_url }}) | Eb |
| ![Split E]({{ "/assets/images/gallery/BitmapSplitPoint_E.png" | relative_url }}) | E |
| ![Split F]({{ "/assets/images/gallery/BitmapSplitPoint_F.png" | relative_url }}) | F |
| ![Split Gb]({{ "/assets/images/gallery/BitmapSplitPoint_Gb.png" | relative_url }}) | Gb |
| ![Split G]({{ "/assets/images/gallery/BitmapSplitPoint_G.png" | relative_url }}) | G |
| ![Split Ab]({{ "/assets/images/gallery/BitmapSplitPoint_Ab.png" | relative_url }}) | Ab |
| ![Split A]({{ "/assets/images/gallery/BitmapSplitPoint_A.png" | relative_url }}) | A |
| ![Split Bb]({{ "/assets/images/gallery/BitmapSplitPoint_Bb.png" | relative_url }}) | Bb |
| ![Split B]({{ "/assets/images/gallery/BitmapSplitPoint_B.png" | relative_url }}) | B |
| ![No Split]({{ "/assets/images/gallery/BitmapSplitPoint_no_split.png" | relative_url }}) | No Split |

### Drawbar Sliders (22x222 pixels, 8-bit)

| Image | Filename | Description |
|-------|----------|-------------|
| ![Drawbar 1]({{ "/assets/images/gallery/BitmapDrawbarNumberedSlider_1.png" | relative_url }}) | `BitmapDrawbarNumberedSlider_1.bin` | Drawbar slider 1 |
| ![Drawbar 2]({{ "/assets/images/gallery/BitmapDrawbarNumberedSlider_2.png" | relative_url }}) | `BitmapDrawbarNumberedSlider_2.bin` | Drawbar slider 2 |
| ![Drawbar 3]({{ "/assets/images/gallery/BitmapDrawbarNumberedSlider_3.png" | relative_url }}) | `BitmapDrawbarNumberedSlider_3.bin` | Drawbar slider 3 |

### MIDI Connection Diagrams (296x108 pixels, 8-bit)

| Image | Filename | Description |
|-------|----------|-------------|
| ![MIDI 1]({{ "/assets/images/gallery/BitmapMIDIConnections_1.png" | relative_url }}) | `BitmapMIDIConnections_1.bin` | MIDI connections diagram 1 |
| ![MIDI 2]({{ "/assets/images/gallery/BitmapMIDIConnections_2.png" | relative_url }}) | `BitmapMIDIConnections_2.bin` | MIDI connections diagram 2 |
| ![MIDI 3]({{ "/assets/images/gallery/BitmapMIDIConnections_3.png" | relative_url }}) | `BitmapMIDIConnections_3.bin` | MIDI connections diagram 3 |

### UI Elements

| Image | Filename | Dimensions | Description |
|-------|----------|------------|-------------|
| ![Worm]({{ "/assets/images/gallery/BitmapWormWearingHat.png" | relative_url }}) | `BitmapWormWearingHat.bin` | 24x24, 8-bit | Easter egg - worm wearing hat |
| ![Arrows]({{ "/assets/images/gallery/BitmapSomeArrows.png" | relative_url }}) | `BitmapSomeArrows.bin` | 294x6, 8-bit | Arrow icons strip |

### Transition Effects

| Image | Filename | Dimensions | Description |
|-------|----------|------------|-------------|
| ![Fade In Picture]({{ "/assets/images/gallery/BitmapFadeInPicture.png" | relative_url }}) | `BitmapFadeInPicture.bin` | 112x25, 8-bit | Fade in picture effect |
| ![Fade Out Picture]({{ "/assets/images/gallery/BitmapFadeOutPicture.png" | relative_url }}) | `BitmapFadeOutPicture.bin` | 114x25, 8-bit | Fade out picture effect |
| ![Fade In Text]({{ "/assets/images/gallery/BitmapFadeInText.png" | relative_url }}) | `BitmapFadeInText.bin` | 80x18, 8-bit | Fade in text effect |
| ![Fade Out Text]({{ "/assets/images/gallery/BitmapFadeOutText.png" | relative_url }}) | `BitmapFadeOutText.bin` | 108x20, 8-bit | Fade out text effect |

### Accompaniment & Edit Graphics

| Image | Filename | Dimensions | Description |
|-------|----------|------------|-------------|
| ![Accger16]({{ "/assets/images/gallery/BitmapAccger16.png" | relative_url }}) | `BitmapAccger16.bin` | 120x95, 8-bit | Accompaniment graphic (German) |
| ![Accita16]({{ "/assets/images/gallery/BitmapAccita16.png" | relative_url }}) | `BitmapAccita16.bin` | 120x95, 8-bit | Accompaniment graphic (Italian) |
| ![Bmphk]({{ "/assets/images/gallery/BitmapBmphk.png" | relative_url }}) | `BitmapBmphk.bin` | 100x120, 8-bit | Unknown graphic |
| ![Dredt0d]({{ "/assets/images/gallery/BitmapDredt0d.png" | relative_url }}) | `BitmapDredt0d.bin` | 168x119, 8-bit | Unknown graphic |
| ![Dredt0k]({{ "/assets/images/gallery/BitmapDredt0k.png" | relative_url }}) | `BitmapDredt0k.bin` | 88x119, 8-bit | Unknown graphic |
| ![Ntedt0d]({{ "/assets/images/gallery/BitmapNtedt0d.png" | relative_url }}) | `BitmapNtedt0d.bin` | 240x127, 8-bit | Note edit graphic |
| ![Ntedt0k]({{ "/assets/images/gallery/BitmapNtedt0k.png" | relative_url }}) | `BitmapNtedt0k.bin` | 127x16, 8-bit | Note edit graphic small |

---

## HDAE5000 Hard Disk Expansion ROM Images

These images were extracted from the HD-AE5000 hard disk expansion ROM. The images are 8-bit indexed color, displayed on the KN5000's LCD during HD-AE5000 operations.

**Palette discovery**: Disassembly analysis found the boot code at `0x28f585` loads palette data from ROM offset `0x65dce`. The icon uses a separate Windows halftone-style palette at `0x6158e`.

### HD-AE5000 Product Logo

![HDAE5000 Logo]({{ "/assets/images/gallery/HDAE5000_Logo.png" | relative_url }})

*320x240, 8-bit indexed color - ROM offset: 0x2898e (CPU: 0x2A898E)*

Shows the HD-AE5000 product name with a stylized hard disk drive graphic.

### Hands Operating HD-AE5000

![HDAE5000 Hands]({{ "/assets/images/gallery/HDAE5000_Hands.png" | relative_url }})

*320x240, 8-bit indexed color - ROM offset: 0x3b98e (CPU: 0x2BB98E)*

Promotional image showing hands operating the HD-AE5000 unit connected to a KN5000 keyboard.

### File Selection Panel

![HDAE5000 File Panel]({{ "/assets/images/gallery/HDAE5000_FilePanel.png" | relative_url }})

*320x240, 8-bit indexed color - ROM offset: 0x4e98e (CPU: 0x2CE98E)*

UI panel showing file selection interface with textured button areas.

### Hard Disk Icon

![HDAE5000 Icon]({{ "/assets/images/gallery/HDAE5000_Icon.png" | relative_url }})

*28x28, 8-bit indexed color - ROM offset: 0x6198e (CPU: 0x2E198E)*

Small icon depicting a hard disk with magnetic head, used in UI elements.

---

## Image Format Notes

- **Table Data BMP**: Standard Windows BMP format, 8-bit indexed color
- **Main CPU raw**: Custom format, raw pixel data without headers, uses RGBA palette at `0xEB37DE`
- **HDAE5000 raw**: Raw pixel data, main images use palette at ROM offset `0x65dce`, icon uses halftone palette at `0x6158e`
- **1-bit bitmaps (Main CPU)**: Monochrome, 224x22 pixels (28 bytes per row), standard byte ordering
- **1-bit bitmaps (Table Data)**: Same visual content as Main CPU but different byte layout due to 16-bit interleaved ROM bus
- **8-bit bitmaps**: 256-color indexed, dimensions vary by image
- **LCD resolution**: 320x240 pixels (QVGA)
- **LCD controller**: MN89304 with 4Mbit Video RAM (IC207)

## Converting New Images

When new images are extracted as `.bin` files:

1. Add metadata to `convert_images.py` in the ROM disassembly repo
2. Run `make gallery` to convert and copy to this site
3. Update this page with the new images
4. Commit both repositories together

See [Reverse Engineering - Embedded Images]({{ site.baseurl }}/reverse-engineering/#embedded-images) for the extraction workflow.
