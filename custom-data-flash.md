---
layout: page
title: Custom Data Flash
permalink: /custom-data-flash/
---

# Custom Data Flash Organization

The Custom Data Flash is a **1MB AMD AM29LV800B** flash ROM at IC19, mapped at **0x300000-0x3FFFFF**. It stores user-writable data: custom accompaniment styles, registration memory, LCD wallpaper screenshots, and serves as a staging area for SubCPU firmware updates.

## Hardware

The firmware identifies the flash chip via the AMD unlock command sequence (`0xAAAA`/`0x5555` writes) and checks device IDs `0x2223` (AM29LV800B-T) and `0x22AB` (AM29LV800B-B). The chip is programmed from the "initial data disk" during factory setup.

## ROM Layout

| Address Range | Size | Contents |
|:---|:---|:---|
| `0x300000-0x316FFF` | 92KB | Section 0: Custom Style Data |
| `0x317000-0x318FFF` | 8KB | Erased boot block sector gap |
| `0x319000-0x346FFF` | 184KB | Sections 1-2: Custom Style Data |
| `0x347000-0x348FFF` | 8KB | Erased sector gap |
| `0x349000-0x376FFF` | 184KB | Sections 3-4: Custom Style Data |
| `0x377000-0x378FFF` | 8KB | Erased sector gap |
| `0x379000-0x3A6FFF` | 184KB | Sections 5-6: Custom Style Data |
| `0x3A7000-0x3AFFFF` | 36KB | Unused (erased) |
| `0x3B0000-0x3B0FFF` | 4KB | Section 7: SubCPU Performance Data |
| `0x3B1000-0x3BFFFF` | 60KB | Unused (erased) |
| `0x3C0000-0x3D2FFF` | 78KB | LCD Wallpaper/Screenshot Storage |
| `0x3D3000-0x3D3FFF` | 4KB | Registration Memory |
| `0x3D4000-0x3DFFFF` | 48KB | Unused (erased) |
| `0x3E0000-0x3FFFFF` | 128KB | SubCPU Payload Staging Area |

The 8KB gaps between style sections correspond to flash boot block sector boundaries. The AM29LV800B has non-uniform sector sizes near the bottom of its address range.

## Section Pointer Table

The firmware computes 8 section pointers at runtime (`LABEL_F16A57` in main CPU ROM) and stores them in internal RAM:

| Section | Address | RAM Ptr | Contents |
|:---|:---|:---|:---|
| 0 | 0x300000 | 0x0C76 | Custom accompaniment styles |
| 1 | 0x319800 | 0x0C7A | Custom accompaniment styles |
| 2 | 0x330000 | 0x0C7E | Custom accompaniment styles |
| 3 | 0x349800 | 0x0C82 | Custom accompaniment styles |
| 4 | 0x360000 | 0x0C86 | Custom accompaniment styles |
| 5 | 0x379800 | 0x0C8A | Custom accompaniment styles |
| 6 | 0x390000 | 0x0C8E | Custom accompaniment styles |
| 7 | 0x3B0000 | 0x0C92 | SubCPU performance data |

## "HK" Header Format

Style sections (0-7) begin with a 4-byte header using 16-bit character encoding:

| Offset | Size | Value | Description |
|:---|:---|:---|:---|
| +0x00 | word | 0x0048 | 'H' (16-bit) |
| +0x02 | word | 0x004B | 'K' (16-bit) |
| +0x04 | 4 bytes | varies | Flags/configuration |
| +0x08 | varies | data | Style parameters, names, MIDI patterns |

Style data contains accompaniment arrangement data including style names (e.g., "Bolero puro"), MIDI patterns, and configuration parameters.

## LCD Wallpaper Storage (0x3C0000)

77,824 bytes for capturing the LCD screen contents:
- **76,800 bytes**: 320x240 pixel image at 8bpp (one pixel per byte)
- **1,024 bytes**: Metadata/padding

Written by the `CaptureLcd` firmware routine. Zero-filled in factory state.

## Registration Memory (0x3D3000)

4KB region storing user registration presets (3 banks + configuration):

| Offset | Size | Contents |
|:---|:---|:---|
| +0x00 | 4 bytes | `HK ` header (ASCII + space + null) |
| +0x04 | 12 bytes | Configuration header (includes bank count) |
| +0x10 | varies | Bank 0: pointer table + parameter data |

