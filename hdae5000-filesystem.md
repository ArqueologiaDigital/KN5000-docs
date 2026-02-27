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

The FSB is the master metadata structure for the entire filesystem. There is one FSB per formatted disk. It is read and written as a single unit:

| Operation | Address | Size |
|-----------|---------|------|
| FS_Read_FSB | 0x287F55 | 832 bytes |
| FS_Write_FSB | 0x288295 | 5,072 bytes |

The FSB can be transferred to/from a PC via the parallel port interface (PPORT commands 03-06), enabling backup and management through the HD-TechManager5000 Windows software.

**FSB Directory Entries:**
- 24 directory entries per FSB
- Each entry is **21 bytes** (0x15)
- Template data sourced from ROM at 0x2E2E60

### FGB (File Group Block)

FGBs function as directory-like containers, grouping related files together within a partition.

### FEB (File Entry Block)

FEBs contain individual file metadata for each stored file on the disk.

## Partition System

The filesystem supports a structured partition layout:

- Up to **16 partitions** per disk
- Up to **40 directory entries** per partition (9 bytes each, insertion-sorted by name)
- Partition status byte: `0x02` = active partition

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

- Stored in RAM at 0x22B430 (20KB buffer)
- Free space calculated by scanning 4-byte groups, clearing bit 7, shift-left by 7
- Maximum sector number: 20,457 (0x4FE9)

## RAM Data Structures

The filesystem maintains several key data structures in RAM:

| Address | Size | Purpose |
|---------|------|---------|
| 0x229D99-0x229DAE | ~22 bytes | CHS parameters from ATA IDENTIFY (cylinders, heads, sectors, state flags) |
| 0x22AA9C | varies | Filesystem buffer base -- up to 20 entries |
| 0x22B430 | 20KB (0x5000) | Sector data/allocation table |
| 0x230440 | 4 bytes | Current file descriptor pointer |
| 0x2304D8-0x2304EF | ~24 bytes | File save state |
| 0x230884 | 360 bytes | Directory entry table (40 x 9-byte entries) |
| 0x230E72 | 2 bytes | Directory entry count |
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
| FS_Init | 0x2870D6 | 3,711 bytes | Being disassembled |
| FS_Read_FSB | 0x287F55 | 832 bytes | Disassembled |
| FS_Write_FSB | 0x288295 | 5,072 bytes | Binary blob |
| FS_Buffer_Setup | 0x289665 | 548 bytes | Disassembled |
| FS_Scan_Directory | 0x289889 | 2,663 bytes | Disassembled |
| FS_Entry_Lookup | 0x28A2F0 | 739 bytes | Disassembled |
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

### Routine Descriptions

**FS_Init** (0x2870D6, 3,711 bytes) -- The master initialization routine that parses the FSB and sets up all filesystem state. This is the most important routine for understanding the on-disk format, and is currently being disassembled.

**FS_Read_FSB / FS_Write_FSB** -- Read and write the master File System Block. FS_Write_FSB is significantly larger (5,072 bytes vs 832 bytes for read), reflecting the complexity of serializing the filesystem metadata with proper sector allocation updates.

**FS_Scan_Directory** (0x289889, 2,663 bytes) -- Scans directory entries within a partition, presumably iterating over FGB/FEB structures to enumerate files.

**FS_Entry_Lookup** (0x28A2F0, 739 bytes) -- Looks up a specific file entry, likely by name or index within a directory.

**File_Format** (0x28E187, 772 bytes) -- Formats the hard disk, creating an empty filesystem with initialized FSB structure.

**Calc_Disk_Space** (0x28E48B, 178 bytes) -- Calculates free disk space by scanning the sector allocation table.

## PC Parallel Port Interface

The HDAE5000 includes a PC parallel port interface (via NEC uPD71055 PPI) that provides filesystem-level operations:

| PPORT Command | Operation |
|---------------|-----------|
| 03 | Read FSB from hard disk |
| 04 | Send FSB to PC |
| 05 | Receive FSB from PC |
| 06 | Write FSB to hard disk |

Beyond FSB transfer, the parallel port can also:

- Send/receive file data
- Support custom ROM data transfer
- Manage 9 region descriptors for block transfer

This interface enables the Technics SX-KN5000 to exchange files with a PC, likely used for backup, data management, and firmware updates via the HD-TechManager5000 Windows software.

## Analysis Status

This is an active reverse engineering effort. The on-disk format of FSB/FGB/FEB structures is **not yet fully understood**. The top priorities for completing our understanding of the filesystem are:

1. **FS_Init** (0x2870D6) -- Parses the master metadata and reveals the on-disk FSB/FGB/FEB layout
2. **FS_Write_FSB** (0x288295) -- Serializes the metadata back to disk, confirming the format

Most of the higher-level file operations (load, save, delete, rename, format) have been disassembled, but they operate on in-memory data structures whose relationship to the on-disk format is mediated by FS_Init and FS_Write_FSB.

## Related Pages

- [HDAE5000 Hard Disk Expansion]({{ site.baseurl }}/hdae5000/) -- Original firmware documentation
- [HDAE5000 Hard Disk Interface]({{ site.baseurl }}/hdae5000-disk-interface/) -- IDE/ATA low-level protocol
- [HDAE5000 Homebrew Development]({{ site.baseurl }}/hdae5000-homebrew/) -- Writing custom extension ROMs
- [Storage Subsystem]({{ site.baseurl }}/storage-subsystem/) -- Overview of all KN5000 storage options
- [Memory Map]({{ site.baseurl }}/memory-map/) -- Full system address space
