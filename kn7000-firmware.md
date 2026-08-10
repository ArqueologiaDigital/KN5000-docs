---
layout: page
title: KN7000 Firmware Images
permalink: /kn7000-firmware/
---

# KN7000 Firmware Images

Two flash images are recovered from the [system-update discs]({{ site.baseurl }}/kn7000-system-update-discs/):
`kn7000_program.rom` (main firmware) and `kn7000_table.rom` (resource archive).
Offsets below are file offsets in hex; integers are little-endian **except** the
`.SLD` size field.

## Program image (`kn7000_program.rom`, 0x3F6F01 bytes)

Panasonic **MN10300/AM33** code, mapped at CPU address `0x48400000`
(file offset + base). See the [KN7000 overview]({{ site.baseurl }}/kn7000/) for the full memory map.

### Boot header (0x0 – 0x80)

Two absolute jumps and a marker byte, then `0xFF` fill to the start of code:

```
0x00: dc 7e ff 00 00   jmp  0x4840FF7E     ; reset entry
0x05: cb ×5            nop                  ; padding
0x0a: dc c5 77 0d 00   jmp  0x484D77CF
0x0f: 16               ROM-present marker   ; firmware only ever compares it to 0xFF
0x10..0x7f: ff         fill
0x80: code begins
```

`jmp` on the MN10300 is `0xDC` + a 32-bit little-endian target; the stored value
plus the `0x48400000` base gives the destination. There is **no in-image
reset-vector table and no version byte** — the true CPU reset vector and the
library/kernel code at `0x4C000000` live in a separate, still-undumped internal
boot ROM.

### Dependency on the undumped library ROM (`0x4C000000`)

The program image is only *half* the code. It makes **7,965 calls to 298
distinct entry points** in a second ROM at `0x4C000000` that is **not present on
the system-update floppies** and has not been dumped. The called addresses span
up to `0x4C5E9A3A`, so that ROM is **at least ~6 MiB**. The way arguments are set
up at the call sites identifies it as the **C runtime + MILK kernel**: e.g.
`0x4C001A48` (1,201 calls — a `printf`/`sprintf`-family formatter fed a
format-string pointer and stacked arguments), `0x4C003051` (a `memcpy`/`strcpy`
taking dest/src pointers), `0x4C0019D5` (a numeric formatter). This is why a
running emulator needs that ROM dumped (or the hot entry points high-level
emulated): the [boot interpreter]({{ site.baseurl }}/kn7000/) runs 3.06 M instructions and then
calls straight into `0x4C0…`.

### Region map

| Range | Contents |
|-------|----------|
| `0x000080` – ~`0x186000` | Main firmware code (region 1) |
| ~`0x185DC0` – `0x186208` | `float64` decibel-ratio table (137 IEEE-754 doubles, e.g. `1.25892544` = 10^0.1) |
| ~`0x186208` – ~`0x3B8000` | Data / resources: multi-language UI text, FAT boot template, flash-chip ID strings, RGB palettes, fonts, GUI resource tables, 9 JPEGs, two Windows `.BMP` images |
| ~`0x3B8000` – `0x3F6F01` | Code region 2: the `MILK MN10300` kernel + zlib 1.0.4 |

### Version numbers

The package labels ("v16" program / "v14" table) come only from the download
filenames; the firmware carries **its own internal version counters**, unrelated
to those:

| Component | Value | Where |
|-----------|-------|-------|
| PROGRAM | **941** | `u16` at file `0x33660C` (the loader reads 32 bits but keeps only the low half), shown by `PROGRAM : %4d` (`0x1D67E0`) |
| TABLE | **84** | ASCII `"84\n"` at table file `0x139EE8`, reached via the pointer at table offset `0x1C` |

RHYTHM and PICTURE versions are read from flash regions not covered by these
updates (the rhythm ROM and the `0x57800000` picture flash).

All four numbers are what the instrument's hidden **SOFT VERSION** screen
prints. At least one surviving KN7000 reports `PROGRAM : 893` / `TABLE : 80` —
an earlier, **unpreserved** pair of images; see the
[SOFT VERSION screen]({{ site.baseurl }}/kn7000-soft-version/).

9,472 bytes of that earlier pair have since been transcribed by hand from
photographs of the instrument's own hex viewer. They put build 941 at build 893
**plus several insertions totalling 6,451 bytes** in the program half, and plus a
single 3-byte insertion in the table half. It is a transcription and **not a
dump**, and no reconstructed image exists — see
[Recovering build 893]({{ site.baseurl }}/kn7000-build-893-recovery/), and
[Reading ROM out of the screen]({{ site.baseurl }}/kn7000-rom-from-the-screen/)
for the capture route meant to replace hand photography.

### Notable strings

