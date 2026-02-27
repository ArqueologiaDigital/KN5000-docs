---
layout: page
title: HDAE5000 Filesystem
permalink: /hdae5000-filesystem/
---

# HD-AE5000 Custom Filesystem

The HD-AE5000 extension board uses a **completely custom, proprietary filesystem** -- not FAT, ext2, or any industry standard. Despite one error string in the ROM mentioning "FAT read error," no FAT boot sector signatures (0x55AA, 0xEB), FAT12/FAT16/FAT32 identifier strings, or standard FAT data structures exist anywhere in the firmware. The firmware was authored by M. Kitajima (Technics/Panasonic), dated Juli-Oktober 1996.

## Hardware

The filesystem operates on the following hardware:

| Component | Details |
|-----------|---------|
| Storage Medium | 2.5" IDE Hard Disk (1.08GB capacity) |
| PC Interface | NEC uPD71055 (i8255-compatible) PPI for parallel port communication |
| Static RAM | 512KB (2x 256KB) at 0x200000-0x27FFFF |
| ROM | 512KB at 0x280000-0x2FFFFF |
| ATA Registers | 0x130010-0x130020 |
| Addressing Mode | CHS (Cylinder/Head/Sector) -- not LBA |

### ATA Commands Used

| Command | Code | Description |
|---------|------|-------------|
| READ SECTORS | 0x20 | Read one or more sectors from disk |
| WRITE SECTORS | 0x30 | Write one or more sectors to disk |
| STANDBY | 0x94 | Spin down the drive motor |
| IDENTIFY DEVICE | 0xEC | Query drive geometry and capabilities |

## Three-Level Block Hierarchy (FSB/FGB/FEB)

The filesystem organizes data using three custom block types arranged in a hierarchy:

```
FSB (File System Block)
 +-- Master metadata for the entire filesystem
 |
 +-- FGB (File Group Block)
 |    +-- Groups files together (directory-like container)
 |    |
 |    +-- FEB (File Entry Block)
 |    |    +-- Individual file metadata
 |    +-- FEB
 |    +-- ...
 |
 +-- FGB
 |    +-- FEB
 |    +-- ...
 +-- ...
```

### FSB (File System Block)

The FSB is the master metadata structure for the entire filesystem. There is one FSB per formatted disk. It is serialized across multiple on-disk sectors:

| Operation | Address | Size | Role |
|-----------|---------|------|------|
| FS_Read_FSB | 0x287F55 | 832 bytes | Display UI initialization (reads from RAM, not disk) |
| FS_Write_FSB | 0x288295 | 5,072 bytes | Serializes in-RAM state to disk sectors |
| Cmd03_ReadFSB | 0x2959F6 | 838 bytes | Reads FSB sectors from disk (PPORT interface) |
| Cmd06_WriteFSB | 0x296294 | 150 bytes | Writes FSB sectors to disk (PPORT interface) |

The FSB can be transferred to/from a PC via the parallel port interface (PPORT commands 03-06), enabling backup and management through the HD-TechManager5000 Windows software.

#### FSB On-Disk Sector Layout

`FS_Write_FSB` serializes the FSB across multiple sectors:

**Sector 0** (32 bytes, staging buffer at 0x22A058):
- Header fields from ROM template at 0x2E2EAC
- VarInt-encoded directory entry count
- Display layout metadata

**Sector 1** (16 directory entries, staging buffer at 0x22B020):
- 16 entries at stride **37 bytes (0x25)** each
- Total: 592 bytes per sector

**Sector 2** (16 bytes, staging buffer at 0x22A078):
- VarInt-encoded current selection/position index
- Display cell reference data

**Sectors 3-4**: Additional navigation and index data.

The FSB supports **5 pages of 24 entries** = 120 total directory slots, with the page selector at 0x23A090 stepping in increments of 24 (values 0, 24, 48, 72, 96).

#### 21-Byte In-RAM Directory Entry (at 0x22A2CA)

FS_Read_FSB initializes 24 entries from a ROM template at 0x2E2E60:

```
Offset  Size  Contents
------  ----  --------
0x00    4     Header (flags/state, first 4 bytes not copied to display tile)
0x04    16    Display tile block (copied to screen for rendering)
0x14    1     Terminator (0x09 = tab character)
```

ROM template contents: `20 20 20 3A 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 09` = `"   :                "` + 0x09 terminator. The colon at byte 3 separates an entry number field from the name field.

#### 37-Byte On-Disk Directory Entry (at 0x22B020)

FS_Write_FSB serializes entries using a 37-byte format from ROM template at 0x2E2EC0:

