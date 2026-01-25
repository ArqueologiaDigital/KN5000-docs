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

## Sub CPU Boot ROM

The 128KB boot ROM (`kn5000_subcpu_boot.ic30`) initializes the sub CPU hardware and provides a bootstrap environment until the payload is ready.

### Memory Map

| Address Range | Size | Description |
|---------------|------|-------------|
| 0x0000-0x00FF | 256B | Special Function Registers (SFR) |
| 0x0100-0x01FF | 256B | Extended SFR / Memory Controller |
| 0x0400-0x04E0 | 225B | Interrupt vector trampolines (copied from ROM) |
| 0x04FE | 1B | Payload ready flag |
| 0x0500-0x05A2 | ~160B | RAM / Stack area |
| 0x120000 | - | Inter-CPU Communication Latch |
| 0x130000 | - | Tone Generator Registers |
| 0xFE0000-0xFFFFFF | 128KB | Boot ROM (mostly 0xFF, code at 0xFF8000+) |

### ROM Structure

The 128KB boot ROM is mostly erased (0xFF):

| Offset | Address | Size | Content |
|--------|---------|------|---------|
| 0x00000-0x17FFF | 0xFE0000-0xFF7FFF | 96KB | Erased (0xFF) |
| 0x18000-0x1828F | 0xFF8000-0xFF828F | 656B | Data tables (audio lookup?) |
| 0x18290-0x1904D | 0xFF8290-0xFF904D | ~2KB | Boot code and routines |
| 0x1F000-0x1FEFF | 0xFFF000-0xFFFEFF | 4KB | Mostly 0xFF |
| 0x1FEE0 | 0xFFFEE0 | 5B | Reset handler (JP BOOT_INIT) |
| 0x1FF00-0x1FFEF | 0xFFFF00-0xFFFFEF | 240B | Interrupt vector table |
| 0x1FFF0-0x1FFFF | 0xFFFFF0-0xFFFFFF | 16B | Reset vectors |

### Boot Sequence (Confirmed)

1. **Reset** (0xFFFEE0): `JP 0xFF8290` jumps to boot initialization
2. **Hardware Init** (0xFF8290): Configures all SFR registers:
   - Port function control (P0FC-PBFC)
   - Serial channels (SC0, SC1)
   - Timers and watchdog
   - DRAM refresh
   - DMA for inter-CPU latch
3. **Stack Setup**: Sets XSP to 0x05A2
4. **Vector Copy** (0xFF846D): Copies 225 bytes of interrupt trampolines from ROM (0xFF8F6C) to RAM (0x0400)
5. **Enable Interrupts**: `EI 0`
6. **Initialization Routines**:
   - Memory test (0xFF8956)
   - DMA/Serial setup (0xFF85AE) - configures inter-CPU latch at 0x120000
   - Tone generator init (0xFF84A8) - initializes registers at 0x130000
7. **Main Loop**: Waits for payload ready flag at 0x04FE, then calls 0x0400

### Interrupt Trampoline System

The boot ROM uses an elegant trampoline system for interrupts:

1. **ROM Vector Table** (0xFFFF00): Contains 4-byte addresses pointing to RAM (0x04xx)
2. **RAM Trampolines** (0x0400): Each is 5 bytes: `JP addr` (4B) + `RET` (1B)
3. **ROM Handlers**: Trampolines initially point back to ROM handlers

This allows the payload to replace interrupt handlers by modifying the trampolines in RAM.

**Trampoline Layout:**

| RAM Address | Handler | Initial Target |
|-------------|---------|----------------|
| 0x0400 | Handler 0 (Reset) | 0xFFFEE0 (ROM) |
| 0x0405 | Handler 1 | 0xFF8432 (Default RETI) |
| 0x040A | Handler 2 | 0xFF8432 (Default RETI) |
| ... | ... | ... |
| 0x0428 | Handler 9 | 0xFF881F (Specific) |
| ... | ... | ... |
| 0x04AA | Handler 35 | 0xFF88B8 (Specific) |
| 0x04B4 | Handler 37 | 0xFF889A (Specific) |

