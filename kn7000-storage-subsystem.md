---
layout: page
title: KN7000 Storage & File System
permalink: /kn7000-storage-subsystem/
---

# KN7000 Storage & File System

The KN7000 can load and save its data on **three storage media** — the built-in
**floppy disk drive**, an **SD-card slot**, and a **USB** link to a PC — all
driven through one **File Management Mode (FMM)** in the firmware. The SD slot and
USB link are **new versus the KN5000** (which had only the floppy drive). This
page documents the storage subsystem from `kn7000_program.rom`: the media, the
file types, and the file-manager function family, all recovered by name from the
[reflection tables]({{ site.baseurl }}/kn7000-firmware/).

## Storage media

| Medium | Hardware | Firmware |
|--------|----------|----------|
| **Floppy disk (FDD)** | FDC **IC103 / IC308** | `Disk*`, `Fmm*Disk*`, `FDCstop…`; formats FAT12/FAT16 |
| **SD card** | SD-card slot (new) | `SdCard*` / `Sdc*` (folders, rename, delete, playlists) |
| **USB** | USB port (new) | *Song Manager* PC software over a USB cable |

The floppy formatter writes the standard Technics boot sector — the template
string `Technics····NO NAME····FAT12···FAT16` sits at file `0x1BA4C7`, so media
are **FAT12/FAT16** and interchangeable with a PC. The on-screen prompts confirm
the model: *"…work on Floppy Disk!"* (`0x1D8514`), *"…to the SD Card brings the
total…"* (`0x1E4C33`), and *"…with a USB cable. Please connect… included Song
Manager Software."* (`0x1E3538` / `0x2BA8B6`).

The SD-card feature set is substantial — the recovered handlers include folder
and song **rename** (`SdcTechnicsFolderRename`, `SdcTechnicsSongRename`,
`SdcSmfSongRename`, `SdcCstSongRename`), **delete** with confirm
(`SdcDeleteYes/No`, `SdcSmfDeleteYes/No`), **save / overwrite** dialogs
(`SdcSaveYes/No`, `SdcOverWriteYes/No`), cursor-vs-new save location
(`SdcSaveCursorLoc` / `SdcSaveNewLoc`), **playlists** (`SdcPlistNaming`), and
naming (`SdcCustomFileNaming`, `SdcTechnicsFileNaming`, `FormatSdNaming`).

## File types

FMM handles a family of file types, each with its own load/save path; the
extensions `.MID` and `.CST` appear in a type table at `0x2637E4`:

| Type | Extension | Contents |
|------|-----------|----------|
| SMF | `.MID` | Standard MIDI File (songs) |
| Custom | `.CST` | registration / "custom" panel setups |
| Technics song | — | native song format |
| Composer | — | user rhythm/style (see the Composer/`TCMP` data) |
| Sequence | — | the on-board sequencer's songs |
| Wallpaper / Picture | — | user display images |
| Playlist | — | ordered play sets (`PlaylistSetting`, `0x265A18`) |

FMM entry points are named per type: `FmmSmfLoadTitleFunc` /
`FmmSmfSaveTitleFunc`, `FmmCstLSTitleFunc`, `FmmComposerLoadFunc`,
`FmmWallpaperLoadFunc`, `FmmPictureLoadFunc`, `FmmSeqSongNameFunc`,
`FmmPdFileNameFunc`, `FmmDocFileNameFunc`, plus medley loaders
(`FmmIntMedleyFunc`, `FmmSmfMedleyFunc`, `FmmDiskMedleySelectFunc`).

## File Management Mode (FMM)

`Fmm*` is the shared file-manager screen used across all three media. Its
functions cluster into the usual operations:

* **Load / Save** — `FmmLoadTitleFunc` (`0x4851CE31`), `FmmSaveTitleFunc`
  (`0x4851D280`), with per-type filters `FmmLoadFilterFunc` / `FmmSaveFilterFunc`.
* **Format / utility** — `FmmFormatFunc` (`0x4851C840`), `FmmDiskModeFunc`,
  `FmmUtilityTitleFunc`, `FmmPreferenceTitleFunc`; disk info via `DiskInfoFunc`,
  `DiskNameFunc`.
* **Naming / password** — `SaveFileNameFunc`, `SaveFileNameSmfFunc`,
  `SaveFileNameCstFunc`, `FmmFileNameFunc`, `FmmPasswordFunc` (media can be
  password-protected).

The file-manager screen strings — `- LOAD -`, `- SAVE -`, `CHECKING`,
`SAVE OK`, `%d KB free (%d%% used)` — live around `0x2637E4`.

## SD subsystem internals (2026-07 reverse engineering)

