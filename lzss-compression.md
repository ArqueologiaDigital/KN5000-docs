---
layout: default
title: LZSS Compression
nav_order: 18
---

# LZSS Compression

The KN5000 firmware uses LZSS compression (SLIDE4K format) for storing preset and parameter data. This page documents all compressed regions and the decompression routines.

## Compressed Data Regions

### Compressed Preset/Parameter Data (SLIDE4K Format)

| Property | Value |
|----------|-------|
| **ROM Component** | table_data |
| **Label** | `Compressed_Preset_Data_LZSS` |
| **Start Address** | `0x08E0000` (ROM offset) / `0x3E0000` (CPU address) |
| **End Address** | `0x08E6D40` |
| **Header Size** | 14 bytes |
| **Compressed Data Size** | 27,953 bytes |
| **Total Size** | 27,967 bytes |
| **Decompressed Size** | ~32,910 bytes |
| **Binary File** | `table_data/includes/preset_data_compressed.bin` |

**Header Structure:**
```
Offset  Size  Content
------  ----  -------
0x00    7     "SLIDE4K" (format signature)
0x07    1     0x00 (null terminator)
0x08    1     0x00
0x09    1     0x95
0x0A    1     0x00
0x0B    2     "}Z" (0x7D, 0x5A)
0x0D    1     0xEE
```

**Important Clarification:**

> **This compressed region does NOT contain the Sub CPU ROM.** Decompression yields ~33KB of parameter-like data, not the 192KB executable code found in `kn5000_subprogram_v142.rom`.

**Decompressed Data Characteristics:**
- Size: 32,910 bytes (0x808E) (vs 196,608 bytes for Sub CPU ROM)
- Content: Parameter/preset data structure, not executable code
- Most bytes are in MIDI range (0-127)
- Contains repeating structural patterns (e.g., `0x80 XX` flags, `00 03` record markers)
- Does NOT match the Sub CPU ROM byte patterns

---

<a id="disputed-interpretations"></a>

### ⚠️ Disputed Interpretation - Requires Further Investigation

> **AI/Human Disagreement:** The runtime destination and transfer mechanism described below was concluded by **Claude Code** (AI assistant) based on code analysis. However, **Felipe Sanches** believes this interpretation may be **incorrect** due to:
>
> 1. Dynamic memory map reconfiguration during boot stages is not fully understood
> 2. The `0x3E0000` address mapping mechanism is unclear
> 3. Transfer sizes (64KB blocks) don't match the preset data size (~33KB)
> 4. The fallback to `0x800000` produces `0xF7` padding bytes, not valid parameters
>
> **This section documents Claude's interpretation but should be treated as unverified.** Alternative interpretations are preserved below and require additional investigation.

---