### Key Hardware Addresses Discovered

**Inter-CPU Communication Latch (0x120000)**

The DMA is configured to use 0x120000 for communication between main CPU and sub CPU. This confirms the latch address documented elsewhere.

**Tone Generator (0x130000)**

The `INIT_TONE_GEN` routine writes initialization patterns to registers at 0x130000, confirming this as the tone generator base address.

### Disassembly Status

**Completed:**
- BOOT_INIT (0xFF8290) - Full hardware initialization
- COPY_VECTORS (0xFF846D) - Vector trampoline copy
- INIT_TONE_GEN (0xFF84A8) - Tone generator setup
- INIT_DMA_SERIAL (0xFF85AE) - DMA/Serial configuration
- MAIN_LOOP - Payload wait loop
- DEFAULT_HANDLER (0xFF8432) - Simple RETI
- HALT_LOOP (0xFF8490) - Error handler
- Vector trampolines (0xFF8F6C) - All 45 handlers
- Interrupt vector table (0xFFFF00)
- INT_HANDLER_9 (0xFF881F) - Serial receive interrupt
- INT_HANDLER_35 (0xFF88B8) - Timer/processing interrupt
- INT_HANDLER_37 (0xFF889A) - DMA complete interrupt
- DELAY_ROUTINE (0xFF89A9) - Variable delay routine
- MEM_TEST_ROUTINE (0xFF89FC) - RAM test
- ROM_CHECKSUM (0xFF8AB4) - Boot ROM integrity check
- SERIAL_INIT (0xFF8B07) - Serial communication init

**TODO:**
- Data tables analysis (0xFF8000)
- SUB_8B37, SUB_8B89, SUB_8C80 helper routines

### Inter-CPU Protocol (Boot ROM Side)

The sub CPU boot ROM handles these commands from the main CPU via the latch at `0x120000`:

| Command | Action | DMA Size |
|---------|--------|----------|
| `E1` | Set up DMA transfer to 0x0544 | 6 bytes |
| `E2` | Set up DMA transfer to 0x054A | 10 bytes |
| `E3` | Signal payload ready (sets bit 6 of 0x04FE) | - |
| `00-1F` | Variable-length DMA to 0x051E | 1-32 bytes |

**State Machine (VAR_0518):**
- State 0: Idle
- State 1: Processing received data, call handler from table
- State 2: Set up secondary DMA transfer
- State 3: Set completion flags
- State 4: Clear ready flag, return to idle

### Source File

`subcpu_boot/kn5000_subcpu_boot.asm` - 1098 lines of disassembled code

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

## Feature Demo Extraction

The Feature Demo is an interactive presentation showcasing keyboard features. Extracting its data structures enables documentation, modification, and source code simplification.

### Components

- **Slides** - Background images with overlaid UI widgets
- **Widgets** - Text, images, shapes, interactive elements
- **MIDI files** - Demo music embedded in ROM
- **Timing data** - Slide duration and transitions

### Known Demo Images

Already extracted to `table_data/images/`:

| File | Size | Description |
|------|------|-------------|
| FTBMP01.BMP | 320x240 | Demo screen 1 |
| FTBMP02.BMP | 320x130 | Demo screen 2 |
| FTBMP03.BMP | 320x120 | Demo screen 3 |
| FTBMP04.BMP | corrupted | Demo screen 4 |
| FTBMP05.BMP | 320x125 | Demo screen 5 |
| FTBMP06.BMP | 320x240 | Demo screen 6 |

See [Image Gallery]({{ site.baseurl }}/image-gallery/) for viewable versions.

### Slide Data Structure

**Tasks:**
1. Locate slide table/index in ROM
2. Document per-slide record format:
   - Slide type/ID
   - Duration/timing
   - Background image reference
   - Widget list pointer
   - MIDI file pointer
   - Transition effects

### UI Widget Types