```
Offset  Size  Contents
------  ----  --------
0x00    35    Name/descriptor string (from template: ":" + 33 spaces + 0x09)
0x20    1     Flag byte 1 (0x2A = '*' if flagged, else 0x20 = space)
0x21    2     Sector allocation index (16-bit)
0x23    1     Flag byte 2 (0x2A = '*' if flagged, else 0x20 = space)
0x24    1     Padding / display cell reference
```

ROM template contents: `3A` + 33x`20` + `09 00 25` = `":"` + spaces + terminator.

### FGB (File Group Block)

FGBs function as directory-like containers, grouping related files together within a partition. Their exact on-disk layout is embedded within the sector data read by `Cmd03_ReadFSB`, which uses 9 region descriptors to address different parts of the filesystem. Each region descriptor is a 32-bit sector address.

### FEB (File Entry Block)

FEBs contain individual file metadata for each stored file on the disk. They are accessed through `FS_Entry_Lookup` (0x28A2F0) using the 9-byte directory entry format described below.

## Partition System

The filesystem supports a structured partition layout:

- Up to **16 partitions** per disk
- Up to **40 directory entries** per partition (9 bytes each, insertion-sorted by name)
- Partition status byte: `0x02` = active partition

### 9-Byte Directory Entry (at 0x230884)

Each partition maintains up to 40 directory entries at RAM 0x230884 (360 bytes total). Entries are insertion-sorted by name. Each 9-byte entry contains handler indices used by `FS_Entry_Lookup` to dispatch through the function pointer table at ROM 0x2E1E14:

```
Offset  Size  Contents
------  ----  --------
0x00    1     Handler index 0 (file type / operation code)
0x01    1     Handler index 1 (secondary type / flags)
0x02    1     Handler index 2 (display cell reference)
0x03    1     Handler index 3 (slot index, used with CHS params at 0x23A092-0x23A094)
0x04    2     Source address / sector reference (16-bit)
0x06    1     Status / protection flags
0x07    2     Sector count or size (16-bit)
```

Each handler index byte is used as a `*4` offset into the ROM function pointer table at 0x2E1E14, selecting the appropriate display/operation callback.

## Sector Allocation

Sector allocation uses a custom variable-length integer encoding scheme:

### VarInt Encoding

Sizes and offsets are encoded using **7-bit variable-length integers (VarInt)** where bit 7 is a continuation flag. This is similar to the encoding used in Protocol Buffers and MIDI:

- If bit 7 is clear (0), this is the last byte of the value
- If bit 7 is set (1), more bytes follow
- Each byte contributes 7 bits of data

| Routine | Address |
|---------|---------|
| VarInt_Encode | 0x28F36B |
| VarInt_Decode | 0x28F3BD |

### Sector Table

- Stored in RAM at 0x22B430 (20KB = 0x5000 bytes buffer)
- Free space calculated by scanning 4-byte groups, clearing bit 7, shift-left by 7
- Maximum sector number: 20,457 (0x4FE9)
- Per-sector metadata at offsets from table base:
  - `table[sector + 22]`: sector type byte (0xFF = free)
  - `table[sector + 23]`: file type code (0x2F = invalid/reserved)

## RAM Data Structures

The filesystem maintains several key data structures in RAM:

| Address | Size | Purpose |
|---------|------|---------|
| 0x229D99-0x229DAE | ~22 bytes | CHS parameters from ATA IDENTIFY (cylinders, heads, sectors, state flags) |
| 0x22A058 | 32 bytes | FSB Sector 0 output buffer (header + entry count) |
| 0x22A078 | 16 bytes | FSB Sector 2 output buffer (position/selection) |
| 0x22AA4C | 4 bytes | Current CHS context pointer |
| 0x22AA4E-0x22AA56 | ~9 bytes | Spinbox state bytes (per CHS field) |
| 0x22AA5C | 2 bytes | Current input state (0-5 for CHS digits) |
| 0x22AA5E | 2 bytes | Current cylinder value |
| 0x22AA60 | 2 bytes | Current head value |
| 0x22AA9C | varies | Filesystem buffer base -- up to 20 entries |
| 0x22A2CA | 504 bytes | FSB main display buffer (24 x 21-byte entries) |
| 0x22B020 | varies | FSB write staging area (16 x 37-byte entries) |
| 0x22B272 | 2 bytes | Sector allocation index / column counter |
| 0x22B430 | 20KB (0x5000) | Sector data/allocation table |
| 0x230430 | 1 byte | Current file type code |
| 0x230438 | 4 bytes | Start sector (for save/restore) |
| 0x230440 | 4 bytes | Current file descriptor pointer / cumulative free space |
| 0x230444 | 4 bytes | Total allocation |
| 0x230450 | 4 bytes | Remaining free space |
| 0x230458-0x2304D7 | 128 bytes | Filename string buffer (null-terminated) |
| 0x2304D8-0x2304EF | ~24 bytes | File save state |
| 0x230636-0x2306B5 | 128 bytes | Second filename buffer (backup copy) |
| 0x230884 | 360 bytes | Directory entry table (40 x 9-byte entries) |
| 0x230E72 | 2 bytes | Directory entry count |
| 0x23A090 | 2 bytes | FSB page selector (values: 0, 24, 48, 72, 96) |
| 0x23A092 | 2 bytes | Current cylinder |
| 0x23A094 | 2 bytes | Current head |
| 0x23A096 | 2 bytes | Display row base |
| 0x23A098 | 2 bytes | Display row cursor |
| 0x23A19E | 4 bytes | Secondary workspace pointer |
| 0x23A1A2 | 4 bytes | Dispatch/vtable pointer |

