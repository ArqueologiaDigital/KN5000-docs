---
layout: page
title: Reverse Engineering
permalink: /reverse-engineering/
---

# Reverse Engineering Strategies

Documented approaches for understanding undocumented aspects of the KN5000 system.

## HDAE5000 Hard Disk Expansion

The HD-AE5000 is an optional hard disk expansion that provides 1.08GB storage for music files. Reverse engineering it requires understanding multiple layers.

### PPI Interface (0x160000)

The main CPU communicates with the HDAE5000 via an 8255 PPI (Programmable Peripheral Interface).

**Tasks:**
1. Document Port A/B/C assignments and control register settings
2. Trace all main CPU firmware accesses to `0x160000`
3. Identify command/response protocol

### HDAE5000 ROM (0x280000)

A 512KB ROM contains the HDAE5000 firmware.

**Tasks:**
1. Disassemble the ROM (determine CPU type first)
2. Identify command handlers and filesystem routines
3. Document the command set

### Filesystem Structure

The 1.08GB hard disk uses a custom or standard filesystem.

**Tasks:**
1. Analyze directory structure and file allocation
2. Document how Flash-ROM/SRAM provides quick directory access
3. Compare with standard FAT if applicable

### Parallel Port Protocol

The HD-TechManager5000 PC software communicates via parallel port.