Expected widget types based on typical presentation systems:

| Widget | Parameters |
|--------|------------|
| TEXT | x, y, font_id, color, string |
| IMAGE | x, y, image_id |
| RECT | x, y, width, height, fill_color, border_color |
| LINE | x1, y1, x2, y2, color |
| ICON | x, y, icon_id |
| BUTTON | x, y, width, height, label, action |
| PIANO | x, y, width, height, highlighted_keys |
| METER | x, y, width, height, value, max |

**Tasks:**
1. Trace slide rendering code
2. Identify all widget types
3. Document parameter format for each
4. Create widget type reference

### ASL Macro Design

Goal: Replace raw data bytes with human-readable macros.

**Slide macros:**
```asm
SLIDE_BEGIN id, background_image, duration_ms, midi_ptr
    ; widgets defined here
SLIDE_END
```

**Widget macros:**
```asm
TEXT x, y, font, color, "string"
IMAGE x, y, image_id
RECT x, y, w, h, fill_color, border_color
LINE x1, y1, x2, y2, color
```

**Example slide definition:**
```asm
SLIDE_BEGIN 1, FTBMP01, 5000, DemoMidi1
    TEXT 10, 20, FONT_LARGE, COLOR_WHITE, "Welcome to KN5000"
    IMAGE 100, 80, ICON_KEYBOARD
    RECT 50, 150, 200, 30, COLOR_BLUE, COLOR_WHITE
SLIDE_END
```

**Tasks:**
1. Design macro syntax for each structure
2. Implement macros in ASL format
3. Ensure macros emit correct binary
4. Add to `feature_demo.inc`

### Embedded MIDI Extraction

MIDI files are embedded for demo music playback.

**Detection:**
- Search for MIDI header: `4D 54 68 64` ("MThd")
- Track chunks start with: `4D 54 72 6B` ("MTrk")

**Tasks:**
1. Scan ROMs for MIDI headers
2. Parse MIDI structure to find boundaries
3. Extract as standalone `.mid` files
4. Verify playback in standard MIDI player
5. Document each file's purpose

**Output directory:**
```
maincpu/midi/
├── demo_song_1.mid
├── demo_song_2.mid
└── ...
```

### Source Code Refactoring

After macros are defined:

1. Identify raw data sections for slides
2. Replace `db`/`dw` sequences with macros
3. Rebuild ROM: `make all`
4. Verify byte-match: `python compare_roms.py`
5. Measure source line reduction

**Goal:** Significantly reduce assembly source length while improving readability.

### Slide Viewer Tool

Optional Python tool for visualizing extracted slides:

**Features:**
- Parse slide data structures
- Render widgets using PIL/Pillow
- Export as PNG or HTML
- Enable slide editing for custom demos

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

## System Update Procedures

The KN5000 supports firmware updates via floppy disk. Understanding this system enables custom firmware development.

### Update File Formats

Official updates distributed as executable files on floppy disk.

