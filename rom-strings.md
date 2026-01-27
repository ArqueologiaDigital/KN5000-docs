---
layout: page
title: ROM String Analysis
permalink: /rom-strings/
---

# ROM String Analysis

This page documents meaningful strings found in each KN5000 ROM through systematic extraction and analysis. String analysis provides valuable insights into firmware functionality, menu systems, instrument databases, and communication protocols.

## Main CPU ROM (kn5000_v10_program.rom)

**Size:** 2MB (2,097,152 bytes)
**Load Address:** 0xE00000
**Total Strings Found:** 9,446

### Product Identification

| Location | String |
|----------|--------|
| 0xE023F0 | `Technics KN5000 ~95 VOCALIST WORKSTATION` |

This product ID string confirms the keyboard model and its "Vocalist Workstation" designation, indicating built-in vocal processing capabilities.

### Key String Tables

| Address | Description | Count |
|---------|-------------|-------|
| 0xE023F0 | Instrument categories | ~50 |
| 0xE0C3BE | Chord database | ~200 |
| 0xECFDFE | Keyboard layout strings | ~30 |

### String Categories

**Instrument Names:**
- Piano variations (Grand Piano, Upright, Electric)
- String ensembles (Strings, Violin, Cello, Orchestra)
- Wind instruments (Flute, Clarinet, Oboe, Saxophone)
- Brass section (Trumpet, Trombone, French Horn)
- Guitars (Acoustic, Electric, Nylon, Steel)
- Synthesizer patches (Synth Pad, Synth Lead, Analog)

**Menu Text:**
- Main menu items (Sound, Rhythm, Sequencer, Disk)
- Sub-menu options (Edit, Copy, Delete, Save, Load)
- Dialog prompts (Yes/No, OK/Cancel, Continue?)
- Error messages (Disk Error, Memory Full, File Not Found)

**Effects Names:**
- Reverb types (Hall, Room, Plate, Spring)
- Chorus/Delay effects
- EQ and filter settings
- DSP processing modes

**System Messages:**
- Boot messages
- Memory test strings
- Calibration routines
- Debug output

---

## Sub CPU Payload ROM (kn5000_subprogram_v142.rom)

**Size:** 192KB (196,608 bytes)
**Purpose:** Tone generator and audio synthesis control
**Total Meaningful Strings:** 88

### Key Strings

| Address | String | Purpose |
|---------|--------|---------|
| 0x31E3 | `KN5000 SOUND RAM` | Memory region identifier |
| 0x31F4 | `User Kit` | User-defined drum kit designation |

### DSP Control Messages

The sub CPU firmware contains control messages for the DSP subsystem:

| Category | Strings |
|----------|---------|
| Reset | DSP reset commands |
| Mute | Channel mute control |
| Disconnect | Audio path disconnect |
| Link | Channel linking |
| Edit | Parameter editing |

### String Distribution

Most strings in this ROM relate to:
- Audio buffer management
- DSP parameter control
- Waveform table identifiers
- Voice allocation messages
- MIDI processing states

---

## Sub CPU Boot ROM (kn5000_subcpu_boot.ic30)

**Size:** 128KB (131,072 bytes)
**Load Address:** 0xFE0000
**Total Strings:** 11

### Analysis

This boot ROM contains minimal strings, which is typical for embedded firmware:

- **ASCII Lookup Tables:** Character conversion tables for serial debugging
- **No Boot Messages:** The firmware does not output status messages during boot
- **No Version Strings:** Unlike application firmware, boot ROMs often lack version identification

The sparse string content indicates this ROM focuses on:
- Hardware initialization
- Memory testing
- Loading the main payload from the Main CPU
- Interrupt vector setup

---

## Table Data ROM (Interleaved Odd/Even)

**Total Size:** 2MB (1MB odd + 1MB even)
**Organization:** 16-bit interleaved (odd = high byte, even = low byte)
**Total Strings Found:** 164+

### Bass Instruments

| String | Type |
|--------|------|
| Acoustic Bass | Standard |
| Electric Bass | Standard |
| Slap Bass | Extended |
| Fretless Bass | Extended |
| Synth Bass | Electronic |

