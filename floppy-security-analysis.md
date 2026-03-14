---
layout: page
title: Floppy Security Analysis
permalink: /floppy-security-analysis/
---

# Floppy Code Injection Analysis

Security analysis of the KN5000 v10 Program ROM's floppy handling code, examining whether bugs could be exploited to inject arbitrary code from a crafted floppy disc.

**Target:** Program ROM v10 (`kn5000_v10_program.asm`, 442,668 lines)
**Scope:** All floppy-related code paths — update handlers, LZSS decompression, normal file I/O

---

## Executive Summary

The firmware has **no cryptographic authentication** of floppy disc content — disc type detection uses a 38-byte ASCII string comparison against known signatures. Combined with an LZSS decompressor that trusts a header-specified output size, there is a viable chain for injecting attacker-controlled data into RAM during boot. However, turning this into arbitrary code execution faces architectural barriers: code runs from ROM, not RAM.

---

## Findings

### 1. LZSS Decompressor Trusts Attacker-Controlled Size

**Severity:** High
**Routine:** `LABEL_EF3FAB` (4KB-window LZSS) at `0xEF3FAB`

The LZSS decompressor reads the expected decompressed size from the [SLIDE4K]({{ site.baseurl }}/lzss-compression/) stream header:

```asm
LD E, (XWA + 002h)     ; Byte 2 of header
SLL 8, XDE
LD L, (XWA + 003h)     ; Byte 3 of header
ADD XHL, XDE
...
ADD XIX, XHL            ; XIX = expected decompressed size (24-bit)
```

The main loop terminates only when `XHL >= XIX`:
```asm
CP XHL, XIX             ; Current output count vs expected
JRL NC, LABEL_EF40B8   ; Exit when done
```

The decompressed size is read directly from the compressed data, which originates from floppy. The output pointer (`XDE3`) advances without any bounds checking against the destination buffer size. The dictionary index wraps with `AND BC, 0fffh`, protecting the 4KB dictionary buffer — but NOT the output buffer.

A parallel 8KB-window variant (`LABEL_EF40C5` at `0xEF40C5`) has the same unbounded output behavior.

---

### 2. Type 7 Update Creates Exploitable Boot Chain

**Severity:** High
**Impact:** Persistent control of RAM initialization data and Table Data ROM content

This is the most viable attack vector, chaining two operations across a reboot.

#### Step 1 — Update disc writes to flash

The type 7 handler (`HANDLE_UPDATE_FILE_TYPE_ID_007h` at `0xEF47FA`) calls:
- `LABEL_EF4D95` — decompresses from floppy, writes to Table Data ROM at `0x800000`
- `LABEL_EF4CF8` — decompresses from floppy, writes to Custom Data Flash at `0x3E0000`

The attacker controls the entire compressed payload on the floppy disc.

#### Step 2 — Next boot decompresses to RAM

During the boot sequence (at `0xEF0710`):
```asm
CP (0FFFEEDh), 0ffh       ; Check update-mode flag
JR NZ, LABEL_EF072A       ; Skip if not update mode
LD XIZ, 00050000h
LD XWA, 003e0000h         ; Source: Custom Data Flash
LD XBC, 00050000h         ; Destination: RAM
CALL LABEL_EF41E3         ; Decompress SLIDE4K → RAM
```

The SLIDE4K wrapper validates the "SLIDE" magic string, then calls the LZSS decompressor with `XBC = 0x050000` (RAM). If the attacker's payload at `0x3E0000` specifies a large decompressed size, the decompressor writes attacker-controlled bytes **sequentially from `0x050000` upward in RAM** with no bounds check.

#### Step 3 — Decompressed data used as initialization

Immediately after decompression:
```asm
LDW (0404h), (XIZ + 0100h)   ; Read from decompressed data + 0x100
LD XWA, XIZ
ADD XWA, 00000100h
LD XBC, 00010000h            ; Destination: RAM at 0x010000
LD XDE, 0000f000h            ; Size: 0xF000 bytes (61 KB)
```

The firmware copies 61 KB from offset `0x100` of the decompressed data to RAM at `0x010000`–`0x01F000`. The attacker fully controls this initialization data.

#### Full chain diagram

```
Floppy Disc (Type 7: "Technics KN5000 Program  DATA FILE PCK")
    │
    ├──> LABEL_EF4D95: Decompress → Table Data ROM (0x800000)
    │    [Attacker controls entire Table Data ROM content]
    │
    └──> LABEL_EF4CF8: Decompress → Custom Data Flash (0x3E0000)
         [Attacker controls SLIDE4K payload staged for next boot]
             │
             v (on next boot, version byte 0xFFFEED == 0xFF)
         LABEL_EF41E3: Decompress 0x3E0000 → RAM 0x050000
             │   [LZSS output size = attacker-controlled header value]
             │   [No bounds check on output buffer]
             v
         Copy 61KB from (0x050000 + 0x100) → RAM 0x010000
             [Attacker controls firmware initialization data]
```