## File Types

The HDAE5000 handles a wide range of KN5000 file types:

| Extension | Description |
|-----------|-------------|
| .LSW | Live Sound Workspace |
| .SDA | Sound Data Archive |
| .PMT | Performance Memory Table |
| .SQF | Sequence File |
| .SEQ | Sequence |
| .CMP | Composition |
| .TM | TechManager(?) |
| .MSP | Music Setup(?) |
| .RCM | Registration/Custom Memory(?) |
| .MD | Music Data |
| .TLX | Text Lyrics eXtended |
| .TTX | Text data |
| .MID | Standard MIDI file |
| .SQT | Sequence Template |
| .XAP | Extension Application (firmware) |

File types are identified by numeric codes internally: values 0-4 map to internal IDs (0xF9, 0x02, 0xFC, 0x00, 0xFB).

## Key Filesystem Routines

All routines reside in the HDAE5000 ROM (base address 0x280000):

| Function | Address | Size | Status |
|----------|---------|------|--------|
| FS_Init | 0x2870D6 | 3,711 bytes | Disassembled -- CHS entry UI with 10 event handlers |
| FS_Read_FSB | 0x287F55 | 832 bytes | Disassembled -- display UI init (24 entries from template) |
| FS_Write_FSB | 0x288295 | 5,072 bytes | Disassembled -- multi-sector serialization |
| FS_Buffer_Setup | 0x289665 | 548 bytes | Disassembled |
| FS_Scan_Directory | 0x289889 | 2,663 bytes | Disassembled -- iterates 20 buffer entries |
| FS_Entry_Lookup | 0x28A2F0 | 739 bytes | Disassembled -- 9-block handler dispatch |
| File_Operation | 0x28D6D1 | 938 bytes | Disassembled |
| File_Save | 0x28DA7B | 381 bytes | Disassembled |
| File_Load | 0x28DBF8 | 564 bytes | Disassembled |
| File_Delete | 0x28DE2C | 579 bytes | Disassembled |
| File_Rename | 0x28E06F | 280 bytes | Disassembled |
| File_Format | 0x28E187 | 772 bytes | Disassembled |
| Calc_Disk_Space | 0x28E48B | 178 bytes | Disassembled |
| Directory_Handler | 0x28F197 | 614 bytes | Disassembled |
| VarInt_Encode | 0x28F36B | -- | Disassembled |
| VarInt_Decode | 0x28F3BD | -- | Disassembled |
| File_Read | 0x29AE24 | 123 bytes | Disassembled |
| Cmd03_ReadFSB | 0x2959F6 | 838 bytes | Disassembled -- PPORT disk read |
| Cmd04_SendFSB | 0x295D3C | 798 bytes | Disassembled -- PPORT send to PC |
| Cmd05_RcvFSB | 0x29605A | 570 bytes | Disassembled -- PPORT receive from PC |
| Cmd06_WriteFSB | 0x296294 | 150 bytes | Disassembled -- PPORT disk write |

### Routine Descriptions

**FS_Init** (0x2870D6, 3,711 bytes) -- CHS address entry UI with 10 event handler sub-routines. Dispatches on parameter DE (indices 0-6 via jump table at 0x2E2D46) to configure cylinder/head spinbox widgets. Does NOT read from disk directly.

**FS_Read_FSB** (0x287F55, 832 bytes) -- Display UI initialization. Copies the 21-byte ROM template to 24 entry slots in RAM at 0x22A2CA, formats entry numbers, and copies 16-byte display tile blocks. Does NOT read from disk -- the actual sector reads are performed by Cmd03_ReadFSB.

**FS_Write_FSB** (0x288295, 5,072 bytes) -- Serializes the in-RAM filesystem state to multiple disk sectors. Writes Sector 0 (header), Sector 1 (16 directory entries at 37 bytes each), Sector 2 (position), and Sectors 3-4 (navigation). Uses ROM handler tables at 0x2E2E7C-0x2E2EA4 (6 tables of function pointers).