- Version screen: `SOFT VERSION` (`0x1D5AD8`), `--- SOFTWARE VERSION ---` (`0x1D5D9C`), `PROGRAM : %4d` / `TABLE   : %4d` / `RHYTHM  : %4d` / `PICTURE : %4d` (`0x1D67E0`+)
- Kernel banner `MILK MN10300 Ver1.0R1` (`0x3B8AAC`); zlib deflate/inflate banners (`0x3B8604` / `0x3B863C`)
- FAT boot template `Technics    NO NAME    FAT12   FAT16` (`0x1BA4BB`)
- Flash-chip IDs `MBM29LV160B`, `MX29LV160B`, `AT49BV16X4` (`0x1CF9EA`+) for the sound-RAM expansion
- Model-compatibility list `@Expansion Board KN7000 SOUND RAM`, then `KN6000`/`KN5000`/`KN3000`/`KN2000`/`KN1600 SOUND RAM` (`0x1B8517`+)
- UI languages: English / German / French / Spanish / Indonesian message blocks (Italian has a menu entry but no translated text), plus an EUC-JP developer easter-egg entry at `0x1A0C4D`
- Developer symbol tables: `_TT_*` tag names, `*Proc` window-procedure names (`AcProgVerBoxProc`, `IvMpVerWinProc`, …), `MT_*` API names (`MT_GetLanguagePtr`, `MT_FLASHWRITE`), GUI object names (`PanelSimulator`, `ClipBoard`, `DefaultWindow`) — the same conventions as the KN5000 (see [Shared Codebase Map]({{ site.baseurl }}/technics-shared-codebase/))

### Embedded images

9 JPEGs plus two genuine Windows `.BMP` files — a 26×46 1bpp treble-clef icon at
`0x19E704` and a 160×100 8bpp photo at `0x345718`. Unlike the KN5000's
headerless raw 8bpp bitmaps, the KN7000 uses standard file formats for at least
part of its artwork, and none of the KN5000 bitmap pixel data is reused.

## Table image (`kn7000_table.rom`, 0x3E94D4 bytes)

A resource archive fronted by an offset directory:

| Offset | Contents |
|--------|----------|
| `0x000` | 85 × `uint32` little-endian offsets: `dir[0]=0x200` (first segment) … `dir[84]=0x3E94D4` (= file size, end sentinel) → **84 segments** |
| `0x154` | zero padding to `0x200` |
| `0x200` | segment data |

Segment *i* spans `dir[i]..dir[i+1]`. The 84 segments break down as **57
baseline JPEGs** (built-in demo slideshows, all verified decodable, 160×80 up to
640×240) and 27 tagged data chunks whose first bytes are an ASCII type tag
(`TCMP`, `TPAD`, `JK`, …). Two 4-byte segments hold the ASCII strings `"84\n"`
(the table version) and a `"ZZZ\n"` placeholder.

> **Where the image stops is not where the chip stops.** IC16 + IC17 are one
> 8 MB flash pair spanning `0x48000000`–`0x487FFFFF`, with this table image as the
> lower half and the program image as the upper half. The table payload ends at
> `0x483E94D3`, which leaves **`0x483E94D4`–`0x483FFFFF` (93,484 bytes) that no
> update disk ships and nobody has ever read** — the exact positional analogue of
> the KN5000's resident updater block. See
> [Where does the flash updater live?]({{ site.baseurl }}/kn7000-firmware-security/#45-where-does-the-flash-updater-live-unresolved).

## Byte-exact disassembly project

The `kn7000_disassembly` repository holds a reconstruction project for the
MN10300 firmware. Because no GNU binutils MN10300 target is available in common
distributions, it ships a small self-contained assembler whose only job is
byte-exact reconstruction: the source starts as a skeleton in which every byte is
pulled in verbatim (a raw range), and reverse engineering proceeds by replacing
those ranges with real disassembled instructions and typed data. A `make verify`
step asserts the rebuilt images stay **100% byte-identical** to the originals at
every step. Disassembly listings are generated with MAME's `unidasm`
(`-arch mn10300`).

This mirrors the KN5000 approach, whose
[ROM reconstruction]({{ site.baseurl }}/rom-reconstruction/) reached 100% byte-perfect matches on
all six ROMs.

### 2,302 functions named by reusing KN5000 knowledge

The disassembly gets a large head start from the
[shared codebase]({{ site.baseurl }}/technics-shared-codebase/): the KN7000 embeds the same "MILK"
UI-toolkit **runtime reflection tables** the KN5000 does — code-pointer arrays
each followed by an index-parallel name-pointer array, used by the firmware's
`MT_GetProcedure`-style lookup. There are **~114 such tables** (one per
widget/handler group), and parsing them all recovers **2,302 named functions** —
`SleepMainTask`, `DispatchEvent`, and the whole `Ac*`/`Vw*`/`Ps*`/`Iv*`/`Tt*`
widget window-procedure set (518 `*Proc` + 353 `*Func` handlers), i.e. the **same
names documented for the KN5000**. These become the named anchors for the
instruction-level disassembly.

### Readable, re-assemblable source

With a purpose-built MN10300 encoder (99.9% round-trip) wired into
the assembler, named functions are converted from raw bytes into real MN10300
source that still rebuilds byte-for-byte. Call targets are resolved to labels —
recovered names where known, else a synthetic `func_<ADDR>` for the internal
helpers — so the reconstruction reads like ordinary source. For example the
object-visibility accessor `SetVisible`:

```
SetVisible:                      # CPU 0x4842D406
    add     -0xc, sp
    call    GetLinkView, 0, 0    # fetch the linked view object
    movhu   (0xc, a0), d1        # load its flag word
    clr     d0
    btst    0x01, d1             # test the "visible" bit
    bne     0x4842d419
    mov     1, d0
    ret     0, 0xc
```

66 functions (the task/event and display/object framework clusters) are
converted this way so far; growing the set converts more, always holding the
100% byte-match invariant.
