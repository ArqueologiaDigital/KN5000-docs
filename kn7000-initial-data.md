---
layout: page
title: KN7000 User Data & the Initial Data Disk
permalink: /kn7000-initial-data/
---

# KN7000 User Data & the Initial Data Disk

Some of the KN7000's on-screen content — the built-in **style names**, the
**Favorites**, the **Custom** panels — does not live in the firmware update images
(`kn7000_program.rom` / `kn7000_table.rom`). It lives in a separate **custom-data
flash** that ships **blank** and is programmed, once, from an **"Initial Data"
floppy disk** during first setup. This page documents that subsystem, recovered by
reverse-engineering the firmware's disk-load/install path.

This is the same design the [KN5000](/system-overview/) uses — its MAME driver
notes that the custom-data flash (IC19) "was dumped from a system that had it
already programmed by the initial data disk" — one more piece of the
[shared codebase](/technics-shared-codebase/).

## The custom-data flash

| Property | Value |
|----------|-------|
| **Read view** (CPU) | `0x56000000` — a `u32`-offset directory archive at flash offset `0x200` |
| **Command/program window** | `0x96800000` — AMD/Fujitsu x16 command set (unlock writes to `0x9680AAAA` / `0x96805554`) |
| **Chip** | 2 MB / 16 Mbit bottom-boot: MBM29LV160B, MX29LV160B or AT49BV16X4 (descriptor table at program `0x1CF9E0`) |
| **Driver** | `FlashWordProgram` `0x4847F721`, `FlashSectorErase` `0x4847F75A`, `FlashReadAutoselect` `0x4847F980`, `FlashReset` `0x4847F6C7` |

A separate **factory read-only** data flash sits at `0x57000000` (rhythm/style data
that extends the table ROM). In emulation both read as zero until dumped, so style
names and Custom/Favorites content fall back to defaults.

## The Initial Data disk (`idd7000`)

The disk carries four files. Each begins with a Technics tag matching the firmware's
disk-file dispatch tables (`DiskFileTagTable` `0x48664090`, `DiskFileExtTable`
`0x48664438`), and installs to one of two destinations:

| File | Destination | Contents |
|------|-------------|----------|
| `01CTMINI.AST` | custom **flash** | Custom/Music-Stylist data; a **compressed** (LZSS-family, ~6:1, declared size `0x1E0000`) payload — the codec parameters are not yet reversed |
| `02UMDINI.MD` | battery **SRAM** | user-Memory style references (44 style-IDs) |
| `03FAVINI.FAV` | battery **SRAM** | Favorites (name + settings) |
| `04HPGINI.HMP` | battery **SRAM** | Home-Page (hotspots + an embedded BMP) |

Only the `.AST` installs to flash; the rest go to battery-backed SRAM (favorites
block `0x50083D72`, magic `"KN7000 SDDIR INF"`). The extractor
(`extract_idd7000.py` in the [kn7000_extraction] tools) parses all four; the flash
image awaits the `.AST` codec.

### Favorites, decoded

The four factory Favorites and what they recall (each setting is an ID whose
`& 0x00700000` bits select built-in / MEMORY / CUSTOM source):

* **Example** — a mix of built-in rhythms and CUSTOM sounds
* **Cool Sounds !** — nine CUSTOM sound/style IDs (`0x2014xx` / `0x2600xx`)
* **Cool Rhythms !** — nine built-in rhythm IDs
* **Entertainer** — panel-setting IDs

### The Home-Page image

`04HPGINI.HMP` embeds a 160×100 Windows BMP — a holiday-themed graphic (a red bow
with holly over sheet music):

<figure style="margin:1rem 0;text-align:center;"><img src="{{ "/assets/images/kn7000/idd7000-homepage.png" | relative_url }}" alt="Initial Data disk home-page image, 160x100" style="image-rendering:pixelated;width:320px;max-width:100%;border:1px solid #ccc;border-radius:3px;"><figcaption style="font-size:0.8rem;color:#777;">The factory home-page image, carved from <code>04HPGINI.HMP</code> (160×100, 2× shown)</figcaption></figure>

It is **byte-identical** to the image already in the program ROM at `0x48745718`
(shown in the [Image Gallery](/kn7000-image-gallery/) as `program_345718`), so the
disk simply re-installs the factory default.

## The boot splash (and the "green screen")

A real KN7000 opens with a **640×240 boot splash** — three chrome music notes
sweeping past the Earth toward a starburst, then the mirrored **"KN7000"** logo. Both
frames are **JPEGs already present in the dumped table ROM**:

| Frame | Table-ROM address |
|-------|-------------------|
| Music notes in space | `0x480566E8`, `0x4805A32E` |
| "KN7000" chrome logo | `0x48066517`, `0x4806B954` |

(Other 640×240 table-ROM images such as "Welcome to SX-KN7000" @`0x48139EF0` belong
to the **demo mode**, not the power-on splash.)

In the emulator, boot currently shows a **green screen** where this animation
should be. Because the frames are **present in the ROM** (not the undumped picture
flash), the green is a **display-path bug** — the firmware isn't decoding/blitting
the splash JPEGs — rather than missing data. Tracking down the boot JPEG-decode path
is the fix.

## How the rhythm menu resolves a style name

Pressing a rhythm-genre button (e.g. BALLAD) resolves style names through a clean
program-ROM chain — all now named in the [disassembly]:

1. `GetCurrentGenreIndex` (`0x48435A1B`) reads the current genre (RAM `0x50034C3C`).
2. `GenreStyleTable` (`0x48735EE4`) — 16 records `{name[16], styleCount@+0x11,
   styleListPtr@+0x14}` — gives that genre's style-ID list (BALLAD = 16 styles).
3. Each style-ID's source bits pick built-in / MEMORY / CUSTOM; `ResolveStyleId`
   (`0x48435B33`) maps it through `StyleNumToBankSlotLUT` (`0x48734EE4`).
4. The **name** is fetched from the custom flash — which is empty in emulation, so
   every slot currently shows the default "8 Beat 1".

So the "all 8 Beat 1" symptom is not a broken table (the table enumerates 16 valid
styles); it is the **empty custom flash**. Populating it — by reversing the `.AST`
codec, or dumping a programmed part — is the fix.

[kn7000_extraction]: https://github.com/felipesanches/kn5000_homebrew
[disassembly]: /kn7000-firmware/
