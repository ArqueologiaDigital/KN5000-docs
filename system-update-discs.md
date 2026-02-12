---
layout: page
title: System Update Discs
permalink: /system-update-discs/
---

# System Update Disc Format

The KN5000 uses 3.5" HD floppy discs (1.44 MB) for firmware updates. This page documents the disc format based on analysis of original Technics update discs archived at [archive.org](https://archive.org/details/technics-kn5000-system-update-disks).

## Disc Layout

Update discs use a **FAT12 filesystem** with a Technics-specific boot sector. The firmware reads specific files by their on-disc location (reading raw sectors at known offsets) rather than parsing the FAT directory by filename.

### Boot Sector (BPB)

The boot sector uses standard FAT12 BIOS Parameter Block fields with OEM ID "Technics":

| Offset | Size | Field | Value |
|--------|------|-------|-------|
| 0x00 | 3 | Jump + NOP | `EB 1C 90` |
| 0x03 | 8 | OEM ID | `Technics` |
| 0x0B | 2 | Bytes/sector | 512 |
| 0x0D | 1 | Sectors/cluster | 1 |
| 0x0E | 2 | Reserved sectors | 1 |
| 0x10 | 1 | Number of FATs | 2 |
| 0x11 | 2 | Root dir entries | 224 |
| 0x13 | 2 | Total sectors | 2880 |
| 0x15 | 1 | Media descriptor | 0xF0 (3.5" HD) |
| 0x16 | 2 | Sectors/FAT | 9 |
| 0x18 | 2 | Sectors/track | 18 |
| 0x1A | 2 | Number of heads | 2 |
| 0x1C | 4 | Hidden sectors | 0 |
| 0x1E | 2 | Boot code | `EB FE` (infinite loop) |

Bytes 32–511 are zero except byte 37 which is `0x01` on v10 discs (extended BPB "current head" field, non-functional).

### Sector Map

| Sectors | Offset | Content |
|---------|--------|---------|
| 0 | 0x0000 | Boot sector (BPB) |
| 1–9 | 0x0200 | FAT 1 |
| 10–18 | 0x1400 | FAT 2 (copy of FAT 1) |
| 19–32 | 0x2600 | Root directory (224 entries × 32 bytes) |
| 33+ | 0x4200 | Data area (cluster 2 starts here) |

### Data Area Layout

Files occupy contiguous clusters starting at cluster 2:

| Cluster | Sector | Offset | File |
|---------|--------|--------|------|
| 2 | 33 | 0x4200 | Signature file (TECHNICS.PRP or TECHNICS.AE) |
| 3 | 34 | 0x4400 | DUMMY.1 |
| 4 | 35 | 0x4600 | DUMMY.2 |
| 5+ | 36+ | 0x4800 | Data file (HKMSPRG.SLD or HKEXTROM.XAP) |

Unused sectors in the data area are filled with `0xE5` (standard DOS format fill byte).

---

## File Contents

### Program ROM Update Disc (Type 7)

Used for compressed program ROM updates (versions 5–10).

| File | Size | Content |
|------|------|---------|
| `TECHNICS.PRP` | 56 bytes | Signature + author credit |
| `DUMMY.1` | 64 bytes | Table data signature placeholder |
| `DUMMY.2` | 64 bytes | Table data signature placeholder |
| `HKMSPRG.SLD` | ~1 MB | SLIDE4K compressed program ROM |

**TECHNICS.PRP** (56 bytes):
```
Technics KN5000 Program  DATA FILE PCK  by T.Nishino\r\n\r\n
```

The first 38 bytes are the disc type signature matched by the firmware (see [Disc Type Detection](#disc-type-detection) below).

**DUMMY.1** and **DUMMY.2** (64 bytes each):
```
Technics KN5000 Table    DATA FILE 1/2 by Nishino Teruhiko !!!\r\n
```

These are non-functional placeholders. Their content matches the Table Data disc type 3 signature, suggesting they were leftover from the uncompressed 2-disc format (types 1–4) where program and table data were split across multiple floppies.

**HKMSPRG.SLD** — SLIDE4K compressed program ROM:

| Offset | Size | Field |
|--------|------|-------|
| 0x00 | 8 | Magic: `SLIDE4K\0` |
| 0x08 | 3 | Decompressed size (24-bit big-endian) |
| 0x0B | var | LZSS compressed data stream |

For the 2 MB program ROM, the size bytes are `20 00 00` (0x200000 = 2,097,152). See [LZSS Compression](lzss-compression.md) for the SLIDE4K format specification.

Observed compressed sizes across firmware versions:

| Version | HKMSPRG.SLD Size | Compression Ratio |
|---------|------------------|-------------------|
| v5 | 1,056,514 bytes | 50.4% |
| v7 | 1,057,941 bytes | 50.4% |
| v10 | 1,058,748 bytes | 50.5% |

### HD-AE5000 Extension Update Disc (Type 6)

Used for HDAE5000 expansion board firmware.

| File | Size | Content |
|------|------|---------|
| `TECHNICS.AE` | 65 bytes | Signature + author credit |
| `DUMMY.1` | 64 bytes | Table data signature placeholder |
| `DUMMY.2` | 64 bytes | Table data signature placeholder |
| `HKEXTROM.XAP` | 524,288 bytes | Raw (uncompressed) extension ROM |

**TECHNICS.AE** (65 bytes):
```
Technics KN5000 HD-AEPRG DATA FILE      by Nishino Teruhiko !!!\r\n\n
```

**HKEXTROM.XAP** — Raw 512 KB extension ROM binary, not compressed.

---

## Disc Type Detection

The firmware identifies update discs by comparing a **38-byte signature** against a table stored in the Table Data ROM at address `0x9FA000`.

### Detection Algorithm

The `Detect_Disk_Type` routine (in both the Table Data Boot ROM at `0x9FBFC4` and Program ROM at `0xEF42FE`):

1. Reads sectors from the floppy into a 512-byte buffer
2. Compares buffer content against each of 8 known signatures (38 bytes each)
3. Returns type code 1–8 on match, or `0xFF` if unknown

The signature is found at the start of TECHNICS.PRP (sector 33, offset 0x4200), which is the first file in the data area.

### Signature Table

All 8 signature strings are stored consecutively in the Table Data ROM:

| Type | ROM Address | Signature (38 bytes) | Purpose |
|------|-------------|----------------------|---------|
| 1 | 0x9FA000 | `Technics KN5000 Program  DATA FILE 1/2` | Program ROM disk 1 of 2 (uncompressed) |
| 2 | 0x9FA028 | `Technics KN5000 Program  DATA FILE 2/2` | Program ROM disk 2 of 2 (uncompressed) |
| 7 | 0x9FA050 | `Technics KN5000 Program  DATA FILE PCK` | Program ROM (SLIDE4K compressed) |
| 3 | 0x9FA078 | `Technics KN5000 Table    DATA FILE 1/2` | Table Data ROM disk 1 of 2 |
| 4 | 0x9FA0A0 | `Technics KN5000 Table    DATA FILE 2/2` | Table Data ROM disk 2 of 2 |
| 8 | 0x9FA0C8 | `Technics KN5000 Table    DATA FILE PCK` | Table Data ROM (SLIDE4K compressed) |
| 5 | 0x9FA0F0 | `Technics KN5000 CMPCUSTOMDATA FILE    ` | Compressed custom data |
| 6 | 0x9FA118 | `Technics KN5000 HD-AEPRG DATA FILE    ` | HDAE5000 extension firmware |

Types 7 and 8 ("PCK" = packed/compressed) replaced the older 2-disc uncompressed format (types 1–4). All archived update discs from v5 onward use type 7.

---

## Update Flow

The firmware update is triggered at boot when the firmware version byte at `0xFFFFE8` equals `0xFF` (a magic value written before reset to signal update mode).

### Sequence

1. **Detect floppy** — Check port PD bit 6 for disc change signal
2. **Read signature** — Read sectors from the floppy, match against signature table
3. **Display status** — Show "Flash Memory Update" on the LCD
4. **Erase flash** — Display "Now Erasing!!" and erase the target flash chip
5. **Program flash** — Read data sectors from floppy and program flash memory
6. **Verify** — Compare programmed data against source
7. **Complete** — Display "Completed!" and "Turn On AGAIN!!"

### Update Handlers by Type

| Type | Handler Address | Destination | Method |
|------|-----------------|-------------|--------|
| 7 (Program PCK) | 0xEF47FA | Custom Data Flash 0x3E0000 | LZSS decompress from floppy |
| 8 (Table PCK) | — | Table Data ROM 0x800000 | LZSS decompress from floppy |
| 6 (HDAE5000) | — | Extension ROM 0x280000 | Direct copy from floppy |
| 1/2 (Program) | — | Table Data ROM 0x800000 | Direct copy (2-disc set) |
| 3/4 (Table) | — | Table Data ROM 0x800000 | Direct copy (2-disc set) |

For type 7, the compressed program ROM is written to Custom Data Flash at `0x3E0000`. On next boot, the decompressor reads from this staging area and programs the actual Program Flash at `0xE00000`. See [Flash Programming](flash-programming.md) for details.

---

## Available Update Discs

The following original update disc images are archived at the [Internet Archive](https://archive.org/details/technics-kn5000-system-update-disks):

| Filename | Type | Version | Format |
|----------|------|---------|--------|
| `kn5000_v5_disk.img` | 7 | v5 | FAT12 + SLIDE4K |
| `kn5000_v6_disk.img` | 7 | v6 | FAT12 + SLIDE4K |
| `kn5000_v7_disk.img` | 7 | v7 | FAT12 + SLIDE4K |
| `kn5000_v8_disk.img` | 7 | v8 | FAT12 + SLIDE4K |
| `kn5000_v9_disk.img` | 7 | v9 | FAT12 + SLIDE4K |
| `kn5000_v10_disk.img` | 7 | v10 | FAT12 + SLIDE4K |
| `hd-ae5000_disk.img` | — | — | Contains AE5-115.EXE (DOS installer) |

Note: The `hd-ae5000_disk.img` contains a DOS executable (`AE5-115.EXE`) that creates the actual update disc when run on a PC, rather than being a ready-to-use update disc itself. The extracted HD-AE5000 update files (TECHNICS.AE, DUMMY.1, DUMMY.2, HKEXTROM.XAP) are available separately in the archive.

### Boot Sector Variations

All program update discs share identical BPB parameters. The OEM ID field varies between versions:

| Version | OEM ID |
|---------|--------|
| v5 | `(O%W{IHC` (garbage — created by non-standard tool) |
| v7, v8, v9, v10 | `Technics` |

This difference is cosmetic and does not affect functionality.

---

## Creating Update Discs

The `anotherworld` custom ROM project includes a tool for creating update discs:

```bash
# Create compressed program ROM update disc
python tools/make_update_disc.py out/custom_program.rom out/update_disc.img --type 7

# Create HDAE5000 extension update disc
python tools/make_update_disc.py out/extension.rom out/update_disc.img --type 6
```

The tool creates byte-identical disc images (boot sector, FAT structure, file layout, fill bytes) matching the original Technics format.

---

## References

- [LZSS Compression](lzss-compression.md) — SLIDE4K format specification and decompression routines
- [Flash Programming](flash-programming.md) — Flash erase/program routines and update handlers
- [FDC Subsystem](fdc-subsystem.md) — Floppy disk controller hardware and driver routines
- [Storage Subsystem](storage-subsystem.md) — Overview of KN5000 storage architecture
- [Internet Archive: Technics KN5000 System Update Disks](https://archive.org/details/technics-kn5000-system-update-disks) — Original disc images

---

*Last updated: February 2026*