**Decompressed Data Structure (Claude's interpretation):**

| Section | Offset | Size | Runtime Destination |
|---------|--------|------|---------------------|
| Main CPU Header | 0x0000-0x00AF | 176 bytes | Main CPU only (word at 0x100 → RAM 0x0404) |
| Sub CPU Audio Params | 0x00B0-0x808D | 32,734 bytes | Sub CPU address 0xF000+ |

**Transfer Mechanism (Claude's interpretation):**

The `SubCPU_Send_Payload` routine at `0xEF0692` handles the preset data transfer:

1. **Decompression**: LZSS data at `0x3E0000` is decompressed to Main CPU RAM at `0x50000`
2. **Word copy**: The word at offset `0x100` is copied to Main CPU RAM `0x0404`
3. **Bulk transfer**: Data from `0x50100` is sent to Sub CPU via E1 protocol

**Anomalies noted by Felipe (reasons for skepticism):**
- The bulk transfers send 64KB blocks (much larger than the ~33KB of meaningful data). Only the first ~33KB sent to Sub CPU 0xF000 contains preset parameters; the remaining bytes would be uninitialized RAM.
- If LZSS decompression fails (returns 0xFFFF), the code falls back to reading directly from `TABLE_DATA_ROM__BASE_ADDR` (0x800000), though this produces mostly 0xF7 padding bytes from the ROM's initial data region - not valid parameter data.
- The source address `0x3E0000` represents the LZSS data via an alternate memory mapping. The same data is at ROM offset `0xE0000`, which maps to `0x8E0000` in the standard Stage 2 boot configuration. The `0x3E0000` mapping mechanism is not understood.

**Alternative interpretations to investigate:**
- The data may have a completely different runtime destination
- The `0x3E0000` memory mapping may point to different physical memory at different boot stages
- There may be other ~33KB data transfers that are the actual destination for this data
- The preset data may be used in a way not yet understood

**Main CPU Header (0x00-0xAF):**
- Mostly zero bytes with sparse configuration values
- Key non-zero positions: 0x18-0x1B, 0x2E, 0x45, 0x57-0x5A, 0x61, 0x94-0x9E, 0xA4-0xA5
- Contains record marker `00 03 01 00` at offset 0x94
- Word at offset 0x100 is copied to Main CPU RAM 0x0404 before bulk transfer

**Sub CPU Audio Parameters (0x100+) - per Claude's interpretation:**
- **Destination**: Sub CPU address 0xF000 (overwrites ROM defaults) - *DISPUTED*
- Variable-length records, often starting with `00 03` marker
- 24 occurrences of `00 03` record markers
- Flag byte `0x80` indicates "value set" (actual value in next byte)
- Pattern `18 XX` appears to indicate parameter type codes
- Common sequence: `64 03 00 7F 20 00 70 80`
- Most values are MIDI-range (0-127), suggesting voice/audio parameters

**Sub CPU 0xF000 Area Usage (IF Claude's interpretation is correct):**

The Sub CPU ROM (`kn5000_subprogram_v142`) contains default values at 0xF000+. These are audio engine configuration tables:

| Address | Purpose |
|---------|---------|
| 0xF000-0xF01F | System configuration, counters |
| 0xF010-0xF100 | Voice parameters (ADSR envelopes) |
| 0xF100-0xF420 | Pitch tables, envelope lookups |
| 0xF420-0xF434 | Runtime buffer initialization |
| 0xF434-0xF460 | Serial buffer structures |
| 0xF48C+ | Voice polyphony/index tables |

If the interpretation is correct, the preset data would overwrite these defaults during boot, configuring factory presets for the audio engine.

**Open Questions - Preset Data Destination (Added due to AI/Human disagreement):**

The following questions remain open regarding where the LZSS preset data actually ends up:

1. **What does 0x3E0000 actually map to?** The memory bank configuration during boot needs investigation.
2. **Are there other ~33KB transfers?** Search for data transfers matching the preset data size.
3. **What happens to the "extra" bytes?** The 64KB transfer vs ~33KB data discrepancy is suspicious.
4. **Why does fallback produce 0xF7 bytes?** This suggests the fallback path may never be intended to work.

**Open Questions - Sub CPU Payload Transfer:**

The Sub CPU executable payload (~192KB) must be transferred to the Sub CPU via the inter-CPU communication latches during boot. The source location remains under investigation:

1. **Memory Map Reconfiguration:** During the two-stage boot process, the Table Data ROM is initially mapped at `0xE00000-0xFFFFFF`, then remapped to `0x800000-0x9FFFFF`. The payload source address may differ between Stage 1 and Stage 2 boot contexts.

2. **Potential Payload Locations:**
   - `0x830000-0x87FFFF` (Table Data ROM, post-remap) - Referenced by `SubCPU_Send_Payload`
   - `0xE30000-0xE7FFFF` (same physical ROM, Stage 1 boot context)
   - Other regions that become visible after memory controller configuration

3. **The `SubCPU_Send_Payload` routine** transfers data from multiple address ranges to different Sub CPU RAM regions. The exact mapping and whether the full 192KB executable is transferred vs. loaded from a separate Sub CPU ROM chip requires further analysis.

See [Boot Sequence](boot-sequence.md) and [Inter-CPU Protocol](inter-cpu-protocol.md) for related documentation.

---

## SLIDE4K Format Specification

SLIDE4K is a variant of LZSS (Lempel-Ziv-Storer-Szymanski) compression with the following parameters:

| Parameter | Value |
|-----------|-------|
| **Sliding Window Size** | 4,096 bytes (4KB) |
| **Window Offset Bits** | 12 bits (0x000 - 0xFFF) |
| **Match Length Bits** | 4 bits (encoded length + 2) |
| **Minimum Match Length** | 2 bytes |
| **Maximum Match Length** | 17 bytes (15 + 2) |
| **Window Pre-fill** | First 4,078 bytes (0xFEE) filled with 0x00 |

### Encoding Format

The compressed data consists of flag bytes followed by literal bytes or back-references:

1. **Flag Byte:** Each bit (LSB first) indicates the type of the next 8 elements:
   - Bit = 1: Literal byte follows
   - Bit = 0: Back-reference follows

2. **Literal Byte:** Single byte copied directly to output

3. **Back-Reference:** Two bytes encoding position and length:
   ```
   Byte 1: Low 8 bits of window offset
   Byte 2: [High 4 bits of offset][4-bit length]

   offset = (byte2 & 0xF0) << 4 | byte1
   length = (byte2 & 0x0F) + 2
   ```

### Decompression Algorithm

```python
def decompress_slide4k(data):
    window = bytearray(4096)
    window[0:0xFEE] = bytes(0xFEE)  # Pre-fill with zeros
    window_pos = 0xFEE
    output = bytearray()

    i = 0
    while i < len(data):
        flags = data[i]
        i += 1

        for bit in range(8):
            if i >= len(data):
                break

            if flags & (1 << bit):
                # Literal byte
                byte = data[i]
                i += 1
                output.append(byte)
                window[window_pos] = byte
                window_pos = (window_pos + 1) & 0xFFF
            else:
                # Back-reference
                if i + 1 >= len(data):
                    break
                low = data[i]
                high = data[i + 1]
                i += 2

                offset = ((high & 0xF0) << 4) | low
                length = (high & 0x0F) + 2

                for _ in range(length):
                    byte = window[offset]
                    output.append(byte)
                    window[window_pos] = byte
                    window_pos = (window_pos + 1) & 0xFFF
                    offset = (offset + 1) & 0xFFF

    return bytes(output)
```

---

## Decompression Routines

All LZSS decompression routines are located in the **table_data** ROM. They are used during boot and firmware update operations.

### LZSS_Decompress (Main Decompressor)

| Property | Value |
|----------|-------|
| **Address** | `0xFFCA50` (CPU) / `0x09FCA50` (ROM) |
| **Label** | `LZSS_Decompress` |
| **Purpose** | Main SLIDE4K decompression routine |

**Description:** This is the primary decompression routine that:
- Allocates a 4KB sliding window buffer via `malloc`
- Pre-fills the window with zeros (positions 0x0000 to 0x0FED)
- Reads the compressed size from the header
- Processes flag bytes and handles literal/back-reference encoding
- Displays progress during decompression
- Frees the window buffer when complete

**Stack Frame Layout:**
```
XSP+0x00: (local variable)
XSP+0x04: Flag byte (with sentinel in high byte)
XSP+0x06: Copy counter for back-reference
XSP+0x08: Match length
XSP+0x0A: Window write position
XSP+0x0C: Window base address (copy of +0x10)
XSP+0x10: Window buffer pointer (from malloc)
```

### LZSS_ReadByte

| Property | Value |
|----------|-------|
| **Address** | `0xFFC8C2` (CPU) / `0x09FC8C2` (ROM) |
| **Label** | `LZSS_ReadByte` |
| **Purpose** | Read next byte from compressed input stream |
| **Returns** | HL = byte read, or 0xFFFF if EOF |

**Description:** Handles sector buffering for reading compressed data. Reads 0x2400 bytes per sector from the table_data ROM and manages sector advancement for large compressed data.

### LZSS_OutputByte

| Property | Value |
|----------|-------|
| **Address** | `0xFFC935` (CPU) / `0x09FC935` (ROM) |
| **Label** | `LZSS_OutputByte` |
| **Purpose** | Write decompressed byte to output buffer |
| **Input** | A = byte to output |

**Description:** Buffers 4 bytes and writes them as a 32-bit word to the destination for efficient memory access. Uses buffer at RAM address 0x0C0A.

### LZSS_OutputByte_Alt

| Property | Value |
|----------|-------|
| **Address** | `0xFFC974` (CPU) / `0x09FC974` (ROM) |
| **Label** | `LZSS_OutputByte_Alt` |
| **Purpose** | Alternate output handler for different buffer |

**Description:** Variant of LZSS_OutputByte that uses buffer at RAM address 0x0C0E instead of 0x0C0A. Used in flash update operations.

### LZSS_ParseHeader

| Property | Value |
|----------|-------|
| **Address** | `0xFFC9B3` (CPU) / `0x09FC9B3` (ROM) |
| **Label** | `LZSS_ParseHeader` |
| **Purpose** | Parse and validate LZSS header for flash updates |

**Description:** Sets up source address (0x3E0000 = Table Data ROM), validates the header against expected signature at 0xA150, and pre-reads 4 sectors for initial buffer fill.

---

## RAM Variables

The LZSS routines use the following RAM locations:

| Address | Size | Purpose |
|---------|------|---------|
| `0x0C20` | 4 | Expected decompressed output size |
| `0x0C24` | 4 | Current output position |
| `0x0C28` | 4 | Source ROM address pointer |
| `0x0C2C` | 4 | Sector read buffer pointer |
| `0x0C30` | 2 | Display X coordinate (progress) |
| `0x0C32` | 2 | Display Y coordinate (progress) |
| `0x0C34` | 2 | Sector offset for progress display |
| `0x0C36` | 1 | Output byte counter (0-3 for 32-bit writes) |
| `0x0C0A` | 4 | Temporary output buffer (LZSS_OutputByte) |
| `0x0C0E` | 4 | Temporary output buffer (LZSS_OutputByte_Alt) |

---

## SLIDE String Markers

The firmware contains "SLIDE" string markers used to detect and validate SLIDE4K format headers:

| Location | Address | Label |
|----------|---------|-------|
| Main CPU | `0xEA2350` | `SLIDE_STRING` |
| Main CPU | `0xEA2376` | `SLIDE_STRING_2` |
| Table Data | `0x9FA150` | (within boot data) |

These strings are used by header validation routines to confirm that compressed data uses the SLIDE4K format before attempting decompression.

---

## Usage Context

### Boot Sequence

During the boot sequence, the Main CPU's `SubCPU_Send_Payload` routine:
1. Transfers uncompressed payload data from 0x830000-0x87FFFF to Sub CPU RAM
2. Optionally attempts to decompress data from 0x3E0000 (the SLIDE4K region)
3. If decompression fails (returns 0xFFFF), uses alternate uncompressed source
4. The Sub CPU ROM itself is a **separate chip** - not transferred from table_data

See [Boot Sequence](boot-sequence.md) for details.

### Firmware Updates

The LZSS decompressor is also used during firmware updates to handle compressed update files. The flash update handlers (at 0x9FD800-0x9FEA9C) can process compressed ROM images using both SLIDE4K and SLIDE8K formats.

---

## Compression Tools

### scripts/decompress_lzss.py

Decompresses SLIDE4K data from the table_data ROM.

```bash
# Extract and decompress from table_data ROM
python scripts/decompress_lzss.py --extract-from-rom original_ROMs/kn5000_table_data.ic11 output.bin

# Decompress standalone compressed file
python scripts/decompress_lzss.py compressed.bin output.bin
```

### scripts/compress_lzss.py

Compresses data using SLIDE4K algorithm. Supports byte-identical output via reference file.

```bash
# Standard compression
python scripts/compress_lzss.py input.bin output.bin

# Byte-identical compression (uses original compression decisions)
python scripts/compress_lzss.py input.bin output.bin --reference original_compressed.bin
```

**Note:** The `--reference` option decodes compression decisions from the original file and replays them, producing byte-identical output when the input data matches. This is necessary because the original Technics compressor uses specific offset/length choices that don't follow a simple greedy or lazy matching algorithm.

### Makefile Targets

```bash
# Full rebuild: assemble preset_data.asm → compress → include in ROM
make rebuild-preset-data

# Recompress only (without reassembly, uses existing uncompressed binary)
make recompress-lzss

# Clean intermediate files
make clean_preset_data
```

The build uses the reference file at `original_ROMs/preset_data_compressed.original.bin` to ensure byte-matching output.

---

## Source Files

### table_data/preset_data.asm

Assembly source file describing the preset data structure. Currently:
- **Header section (0x00-0xAF):** Fully defined with explicit `db` statements
- **Parameter section (0xB0+):** Binary include with documentation

```
table_data/preset_data.asm           <- Assembly source
    ↓ (assemble)
table_data/includes/preset_data.bin  <- Uncompressed binary
    ↓ (LZSS compress with --reference)
table_data/includes/preset_data_compressed.bin  <- Compressed, included in ROM
```

As reverse engineering progresses, more of the parameter section can be converted from binary include to documented data definitions.

### Related Files

| File | Description |
|------|-------------|
| `table_data/preset_data.asm` | Assembly source for preset data |
| `table_data/includes/preset_data_uncompressed.bin` | Original decompressed data (reference) |
| `table_data/includes/preset_data_compressed.bin` | Compressed output for ROM inclusion |
| `original_ROMs/preset_data_compressed.original.bin` | Reference for byte-matching compression |

---

## Future Work

- [ ] Reverse engineer parameter record format in detail
- [ ] Determine the exact purpose of each parameter type (`18 XX` codes)
- [ ] Convert more of preset_data.asm from binary include to documented data
- [ ] Investigate if any other data in the ROMs uses SLIDE4K compression
