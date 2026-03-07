---
layout: page
title: Sound Categories
permalink: /sound-categories/
---

# Sound Categories

The KN5000 organizes its sounds into 16 categories (plus 2 user memory slots), managed by a pointer table at `0xE023B0` in the Main CPU Program ROM.

## Architecture

```
SOUND_DATA_SECTION_PTRS (0xE023B0)
├─ [0]  → SOUND_DATA_PIANO          (0xE02510)  Binary block, 8320 bytes
├─ [1]  → SOUND_DATA_GUITAR         (0xE04590)  Binary block, 1440 bytes
├─ [2]  → SOUND_DATA_STRINGS_VOCAL  (0xE04B30)  Binary block, 8320 bytes
├─ [3]  → SOUND_DATA_BRASS_PTRS     (0xE06BB0)  Pointer table → 3-byte patch entries
├─ [4]  → SOUND_DATA_FLUTE          (0xE06F30)  Binary block, 2498 bytes
├─ [5]  → SOUND_DATA_SAX_REED       (0xE08BB0)  Binary block, 1440 bytes
├─ [6]  → SOUND_DATA_MALLET_ORCH_PERC (0xE09150) Binary block, 7296 bytes
├─ [7]  → SOUND_DATA_WORLD_PERC     (0xE0ADCD)  Pointer table → 3-byte patch entries
├─ [8]  → SOUND_DATA_ORGAN_ACCORDION (0xE0B190) Inline 2-byte pairs, 128 entries
├─ [9]  → SOUND_DATA_ORCHESTRAL_PAD (0xE0B250)  Binary block, 128 bytes
├─ [10] → SOUND_DATA_SYNTH          (0xE0B2D0)  Binary block, 256 bytes
├─ [11] → SOUND_DATA_BASS           (0xE0B3D0)  Binary block, 18 bytes
├─ [12] → SOUND_DATA_DIGITAL_DRAWBAR (0xE0B3E2) Binary block, 18 bytes
├─ [13] → SOUND_DATA_ACCORDION_REG  (0xE0B3F4)  Binary block, 18 bytes
├─ [14] → SOUND_DATA_GM_SPECIAL     (0xE0B406)  Binary block, 18 bytes
└─ [15] → SOUND_DATA_DRUM_KITS      (0xE0B418)  Binary block, 213 bytes

SOUND_CATEGORY_NAMES (0xE023F0)
├─ [0]  "PIANO"
├─ [1]  "GUITAR"
├─ [2]  "STRINGS & VOCAL"
├─ [3]  "BRASS"
├─ [4]  "FLUTE"
├─ [5]  "SAX & REED"
├─ [6]  "MALLET&ORCH PERC"
├─ [7]  "WORLD PERC"
├─ [8]  "ORGAN&ACCORDION"
├─ [9]  "ORCHESTRAL PAD"
├─ [10] "SYNTH"
├─ [11] "BASS"
├─ [12] "DIGITAL DRAWBAR"
├─ [13] "ACCORDION REG."
├─ [14] "GM SPECIAL"
├─ [15] "DRUM KITS"
├─ [16] "MEMORY A"         (user-stored, in DRAM)
└─ [17] "MEMORY B"         (user-stored, in DRAM)
```

## Pointer Table (0xE023B0)

The `SOUND_DATA_SECTION_PTRS` table contains 16 × 32-bit pointers, one per factory sound category. Each pointer references the start of that category's voice data in ROM.

A metadata record at `0xE023A0` precedes the pointer table:

| Offset | Value | Description |
|--------|-------|-------------|
| +0 | Pointer to `SOUND_CATEGORY_NAMES` | Name string table |
| +4 | 0x0012 | Number of name entries (18, includes MEMORY A/B) |
| +8 | 0x0028 | Unknown (possibly record stride or count) |
| +12 | 0xFFFFFFFF | Sentinel / end marker |

## Data Formats

The 16 categories use three different data formats:

### Format 1: Binary Block

Used by most categories. Each block starts with a variable-length header followed by 2-byte records.

**Large categories (PIANO, STRINGS & VOCAL):**

| Offset | Size | Description |
|--------|------|-------------|
| 0x00-0x07 | 8 bytes | Sub-category index (sequential: 0,1,2,3,4,5,6,7) |
| 0x08-0x7F | 120 bytes | Zero padding (alignment to 128 bytes) |
| 0x80+ | Variable | 2-byte voice records: `{voice_id, variation}` |

These have 8 sub-categories with up to 4096 voice records total (8320 bytes = 128 header + 8192 data).

**Medium categories (GUITAR, SAX & REED, FLUTE, MALLET & ORCH PERC):**

No 128-byte header. Data begins immediately with 2-byte records. FLUTE has a 10-entry sub-category index (bytes 0-9) before the voice data, suggesting 10 sub-groups.

**Small categories (BASS, DIGITAL DRAWBAR, ACCORDION REG., GM SPECIAL):**

Only 18 bytes each — likely 9 voice entries of 2 bytes.

### Format 2: Pointer Table with 3-Byte Patch Entries

Used by **BRASS** (128 entries) and **WORLD PERC** (128 entries).

Each category contains:
1. A table of 128 × 32-bit pointers (512 bytes)
2. 128 × 3-byte patch entries, each referenced by one pointer

**Patch entry format:**

| Byte | Description |
|------|-------------|
| 0 | Voice/program number (0x00-0x7F) |
| 1 | Bank/variation number (0x00-0x05) |
| 2 | Terminator (always 0xFF) |

**Example BRASS entries:**

