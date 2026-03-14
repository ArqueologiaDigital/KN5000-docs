---
layout: page
title: Waveform ROM Format
permalink: /waveform-rom-format/
---

# Waveform ROM Format

The KN5000's tone generator (IC303, TC183C230002) reads waveform data from four 32Mbit (4MB) mask ROMs (IC304-IC307). These ROMs contain the PCM sample data used for all wavetable synthesis. This page documents the format of IC307, the only dumped waveform ROM.

## ROM Inventory

| IC | Part Number | Size | MAME Offset | Status |
|----|-------------|------|-------------|--------|
| IC304 | QS6GU3C32375 | 4 MB | 0x000000 | **NO_DUMP** |
| IC305 | QS6GT3C33A01 | 4 MB | 0x400000 | **NO_DUMP** |
| IC306 | QS6GU3C32374 | 4 MB | 0x800000 | **NO_DUMP** |
| IC307 | QS6GX3C32008 | 4 MB | 0xC00000 | **Dumped** (CRC: 20ff4629) |

The four ROMs form a contiguous 16 MB waveform address space, declared as `ROM_REGION16_LE` in the MAME driver (16-bit little-endian word access).

## IC307 Binary Layout

IC307 (4,194,304 bytes) has three distinct regions:

```
Offset      Size     Contents
─────────────────────────────────────────
0x000000    6,704    Index table + parameter records
0x001A30    4,187,536  Signed 16-bit PCM waveform data
0x3FFFC0    64       Padding (0xFF)
```

### 1. Main Index Table (0x0000 - 0x0317)

198 entries, 4 bytes each (two 16-bit LE words):

```
struct index_entry {
    uint16_t param_ptr;       // Byte offset to parameter record within ROM
    uint16_t wave_offset;     // Waveform data offset (multiply by 16 for byte address)
};
```

The first entry's `param_ptr` value (0x0318 = 792 = 198 * 4) confirms the table size: it points immediately past itself.

**Addressing scheme:** The `wave_offset` field uses a **x16 byte multiplier**. Multiplying the stored value by 16 yields the byte offset of the waveform PCM data within the ROM. This is equivalent to x8 in 16-bit word addresses, meaning the minimum addressable granularity is **8 samples (16 bytes)**.

Example: Entry 0 has `wave_offset = 0x01A3`. Byte offset = `0x01A3 * 16 = 0x1A30`, which is exactly where the PCM data begins.

### 2. Parameter Records (0x0318 - 0x1A2F)

Variable-length records referenced by the main index. Each record starts with a waveform offset word (same value cached in the main index), followed by zero or more parameter words.

**Record format:**

```
uint16_t wave_start;      // Waveform start offset (same as index wave_offset)
uint16_t params[];        // 0-N parameter words (key zones, tuning, flags)
```

Record sizes range from 2 bytes (waveform offset only, no params) to 850 bytes (424 parameter words). The most common sizes are:

| Record Size | Entries | Interpretation |
|-------------|---------|----------------|
| 2 bytes (0 params) | 1 | Single waveform, no key zones |
| 4 bytes (1 param) | 31 | Single key zone boundary |
| 6 bytes (2 params) | 25 | Two key zone boundaries |
| 8 bytes (3 params) | 44 | Three zones + terminal flag |
| 10 bytes (4 params) | 45 | Four zones (common for split instruments) |
| 12+ bytes | 46 | Multi-zone or per-key tuning data |

**Parameter word encoding:** Each parameter word is structured as `[flags:8][value:8]`:

| High Byte (Flags) | Meaning |
|---|---|
| 0x00 | Normal key zone boundary |
| 0x01 | Per-key pitch/tuning adjustment |
| 0x08 | Per-key pitch/tuning adjustment (alternate range) |
| 0x0A | Transition marker |
| 0x1C | Initial/header parameter |
| 0x40 | Mid-record marker (possible loop point or split) |
| 0x80 | End-of-record marker |
| 0xC0 | Terminal zone boundary (0x80 OR 0x40) |

| Low Byte (Value) | Meaning |
|---|---|
| 0x00 - 0x7F | MIDI key number (for key zone boundaries) |
| 0xF0 - 0xFF | Signed pitch offset (for per-key tuning: 0xFF = -1, 0xFE = -2, etc.) |

**Key zone evidence:** Multiple entries sharing the same waveform offset have systematically transposed key zone parameters:

