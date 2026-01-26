---
layout: page
title: Project Issues
permalink: /issues/
---

# Project Issues

This page is auto-generated from the [Beads](https://github.com/beads-ai/beads) issue tracker.

**Total Issues:** 92 (71 open, 21 closed)

**Quick Links:** 
[Boot Sequence](#boot-sequence) (5) · [Control Panel](#control-panel) (1) · [Feature Demo](#feature-demo) (11) · [Firmware Update](#firmware-update) (8) · [HD-AE5000 Expansion](#hd-ae5000-expansion) (5) · [Image Extraction](#image-extraction) (6) · [Main CPU ROM](#main-cpu-rom) (1) · [Other](#other) (12) · [Sound & Audio](#sound-audio) (11) · [Sub CPU](#sub-cpu) (3) · [Table Data ROM](#table-data-rom) (1) · [Video & Display](#video-display) (7)

---

## Open Issues

### Boot Sequence {#boot-sequence}

#### 🟡 Boot: Document HDAE5000 detection and init {#issue-kn5000-izk}

**ID:** `kn5000-izk` | **Priority:** Medium | **Created:** 2026-01-25

Trace how main CPU detects presence of HD-AE5000 expansion at boot. Document: PPI probe at 0x160000, ROM detection at 0x280000, initialization sequence if present, graceful handling if absent.

---

#### 🟡 Boot: Document LCD splash screen sequence {#issue-kn5000-vql}

**ID:** `kn5000-vql` | **Priority:** Medium | **Created:** 2026-01-25

Trace LCD initialization and splash screen display. Document: LCD controller (MN89304) register setup, video RAM initialization, Technics/KN5000 logo display timing, any boot progress indicators shown on screen.

---

#### 🟡 Boot: Document audio subsystem initialization {#issue-kn5000-9bd}

**ID:** `kn5000-9bd` | **Priority:** Medium | **Created:** 2026-01-25

Trace initialization of tone generator and audio path. Document: sub CPU commands for audio init, DAC setup (IC310), DSP initialization (IC311), any audio self-test or calibration, when audio becomes ready for playback.

---

#### 🟡 Boot: Document control panel initialization {#issue-kn5000-bq4}

**ID:** `kn5000-bq4` | **Priority:** Medium | **Created:** 2026-01-25

Trace initialization of control panel serial communication. Document: when serial channel to CPL/CPR MCUs is configured, initial command sequence sent to panels, LED initialization pattern, how main CPU confirms panel MCUs are responding.

---

#### ⚪ Boot: Create complete boot sequence timeline {#issue-kn5000-mhj}

**ID:** `kn5000-mhj` | **Priority:** Low | **Created:** 2026-01-25

Compile all boot documentation into a comprehensive timeline. Create diagram showing: time from power-on, which subsystem initializes when, dependencies between init stages, total boot time to user-ready state. Add to documentation website.

---

### Control Panel {#control-panel}

#### 🟠 Control Panel Protocol: Reverse engineer serial communication for HLE {#issue-kn5000-9ye}

**ID:** `kn5000-9ye` | **Priority:** High | **Created:** 2026-01-25

Reverse engineer the serial protocol between maincpu and control panel MCUs (LEDs, buttons, rotary encoders). The MCUs lack ROM dumps, so MAME emulation requires HLE based on protocol understanding. Analyze maincpu-side code to document all commands, responses, and state machines.

**Depends on:** [`kn5000-p2c`](#issue-kn5000-p2c), [`kn5000-j3c`](#issue-kn5000-j3c), [`kn5000-ljl`](#issue-kn5000-ljl), [`kn5000-unb`](#issue-kn5000-unb), [`kn5000-32b`](#issue-kn5000-32b), [`kn5000-qhm`](#issue-kn5000-qhm)

---

### Feature Demo {#feature-demo}

#### 🟠 FeatureDemo: Identify and catalog UI widget types {#issue-kn5000-x13}

**ID:** `kn5000-x13` | **Priority:** High | **Created:** 2026-01-25

Analyze slide rendering code to identify all widget types: static text, styled text, images/icons, rectangles, lines, buttons, animations, piano keyboard display, waveform display, level meters. Document rendering parameters for each type.

---

#### 🟠 FeatureDemo: Locate slide data structures in ROM {#issue-kn5000-h7o}

**ID:** `kn5000-h7o` | **Priority:** High | **Created:** 2026-01-25

Find where Feature Demo presentation data is stored. Search for references to FTBMP01-06 images. Identify: slide table/index, per-slide data records, pointers to resources (images, text, MIDI). Document base addresses and overall structure.

---

#### 🟠 FeatureDemo: Reverse engineer slide record format {#issue-kn5000-bds}

**ID:** `kn5000-bds` | **Priority:** High | **Created:** 2026-01-25

Document the binary format of each slide record. Identify fields: slide type, duration/timing, background image ID, widget list pointer, MIDI file pointer, transition effects. Create struct definition documenting each field offset and size.

---

#### 🟡 FeatureDemo: Create ASL macros for slide definitions {#issue-kn5000-4q0}

**ID:** `kn5000-4q0` | **Priority:** Medium | **Created:** 2026-01-25

Design and implement ASL assembler macros for concise slide definitions: SLIDE_BEGIN/END, WIDGET_TEXT, WIDGET_IMAGE, WIDGET_RECT, SLIDE_MIDI, SLIDE_TIMING, etc. Macros should emit correct binary format while being human-readable.

---

#### 🟡 FeatureDemo: Create ASL macros for widget definitions {#issue-kn5000-br1}

**ID:** `kn5000-br1` | **Priority:** Medium | **Created:** 2026-01-25

Implement widget-specific macros: TEXT x,y,font,color,"string" / IMAGE x,y,id / RECT x,y,w,h,color / LINE x1,y1,x2,y2,color / BUTTON x,y,w,h,label. Ensure macros handle alignment and padding correctly.

---

#### 🟡 FeatureDemo: Document widget parameter formats {#issue-kn5000-dqi}

**ID:** `kn5000-dqi` | **Priority:** Medium | **Created:** 2026-01-25

For each widget type, document all parameters: position (x,y), size (w,h), colors, font ID, text string pointer, image ID, alignment, padding, border style, animation params. Create comprehensive widget parameter reference.

---

#### 🟡 FeatureDemo: Extract MIDI files as standalone files {#issue-kn5000-kxw}

**ID:** `kn5000-kxw` | **Priority:** Medium | **Created:** 2026-01-25

Extract all embedded MIDI data as playable .mid files. Parse MIDI structure to find exact boundaries. Name files descriptively. Verify extracted files play correctly in standard MIDI player. Add to project assets.

---

#### 🟡 FeatureDemo: Locate embedded MIDI data {#issue-kn5000-qjx}

**ID:** `kn5000-qjx` | **Priority:** Medium | **Created:** 2026-01-25

Find all embedded MIDI files in the ROM. Search for MIDI headers (4D 54 68 64 = 'MThd'). Document: offset, size, apparent purpose (demo song, UI sound, jingle). May be in main CPU ROM or table data ROM.

---

#### 🟡 FeatureDemo: Refactor assembly to use slide macros {#issue-kn5000-21e}

**ID:** `kn5000-21e` | **Priority:** Medium | **Created:** 2026-01-25

Replace raw data definitions in assembly source with new macros. Convert existing db/dw sequences to SLIDE_BEGIN, WIDGET_*, SLIDE_END. Verify rebuilt ROM still matches original byte-for-byte. Measure source code line reduction.

---

#### ⚪ FeatureDemo: Create slide viewer/editor tool {#issue-kn5000-waa}

**ID:** `kn5000-waa` | **Priority:** Low | **Created:** 2026-01-25

Build a tool to parse and display Feature Demo slides outside the keyboard. Could be Python script with PIL/Pillow for rendering. Useful for: verifying extraction, editing slides, creating custom demos. Output as PNG or HTML.

---

#### ⚪ FeatureDemo: Document demo sequence and timing {#issue-kn5000-0bq}

**ID:** `kn5000-0bq` | **Priority:** Low | **Created:** 2026-01-25

Create complete documentation of the Feature Demo: slide order, timing between slides, which MIDI plays when, user interaction points (if any), loop behavior. Add screenshots/video to documentation website.

---

### Firmware Update {#firmware-update}

#### 🟡 Update: Document FDC interaction during update {#issue-kn5000-70b}

**ID:** `kn5000-70b` | **Priority:** Medium | **Created:** 2026-01-25

Trace how the Floppy Disk Controller (0x110000) is used during updates. Document: disk detection, file reading sequence, sector layout, error recovery, multi-disk handling (Change FD 2 of 2 message).

---

#### 🟡 Update: Document HDAE5000 update procedure {#issue-kn5000-e7f}

**ID:** `kn5000-e7f` | **Priority:** Medium | **Created:** 2026-01-25

Analyze how HD-AE5000 firmware is updated. Document: separate update disk format, communication via PPI (0x160000), Flash chips on expansion board, version compatibility checks. Reference v1.10i through v2.0i updates.

---

#### 🟡 Update: Document update progress display {#issue-kn5000-6f7}

**ID:** `kn5000-6f7` | **Priority:** Medium | **Created:** 2026-01-25

Analyze LCD messages during update process. Correlate extracted 1-bit bitmaps with update stages: Flash Memory Update, Please Wait, Now Erasing, FD to Flash Memory, Completed, Turn On AGAIN, Illegal Disk. Document state machine.

---

#### 🟡 Update: Document validation and error handling {#issue-kn5000-acu}

**ID:** `kn5000-acu` | **Priority:** Medium | **Created:** 2026-01-25

Trace update validation routines. Document: file header validation, checksum algorithms, version checking, ROM verification after write, error recovery procedures, what triggers 'Illegal Disk' message.

---

#### 🟡 Update: Reverse engineer Flash erase algorithm {#issue-kn5000-dkx}

**ID:** `kn5000-dkx` | **Priority:** Medium | **Created:** 2026-01-25

Trace the Flash ROM erase routine in firmware. Document: chip unlock sequence, sector erase commands, chip erase commands, erase verification, timeout handling. Note any chip-specific variations. Cross-reference with Flash datasheet.

---

#### 🟡 Update: Reverse engineer Flash program algorithm {#issue-kn5000-1tn}

**ID:** `kn5000-1tn` | **Priority:** Medium | **Created:** 2026-01-25

Trace the Flash ROM programming routine. Document: byte/word program commands, unlock sequences, program verification, error handling, write protection. Identify if using byte-program or page-buffer mode.

---

#### ⚪ Update: Create update file parser tool {#issue-kn5000-87m}

**ID:** `kn5000-87m` | **Priority:** Low | **Created:** 2026-01-25

Build Python tool to parse and analyze update floppy files. Extract: header info, version numbers, payload data, checksums. Enable creation of custom update files for homebrew development.

---

#### ⚪ Update: Document complete update procedure for users {#issue-kn5000-7v8}

**ID:** `kn5000-7v8` | **Priority:** Low | **Created:** 2026-01-25

Write end-user documentation for performing system updates. Include: required materials, step-by-step instructions, troubleshooting, safety warnings about power loss during update. Add to documentation website.

---

### HD-AE5000 Expansion {#hd-ae5000-expansion}

#### 🟠 HDAE5000: Disassemble ROM at 0x280000 {#issue-kn5000-kuu}

**ID:** `kn5000-kuu` | **Priority:** High | **Created:** 2026-01-25

Disassemble and analyze the 512KB HDAE5000 ROM mapped at 0x280000. Identify entry points, command handlers, filesystem routines, and communication protocols. Determine CPU type if different from main board.

---

#### 🟡 HDAE5000: Document filesystem structure {#issue-kn5000-44c}

**ID:** `kn5000-44c` | **Priority:** Medium | **Created:** 2026-01-25

Analyze how files are organized on the 1.08GB hard disk. Document directory structure, file allocation table format, metadata storage, and how the Flash-ROM/SRAM quick directory access works. Compare with standard DOS/FAT if applicable.

---

#### 🟡 HDAE5000: Document interface cable pinout {#issue-kn5000-mzz}

**ID:** `kn5000-mzz` | **Priority:** Medium | **Created:** 2026-01-25

Determine the pinout of the cable connecting HD-AE5000 to KN5000. Identify connector types, signal assignments (accent data, accent control, accent bus, accent power), and voltage levels. Reference service manual if available.

---

#### 🟡 HDAE5000: Reverse engineer parallel port protocol {#issue-kn5000-t8n}

**ID:** `kn5000-t8n` | **Priority:** Medium | **Created:** 2026-01-25

Document the parallel port communication protocol used by HD-TechManager5000 PC software. Capture and analyze traffic if possible. Identify handshaking signals, command/response format, file transfer protocol, and error handling.

---

#### ⚪ HDAE5000: Analyze HD-TechManager5000 software {#issue-kn5000-qnf}

**ID:** `kn5000-qnf` | **Priority:** Low | **Created:** 2026-01-25

Reverse engineer the Windows HD-TechManager5000 software to understand the PC side of the parallel port protocol. Extract command definitions, file format handling, and UI functionality. Installation disks available at archive.org.

---

### Image Extraction {#image-extraction}

#### 🟠 Images: Find embedded image locations in main CPU ROM {#issue-kn5000-87u}

**ID:** `kn5000-87u` | **Priority:** High | **Created:** 2026-01-25

Scan the main CPU ROM for embedded images. Look for: BMP headers (0x42 0x4D), consistent pixel data patterns, references in code to image addresses, LCD display routines that load image data. Document offset, size, and apparent format for each image found.

---

#### 🟠 Images: Find embedded image locations in table data ROM {#issue-kn5000-16s}

**ID:** `kn5000-16s` | **Priority:** High | **Created:** 2026-01-25

Scan the 2MB table data ROM for embedded images. This ROM likely contains most graphical assets. Look for BMP headers, icon data, splash screens, UI elements. Cross-reference with table_data/images/ directory which may already have some extractions.

---

#### 🟡 Images: Extract all images as binary files {#issue-kn5000-pcq}

**ID:** `kn5000-pcq` | **Priority:** Medium | **Created:** 2026-01-25

Create extraction script to dump all identified images as individual binary files. Output to maincpu/images/ and table_data/images/ directories. Name files descriptively based on apparent purpose (icon_play.bin, splash_logo.bin, etc.). Generate manifest listing all extracted images.

---

#### 🟡 Images: Reverse engineer image format {#issue-kn5000-36g}

**ID:** `kn5000-36g` | **Priority:** Medium | **Created:** 2026-01-25

Document the image format(s) used. Determine: pixel format (1bpp, 4bpp, 8bpp, RGB), dimensions encoding, palette format if indexed, compression if any, header structure. The LCD controller IC206 (MN89304) specs may indicate supported formats.

---

#### 🟡 Images: Update assembly sources to include binary images {#issue-kn5000-4rr}

**ID:** `kn5000-4rr` | **Priority:** Medium | **Created:** 2026-01-25

Modify assembly sources to include extracted image binaries using ASL incbin directive. Ensure correct alignment and placement. Verify rebuilt ROM matches original byte-for-byte at image locations. Update extract_include_binaries.py if needed.

---

#### ⚪ Images: Convert images to viewable formats {#issue-kn5000-pkx}

**ID:** `kn5000-pkx` | **Priority:** Low | **Created:** 2026-01-25

Create conversion tools to export extracted images as PNG/BMP for documentation. Handle any custom palette or pixel format. Add converted images to documentation website for reference. Useful for identifying what each image represents.

---

### Main CPU ROM {#main-cpu-rom}

#### 🟠 maincpu: Fix 177 divergent bytes {#issue-kn5000-kqy}

**ID:** `kn5000-kqy` | **Priority:** High | **Created:** 2026-01-25

Main CPU ROM (kn5000_v10_program.rebuilt.rom) is at 99.99% match with 177 incorrect bytes remaining. Need to identify each divergent byte offset, decode the expected vs actual instruction, and fix the assembly source or macros in tmp94c241.inc.

---

### Other {#other}

#### 🔴 ROM Reconstruction: Achieve 100% byte-matching for all ROMs {#issue-kn5000-99f}

**ID:** `kn5000-99f` | **Priority:** Critical | **Created:** 2026-01-25

**Depends on:** [`kn5000-cfe`](#issue-kn5000-cfe), [`kn5000-kqy`](#issue-kn5000-kqy), [`kn5000-hlw`](#issue-kn5000-hlw)

---

#### 🟠 Document all serial command bytes and their purposes {#issue-kn5000-p2c}

**ID:** `kn5000-p2c` | **Priority:** High | **Created:** 2026-01-25

Analyze maincpu code to catalog all 2-byte command sequences sent to control panel MCUs. Commands seen so far: 1f/1d/1e/dd (init), 20/25/2b (data), e0/e2/e3/eb (extended). Map each command to its purpose and expected response.

---

#### 🟠 Extract hardware info from service manual schematics {#issue-kn5000-z9k}

**ID:** `kn5000-z9k` | **Priority:** High | **Created:** 2026-01-25

Analyze the KN5000 service manual (59 pages) to extract hardware architecture details. Focus on: CPU section (II-11), Control section (II-9), Block diagram (II-3/4), Control panel boards (II-35, II-38). Document IC pinouts, signal names, and interconnections.

**Notes:** Significant progress: Analyzed schematic pages II-9 to II-38. Documented main CPU (TMP94C241F), all memory ICs, control panel MCUs (M37471M2196S), button mappings, serial signals. Created hardware-architecture.md page.

**Depends on:** [`kn5000-bcn`](#issue-kn5000-bcn), [`kn5000-jwk`](#issue-kn5000-jwk), [`kn5000-xhi`](#issue-kn5000-xhi)

---

#### 🟠 Trace CPANEL_SERIAL_ROUTINE_* handlers {#issue-kn5000-32b}

**ID:** `kn5000-32b` | **Priority:** High | **Created:** 2026-01-25

Trace execution flow through all CPANEL_SERIAL_ROUTINE_0 through CPANEL_SERIAL_ROUTINE_8 handlers. Document what each handler does, when it's called, and how it processes data.

---

#### 🟡 ASL Macros: Document new TMP94C241 instruction encodings {#issue-kn5000-3o6}

**ID:** `kn5000-3o6` | **Priority:** Medium | **Created:** 2026-01-25

Several new macros were added to tmp94c241.inc during subcpu_boot disassembly:

Jump/Call macros:
- JRL_T target: Jump relative long (78 LL HH) - 3 bytes vs jp's 4 bytes
- CALR target: Call relative (1e LL HH) - 3 bytes vs call's 4 bytes  
- CALL_ABS24 target: Call absolute 24-bit (1d LL MM HH)

Block transfer macros:
- LDIR_94: Block copy with TMP94C241 encoding (83 11 vs ASL's 85 11)

Register load macros (for correct immediate encoding):
- LD_A value: Load A with immediate (21 nn)
- LD_D value: Load D with immediate (24 nn)

These address encoding differences between TMP94C241 and TMP96C141 (which ASL targets).

TODO: Document general encoding patterns for creating future macros.

---

#### 🟡 Analyze ROTA/ROTB rotary encoder circuit {#issue-kn5000-xhi}

**ID:** `kn5000-xhi` | **Priority:** Medium | **Created:** 2026-01-25

Block diagram shows ROTA and ROTB signals from control panel. Find the encoder circuit in schematics, determine: number of encoders, connection to MCU pins, any conditioning circuitry (pull-ups, filters). This helps understand encoder data format in protocol.

---

#### 🟡 Design MAME HLE device for control panel {#issue-kn5000-qhm}

**ID:** `kn5000-qhm` | **Priority:** Medium | **Created:** 2026-01-25

Based on protocol documentation, design the C++ interface for a MAME HLE device that emulates control panel MCU behavior. Define state machine, command handlers, and input/output bindings.

**Depends on:** [`kn5000-p2c`](#issue-kn5000-p2c), [`kn5000-j3c`](#issue-kn5000-j3c), [`kn5000-ljl`](#issue-kn5000-ljl), [`kn5000-unb`](#issue-kn5000-unb)

---

#### 🟡 Map LED indices to physical panel LEDs {#issue-kn5000-ljl}

**ID:** `kn5000-ljl` | **Priority:** Medium | **Created:** 2026-01-25

Analyze CPANEL_INDEX_FOR_LEDS and LED command handling to understand LED addressing scheme. Create a mapping from index to physical LED name/location on the KN5000 front panel.

---

#### 🟡 Map button indices to physical panel buttons {#issue-kn5000-j3c}

**ID:** `kn5000-j3c` | **Priority:** Medium | **Created:** 2026-01-25

Analyze STATE_OF_CPANEL_BUTTONS array and related code to understand how button states are indexed. Create a mapping from array index to physical button name/location on the KN5000 front panel.

---

#### 🟡 Understand rotary encoder data format {#issue-kn5000-unb}

**ID:** `kn5000-unb` | **Priority:** Medium | **Created:** 2026-01-25

Analyze how rotary encoder values are transmitted. Determine: absolute vs relative encoding, resolution/steps per rotation, which commands query encoder state.

---

#### 🟡 Update website with service manual findings {#issue-kn5000-8q2}

**ID:** `kn5000-8q2` | **Priority:** Medium | **Created:** 2026-01-25

After extracting info from service manual schematics, update kn5000-docs website: add hardware architecture page, update control-panel-protocol.md with confirmed signals (DATA/BCK/ROTA/ROTB), add IC reference table, include block diagram description.

**Depends on:** [`kn5000-z9k`](#issue-kn5000-z9k)

---

#### ⚪ Maintain documentation website {#issue-kn5000-9a0}

**ID:** `kn5000-9a0` | **Priority:** Low | **Created:** 2026-01-25

Keep the kn5000-docs Jekyll website in sync with reverse engineering progress. Update status, add findings, maintain open questions list. Website repo: claude_jail/kn5000-docs/

---

### Sound & Audio {#sound-audio}

#### 🟠 Sound: Document DAC IC310 {#issue-kn5000-xel}

**ID:** `kn5000-xel` | **Priority:** High | **Created:** 2026-01-25

Identify and document the DAC chip (IC310). Find datasheet. Document: resolution (bits), sample rate, number of channels, interface protocol (I2S, parallel), output specifications.

---

#### 🟠 Sound: Document DSP IC311 {#issue-kn5000-xv2}

**ID:** `kn5000-xv2` | **Priority:** High | **Created:** 2026-01-25

Identify and document the DSP chip (IC311). Find datasheet. Document: DSP architecture, instruction set if programmable, effects capabilities (reverb, chorus, EQ), interface to main/sub CPU, audio data format.

---

#### 🟠 Sound: Document Waveform ROM (IC306-307) {#issue-kn5000-d38}

**ID:** `kn5000-d38` | **Priority:** High | **Created:** 2026-01-25

Analyze the waveform ROM chips. Document: total size, data format, sample encoding (PCM bits, compression), how samples are indexed, instrument mapping. These contain the raw sound samples for synthesis.

---

#### 🟡 Sound: Document MIDI implementation {#issue-kn5000-ake}

**ID:** `kn5000-ake` | **Priority:** Medium | **Created:** 2026-01-25

Fully document MIDI capabilities. Trace: MIDI IN/OUT/THRU handling, channel assignments, supported controllers (CC), SysEx commands, GM/GS/XG compatibility, MIDI clock sync, sequencer integration.

---

#### 🟡 Sound: Document audio output path {#issue-kn5000-jy9}

**ID:** `kn5000-jy9` | **Priority:** Medium | **Created:** 2026-01-25

Trace complete audio signal path from DAC to output jacks. Document: analog circuitry, amplifier stages, headphone amp, line out levels, speaker amp (if internal), any analog effects or mixing.

---

#### 🟡 Sound: Document effects processing chain {#issue-kn5000-si0}

**ID:** `kn5000-si0` | **Priority:** Medium | **Created:** 2026-01-25

Trace the audio effects signal path. Document: reverb types and parameters, chorus/flanger, EQ, effects routing (insert vs send), which chip handles each effect (DSP vs sub CPU), effects presets.

---

#### 🟡 Sound: Document rhythm/accompaniment engine {#issue-kn5000-98j}

**ID:** `kn5000-98j` | **Priority:** Medium | **Created:** 2026-01-25

Analyze how auto-accompaniment works. Document: rhythm pattern format, chord detection algorithm, bass/chord/rhythm part generation, style structure (intro/main/fill/ending), variation switching.

---

#### 🟡 Sound: Document synthesis architecture {#issue-kn5000-tvq}

**ID:** `kn5000-tvq` | **Priority:** Medium | **Created:** 2026-01-25

Understand how sounds are generated. Document: oscillator count (polyphony), synthesis method (sample playback, wavetable, FM), envelope generators (ADSR), LFO, filters. Trace sub CPU code for synthesis routines.

---

#### 🟡 Sound: Trace main CPU to Sub CPU command protocol {#issue-kn5000-061}

**ID:** `kn5000-061` | **Priority:** Medium | **Created:** 2026-01-25

Document how main CPU sends commands to sub CPU for sound generation. Trace latch communication at 0x120000. Document: note-on/off commands, program change, pitch bend, volume, pan, effects parameters. Create command reference.

---

#### ⚪ Sound: Extract and catalog all instrument patches {#issue-kn5000-cox}

**ID:** `kn5000-cox` | **Priority:** Low | **Created:** 2026-01-25

Extract instrument definitions from ROM. Document: patch names, sample mappings, envelope settings, filter settings, effects assignments. Create patch list matching front panel sound groups.

---

#### ⚪ Sound: Extract and convert waveform samples {#issue-kn5000-mrx}

**ID:** `kn5000-mrx` | **Priority:** Low | **Created:** 2026-01-25

Extract raw waveform data from ROM as playable audio. Convert to WAV format. Catalog samples by instrument type. Document sample rates, loop points, root notes. Useful for MAME sound emulation verification.

---

### Sub CPU {#sub-cpu}

#### 🟡 SubCPU: Document boot sequence handshake {#issue-kn5000-51z}

**ID:** `kn5000-51z` | **Priority:** Medium | **Created:** 2026-01-25

Trace the complete boot sequence: 1) Main CPU reset/init, 2) Sub CPU held in reset?, 3) Payload transfer trigger, 4) DMA transfer execution, 5) Sub CPU release from reset?, 6) Sub CPU boot ROM hands off to payload, 7) Sub CPU signals ready to main CPU. Document timing requirements.

---

#### 🟡 SubCPU: Document payload memory layout {#issue-kn5000-1ru}

**ID:** `kn5000-1ru` | **Priority:** Medium | **Created:** 2026-01-25

Analyze the 192KB sub CPU payload structure. Document: entry point address, interrupt vectors, code segments, data segments, any embedded tables or wavetables, and relationship to the 128KB boot ROM. Cross-reference with subcpu/kn5000_subprogram_v142.asm.

---

#### 🟡 SubCPU: Identify sub CPU type and memory map {#issue-kn5000-ayt}

**ID:** `kn5000-ayt` | **Priority:** Medium | **Created:** 2026-01-25

Determine the sub CPU chip type (IC27 on main board). Document its memory map: where the 128KB boot ROM resides, where the 192KB payload is loaded, RAM areas, and any memory-mapped I/O for tone generator control. Check service manual schematics.

---

### Table Data ROM {#table-data-rom}

#### 🟡 table_data: Improve from 32.42% match {#issue-kn5000-hlw}

**ID:** `kn5000-hlw` | **Priority:** Medium | **Created:** 2026-01-25

Table data ROM (kn5000_table_data.rebuilt.rom) is at 32.42% match with 1,417,294 incorrect bytes. This ROM is mostly binary data (images, assets). Lower priority than code ROMs - focus on verifying include() paths and binary data extraction.

---

### Video & Display {#video-display}

#### 🟡 Video: Document UI widget rendering {#issue-kn5000-5dc}

**ID:** `kn5000-5dc` | **Priority:** Medium | **Created:** 2026-01-25

Analyze how UI elements are drawn: buttons, sliders, menus, piano keyboard display, waveform displays, level meters. Document widget drawing routines, any sprite system, and how interactive elements are updated.

---

#### 🟡 Video: Document font system and text rendering {#issue-kn5000-kev}

**ID:** `kn5000-kev` | **Priority:** Medium | **Created:** 2026-01-25

Analyze how text is rendered on the LCD. Document: font data location in ROM, font format (bitmap or vector), character encoding, font sizes available, text drawing routines, any internationalization support.

---

#### 🟡 Video: Document pixel format and color palette {#issue-kn5000-hy8}

**ID:** `kn5000-hy8` | **Priority:** Medium | **Created:** 2026-01-25

Determine exact pixel format used by the display. Document: bits per pixel (likely 8bpp indexed), palette format and location, how palette is loaded, any direct color modes. Analyze extracted images to confirm format.

---

#### 🟡 Video: Document screen layout and regions {#issue-kn5000-rq0}

**ID:** `kn5000-rq0` | **Priority:** Medium | **Created:** 2026-01-25

Map the LCD screen layout: header area, main content area, status bar, any fixed regions. Document how different screens/modes use the display real estate. Create annotated screenshots showing region boundaries.

---

#### 🟡 Video: Reverse engineer drawing primitives {#issue-kn5000-gln}

**ID:** `kn5000-gln` | **Priority:** Medium | **Created:** 2026-01-25

Find and document graphics drawing routines in firmware: pixel plotting, line drawing, rectangle fill, bitmap blitting (BLT), text rendering. Document function addresses, parameters, and any hardware acceleration used.

---

#### ⚪ Video: Document animation and transition effects {#issue-kn5000-nmg}

**ID:** `kn5000-nmg` | **Priority:** Low | **Created:** 2026-01-25

Analyze fade-in/fade-out effects, screen transitions, any animated elements. Document: how BitmapFadeIn/FadeOut images work, timing of transitions, any hardware support for effects, scrolling implementation.

---

#### ⚪ Video: Extract and document all fonts {#issue-kn5000-dj3}

**ID:** `kn5000-dj3` | **Priority:** Low | **Created:** 2026-01-25

Extract font data from ROMs as usable assets. Convert to standard format (BDF, TTF, or PNG atlas). Document character coverage, sizes, styles. Add font samples to image gallery on website.

---

## Recently Closed

| Issue | Title | Closed |
|-------|-------|--------|
| `kn5000-jwk` | Document DATA/BCK serial interface pinout | 2026-01-26 |
| `kn5000-bcn` | Identify control panel MCU chip type from schematics | 2026-01-26 |
| `kn5000-toq` | Sound: Identify and document Sub CPU (IC27) | 2026-01-26 |
| `kn5000-7vw` | Update: Identify Flash ROM chip types | 2026-01-26 |
| `kn5000-qtl` | Update: Document key combinations for update mode | 2026-01-26 |
| `kn5000-3cm` | Update: Map file types to system components | 2026-01-26 |
| `kn5000-psz` | Update: Document floppy disk file formats | 2026-01-26 |
| `kn5000-6qi` | Video: Document LCD controller IC206 (MN89304) | 2026-01-26 |
| `kn5000-m91` | Video: Document Video RAM IC207 (M5M44265CJ8S) | 2026-01-26 |
| `kn5000-t75` | Video: Trace LCD initialization in firmware | 2026-01-26 |
| `kn5000-618` | HDAE5000: Analyze PPI interface at 0x160000 | 2026-01-26 |
| `kn5000-595` | Boot: Document sub CPU startup handshake | 2026-01-26 |
| `kn5000-c3p` | SubCPU: Trace payload transfer initialization | 2026-01-26 |
| `kn5000-dui` | SubCPU: Analyze inter-CPU latch protocol at 0x120000 | 2026-01-26 |
| `kn5000-fmq` | SubCPU: Document MicroDMA registers on TMP94C241F | 2026-01-26 |
| `kn5000-52e` | Boot: Document peripheral initialization order | 2026-01-26 |
| `kn5000-cav` | Boot: Document memory initialization sequence | 2026-01-26 |
| `kn5000-24m` | Boot: Document reset vector and early initialization | 2026-01-26 |
| `kn5000-b21` | SubCPU Boot: Fix remaining 1,981 byte divergences | 2026-01-26 |
| `kn5000-ii4` | SubCPU Boot: Disassemble DMA transfer routines (0xFF8604-... | 2026-01-26 |

*...and 1 more closed issues*

---

## Statistics

### By Priority

| Priority | Count |
|----------|-------|
| Critical | 1 |
| High | 14 |
| Medium | 44 |
| Low | 12 |

### By Category

| Category | Count |
|----------|-------|
| Boot Sequence | 5 |
| Control Panel | 1 |
| Feature Demo | 11 |
| Firmware Update | 8 |
| HD-AE5000 Expansion | 5 |
| Image Extraction | 6 |
| Main CPU ROM | 1 |
| Other | 12 |
| Sound & Audio | 11 |
| Sub CPU | 3 |
| Table Data ROM | 1 |
| Video & Display | 7 |

---

*Last updated: 2026-01-26 08:40*