**Known files (from [archive.org](https://archive.org/details/technics-kn5000-system-update-disks)):**

| File | Version | Date |
|------|---------|------|
| KN5KPV5.EXE | v5 | 1997-11-12 |
| KN5KPV6.EXE | v6 | 1998-01-16 |
| KN5KPV7.EXE | v7 | 1998-06-26 |
| KN5KPV8.EXE | v8 | 1998-11-13 |
| KN5KPV9.EXE | v9 | 1999-01-26 |
| KN5KPV10.EXE | v10 | 1999-08-02 |

**Tasks:**
1. Analyze file header format
2. Document payload structure
3. Identify checksum algorithm
4. Check for compression

### Update Mode Entry

Special key combinations trigger update mode at power-on.

**Tasks:**
1. Find key combo detection code in firmware
2. Document required button sequence
3. Identify any service mode entries

### File Types and Target Components

Different file types update different system components.

| Target | Address | Description |
|--------|---------|-------------|
| Main CPU Program | 0xE00000 | 2MB program Flash |
| Custom Data | 0x300000 | 1MB user storage Flash |
| Sub CPU Payload | via DMA | 192KB loaded at boot |
| HDAE5000 | 0x280000 | Expansion board firmware |

**Tasks:**
1. Map file naming patterns to targets
2. Document multi-file updates
3. Identify version compatibility checks

### Flash ROM Chips

**Tasks:**
1. Identify chip manufacturer and part numbers from service manual
2. Document capacity and sector size
3. Identify command set (JEDEC/AMD/Intel)

**Expected chip locations:**
- IC4/IC6: Program Flash (0xE00000)
- Custom Data Flash (0x300000)

### Flash Erase Algorithm

Flash memory must be erased before programming.

**Typical sequence:**
1. Write unlock sequence to chip
2. Issue sector erase or chip erase command
3. Poll for completion
4. Verify erasure (all 0xFF)

**Tasks:**
1. Trace erase routine in firmware
2. Document unlock sequence
3. Identify sector vs chip erase usage
4. Document timeout handling

### Flash Program Algorithm

Writing data to Flash ROM.

**Typical sequence:**
1. Write unlock sequence
2. Issue program command
3. Write data byte/word
4. Poll for completion
5. Verify written data

**Tasks:**
1. Trace program routine in firmware
2. Identify byte-program vs page-buffer mode
3. Document write verification
4. Trace error handling

### FDC Interaction

Floppy Disk Controller at `0x110000` (IC208: D72068GF-3B9).

**Tasks:**
1. Document disk detection sequence
2. Trace file reading routines
3. Analyze sector layout expectations
4. Document multi-disk handling ("Change FD 2 of 2")

### Update Progress Display

LCD messages during update (extracted as 1-bit bitmaps):

| Bitmap | Message | Stage |
|--------|---------|-------|
| `Bitmap_1bit_Flash_Memory_Update.bin` | Flash Memory Update | Start |
| `Bitmap_1bit_Please_Wait.bin` | Please Wait | Processing |
| `Bitmap_1bit_Now_Erasing.bin` | Now Erasing | Erase phase |
| `Bitmap_1bit_FD_to_Flash_Memory.bin` | FD to Flash Memory | Write phase |
| `Bitmap_1bit_Completed.bin` | Completed | Success |
| `Bitmap_1bit_Turn_On_AGAIN.bin` | Turn On AGAIN | Restart needed |
| `Bitmap_1bit_Illegal_Disk.bin` | Illegal Disk | Error |
| `Bitmap_1bit_Change_FD_2_of_2.bin` | Change FD 2 of 2 | Multi-disk |

**Tasks:**
1. Correlate bitmaps with update state machine
2. Document state transitions
3. Identify error conditions

### Validation and Error Handling

**Tasks:**
1. Document file header validation
2. Trace checksum verification
3. Identify version checking logic
4. Document ROM verification after write
5. Analyze "Illegal Disk" trigger conditions

### HDAE5000 Update

Separate update procedure for HD-AE5000 expansion.

**Versions:**
- v1.10i (1998-07-06)
- v1.15i (1998-10-13)
- v2.0i (1999-01-15) - Added lyrics display

**Tasks:**
1. Document separate update disk format
2. Trace communication via PPI (0x160000)
3. Identify Flash chips on expansion board
4. Document version compatibility

### Homebrew Development

Understanding the update system enables:
- Custom firmware creation
- Feature modifications
- Bug fixes for aging hardware
- Preservation of update capability

**Tools needed:**
- Update file parser (extract/create update files)
- Checksum calculator
- Flash programmer emulation for testing

---

## References

- [Service Manual PDF]({{ site.baseurl }}/service_manual/technics_sx-kn5000.pdf)
- [System Update Disks Archive](https://archive.org/details/technics-kn5000-system-update-disks)
- [HDAE5000 Technical Info](https://www.keysoftservice.ch/hdae5000-e.htm)
- [Image Gallery]({{ site.baseurl }}/image-gallery/) - Extracted graphics from firmware