### Percussion and Drum Kits

**Standard Kits:**
- Jazz Kit
- Rock Kit
- Brush Kit
- Electronic Kit

**Extended Kits:**
- House Kit
- Hip-Hop Kit
- Latin Percussion
- Orchestral Percussion

### Notable Strings

| String | Description |
|--------|-------------|
| Tubular Bells C4 | Note-specific tubular bell sample |
| Tubular Bells D4 | Note-specific tubular bell sample |
| Tubular Bells E4 | Note-specific tubular bell sample |

The note designations (C4, D4, E4, etc.) indicate multi-sampled instruments with samples for individual notes.

### Rhythm Styles with BPM

| Style | Tempo Range |
|-------|-------------|
| Ballad | 48-72 BPM |
| Swing | 88-140 BPM |
| Jazz | 100-185 BPM |
| Rock | 100-140 BPM |
| House | 118-135 BPM |

---

## Custom Data Flash (kn5000_custom_data.ic19)

**Size:** 1MB (1,048,576 bytes)
**Load Address:** 0x300000
**Total Strings Found:** 324
**Unique Rhythm/Style Names:** 89

### Purpose

This flash memory stores user-customizable data including:
- User-defined rhythms
- Custom sound settings
- Panel memory configurations
- Registration data

### Rhythm Categories

| Category | Example Styles |
|----------|----------------|
| Jazz/Swing | Big Band Swing, Bebop, Cool Jazz |
| Rock/Pop | Classic Rock, Pop Ballad, Soft Rock |
| Brazilian | Bossa Nova, Samba, Baiao |
| Latin | Cha-Cha, Mambo, Salsa, Merengue |
| Classical | Waltz, March, Polonaise |

### Designer Attributions

Some factory presets include designer credits:

| Designer | Styles |
|----------|--------|
| Ray Conniff | Easy Listening arrangements |
| Arthur | Various factory presets |

### Special Entries

| Entry | Meaning |
|-------|---------|
| `Clear` | Empty user slot (available for user data) |
| `Init` | Factory default initialization state |

These markers indicate the state of user-configurable memory slots.

---

## HDAE5000 ROM (hd-ae5000_v2_06i.ic4)

**Size:** 512KB (524,288 bytes)
**Load Address:** 0x280000

### Version Information

| Property | Value |
|----------|-------|
| Internal Version | `Technics Software section M. Kitajima 2.33J` |
| Author | M. Kitajima |
| Development Period | Juli-Oktober 1996 |

### PPORT Menu Commands

Commands for PC parallel port communication:

| Command | Description |
|---------|-------------|
| Send Infos About HD | Report HD information to PC |
| Exit PPORT | End parallel port session |
| Read FSB from HD | Read File System Block |
| Sending FSB to PC | Transfer FSB to PC |
| Rcv FSB from PC | Receive FSB from PC |
| Writing FSB to HD | Write FSB to HD |
| Load HD to Memory | Load file to KN5000 memory |
| Send data to PC | Data transfer to PC |
| Sending files to PC | File transfer to PC |
| Rcv data from PC | Receive data from PC |
| Save memory to HD | Save to hard disk |
| Delete files | Delete HD files |
| Formating HD | Format hard disk |
| Switch HD-motor off | Spin down HD |
| Send XapFile flash | XAP file transfer |

### Windows DLL Callback Names

The ROM contains Windows DLL function callback names, indicating the PC-side software interface:

- Standard Windows callback conventions
- File transfer protocol handlers
- Status reporting functions

---

## String Extraction Methodology

Strings were extracted using systematic scanning with the following criteria:

1. **Minimum Length:** 4 characters
2. **Character Set:** Printable ASCII (0x20-0x7E)
3. **Termination:** Null-terminated (0x00) or fixed-length fields
4. **Filtering:** Manual review to exclude false positives from binary data

### Tools Used

- Binary string extraction (custom scripts)
- Cross-reference with disassembly
- Pattern matching for structured data

---

## References

- [Memory Map]({{ site.baseurl }}/memory-map/) - ROM address locations
- [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) - ROM chip identification
- [HDAE5000]({{ site.baseurl }}/hdae5000/) - Hard disk expansion details