**FS_Scan_Directory** (0x289889, 2,663 bytes) -- Scans directory entries within a partition, iterating over FGB/FEB structures at the filesystem buffer base (0x22AA9C, up to 20 entries).

**FS_Entry_Lookup** (0x28A2F0, 739 bytes) -- Looks up a specific file entry by dispatching 9 handler index bytes (at 0x22ABE8) through the function pointer table at ROM 0x2E1E14.

**File_Format** (0x28E187, 772 bytes) -- Formats the hard disk, creating an empty filesystem. Validates sectors (max 20,457 = 0x4FE9), marks free sectors with 0xFF in the allocation table, and stores file type codes.

**Calc_Disk_Space** (0x28E48B, 178 bytes) -- Calculates free disk space by scanning the sector allocation table at 0x22B430.

## PC Parallel Port Interface

The HDAE5000 includes a PC parallel port interface (via NEC uPD71055 PPI) that provides filesystem-level operations:

| PPORT Command | Routine | Operation |
|---------------|---------|-----------|
| 03 | Cmd03_ReadFSB (0x2959F6) | Read FSB sectors from hard disk into RAM |
| 04 | Cmd04_SendFSB (0x295D3C) | Send FSB data from RAM to PC |
| 05 | Cmd05_RcvFSB (0x29605A) | Receive FSB data from PC into RAM |
| 06 | Cmd06_WriteFSB (0x296294) | Write FSB data from RAM to hard disk |

### PPORT FSB Transfer Packet Format

The PPORT commands use a structured packet at RAM 0x239168:

```
Offset  Size  Contents
------  ----  --------
0x00    1     Sector flags byte 1 (bitmask for regions 0-5, 7)
0x01    1     Head flags byte 2 (bitmask for region 8)
0x02-0x2B  42  Header/padding (44 bytes total including flags)
0x2C    36    9 region descriptors (32-bit sector address each)
```

The **9 region descriptors** are mapped to sector flag bits:

| Flag Byte | Bit | Region | RAM Address |
|-----------|-----|--------|-------------|
| Byte 1 | 0 | Region 0 | 0x23910C |
| Byte 1 | 1 | Region 1 | 0x23911C |
| Byte 1 | 2 | Region 2 | 0x239124 |
| Byte 1 | 3 | Region 3 | 0x23912C |
| Byte 1 | 4 | Region 4 | 0x239134 |
| Byte 1 | 5 | Region 5 | 0x23913C |
| Byte 1 | 7 | Region 6 | 0x239148 |
| Byte 2 | 0 | Region 7 | 0x239150 |

Note: Byte 1, bit 6 is explicitly unused (skipped in the dispatch logic).

Beyond FSB transfer, the parallel port can also send/receive file data and support custom ROM data transfer. This interface enables the Technics SX-KN5000 to exchange files with a PC via the HD-TechManager5000 Windows software.

## Analysis Status

All key filesystem routines have been **fully disassembled** to native TLCS-900 assembly. The on-disk FSB format has been largely reconstructed:

**Well understood:**
- Multi-sector FSB layout (Sectors 0-4) and their RAM staging buffers
- 21-byte in-RAM directory entry format (ROM template at 0x2E2E60)
- 37-byte on-disk directory entry format (ROM template at 0x2E2EC0)
- VarInt encoding for sector addresses and counts
- Sector allocation table structure at 0x22B430
- PPORT FSB transfer protocol (9 region descriptors, flag bytes)
- All file operations (save, load, delete, rename, format)

**Partially understood:**
- 9-byte directory entry fields (handler indices known, semantic meaning of each byte needs field-level annotation)
- FGB/FEB internal structure (accessed through region descriptors, exact field layouts within each block type need further tracing)
- Relationship between the 5-page FSB (120 entries) and the 16-partition system
- FS_Scan_Directory buffer layout at 0x22AA9C (20 entries, complex stride pattern with offsets 0x100 and 0x114)

**Next steps:**
- Annotate FS_Read_FSB with field-level comments (issue kn5000-q7xb)
- Annotate sector allocation and VarInt encoding (issue kn5000-c5gn)
- Annotate file operations in detail (issue kn5000-li65)
- Map RAM data structures with field labels (issue kn5000-c47b)

## Related Pages

- [HDAE5000 Hard Disk Expansion]({{ site.baseurl }}/hdae5000/) -- Original firmware documentation
- [HDAE5000 Hard Disk Interface]({{ site.baseurl }}/hdae5000-disk-interface/) -- IDE/ATA low-level protocol
- [HDAE5000 Homebrew Development]({{ site.baseurl }}/hdae5000-homebrew/) -- Writing custom extension ROMs
- [Storage Subsystem]({{ site.baseurl }}/storage-subsystem/) -- Overview of all KN5000 storage options
- [Memory Map]({{ site.baseurl }}/memory-map/) -- Full system address space