**Tasks:**
1. Capture and analyze parallel port traffic
2. Document handshaking, command format, file transfer protocol
3. Reverse engineer the Windows software (available at [archive.org](https://archive.org/details/technics-kn5000-system-update-disks))

### Interface Cable Pinout

**Tasks:**
1. Identify connector types from service manual
2. Document signal assignments (accent data/control/bus/power)
3. Verify voltage levels

---

## Sub CPU Payload Loading

The main CPU (TMP94C241F) loads a 192KB executable payload to the sub CPU (IC27) at boot time using MicroDMA.

### MicroDMA Mechanism

The TMP94C241F has a built-in MicroDMA controller for high-speed transfers.

**Key Registers:**
- `DMAS` - DMA Source address
- `DMAD` - DMA Destination address
- `DMAC` - DMA Count (transfer size)
- `DMAM` - DMA Mode (transfer settings)

**Tasks:**
1. Document MicroDMA register addresses and bit definitions from TMP94C241F datasheet
2. Identify which DMA channel is used for sub CPU transfer
3. Find initialization code in main CPU firmware

### Inter-CPU Communication (0x120000)

The main and sub CPUs communicate via latches at `0x120000`.

**Tasks:**
1. Document latch register layout (command, status, data bytes)
2. Identify handshaking signals
3. Trace how main CPU signals "payload ready"
4. Trace how sub CPU acknowledges receipt

### Boot Sequence

**Expected flow:**
1. Main CPU initializes after reset
2. Sub CPU held in reset (or waiting)
3. Main CPU configures DMA: source = payload in ROM, dest = sub CPU memory
4. DMA transfer executes (192KB)
5. Main CPU signals transfer complete via latch
6. Sub CPU boot ROM jumps to payload entry point
7. Sub CPU signals ready to main CPU

**Tasks:**
1. Trace complete boot sequence in main CPU firmware
2. Identify sub CPU type (IC27) from service manual
3. Document sub CPU memory map
4. Analyze 192KB payload structure (entry point, vectors, segments)

### Payload Structure

The sub CPU payload (`subcpu/kn5000_subprogram_v142.asm`) is 192KB.

**Layout to document:**
- Entry point address
- Interrupt vector table
- Code segments
- Data segments
- Embedded wavetables or lookup data
- Relationship to 128KB boot ROM

---

## Embedded Images

The ROMs contain icons, UI elements, and splash screens for the LCD display.

### Image Locations

**Main CPU ROM:**
- 1-bit status bitmaps (Please Wait, Completed, etc.)
- UI elements (drawbar sliders, icons)
- Various graphics referenced by display routines

**Table Data ROM:**
- Feature demo BMP images (FTBMP01-06)
- Additional UI assets

### Image Format

The LCD controller is IC206 (MN89304) with 4Mbit Video RAM (IC207).

**Format characteristics to document:**
- Pixel depth (1bpp, 4bpp, 8bpp, or RGB)
- Dimension encoding
- Palette format (if indexed color)
- Compression (if any)
- Header structure

### Extraction Workflow

1. **Scan ROMs** for image signatures (BMP headers: `0x42 0x4D`)
2. **Trace display code** to find image address references
3. **Extract to binary files** in `maincpu/images/` and `table_data/images/`
4. **Name descriptively** based on apparent purpose
5. **Update assembly sources** with `incbin` directives
6. **Verify byte-match** after rebuild

### Current Progress

**Already extracted:**
- `maincpu/images/` - 18+ files (1-bit bitmaps, UI elements)
- `table_data/images/` - 6 BMP files (feature demo screens)

**Tools:**
- `extract_include_binaries.py` - Extraction script

### Conversion for Documentation

For website documentation, images can be converted to PNG format for viewing. This helps identify what each image represents and aids in understanding the UI.

---

## Boot Sequence

Understanding the complete boot sequence is essential for MAME emulation and debugging.

### Reset Vector and Early Init

The main CPU begins execution at the reset vector (near `0xE00000`).

**Tasks:**
1. Document initial stack pointer setup
2. Trace memory controller configuration
3. Document clock/PLL initialization
4. Identify watchdog setup

### Memory Initialization

**Hardware:**
- DRAM: IC9/IC10 (M5M44260AJ7S, 4Mbit each)
- SRAM: IC21 (1Mbit, battery-backed)

**Tasks:**
1. Document DRAM refresh setup
2. Trace SRAM initialization
3. Document memory mapping configuration
4. Identify any memory tests performed

### Peripheral Initialization Order

Peripherals are initialized in a specific sequence after memory setup.

**Expected order:**
1. Serial channels (SC0/SC1) - for control panel and MIDI
2. Timers (T0-TB) - for timing and PWM
3. Interrupt controllers (INTA/INT0)
4. FDC at `0x110000` - floppy disk controller
5. LCD controller (IC206)
6. Other I/O

**Tasks:**
1. Trace each peripheral init in firmware
2. Document register values written
3. Create initialization order diagram

### Sub CPU Startup

**Sequence:**
1. Main CPU releases sub CPU from reset
2. MicroDMA transfers 192KB payload
3. Latch communication at `0x120000`
4. Sub CPU signals ready

See [Sub CPU Payload Loading](#sub-cpu-payload-loading) for details.

### Control Panel Initialization

**Tasks:**
1. Document when serial channel to CPL/CPR MCUs is configured
2. Trace initial command sequence sent to panels
3. Document LED initialization pattern
4. Identify panel ready confirmation

### LCD Splash Screen

**Tasks:**
1. Document LCD controller register setup
2. Trace Video RAM initialization
3. Document Technics/KN5000 logo display timing
4. Identify boot progress indicators

### Optional Hardware Detection

**HDAE5000:**
1. Probe PPI at `0x160000`
2. Check for ROM at `0x280000`
3. Initialize if present, skip gracefully if absent

### Audio Subsystem

**Tasks:**
1. Document tone generator initialization via sub CPU
2. Trace DAC setup (IC310)
3. Document DSP initialization (IC311)
4. Identify audio ready state

### Boot Timeline Goal

Create comprehensive timeline showing:
- Time from power-on for each stage
- Dependencies between init stages
- Total boot time to user-ready state

---

## Video Hardware

The KN5000 has a 320x240 QVGA LCD display for user interface.

### Hardware Components

| IC | Part Number | Function |
|----|-------------|----------|
| IC206 | MN89304 | LCD Controller |
| IC207 | M5M44265CJ8S | 4Mbit Video RAM |

### LCD Controller (MN89304)

Matsushita/Panasonic LCD controller.

**Tasks:**
1. Find datasheet (if available)
2. Document register map
3. Identify supported video modes
4. Document pixel formats
5. Trace timing parameters
6. Find memory-mapped I/O addresses

### Video RAM Organization

4Mbit VRAM supports various configurations:

| Color Depth | Bytes/Pixel | Frame Size | Frames in 4Mbit |
|-------------|-------------|------------|-----------------|
| 8bpp (256 colors) | 1 | 76,800 bytes | ~6.8 frames |
| 16bpp (65K colors) | 2 | 153,600 bytes | ~3.4 frames |
| 4bpp (16 colors) | 0.5 | 38,400 bytes | ~13.6 frames |

**Tasks:**
1. Determine actual color depth used
2. Document memory organization
3. Identify double-buffering if used
4. Trace access patterns from main CPU

### Pixel Format and Palette

Based on extracted images, likely 8bpp indexed color.

**Tasks:**
1. Confirm bits per pixel
2. Document palette format and location
3. Trace how palette is loaded
4. Identify any direct color modes

### Drawing Primitives

Firmware contains graphics routines for:

**Tasks:**
1. Find pixel plotting routine
2. Document line drawing algorithm
3. Trace rectangle fill
4. Analyze bitmap blitting (BLT)
5. Identify any hardware acceleration

### Font System

**Tasks:**
1. Locate font data in ROM
2. Document font format (bitmap vs vector)
3. Identify character encoding
4. Document available font sizes
5. Trace text rendering routines
6. Check internationalization support

### UI Widget Rendering

The UI includes various interactive elements:
- Buttons and menus
- Sliders (drawbar controls)
- Piano keyboard display
- Waveform displays
- Level meters

**Tasks:**
1. Document widget drawing routines
2. Identify any sprite system
3. Trace interactive element updates

### Screen Layout

**Tasks:**
1. Map screen regions (header, content, status bar)
2. Document how different modes use display
3. Create annotated screenshots

### Animation and Effects

Transition effects found in extracted images:
- `BitmapFadeInPicture.bin` / `BitmapFadeOutPicture.bin`
- `BitmapFadeInText.bin` / `BitmapFadeOutText.bin`

**Tasks:**
1. Analyze fade effect implementation
2. Document screen transition timing
3. Identify scrolling implementation
4. Check for hardware effect support

### Font Extraction

**Goal:** Extract fonts as usable assets.

**Tasks:**
1. Extract font bitmaps from ROM
2. Convert to standard format (BDF, PNG atlas)
3. Document character coverage
4. Add samples to [Image Gallery]({{ site.baseurl }}/image-gallery/)

---

## Sound Hardware

The KN5000 has a sophisticated sound generation system with dedicated processors for synthesis and effects.

### Architecture Overview

```
Main CPU (TMP94C241F)
    │
    │ Commands via 0x120000 latches
    ▼
Sub CPU (IC27) ──────► Waveform ROM (IC306-307)
    │                      │
    │ Audio data           │ Samples
    ▼                      ▼
DSP (IC311) ◄──────────────┘
    │
    │ Processed audio
    ▼
DAC (IC310)
    │
    │ Analog audio
    ▼
Output Jacks (Line, Headphones, Speakers)
```

### Hardware Components

| IC | Function | Description |
|----|----------|-------------|
| IC27 | Sub CPU | Tone generator control, synthesis engine |
| IC306-307 | Waveform ROM | PCM sample storage for all instruments |
| IC311 | DSP | Digital effects (reverb, chorus, EQ) |
| IC310 | DAC | Digital-to-analog conversion for audio output |

### Sub CPU (IC27)

The Sub CPU handles all real-time sound generation, receiving commands from the main CPU.

**Tasks:**
1. Identify exact chip type from service manual schematics
2. Find datasheet and document architecture
3. Document clock speed and memory map
4. Analyze I/O capabilities and interfaces

### DSP (IC311)

Digital Signal Processor for audio effects.

**Tasks:**
1. Identify chip type and find datasheet
2. Determine if programmable or fixed-function
3. Document effects capabilities (reverb types, chorus, EQ)
4. Trace interface to main/sub CPU
5. Document audio data format and routing

### DAC (IC310)

Converts digital audio to analog output.

**Tasks:**
1. Identify chip type and specifications
2. Document resolution (bits) and sample rate
3. Identify number of output channels
4. Document interface protocol (I2S, parallel, etc.)
5. Trace analog output path

### Waveform ROM (IC306-307)

Contains all PCM samples for instrument sounds.

**Tasks:**
1. Document total ROM size
2. Analyze sample encoding (PCM bit depth, compression)
3. Document sample indexing scheme
4. Map samples to instrument patches
5. Identify loop points and root notes

### Main CPU ↔ Sub CPU Protocol

Communication via latches at `0x120000`.

**Expected command types:**
- Note On/Off (key number, velocity, channel)
- Program Change (instrument selection)
- Control Change (volume, pan, expression, sustain)
- Pitch Bend
- Effects parameters (reverb depth, chorus rate, etc.)

**Tasks:**
1. Trace all accesses to `0x120000` in main CPU firmware
2. Document command byte format
3. Create complete command reference
4. Identify response/status mechanism

### Synthesis Architecture

**Questions to answer:**
- Polyphony count (simultaneous voices)
- Synthesis method (sample playback, wavetable, FM hybrid?)
- Envelope generators (ADSR parameters)
- LFO capabilities
- Filter types and parameters

**Tasks:**
1. Analyze sub CPU firmware for synthesis routines
2. Document oscillator/voice architecture
3. Trace envelope generator implementation
4. Identify filter algorithms

### Effects Processing

**Known effects (from panel labels):**
- Reverb (multiple types: Hall, Room, Plate, etc.)
- Chorus/Flanger
- EQ (bass, treble, presence)

**Tasks:**
1. Determine which chip handles each effect
2. Document effects parameter ranges
3. Trace effects routing (insert vs send)
4. Catalog effects presets

### Audio Output Path

From DAC to physical jacks.

**Outputs:**
- Line Out (L/R)
- Headphone jack
- Internal speakers (if present)

**Tasks:**
1. Trace analog signal path from DAC
2. Document amplifier stages
3. Identify any analog mixing or effects
4. Document output levels and impedances

### MIDI Implementation

Full MIDI capability for external control and sequencing.

**Tasks:**
1. Document MIDI IN/OUT/THRU signal handling
2. Identify channel assignments (parts to channels)
3. Document supported Control Change (CC) messages
4. Analyze SysEx command format
5. Check GM/GS/XG compatibility level
6. Document MIDI clock sync behavior

### Rhythm/Accompaniment Engine

Auto-accompaniment system for backing tracks.

**Components:**
- Rhythm patterns (drums, percussion)
- Bass patterns
- Chord patterns
- Style variations (Intro, Main A/B, Fill, Ending)

**Tasks:**
1. Analyze rhythm pattern data format in ROM
2. Document chord detection algorithm
3. Trace bass/chord part generation
4. Document style structure and switching

### Sample/Patch Extraction

**Goals:**
1. Extract all instrument patch definitions
2. Document patch parameters (samples, envelopes, filters)
3. Create patch list matching front panel sound groups
4. Extract raw waveforms as WAV files for analysis
5. Document sample rates, loop points, root notes

---

## References

- [Service Manual PDF]({{ site.baseurl }}/service_manual/technics_sx-kn5000.pdf)
- [System Update Disks Archive](https://archive.org/details/technics-kn5000-system-update-disks)
- [HDAE5000 Technical Info](https://www.keysoftservice.ch/hdae5000-e.htm)
- [Image Gallery]({{ site.baseurl }}/image-gallery/) - Extracted graphics from firmware
