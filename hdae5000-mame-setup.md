---
layout: page
title: HDAE5000 MAME Setup Guide
permalink: /hdae5000-mame-setup/
---

# HD-AE5000 MAME Setup Guide

*Last updated: March 30, 2026*

This guide explains how to set up and use the HD-AE5000 hard disk expansion board in MAME's KN5000 emulation.

> **See Also**: [HDAE5000 Overview]({{ site.baseurl }}/hdae5000/) for firmware analysis, [Disk Interface]({{ site.baseurl }}/hdae5000-disk-interface/) for the low-level ATA protocol, [Filesystem]({{ site.baseurl }}/hdae5000-filesystem/) for the on-disk format.

## Quick Start

### Running with HDAE5000 (no disk)

To boot the KN5000 with the HDAE5000 extension board but no hard disk attached:

```bash
fs_mame kn5000 -ui_active -window -extension hdae5000
```

The firmware will display the HD-AE5000 splash screen ("Start-up! Please wait..."), poll for the drive, time out after a few seconds, and display **"Hard disk reset error"**. This is normal --- it means the firmware correctly detected that no drive is present. After dismissing the error, the keyboard boots normally with disk-related features disabled.

### Running with a Hard Disk Image

```bash
fs_mame kn5000 -ui_active -window -extension hdae5000 -hard1 kn5000_disk.hd
```

The `-hard1` flag attaches a raw disk image to the ATA slot on the HDAE5000.

## Creating a Disk Image

### Blank Disk

The HDAE5000 firmware uses CHS (Cylinder/Head/Sector) addressing and a custom filesystem (FSB/FGB/FEB --- not standard FAT). The geometry is read from the drive's ATA IDENTIFY DEVICE response. The firmware's internal sector limit is **20,457 sectors** (~10.5 MB usable), though the original hardware shipped with larger drives (the excess capacity was simply unused by the firmware).

Create a blank raw disk image:

```bash
# ~10 MB disk (within firmware's 20,457-sector addressable range)
dd if=/dev/zero of=kn5000_disk.hd bs=512 count=20480
```

MAME's ATA HLE device calculates CHS geometry from the file size automatically.

### Important: Use Raw Images, Not CHD

The HDAE5000 ATA interface requires **raw disk images** (plain sector dumps). MAME's CHD (Compressed Hunks of Data) format does **not** work --- MAME returns raw CHD header bytes instead of decompressed sector data when accessed through the `ata_interface_device`.

| Format | Extension | Works? | Notes |
|--------|-----------|--------|-------|
| Raw image | `.hd` | Yes | Plain sector dump, no header |
| Raw image | `.img` | Yes | Same format, different extension |
| CHD | `.chd` | No | Returns header bytes, not sector data |

If you have a CHD image, extract it first:

```bash
chdman extracthd -i disk.chd -o disk.hd
```

### Using an Existing FAT16 Image

If you have a disk image from the [App Loader]({{ site.baseurl }}/app-loader/) or other tools, copy it with the `.hd` extension:

```bash
cp your_disk.img kn5000_disk.hd
```

## Boot Sequence with HDAE5000

When the KN5000 boots with the HDAE5000 extension:

1. **Main firmware boot** --- Normal KN5000 initialization (SubCPU payload, NVRAM validation)
2. **Extension detection** --- Main CPU detects the HDAE5000 ROM at 0x280000
3. **HD-AE5000 splash screen** --- Displays "Start-up! Please wait..."
4. **ATA drive polling** --- Firmware polls status register at 0x13001E, checking for BSY=0 and DRDY=1
5. **Drive identification** --- If a drive responds, firmware issues IDENTIFY DEVICE (0xEC) to read CHS geometry
6. **Filesystem check** --- Reads the FSB (File System Block) and validates the custom filesystem
7. **Normal operation** --- Disk menu becomes available for file management

### What Happens Without a Disk

Without a disk image (or with an empty ATA slot), step 4 times out after ~4 million polling iterations. The firmware then displays:

```
!SYSTEM ERROR!
Hard disk reset error.
Please call your dealer or service center.
```

This is the expected behavior. After dismissing the error, the KN5000 boots normally --- disk-related menu items are simply unavailable.

### What Happens With a Blank Disk

With a blank (all-zeros) disk image, the drive responds to ATA commands but the filesystem is not initialized. The firmware will detect the drive but report an FSB error.