---

### 3. No Disc Authentication

**Severity:** High
**Routine:** `Detect_Disk_Type` at `0xEF42FE`

Disc type detection is a plain 38-byte ASCII string comparison. The 8 signatures are known plaintext strings stored in ROM (see [System Update Discs — Signature Table]({{ site.baseurl }}/system-update-discs/#signature-table)):

| Type | Signature |
|------|-----------|
| 1 | `Technics KN5000 Program  DATA FILE 1/2` |
| 2 | `Technics KN5000 Program  DATA FILE 2/2` |
| 3 | `Technics KN5000 Table    DATA FILE 1/2` |
| 4 | `Technics KN5000 Table    DATA FILE 2/2` |
| 5 | `Technics KN5000 CMPCUSTOMDATA FILE    ` |
| 6 | `Technics KN5000 HD-AEPRG DATA FILE    ` |
| 7 | `Technics KN5000 Program  DATA FILE PCK` |
| 8 | `Technics KN5000 Table    DATA FILE PCK` |

There is no HMAC, CRC, RSA signature, or any other integrity check. Anyone with the signature string can create a disc that the firmware accepts as a valid update.

The handler dispatch does validate the type range (1–8) before jumping:
```asm
DEC 1, WA
CP WA, 0
JRL LT, SHOW_ILLEGAL_DISK_MESSAGE
CP WA, 7
JRL GT, SHOW_ILLEGAL_DISK_MESSAGE
```

---

### 4. Type 7 Decompressor Reads Size from Floppy Stream

**Routine:** `LABEL_EF4D95` at `0xEF4D95`

The inline LZSS decompressor for type 7/8 updates reads the decompressed size directly from the floppy data stream (3 bytes → 24-bit value stored at `0x063E`). The decompression loop continues until the byte counter reaches this value. Each decompressed byte is accumulated in a 4-byte buffer, then written to flash via `LABEL_EF3D7B`.

The flash destination starts at `TABLE_DATA_ROM__BASE_ADDR` (`0x800000`) and advances by 4 each write. If the attacker sets the decompressed size larger than 2 MB (the Table Data ROM size), writes continue past `0x9FFFFF` — but fail silently due to the chip-specific AMD flash unlock sequence (see Finding 6).

---

### 5. Compressed Stream Exhaustion → Infinite Loop

**Severity:** Low (denial of service only)

The byte reader `LABEL_EF4C07` refills the sector buffer from floppy in 4-track chunks. If the attacker inflates the expected decompressed size but provides a short compressed stream, the decompressor exhausts the floppy data. The FDC read routine (`LABEL_EF42CC`) then retries indefinitely, creating an **infinite loop** requiring a power cycle.

---

## Mitigating Factors

### Hardcoded sector counts and flash destinations

Sector counts and flash write addresses are hardcoded in the firmware, not read from disc data:

| Type | Starting Sector | Flash Destination |
|------|-----------------|-------------------|
| 1 | 0x24 (36) | `0x800000` (Table Data ROM) |
| 3 | 0x24 (36) | `0x800000` (Table Data ROM) |
| 5 | 0x24 (36) | `0x300000` (Custom Data Flash) |
| 6 | 0x24 (36) | `0x280000` (HDAE5000 ROM) |
| 7 | 4-track chunks | `0x800000` + `0x3E0000` |
| 8 | 4-track chunks | `0x800000` |

The attacker cannot redirect writes to arbitrary flash regions. The disc type determines which hardcoded handler runs.

### Flash chip-select isolation

Flash write routines use chip-specific AMD/Atmel unlock sequences. `LABEL_EF3D7B` (Table Data ROM writer) sends unlock commands to `0x815554` and `0x80AAA8` — addresses decoded by the Table Data ROM flash chip only. Writes to addresses outside that chip's range (`0x800000`–`0x9FFFFF`) fail silently. The Program ROM flash at `0xE00000` has its own unlock addresses and cannot be reprogrammed via the Table Data ROM writer.

### Code runs from ROM

The TLCS-900/H2 executes code from Program ROM (`0xE00000`–`0xFFFFFF`). Interrupt vectors are also in ROM. A RAM buffer overflow from `0x050000` upward corrupts RAM data but does not directly overwrite executable code.

### Stack location

The stack is in internal RAM (`0x000000`–`0x0003FF`), which is below the overflow origin at `0x050000`. Sequential upward overflow cannot reach the stack.

### LZSS dictionary wraps safely

The dictionary index in both LZSS variants uses `AND BC, 0fffh` (4KB) or `AND BC, 01fffh` (8KB), preventing dictionary buffer overflow.

### Normal file I/O uses ROM sources

The SLIDE4K wrapper `LABEL_EF41E3` has only 3 callers:

| Call Site | Source | Destination | Floppy-Reachable? |
|-----------|--------|-------------|-------------------|
| Boot (`0xEF0710`) | Custom Data Flash `0x3E0000` | RAM `0x050000` | **Yes** (via type 7 update) |
| `0xF477D3` | Table Data ROM `0x988018`+ | RAM `0x069800` | Indirectly (if Table Data ROM corrupted) |
| `0xF871A0` | Table Data ROM `0x9C4000`+ | RAM `0x069800` | Indirectly (if Table Data ROM corrupted) |

No callers decompress directly from floppy to RAM. The boot-time path is the only one reachable from floppy data, via Custom Data Flash as a staging area.

---

## Open Questions

These areas require further investigation to determine whether the data-control primitive can be elevated to code execution:

1. **Function pointers in RAM at `0x010000`–`0x01F000`**: If any of the 61 KB of boot initialization data contains callback addresses, jump table entries, or object vtable pointers, these could be overwritten to redirect control flow.

2. **Secondary LZSS payloads via Table Data ROM**: Since the type 7 update gives the attacker full control of Table Data ROM content, and two routines decompress from Table Data ROM to RAM at `0x069800`, the attacker could embed secondary malicious SLIDE4K payloads that overflow during normal firmware operation.

3. **The `EXEC` tag in the SSF presentation system**: If the XML parser at `AcPresentationControlProc` (`0xF8450B`) implements the `EXEC` tag by dispatching to data-specified routines, and Table Data ROM content influences those routines, this could provide a code execution path. See [Feature Demo & Presentation System]({{ site.baseurl }}/feature-demo/).

---

## Key Code References

| Routine | Address | Purpose |
|---------|---------|---------|
| `LABEL_EF3FAB` | `0xEF3FAB` | 4KB-window LZSS decompressor |
| `LABEL_EF40C5` | `0xEF40C5` | 8KB-window LZSS decompressor |
| `LABEL_EF41E3` | `0xEF41E3` | SLIDE4K/8K wrapper (magic check, dispatch) |
| `LABEL_EF3D7B` | `0xEF3D7B` | Flash write — Table Data ROM (AMD protocol) |
| `LABEL_EF3815` | `0xEF3815` | Flash write — Custom Data / HDAE5000 |
| `LABEL_EF42CC` | `0xEF42CC` | FDC sector read loop |
| `Detect_Disk_Type` | `0xEF42FE` | 38-byte signature matching |
| `Erase_and_Burn____when_disk_is_valid` | `0xEF4745` | Update handler dispatch (validates type 1–8) |
| `LABEL_EF441B` | `0xEF441B` | Uncompressed disc → flash writer |
| `LABEL_EF454D` | `0xEF454D` | Extension/custom data → flash writer |
| `LABEL_EF4D95` | `0xEF4D95` | Type 7/8 inline LZSS → Table Data ROM |
| `LABEL_EF4CF8` | `0xEF4CF8` | Type 7 inline LZSS → Custom Data Flash |
| `LABEL_EF4C07` | `0xEF4C07` | Byte reader with floppy refill |
| `LABEL_EF4C7A` | `0xEF4C7A` | Decompressed byte → flash accumulator |
| `FLASH_MEM_UPDATE` | `0xEF4F6F` | Top-level update entry point |
| `String_Compare` | `0xFF0CDA` | Byte-by-byte string comparison |

---

## Related Pages

- [System Update Discs]({{ site.baseurl }}/system-update-discs/) — Disc format, signatures, update flow, no-code-execution finding
- [LZSS Compression]({{ site.baseurl }}/lzss-compression/) — SLIDE4K format specification
- [Flash Programming]({{ site.baseurl }}/flash-programming/) — Flash erase/program routines
- [FDC Subsystem]({{ site.baseurl }}/fdc-subsystem/) — Floppy disk controller handlers
- [Feature Demo & Presentation System]({{ site.baseurl }}/feature-demo/) — SSF XML system with `EXEC` tag
- [Storage Subsystem]({{ site.baseurl }}/storage-subsystem/) — Storage architecture overview
- [Boot Sequence]({{ site.baseurl }}/boot-sequence/) — Power-on initialization including SLIDE4K decompression

---

*Last updated: February 2026*