Note: The registration memory uses 8-bit ASCII "HK" encoding (not 16-bit like the style sections).

Pointer entries within registration banks are 6 bytes each: 2-byte offset followed by 4-byte data value.

### Registration Memory Architecture

The firmware calls the registration memory system "Panel Memory" (PMEM). It allows users to save and recall complete instrument configurations using the PANEL MEMORY buttons (PM1-PM8).

**Terminology mapping:**
- **Panel Memory** = User-facing name for registration memory
- **MSP** (Music Style Programmer) = Internal firmware name for the settings data structure
- **RegObjTable** = Registration Object Table — the firmware's parameter registration system

**MSP Settings Structure:**
The active panel memory state is held in DRAM at `MSP_SETTINGS__BASE_ADDR` (0x1E8800), with a size of `MSP_SETTINGS` (0xC9A = 3,226 bytes per slot). The factory default template is at ROM address `MSP_DefaultSettings` (0xE15A68) and `MSP_FACTORY_DEFAULTS` (0xF6F62F).

**Registration Object Table system:**
The firmware uses a macro-driven registration system (`RegObjTable` / `RegObjTabl`) to register each parameter. Each registered object specifies:

| Field | Description |
|-------|-------------|
| ParamA | Object type/ID (e.g., 0x1600001-0x160000F for different setting categories) |
| ParamB | Handler function pointer (ROM address, e.g., 0xFA44E2, 0xFA48A9) |
| ParamC | Parameter descriptor / validation data |
| ParamD | DRAM storage address for this parameter |
| ParamE | Object flags/config (bits specify save/load behavior) |

Multiple subsystems register their parameters with unique type IDs:
- Type 0x01: Voice/instrument settings (handler at 0xFA48A9)
- Type 0x02: Volume/mix settings (handler at 0xFA496C)
- Type 0x03: Accompaniment settings (handler at 0xFA4A18)
- Type 0x04: Sound group settings (handler at 0xFA44E2)
- Type 0x0C: DSP/effect settings (handler at 0xFA58FB)
- Type 0x0D: Digital effect settings (handler at 0xFA5948)
- Type 0x0F: Advanced configuration (handler at 0xFA62CB)
- Type 0x10: Part settings (handler at 0xFA5995)

**MIDI SysEx Interface:**
Panel memory data can be transferred via MIDI System Exclusive messages, handled by `ExcPmemFunc` in the firmware. The SysEx handler supports indices 0-9, each selecting a specific PMEM operation (dump request, data receive, etc.). The dispatch table is at ROM address 0xE7FDD6.

**UI Integration:**
The Panel Memory UI is managed by `PmemModeBoxProc` and `IvPmemWindowPageCtlProc` routines (in the "toshi" code section). The MENU system displays "PANEL MEMORY MODE" for configuration, "PMEM BANK SELECT" for bank switching, and integrates with the broader settings menu alongside PERFORMANCE, CURRENT PANEL, PART SETTING, MIDI SETTING, COMPOSER, SEQUENCER, MSP USER, and SOUND MEMORY pages.

**Save/Recall Flow:**
1. **Save (Store):** Pressing PANEL MEMORY SET + PM1-PM8 iterates through all registered objects, reads their current DRAM values, and serializes them to the Custom Data Flash at 0x3D3000
2. **Recall (Load):** Pressing PM1-PM8 reads the stored data from flash, deserializes it, and writes values back to each registered parameter's DRAM address, triggering the associated handler functions to apply changes (e.g., sending audio commands to the SubCPU)
3. **Bank Switch:** Users can select different registration banks (3 banks available in the 4KB flash region), with the active bank index stored in the configuration header

## SubCPU Payload Staging (0x3E0000)

The 128KB region at 0x3E0000-0x3FFFFF is used during firmware updates to stage the compressed SubCPU executable payload. The `SubCPU_Send_Payload` routine reads from this address during boot if the LZSS decompression path from the Table Data ROM is used as a fallback source. Empty (0xFF fill) in factory-programmed state.

## Flash Programming

The main CPU ROM contains dedicated flash management routines:
- `Flash_IdentifyChip` (0xEF3723): Detects flash chip type using AMD command protocol
- `Flash_IdentifyAndValidateChip` (0xEF37A5): Validates chip ID against known device IDs
- `Flash_BurnWithProgress` (referenced by floppy update handlers): Programs flash sectors with progress indication

The flash programming uses the standard AMD byte-programming algorithm with polling for completion.