Live tracing plus disassembly settled how the SD side actually hangs together —
including one correction to earlier notes: **the second SIO serial channel
(`0x34000820`) is the MIDI-2 UART, not the SD link** (its RX handler is a
standard MIDI parser; the hot status polling seen on SD screens is just the
engine loop's idle MIDI pump).

The SD stack proper is a layered, DOS-like design:

* A **state machine** over the state byte `0x50083cd8`
  (`SD_GetState`/`SD_SetState`), ticked from the engine loop
  (`0x485519bc`). In state 0 it queries the MILK GUI **property system** —
  `GetProperty(object 0x0210033F, property 0x60047)` — and does nothing while
  the answer is −1. That property is the firmware's own "SD present/enabled"
  source, and it is the gate the emulator must satisfy first.
* Once un-gated, mount work is posted as a 16-byte command message to a
  dedicated **disk worker task** (`0x4854ad90`, created by `DiskInit`
  `0x4854aced`), which runs card-detect (GPIO `0x3400016c` bit 4, with a
  software override at `0x50005204`), card initialisation, and the mount.
* Files are reached through a **virtual file system**: the SD card is device
  `"d"`, mounted as drive **`"C:"`**, through per-device function pointers in a
  RAM device table (`0x500079f8`) — the same VFS the floppy uses. The FAT
  layer sits on top; the fops funnel into a disk-worker command poster
  (`0x4847030e`, message type 3) whose read/write commands drive the physical
  transport below.
* Success sets card-ready (`0x50083bc2 = 1`) and state 3 (mounted); the SD
  screens' "WAIT!" dialog is literally waiting for that state transition, and
  ERROR 93 ("SD lid is open") is its failure branch.

The **physical transport** — earlier "the remaining unknown to model" — is now
fully identified and emulated: it is a plain **byte-wide SPI master**. The 16-bit
register `0x9805000C` is one full-duplex SPI shift register to the card slot; each
write clocks eight bits (MSB-first) and a handshake through the ICR of
external-interrupt group `0x1C` (register `0x34000170`, polled on bit 4) signals
completion. The chip-select is a GPIO latch bit — `0x36008004` bit 1, active-low.
The firmware speaks **stock SD SPI** (the wake-up `0xFF` clocks with CS released,
then `CMD0`/`CMD1`/`CMD59`/`CMD9`/`CMD16`/`CMD10`, CRC7-framed commands, `0xFE`
data tokens, CRC16 data blocks), so MAME's generic `spi_sdcard` device serves it
directly. Two CRC quirks had to be patched into an overlay of that device: the
CSD block needed its CRC16 appended, and the SD **data-block CRC16 uses an init
value of `0x0000`** where MAME's `util::crc16` starts from `0xFFFF` — that
mismatch failed every CSD read until it was fixed.

### Emulation status: the SD card mounts and the file browser works

**The SD card mounts.** With a card image attached, the SPI handshake runs its
full init sequence and the mount chain reaches **state 3** with card-ready set —
reaching that state reads the **boot sector and FAT from the host image**, so
sector reads work against a real filesystem. From the **SD MENU** the **SD LOAD**
browser is live: it reports the correct free space (e.g. "65,268 KB free — 0%
used" for a 64 MB card) and paints the **FOLDER / SONG columns** with the FOLDER /
ALPHABET / NUMBER sort options and PREV/NEXT navigation. The SD LOAD screen is a
genuine **PAGE 1/3 → 2/3 → 3/3** multi-page screen (page 1 is the file browser,
pages 2–3 are the data-type load categories: CURRENT PANEL, PANEL MEMORY,
SEQUENCER, EFFECT MEMORY, FAVORITES, ALL CUSTOM STYLE…), and the emulated PAGE
Up/Down buttons walk it correctly.

**A real card image is attached by default.** `run.sh` now passes
`-harddisk sdcard_from_real_kn7000.img` for the KN7000 model (commit `8a7d8b2`);
callers can substitute their own image, or pass `-harddisk ""` for an empty slot.
This default exists because of a hardware **conflation of card-detect signals**:
the hinged slot **cover switch** and the **card-present line** feed the *same*
detect input — the polled ICR of external-interrupt group `0x1B`
(`0x3400016C` bit 4) — so the firmware cannot tell an *empty slot* apart from an
*open lid*. Both read as bit 4 = 1, and both surface as **ERROR 93 ("SD lid is
open")**. Consequently a card image is required to satisfy the check even with the
cover modelled closed (`SDCOVER`, default CLOSED); with no image the same screen
correctly shows ERROR 93 — the firmware's own no-card branch, not an emulation
bug.

**The state machine is edge-driven, so the card is inserted after boot.** The SD
mount is demand-driven off the debounced *transition* of the detect line, not its
level — a line that reads "present" from power-on never edges, and nothing ever
fires. The driver therefore models the slot as **empty at power-on** and inserts
the card a few seconds after boot (an insert timer at t≈6 s), producing the 1→0
detect edge that posts the insert message and kicks off the mount. Toggling the
cover switch live reproduces the same edge: closing with a card fires the mount,
opening triggers removal and the ERROR 93 gate.

The physical SD path is the byte-wide SPI mailbox described above; it is separate
from the **floppy's FDC** (IC103, N82077AA-compatible, memory-mapped at
`0x98020000`), though both share the disk-worker/VFS command layer higher up. The
FDC is wired, but the floppy **FORMAT** path is still open.

## Relationship to the KN5000

The floppy/FAT layer and the FMM screen design are **shared with the KN5000**
([Storage / FDC]({{ site.baseurl }}/fdc-subsystem/), [Shared Codebase Map]({{ site.baseurl }}/technics-shared-codebase/)).
The KN7000 **extends** it with the SD-card slot (folders, playlists, rename — a
much richer file model) and the USB *Song Manager* PC link, neither of which the
KN5000 had. Those additions are visible precisely as the extra `Sdc*` / USB
handlers layered on top of the common `Fmm*` core.
