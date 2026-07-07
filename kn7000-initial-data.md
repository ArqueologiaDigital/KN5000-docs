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
| `01CTMINI.AST` | custom **flash** | Custom/Music-Stylist data; the payload is **raw zlib/DEFLATE** (no wrapper) starting at file offset `0x10`. Version byte `0x01` = compressed flag; the u32 at `+4` (`0x1E0000`) is the **decompressed** size. It inflates to the content of the writable **custom flash** (the region the idd7000 disk programs — write/command window `0x96800000`; `0x56000000`/`0x57000000` are the separate factory flashes), landing at flash offset `0x20000` (`0x1E0000` B fill it to the 2 MB end). Decoded, it carries the real style/sound names (`Swing And Jive`, `Calypso Dance`, `Jazz Fusion`, …) |
| `02UMDINI.MD` | battery **SRAM** | user-Memory style references (44 style-IDs) |
| `03FAVINI.FAV` | battery **SRAM** | Favorites (name + settings) |
| `04HPGINI.HMP` | battery **SRAM** | Home-Page (hotspots + an embedded BMP) |

Only the `.AST` installs to flash; the rest go to battery-backed SRAM (favorites
block `0x50083D72`, magic `"KN7000 SDDIR INF"`). The extractor
(`extract_idd7000.py` in the [kn7000_extraction] tools) parses all four and now
**decodes the `.AST`** (raw DEFLATE) to a `.flash.bin`.

**The `.AST` codec is plain zlib.** The firmware links **zlib 1.0.4** — its inflate
error strings (`unknown compression method`, `invalid window size`, `incorrect header
check`, `need dictionary`, `incorrect data check`) sit at `0x485CD20C`, right after the
style-type name table (`8 Beat`, `16 Beat`, `Dance Pop`, … at `0x485CCF2C`). The payload
is a *raw* DEFLATE stream (no 2-byte zlib header) at file offset `0x10`; inflating it with
`zlib.decompressobj(-15)` yields exactly `0x1E0000` bytes = the custom-flash region from
offset `0x20000` to the 2 MB end. (The earlier "Huffman/LZH, not zlib" and "LZSS-variant"
readings were wrong — pylzss's 1.1 MB partial was a false positive; the near-uniform byte
histogram is just well-compressed DEFLATE output.) Populating the emulated custom flash
(`0x96800000`, the region reader `0x4847FB68` / parser `0x4847F9F7` currently see as all
zeros) from this decoded image is what will replace the `8 Beat 1` placeholders with the
real names.

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

In the emulator, boot first showed a **green screen** where this animation should be.
Fixing it took untangling **two** independent bugs:

1. **The display model.** KN7000 pictures are **not palettized** — a picture pixel is a
   12-bit (4:4:4) direct colour split across two work-RAM planes (`0x500D4080` byte =
   `0xD0 | red4`; companion `0x500F9880` byte = `(green4<<4) | blue4`). The firmware
   composites these into a 640×240 RGB565 image at `0x9CE00000` — the exact buffer the
   LCD controller scans. The driver now presents `0x9CE00000` directly, so the whole
   display (UI *and* pictures) is pixel-exact.

2. **The JPEG decoder.** With the display fixed, the splash showed *noise* instead of
   green — the software JPEG decoder was producing garbage. The cause was a single
   **unimplemented CPU instruction**: the MN10300/AM33 `udf07` op (a **bit-search**,
   `BSCH`) used in the decoder's Huffman step. The CPU core was silently skipping it,
   desyncing the entire bit stream. Implementing it (bit position of the most-significant
   set bit) made the splash decode **pixel-clean** — verified against a reference decode
   of the same table-ROM JPEGs.

With both fixed, the emulated KN7000 now plays its real power-on splash — the chrome
music notes sweeping over the Earth, then the mirrored "KN7000" logo. (Details in the
driver's `display-dual-plane-direct-color.md` and `mn10300-udf-instructions-unimplemented.md`
notes.)

<figure style="margin:1rem 0;text-align:center;"><img src="{{ "/assets/images/kn7000/splash-working.png" | relative_url }}" alt="The emulated KN7000 boot splash, decoded and rendered correctly" style="max-width:100%;border:1px solid #ccc;border-radius:3px;"><figcaption style="font-size:0.8rem;color:#777;">The boot splash rendering correctly in emulation after both fixes (dual-plane display + the <code>udf07</code> bit-search CPU op).</figcaption></figure>

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