### Formatting the Hard Disk

The HD-AE5000 firmware has a built-in format function accessible from the disk menu (**HD FORMAT**). To use it:

1. **Write protection must be OFF** (the HD FORMAT icon is grayed out when write-protected)
2. The firmware prompts for a **safety code**: enter **0 5 0 3 5 4** using the UP/DOWN data wheel
3. Confirm to begin formatting

This creates the custom HDAE5000 filesystem (FSB/FGB/FEB structures) on the disk.

Alternatively, the original HD-TechManager5000 PC software could format the disk via the parallel port interface (command 0x17).

## ATA Interface Details

The HDAE5000 maps ATA registers directly to the main CPU address space:

| Address | ATA Register | Width |
|---------|-------------|-------|
| 0x130010 | Data | 16-bit |
| 0x130012 | Error / Features | 8-bit |
| 0x130014 | Sector Count | 8-bit |
| 0x130016 | Sector Number / LBA Low | 8-bit |
| 0x130018 | Cylinder Low / LBA Mid | 8-bit |
| 0x13001A | Cylinder High / LBA High | 8-bit |
| 0x13001C | Device/Head | 8-bit |
| 0x13001E | Status / Command | 8-bit |
| 0x130020+ | Alt Status / Device Control (CS1) | 8-bit |

The firmware uses **CHS addressing** exclusively and **PIO mode** for all data transfers (no DMA). The ATA INTRQ signal is routed through the extension slot connector to the main CPU's INT9.

## Troubleshooting

### Boot hangs at splash screen

If the emulator appears stuck on "Start-up! Please wait..." for more than 10 seconds, the ATA device may be instantiated but not responding with DRDY. This was fixed in the March 30, 2026 commit --- ensure you have the latest `kn5000_pr6_hdae5000` branch or newer.

**Root cause**: MAME's ATA HLE device goes through a multi-millisecond reset/diagnostic sequence, during which the status register returns BSY=1. The firmware's tight polling loop (4M iterations) becomes extremely slow when each read hits the ATA device subsystem. The fix sets the default ATA slot to empty (no device) unless a disk image is explicitly provided.

### "Hard disk reset error" with a disk image attached

Verify:
1. The disk image is a **raw image** (not CHD)
2. The file extension is `.hd` or `.img`
3. The image is attached with `-hard1` (not `-hard`)
4. The image file is not zero bytes

### Drive detected but filesystem errors

A blank disk image will pass the ATA polling but fail filesystem validation. The firmware expects its custom FSB/FGB/FEB filesystem structures. Creating a properly formatted disk requires either:
- The original HD-TechManager5000 PC software (via parallel port emulation --- not yet implemented)
- A disk image tool that creates the HDAE5000 filesystem format (not yet available)

## Current Emulation Status

| Feature | Status | Notes |
|---------|--------|-------|
| Extension board detection | Working | ROM mapped at 0x280000-0x2FFFFF |
| Extension RAM | Working | 512KB at 0x200000-0x27FFFF |
| ATA register access | Working | CS0 (0x130010-0x13001F) and CS1 (0x130020-0x13002F) |
| ATA INTRQ routing | Working | Routed to main CPU INT9 via extension slot |
| Drive identification | Working | IDENTIFY DEVICE returns geometry from image size |
| Sector read/write | Working | PIO mode, 512-byte sectors |
| PPI parallel port | Stub | 8255 device instantiated but callbacks not wired |
| PC communication | Not implemented | Requires PPI callback wiring + PC-side emulation |
| Audio output | Not implemented | Extension board audio DAC not emulated |

## Related Pages

- [HDAE5000 Overview]({{ site.baseurl }}/hdae5000/) --- Firmware structure and initialization
- [HDAE5000 Disk Interface]({{ site.baseurl }}/hdae5000-disk-interface/) --- Low-level ATA protocol
- [HDAE5000 Filesystem]({{ site.baseurl }}/hdae5000-filesystem/) --- On-disk data structures
- [HDAE5000 Homebrew]({{ site.baseurl }}/hdae5000-homebrew/) --- Writing custom software
- [App Loader]({{ site.baseurl }}/app-loader/) --- Loading applications from disk
- [MAME Branch Review]({{ site.baseurl }}/mame-branch-review/) --- Development roadmap
