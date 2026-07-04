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
[reflection tables](/kn7000-firmware/).

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

## Relationship to the KN5000

The floppy/FAT layer and the FMM screen design are **shared with the KN5000**
([Storage / FDC](/fdc-subsystem/), [Shared Codebase Map](/technics-shared-codebase/)).
The KN7000 **extends** it with the SD-card slot (folders, playlists, rename — a
much richer file model) and the USB *Song Manager* PC link, neither of which the
KN5000 had. Those additions are visible precisely as the extra `Sdc*` / USB
handlers layered on top of the common `Fmm*` core.
