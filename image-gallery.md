---
layout: page
title: Image Gallery
permalink: /image-gallery/
---

# Embedded Image Gallery

Images extracted from the KN5000 firmware ROMs. These graphics are displayed on the built-in LCD screen (320x240 pixels, controlled by IC206 MN89304).

## Feature Demo Images (Table Data ROM)

These BMP images are used in the keyboard's feature demonstration mode.

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

## Main CPU ROM Images (Raw Binary)

These images are stored as raw bitmap data in the main CPU ROM. They require conversion tools to view. Dimensions and format vary.

### Status Messages (1-bit bitmaps, 616 bytes each)

| Filename | Purpose |
|----------|---------|
| `Bitmap_1bit_Please_Wait.bin` | "Please Wait" message |
| `Bitmap_1bit_Completed.bin` | "Completed" message |
| `Bitmap_1bit_Now_Erasing.bin` | "Now Erasing" message |
| `Bitmap_1bit_Illegal_Disk.bin` | "Illegal Disk" error |
| `Bitmap_1bit_Turn_On_AGAIN.bin` | "Turn On Again" instruction |
| `Bitmap_1bit_Flash_Memory_Update.bin` | Flash update message |
| `Bitmap_1bit_FD_to_Flash_Memory.bin` | FD to Flash message |
| `Bitmap_1bit_Change_FD_2_of_2.bin` | Multi-disk prompt |

### Logos

| Filename | Size | Description |
|----------|------|-------------|
| `BitmapTechnicsLogo.bin` | 14,040 bytes | Technics brand logo |
| `BitmapKN5000Logo.bin` | 7,200 bytes | KN5000 model logo |

### UI Elements

| Filename | Size | Description |
|----------|------|-------------|
| `BitmapDrawbarNumberedSlider_1.bin` | 4,884 bytes | Drawbar slider graphic |
| `BitmapDrawbarNumberedSlider_2.bin` | 4,884 bytes | Drawbar slider graphic |
| `BitmapDrawbarNumberedSlider_3.bin` | 4,884 bytes | Drawbar slider graphic |
| `BitmapSomeArrows.bin` | 1,764 bytes | Arrow icons |
| `BitmapWormWearingHat.bin` | 576 bytes | Easter egg? |

### Split Point Indicators

12 images showing keyboard split point notes (C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B, plus "no split").

Each file is 3,016 bytes: `BitmapSplitPoint_*.bin`

### MIDI Connection Diagrams

| Filename | Size | Description |
|----------|------|-------------|
| `BitmapMIDIConnections_1.bin` | 31,968 bytes | MIDI setup diagram |
| `BitmapMIDIConnections_2.bin` | 31,968 bytes | MIDI setup diagram |
| `BitmapMIDIConnections_3.bin` | 31,968 bytes | MIDI setup diagram |

### Transition Effects

| Filename | Size | Description |
|----------|------|-------------|
| `BitmapFadeInPicture.bin` | 2,800 bytes | Fade-in effect |
| `BitmapFadeOutPicture.bin` | 2,850 bytes | Fade-out effect |
| `BitmapFadeInText.bin` | 1,440 bytes | Text fade-in |
| `BitmapFadeOutText.bin` | 2,160 bytes | Text fade-out |

### Other Graphics

| Filename | Size | Description |
|----------|------|-------------|
| `BitmapAccger16.bin` | 11,400 bytes | Accompaniment graphic (German?) |
| `BitmapAccita16.bin` | 11,400 bytes | Accompaniment graphic (Italian?) |
| `BitmapBmphk.bin` | 12,000 bytes | Unknown |
| `BitmapDredt0d.bin` | 19,992 bytes | Unknown |
| `BitmapDredt0k.bin` | 10,472 bytes | Unknown |
| `BitmapNtedt0d.bin` | 30,480 bytes | Note edit graphic |
| `BitmapNtedt0k.bin` | 2,032 bytes | Note edit graphic |

---

## Image Format Notes

- **Table Data BMP**: Standard Windows BMP format, 8-bit indexed color
- **Main CPU raw**: Custom format, likely raw pixel data without headers
- **1-bit bitmaps**: Monochrome, dimensions need to be determined from code
- **LCD resolution**: 320x240 pixels (QVGA)
- **LCD controller**: MN89304 with 4Mbit Video RAM (IC207)

## Contributing

Help needed:
1. Determine dimensions of raw .bin images from display code analysis
2. Create conversion tools for raw formats
3. Identify purpose of unknown images
4. Extract any remaining embedded images

See [Reverse Engineering - Embedded Images]({{ site.baseurl }}/reverse-engineering/#embedded-images) for the extraction workflow.