| Index | Bytes | Interpretation |
|-------|-------|----------------|
| 0 | `00 00 FF` | Program 0, bank 0 |
| 1 | `01 00 FF` | Program 1, bank 0 |
| 3 | `01 01 FF` | Program 1, bank 1 |
| 31 | `26 01 FF` | Program 38, bank 1 |
| 84 | `75 02 FF` | Program 117, bank 2 |

**WORLD PERC** entries are simpler — mostly sequential program numbers with bank 0 (e.g., `00 00 FF`, `01 00 FF`, ... `7F 00 FF`).

### Format 3: Inline 2-Byte Pairs

Used by **ORGAN & ACCORDION** only. Contains 128 × 2-byte entries directly in the ROM (no pointer indirection, no binary include).

Each entry is `{voice_id, 0x00}` with voice IDs in the 0xF0-0xFD range, suggesting organ voices use a separate synthesis mode (IDs ≥ 0xF0 may select drawbar/pipe organ algorithms instead of standard PCM voices).

**Organ voice groups (by voice_id):**

| Voice ID | Count | Likely Type |
|----------|-------|-------------|
| 0xF0 | 24 | Standard organ |
| 0xF1 | 8 | Organ variant 1 |
| 0xF2 | 8 | Organ variant 2 |
| 0xF3 | 8 | Organ variant 3 |
| 0xF5 | 8 | Organ variant 5 |
| 0xF7 | 8 | Organ variant 7 |
| 0xFC | 8 | Organ variant C |
| 0xFD | 8 | Organ variant D |

## Category Size Summary

| Index | Category | Format | Size | Entries |
|-------|----------|--------|------|---------|
| 0 | PIANO | Binary block | 8,320 B | ~4,096 voice records |
| 1 | GUITAR | Binary block | 1,440 B | ~720 voice records |
| 2 | STRINGS & VOCAL | Binary block | 8,320 B | ~4,096 voice records |
| 3 | BRASS | Pointer table | 896 B | 128 patch entries |
| 4 | FLUTE | Binary block | 2,498 B | ~1,185 voice records |
| 5 | SAX & REED | Binary block | 1,440 B | ~720 voice records |
| 6 | MALLET & ORCH PERC | Binary block | 7,296 B | ~3,584 voice records |
| 7 | WORLD PERC | Pointer table | 896 B | 128 patch entries |
| 8 | ORGAN & ACCORDION | Inline pairs | 256 B | 128 entries |
| 9 | ORCHESTRAL PAD | Binary block | 128 B | 64 voice records |
| 10 | SYNTH | Binary block | 256 B | 128 voice records |
| 11 | BASS | Binary block | 18 B | 9 voice records |
| 12 | DIGITAL DRAWBAR | Binary block | 18 B | 9 voice records |
| 13 | ACCORDION REG. | Binary block | 18 B | 9 voice records |
| 14 | GM SPECIAL | Binary block | 18 B | 9 voice records |
| 15 | DRUM KITS | Binary block | 213 B | ~106 voice records |

**Total sound data in Program ROM:** ~31,745 bytes (0xE02510-0xE0B4EC)

## Sound Selection Flow

When a user selects a sound:

1. **UI event** — Sound button press generates a control panel event
2. **Category lookup** — Main CPU reads `SOUND_DATA_SECTION_PTRS[category_index]` to get the data pointer
3. **Voice lookup** — Within the category data, the selected voice index maps to a `{voice_id, bank}` pair
4. **Command encoding** — `Audio_SendCommand` formats a MIDI Program Change (or extended command) with the voice/bank parameters
5. **Inter-CPU transfer** — Command sent via `sendCOMM` → `InterCPU_Send_Data_Block` → latch at 0x120000
6. **Sub CPU processing** — `Audio_CmdHandler_00_1F` writes to ring buffer → `MIDI_Dispatch` routes to `Voice_ProgChange`
7. **Voice activation** — Sub CPU updates the voice parameter block (287 bytes at `0x041300 + channel × 0x11F`)

## Research Needed

- [ ] Decode the exact binary format of large categories (PIANO, STRINGS & VOCAL, MALLET & ORCH PERC)
- [ ] Determine meaning of sub-category indices in headers (bytes 0-7 or 0-9)
- [ ] Map voice_id/bank pairs to actual sound names (e.g., voice 0x00 bank 0 = "Grand Piano 1")
- [ ] Trace UI event codes that trigger sound selection
- [ ] Document MEMORY A/B user sound storage format in DRAM
- [ ] Understand voice IDs ≥ 0xF0 (organ drawbar mode hypothesis)
- [ ] Analyze relationship between these voice_id values and Table Data ROM waveform indices

## Code References

| Symbol | Address | Description |
|--------|---------|-------------|
| `SOUND_DATA_SECTION_PTRS` | 0xE023B0 | 16-entry pointer table to category data |
| `SOUND_CATEGORY_NAMES` | 0xE023F0 | 18 × padded ASCII category name strings |
| `SOUND_DATA_PIANO` | 0xE02510 | Piano voice data (8320 bytes) |
| `SOUND_DATA_BRASS_PTRS` | 0xE06BB0 | Brass pointer table (128 entries) |
| `SOUND_DATA_WORLD_PERC` | 0xE0ADCD | World Perc pointer table (128 entries) |
| `SOUND_DATA_ORGAN_ACCORDION` | 0xE0B190 | Organ inline 2-byte pairs (128 entries) |
| `Audio_SendCommand` | 0xFF0B6B | Main CPU audio command interface (197+ call sites) |
| `Voice_ProgChange` | Sub CPU | Sub CPU program change handler |

## Related Pages

- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) - Sound generation overview
- [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) - Command transfer details
- [SysEx Messages]({{ site.baseurl }}/sysex-messages/) - Sound parameter SysEx
- [Storage Subsystem]({{ site.baseurl }}/storage-subsystem/) - Table Data ROM (waveform storage)