```
Entry 185 (wave 0xFCA6): params = 0040 0030 0020 0010  (keys 64, 48, 32, 16)
Entry 186 (wave 0xFCA6): params = 0048 0038 0028 0018  (keys 72, 56, 40, 24)
Entry 187 (wave 0xFCA6): params = 0050 0040 0030 0020  (keys 80, 64, 48, 32)
```

Key zone values are listed in **descending order** (highest key first). The values correspond to MIDI note numbers and represent the boundaries where the tone generator changes pitch zones during playback.

### 3. Waveform PCM Data (0x1A30 - 0x3FFFBF)

**Format:** Signed 16-bit PCM, little-endian. Full 16-bit dynamic range (-32767 to +32767).

The byte distribution confirms signed PCM encoding:
- High bytes cluster near 0x00 and 0xFF (values near zero)
- Symmetric distribution around the zero line
- All 256 byte values present (no unused codes)

**186 unique waveforms** are indexed, ranging from 80 to tens of thousands of samples. Most are multi-cycle PCM recordings (not single-cycle wavetable entries), confirming the KN5000 uses **PCM sample-based synthesis** rather than traditional single-cycle wavetable synthesis.

**Notable waveform:** Index 0 (offset 0x01A3 = byte 0x1A30) contains a **256-sample sine wave** with less than 0.5 LSB average error from a mathematically perfect sine. This is likely used as a test tone or fallback waveform.

| Waveform | Offset | Samples | Description |
|----------|--------|---------|-------------|
| 0 | 0x01A3 | 256 | Perfect sine wave (single cycle) |
| 1 | 0x01C3 | 1,408 | Complex multi-cycle sample |
| 2 | 0x0273 | 1,152 | Complex multi-cycle sample |
| ... | ... | ... | Various instrumental timbres |
| 185 | 0xFCA6 | ~16,000+ | Long sample (shared by 6 entries) |
| 186 | 0xFEF6 | ~1,575,000 | Very long sample (shared by 7 entries) |

## Tone Generator Interface

The SubCPU firmware writes waveform addresses to the tone generator via two per-voice registers:

| Register Offset | Struct Offset | Description |
|-----------------|---------------|-------------|
| +0x0040 (group 0, bank 1) | +2 | Waveform pointer low (16-bit) |
| +0x0080 (group 0, bank 2) | +4 | Waveform pointer high (16-bit, bit 15 = latch strobe) |
| +0x00C0 (group 0, bank 3) | +6 | Waveform control |

Together, the low and high pointer registers form a 32-bit address into the 16 MB waveform ROM space. The latch strobe protocol (write with bit 15 SET, then rewrite with bit 15 CLEAR) triggers the tone generator hardware to load the sample data from the addressed ROM location.

## Sample Rate

The native sample rate of the waveform data is not explicitly stored in the ROM. The tone generator hardware plays back samples at a rate determined by the pitch registers (groups 4 and 5), which are computed from the MIDI note number. The waveform data is recorded at a fixed base sample rate and pitch-shifted by the hardware during playback.

Based on the DAC specification (PCM69AU, 18-bit stereo) and typical Matsushita tone generator designs, the output sample rate is likely **48 kHz** or **44.1 kHz**.

## Relationship to Other ROMs

The waveform ROMs are separate from:
- **Rhythm Data ROM** (IC14, 4 MB) -- Contains drum pattern sequencing data, not PCM audio. Uses a completely different format with 0x83 delimiter bytes.
- **Table Data ROM** (IC1/IC3, 2 MB) -- Contains voice parameter tables, pitch lookup tables, and other firmware data. Accessed by the SubCPU to configure tone generator registers.
- **Waveform RAM** (IC308/IC309, 2 x 4Mbit DRAM @ 0x1E0000) -- Writable sample memory, possibly for user waveforms or DSP buffer. Currently stubbed in MAME.

## Open Questions

- What is the exact base sample rate of the waveform data?
- How does the tone generator's address bus map to the 4-chip ROM layout? (Direct linear mapping via chip select, or interleaved?)
- What waveforms are in IC304-IC306? (The KN5000 has hundreds of sound presets; IC307 alone has 186 waveforms.)
- Do the parameter records encode loop start/end points for sustain loops?
- What is the relationship between the 198 index entries and the ~700 sound presets in the KN5000?
- Are waveform ROMs shared across Technics keyboard models (KN6000, KN7000)?

## Related Pages

- [Tone Generator]({{ site.baseurl }}/tone-generator/) -- Register map and voice parameter structure
- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) -- Overall audio architecture
- [Sound Categories]({{ site.baseurl }}/sound-categories/) -- Voice preset organization
