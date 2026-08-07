---
layout: page
title: ROM Reconstruction
permalink: /rom-reconstruction/
---

# ROM Reconstruction

Goal: rebuild every KN5000 firmware image from disassembled source, byte for byte.

`make all` assembles the LLVM sources and then runs `scripts/build/compare_roms.py`,
which prints a similarity figure per verification section. As of August 2026 it reports
**15 sections, all at 100.00%** — nine from the primary LLVM build and six from the
archived ASL mirror build, which is still assembled and compared on every run.

Byte-identity is the project's only acceptance criterion. Any change that drops a
section below 100.00% is reverted, not explained away.

## Firmware Version History

Official firmware updates were distributed on floppy disk. All versions are archived at [archive.org](https://archive.org/details/technics-kn5000-system-update-disks).

> **Provenance note.** The release dates below are inherited from earlier revisions of this
> page and come from the update-disc listing, not from anything inside the ROM images. The
> 2026-08 conversion work did not verify them, and no corresponding dates exist in the
> disassembly repository. Treat them as unconfirmed.

### Main Board Firmware

| Version | Release Date | Notes |
|---------|--------------|-------|
| v5 | 1997-11-12 | Earliest available |
| v6 | 1998-01-16 | |
| v7 | 1998-06-26 | Source tree exists, builds 100% |
| v8 | 1998-11-13 | |
| v9 | 1999-01-26 | Source tree exists, builds 100% |
| **v10** | 1999-08-02 | **Primary disassembly target** |

### HD-AE5000 Firmware

| Version | Release Date | Notes |
|---------|--------------|-------|
| v1.10i | 1998-07-06 | Initial release |
| v1.15i | 1998-10-13 | |
| v2.0i | 1999-01-15 | Added lyrics display |

## Verification Sections

### Primary build (LLVM)

| Section | Original image | Size | Base | Top-level source |
|---------|----------------|------|------|------------------|
| maincpu v10 | `kn5000_v10_program.rom` | 2MB | 0xE00000 | `v10/maincpu/kn5000_v10_program.s` |
| maincpu v9 | `kn5000_v9_program.rom` | 2MB | 0xE00000 | `v9/maincpu/kn5000_v9_program.s` |
| maincpu v7 | `kn5000_v7_program.rom` | 2MB | 0xE00000 | `v7/maincpu/kn5000_v7_program.s` |
| subcpu payload v142 | `kn5000_subprogram_v142.rom` | 192KB | 0x0400 | `v142/subcpu/kn5000_subprogram_v142.s` |
| **subcpu v142 update image** | `kn5000_subprogram_v142_compressed.rom` | 93,203B | 0x3E0000 | *(compressed from the built payload — see below)* |
| subcpu boot | `kn5000_subcpu_boot.ic30` | 128KB | 0xFE0000 | `subcpu/boot/kn5000_subcpu_boot.s` |
| hdae5000 | `hd-ae5000_v2_06i.ic4` | 512KB | 0x280000 | `hdae5000/hd-ae5000_v2_06i.s` |
| table data | `kn5000_table_data.rom` | 2MB | 0x800000 | `table_data/kn5000_table_data.s` |
| custom data | `kn5000_custom_data.ic19` | 1MB | 0x300000 | `custom_data/kn5000_custom_data.s` |

### Legacy ASL mirror build

The project's original ASL sources are kept in `archive/asl/` and are still built and
compared: maincpu, subcpu boot, subcpu payload, table data, custom data and hdae5000 —
six more sections, all at 100.00%.

The mirror is not a museum piece; it constrains the work. The ASL sources still
`binclude` several data blobs *whole* (`initial_data.bin`, `icons_to_strings.bin`,
`wallpaper1_to_icons.bin`, …), so those files must stay byte-identical on disk even
after the LLVM sources stop referencing them. Conversions therefore slice with
`.incbin "file", offset, length` rather than splitting a blob into new files.

### The v1.42 sub-CPU firmware-update image

New in August 2026: the sub-CPU payload is now verified in *both* of the forms it ships in.

`original_ROMs/kn5000_subprogram_v142_compressed.rom` is the v1.42 payload as it appears
on a firmware-update disk ("Program DATA FILE PCK", File Type 007, flashed to Custom Data
`0x3E0000`). It is an 11-byte header — `"SLIDE4K"` + NUL, then a 24-bit **big-endian**
decompressed size (`03 00 00` = 196,608) — followed by the LZSS stream.

Because the payload itself is already source-built, recompressing the build output with
the factory stream's own decisions must reproduce the update image exactly. The Makefile
rule does that and then seals it with `cmp`:

```make
rebuilt_ROMs/kn5000_subprogram_v142_compressed.rom: \
		rebuilt_ROMs/kn5000_subprogram_v142.llvm.rom \
		original_ROMs/kn5000_subprogram_v142_compressed.rom
	python3 scripts/build/compress_lzss.py $< $@ --strict --with-header \
		--reference original_ROMs/kn5000_subprogram_v142_compressed.rom
	cmp $@ original_ROMs/kn5000_subprogram_v142_compressed.rom
```

`--with-header` (added at the same time) emits and validates the SLIDE4K header;
`--strict --reference` replays the factory encoder's match/literal decisions so the
output is byte-identical rather than merely equivalent. The section appears in
`compare_roms.py` as *subcpu v142 update image*.

See [LZSS Compression]({{ site.baseurl }}/lzss-compression/) for the format, and
[Sub-CPU Firmware Images]({{ site.baseurl }}/subcpu-firmware-images/) for what this means
for the v1.40 and v1.41 payloads.

### Generated data with its own verification targets

Two families of compressed data are no longer bincluded as opaque payloads; they are
rebuilt from checked-in sources and compared against factory slices.

| Target | What it rebuilds | Check |
|--------|------------------|-------|
| `make verify-demo-presets` | 19 SLIDE4K demo-song presets, from `.mid` + `.yaml` sidecars | 19/19 byte-identical |
| `make verify-help-databases` | 6 SLIDE8K help databases, recompressed from the checked-in decompressed database binaries | 6/6 byte-identical |

**Demo presets.** All 19 presets (entries 0–17 at 0x9C4050–0x9F94CA plus the Feature
Presentation at 0x8E0000) round-trip from a `.mid` file — the musical content, editable
in any DAW — and a `.yaml` sidecar carrying everything MIDI cannot express: song header,
cell topology, padding, stream order, running-status flags and the durations MIDI cannot
represent. `compress_lzss.py --strict` aborts the build if any payload stops matching the
factory stream, so an edit can never silently ship different music.

**Help databases.** The five live multilingual help databases (English, German, French,
Spanish, Indonesian) plus one stale sixth block are SLIDE8K — a previously undocumented
8 KB-window LZSS variant. The firmware itself supports both widths: the main-CPU routine
`SLIDE_Parse_Header` reads the digit in the magic and branches on it, `0x34` (`'4'`) to
`SLIDE_Decompress_4K_Init` and `0x38` (`'8'`) to `SLIDE_Decompress_8K_Init`. Each database
decompresses to exactly 0x9000 bytes.
`compress_slide8k.py --strict --reference` replays the factory encoder's decisions,
which is necessary because the final flag bytes carry nonzero unused bits that a plain
re-encode would not reproduce.

The sixth block, at ROM 0x983B3A, is a superseded German revision that nothing points at.
It is **truncated, not merely corrupt**: its stream decodes identically to the live German
database for exactly 0x55E0 output bytes, and the element that would produce output 0x55E0
is the first to read past 0x985FFF — because the factory image wrote the two Music Stylist
pointer tables at 0x986000/0x987000 straight over this obsolete block's tail. It is
therefore kept as a byte-exact raw slice of the dump and is *not* rebuilt from source; a
whole-extent reference slice is still round-trip-verified by `make verify-help-databases`
to pin the bytes down.

## What the August 2026 conversion waves changed

The work was scoped by an audit of every binary include and compressed region in the
repository (10 agents: 7 scanners and 3 adversarial verifiers). It inventoried **598
`.incbin`/`binclude` directives**, of which **505 are honest build products** — compiled
from C or assembly, or generated from documented data — and produced **55 findings** with
**24 adversarial verdicts**. Four waves of conversion followed: **24 packages**, each
gated on a full rebuild at 100.00%. The method is written up on the
[Disassembly Workflow]({{ site.baseurl }}/disassembly-workflow/) page.

### Table Data ROM: from opaque halves to labelled source

Before the waves, the LLVM source for the 2 MB table-data ROM pulled **1,262,528 bytes —
60% of the ROM — out of anonymous blob files**: `initial_data.bin` (524,271 B) and
`icons_to_strings.bin` (520,920 B) each as a single unlabelled `.incbin`, plus
`wallpaper1_to_icons.bin`, `icon_pixel_data.bin`, `icon_table.bin`, `wallpaper_gap.bin`,
`hkst_55.ssf` and six `bootcode_*.bin` code blobs.

Today that figure is **zero**. `initial_data.bin` is not referenced by the LLVM build at
all; `icons_to_strings.bin` survives only as 13 labelled, explicitly sized slices
(126,674 B: ten font glyph banks, the truncated German help block, the Composer factory
memory image and one residue block); `wallpaper1_to_icons.bin` as 87 named bitmap slices;
`icon_pixel_data.bin` as 177 named icon slices. Every remaining `.incbin` in the table-data
sources carries a label, a length and a comment saying what it is.

Symbol counts tell the same story: `symbols/table_data_symbols_reference.txt` went from
**133 symbols to 4,153**. The sub-CPU payload's reference file went from 3,862 to 4,326.

### Regions newly converted or identified

| Region | ROM range | Now |
|--------|-----------|-----|
| Section directory + preset banks | 0x800000–0x82FFFF | `table_data/preset_banks.s` (+ generator) |
| Tone database | 0x830000–0x87FFEF | three modules: directory/offset table, 579 tone records, aux tables |
| UI bitmaps, frames, icon tables | 0x913000–0x944D77 | `table_data/ui_bitmaps.s`, symbolic descriptor tables |
| Font descriptors + glyph banks | 0x945C00–0x950A5F | `table_data/fonts.s` (10 fonts) |
| Music Stylist preset database | 0x951000–0x98156F | `table_data/style_records.s`, 1000 × 198 B records |
| Help index, intro strings, help DBs | 0x988000–0x9999D2 | `table_data/help_databases.s` + source-built SLIDE8K |
| Panel Memory factory presets | 0x99EC00–0x9ABF3F | `table_data/panel_memory_presets.s` |
| Composer factory memory image | 0x9B4000–0x9C3FFF | `Composer_FactoryMemoryImage` — one labelled 64 KB include, layout documented in-source |
| Boot FDC command-layer driver | 0x9FD8A5–0x9FEA9C | `table_data/boot_fdc_driver.s` (2,316 lines) |
| Boot disk-format probe | 0x9FEB2B–0x9FEC6D | `table_data/boot_disk_probe.s` |
| Boot CP-serial driver | 0x9FEC6E–0x9FFB2E | `boot_cpserial.s` + `_isr.s` + `_states.s` |
| Boot C runtime (heap, memcmp, divide) | 0x9FFB2F–0x9FFE7F | `table_data/boot_clib.s` |
| Boot debug group (NOP-patched out) | 0x9FFE80–0x9FFEDF | `table_data/boot_debug.s` |
| Sub-CPU DSP data zones A0 / A / B | 0x00F7E6–0x01E17E | carved into labelled tables in `v142/subcpu/subcpu_data_tables.s` |

Several long-standing descriptions were **corrected** by this work, not merely extended:

- `bootcode_flash_handlers.bin` was never "flash update handlers" — it is the bootloader's
  complete uPD72068 FDC command layer, a compact port of the maincpu FDC driver.
- `bootcode_utils.bin` was not "motor control / VGA display / progress bar" — it is the
  floppy disk-format probe plus the bootloader's own CP-serial driver, which is
  **independent of** the runtime `CPanel_*` stack in the program ROM.
- The incbin boundary at 0x9FC6F6 was splitting a five-byte `ld A,(0x160002)` in half. It
  byte-matched, but only by accident; the instruction is now emitted whole.
- There is no "exponential pitch table at 0x13318" in the sub-CPU payload. 0x13318 is the
  middle of `DSP_MixerGain_Curve` (0x0131CF–0x0133CE), a 128-entry piecewise-exponential
  **gain** curve ending at digital full scale 0x7FFFFF00; the only proven consumer,
  `DSP_MixerCoeff_Compute`, treats its entries as amplitude.
- The claim that the sub-CPU executable lives at table-data 0x830000 is wrong. That region
  is the tone database; the runtime code payload's source path is a separate question.

## Where the source still holds raw ROM slices

Three wave-groups of work remain (hdae5000 + sub-CPU boot data; the v7 tree; a final
sweep). Measured from the current sources — total bytes emitted by `.incbin` directives
per ROM tree:

| ROM tree | `.incbin` bytes | Character of what remains |
|----------|-----------------|---------------------------|
| `v10/maincpu` | 860,028 | Overwhelmingly `includes/generated/*.bin` — C-compiled screen/widget data, an honest build product |
| `v9/maincpu` | 860,028 | Same shape as v10 |
| `v7/maincpu` | 995,213 | **Raw ROM slices behind a `generated/` path** — see the note below |
| `v142/subcpu` | 0 | No binary includes at all |
| `subcpu/boot` | 656 | One blob, `subcpu_boot_data_8000.bin` — mixed code/data, needs a ≥5-way split |
| `hdae5000` | 340,790 | Four slices of `code_29af2d_2fffff.bin`; despite the name it is graphics, palettes, text and pointer tables, including an unidentified boot-splash image at 0x2E61CE |
| `table_data` | 1,113,121 | All labelled: BMPs, wallpapers, font glyph banks, icon/bitmap slices, and the source-built compressed payloads |
| `custom_data` | 667,648 | Six factory-style-database sections; blob-level documentation judged adequate (this is one unit's user-data area, not firmware) |

**The v7 tree deserves a warning.** `scripts/build/extract_v7_bins.py` runs at build time
and `dd`-slices the v7 ROM into `v7/maincpu/includes/generated/`. Some of those slices are
explicitly v7-specific (139 `v7_block_*`, 24 `v7_fix_*`, 16 `v7_data_*` and the transplant
set — 136,775 bytes between them). The rest — 858,438 bytes under names shared with the v9
tree (`naka_*`, `sound_data_*`, …) — are C-compile outputs that the script **overwrites**
with raw ROM bytes whenever a >50%-similarity check fires. The v7 ROM therefore rebuilds
byte-perfectly while much of its "source" is the ROM itself, and the similarity heuristic
is a silent-corruption risk: a genuinely different block that happens to match at 51%
would be silently accepted. Fixing this means parameterising the C sources per firmware
version so compilation alone reproduces the v7 bytes, then deleting the overwrite. It is
the single largest item left in the plan.

Additional known-unfinished items:

- **maincpu inline `.byte` regions have never been classified** — the audit puts it at
  roughly 676 KB across the three trees (~460 KB in v7, ~108 KB in v9, the remainder in
  v10). Some of it is labelled-but-undecoded tables, some is code stored as bytes, some is
  v7 conversion residue. Separating the three is a whole wave of work on its own.
- The sub-CPU boot ROM source still spells its erased region as **98,304 individual
  `.byte 0xff` lines**; collapsing them to one `.fill` is queued.
- The hdae5000 string table around 0x2A7736–0x2A8499 is currently **mis-decoded as
  instructions** (runs of `nop` are the tables' 0x00 padding).
- Seven of the thirteen `table_data/includes/bootcode_*.bin` files are now referenced by
  no source file at all — orphans awaiting cleanup. (The other six are still bincluded by
  the ASL mirror and must stay.)
- The v1.41 sub-CPU payload has no source tree; see
  [Sub-CPU Firmware Images]({{ site.baseurl }}/subcpu-firmware-images/).

### Disassembly status diagram

![ROM Status Diagram]({{ "/assets/images/rom-status-diagram.png" | relative_url }})

**Legend:** green = disassembled code · blue = known data structures · cyan = strings ·
light green = pointer/jump tables · purple = binary includes · red = raw bytes, unknown ·
orange = raw bytes known to be code · gray = padding/unused · yellow = undetermined.
Rectangle width is proportional to ROM size.

> **This image is stale.** It was generated on 2026-02-07, before the source tree was
> reorganised per firmware version, and `scripts/build/generate_rom_status_diagram.py`
> still looks for the pre-split ASL paths (`maincpu/kn5000_v10_program.asm`, …) that no
> longer exist. Treat the picture as historical until the generator is repointed at the
> `.s` sources; the tables above are measured from the current tree.

## Original ROM Files

The original firmware dumps are stored in `original_ROMs/`:

| File | Size | Description |
|------|------|-------------|
| `kn5000_v10_program.rom` | 2MB | Main CPU program ROM (also v9, v7) |
| `kn5000_subprogram_v142.rom` | 192KB | Sub CPU payload (sent by main CPU at boot) |
| `kn5000_subprogram_v142_compressed.rom` | 93,203B | Same payload as shipped on update disks |
| `kn5000_subcpu_boot.ic30` | 128KB | Sub CPU boot ROM |
| `kn5000_table_data_rom_odd.ic1` | 1MB | Table data ROM (odd words) |
| `kn5000_table_data_rom_even.ic3` | 1MB | Table data ROM (even words) |
| `kn5000_custom_data.ic19` | 1MB | Custom data flash (user storage) |
| `hd-ae5000_v2_06i.ic4` | 512KB | HDAE5000 hard disk expansion ROM |

**ROM interleaving:** the table-data ROM uses 16-bit **word-level** interleaving across two
physical chips. `kn5000_table_data.rom` is built by alternating 16-bit words from
`odd.ic1` and `even.ic3`, not individual bytes.

Reference disassembly files (`.unidasm`) are generated with MAME's `unidasm` tool for analysis.

## Assembler

The project uses a **custom LLVM backend** (`llvm-mc -triple=tlcs900`) for assembly. All
instructions are encoded natively — no workaround macros needed.

**Build process:**

1. `llvm-mc` assembles `.s` files to ELF object files
2. `ld.lld` links with a linker script that sets the ROM base address
3. `llvm-objcopy` extracts the raw binary from the ELF
4. generated payloads (demo presets, help databases, the v142 update image) are
   recompressed and `cmp`-checked
5. `compare_roms.py` verifies every section byte-for-byte against the originals

```bash
cd kn5000-roms-disasm
make all                              # build everything + compare
python3 scripts/build/compare_roms.py # compare only
make verify-demo-presets              # 19/19
make verify-help-databases            # 6/6
```

**History:** the project originally used ASL (Alfred Arnold's Macro Assembler), which only
supported TMP96C141 — requiring 110+ workaround macros for TMP94C241F-specific
instructions. The LLVM backend was developed to encode all TLCS-900/H2 instructions
natively. ASL sources are archived in `archive/asl/` and are still built and verified.

## Source Organisation

Each firmware version has its own tree (`v7/`, `v9/`, `v10/` for the maincpu; `v142/` for
the sub-CPU payload), with `shared/` modules included by more than one ROM. Current
measured sizes:

| Tree | `.s` files | Lines | Symbols in reference file |
|------|-----------:|------:|--------------------------:|
| `v10/maincpu` | 155 | 467,674 | 39,231 |
| `v9/maincpu` | 155 | 467,666 | *(shares the maincpu reference)* |
| `v7/maincpu` | 155 | 337,153 | *(shares the maincpu reference)* |
| `v142/subcpu` | 5 | 69,520 | 4,326 |
| `subcpu/boot` | 1 | 100,869 | 53 |
| `hdae5000` | 7 | 78,359 | 223 |
| `table_data` | 26 | 79,177 | 4,153 |
| `custom_data` | 1 | 146 | — |

The per-file breakdown lives on the [Source Code Map]({{ site.baseurl }}/source-map/) page.

**Subsystem entry points (main CPU):**

- **FDC** — `storage/fdc_routines.s`: `FDC_COMMAND_DISPATCHER`, per-command handlers,
  `Reset_Floppy_Disk_Controller`, `Check_for_Floppy_Disk_Change`;
  `fdc_constants.s` holds the 0x110000-base I/O addresses, uPD765-compatible command
  codes and status-bit definitions.
- **MIDI / encoders** — `midi/midi_encoder_routines.s`: `CPanel_EncoderDispatch`,
  `Encoder_ProcessModwheel` / `Volume` / `Breath` / `Foot` / `Expression`.
- **Control panel** — `ui/cpanel_routines.s`: serial state machine (`CPanel_SM_*`),
  packet processors (`CPanel_RX_*`), LED control, buffer management.
- **SysEx** — `midi/sysex_routines.s`: `ExcSendFunc`, `ExcPmemFunc`, `ExcSmemFunc`,
  `ExcCompFunc`, `ExcSeqFunc`, `ExcMspFunc`.
- **Feature demo** — `demo/demo_routines.s`, `demo/fdemotext_routines.s`.
- **Computer interface** — `midi/computer_interface_config.s`,
  `midi/computer_interface_pcg.s`.
- **File I/O** — `file_io/`: title handlers, disk operations, filename/password UI,
  composer filters, SMF operations, wallpaper loading, single load, medley, misc UI.
- **GUI constants** — `gui_constants.s`: display dirty flags (0x0205E4), offscreen buffer
  addresses (0x043C00, 0x056800, 0x05FE00, 0x069400), 320×240 @ 8bpp.

## Sub CPU Boot ROM

The 128 KB sub-CPU boot ROM rebuilds at 100.00%. Routines identified include the tone
generator init loop (`SUB_8437`), register-pair writers, `COPY_WORDS`/`FILL_WORDS`,
`CHECKSUM_CALC`, the inter-CPU handler set, and the debug/diagnostic tail at 0xFFFE80.

**DMA transfer routines (0xFF8604–0xFF881E):**

| Routine | Address | Size | Description |
|---------|---------|------|-------------|
| `SendData_Chunked` | 0xFF8604 | 69 bytes | Send data in 32-byte chunks via DMA |
| `SendData_Block` | 0xFF8649 | 99 bytes | Send single data block via DMA |
| `SendCmd_E3` | 0xFF86AC | 48 bytes | Send E3 (payload ready) command |
| `SendParams_E2` | 0xFF86DC | 112 bytes | Wait for DMA, then send E2 command |
| `TwoPhase_Transfer` | 0xFF874C | 211 bytes | Two-phase DMA with E1 command, 200-cycle delays |

Still open here: `subcpu_boot_data_8000.bin` (656 bytes at 0xFF8000) is a mixed
code/data blob that code references at six or more internal addresses; it needs to be
split and its 8-entry dispatch table emitted as symbolic `.long`s.

## Table Data ROM

The table-data ROM holds the first-stage bootloader plus almost all factory data. See
[Table Data ROM]({{ site.baseurl }}/table-data-rom/) for the region-by-region reference
and [Memory Map]({{ site.baseurl }}/memory-map/) for the current layout.

**First-stage bootloader (0x9FB496–0x9FFFFF).** All of it is now symbolic assembly. At
reset the table-data ROM is mapped at 0xE00000–0xFFFFFF, so ROM address 0x9Fxxxx executes
at boot-time alias 0xFFxxxx (+0x600000) until `Boot_Init` reprograms the memory
controller. Source labels are at ROM addresses; the 0xFFxxxx aliases appear in comments,
and the handful of `CALL`-absolute sites that must stay numeric are marked as such.

| Component | Address range | Module |
|-----------|---------------|--------|
| FDC dispatch offset tables | 0x9FB496–0x9FB4D1 | `kn5000_table_data.s` (three tables) |
| `Boot_BitMaskTable` + `Boot_InitParams` | 0x9FB4D2–0x9FB4E7 | `kn5000_table_data.s` |
| `Boot_Init`, halt handler, `Boot_ClearRAM` | 0x9FB4E8–0x9FB7F1 | `kn5000_table_data.s`, `shared/` |
| HDAE5000 boot-flash tail | 0x9FC6F6–0x9FC8C1 | `kn5000_table_data.s` (was `bootcode_hdae_to_lzss.bin`) |
| LZSS decoder suite | 0x9FC8C2–0x9FCC29 | `kn5000_table_data.s` (872 bytes, five routines) |
| FDC command-layer driver | 0x9FD8A5–0x9FEA9C | `boot_fdc_driver.s` |
| Disk-format probe | 0x9FEB2B–0x9FEC6D | `boot_disk_probe.s` |
| CP-serial driver (polling half) | 0x9FEC6E–0x9FF228 | `boot_cpserial.s` |
| CP-serial ISRs | 0x9FF229–0x9FF2F1 | `boot_cpserial_isr.s` |
| CP-serial state handlers/codecs | 0x9FF2F2–0x9FFB2E | `boot_cpserial_states.s` |
| Boot C runtime | 0x9FFB2F–0x9FFE7F | `boot_clib.s` |
| Debug group (disabled) | 0x9FFE80–0x9FFEDF | `boot_debug.s` |
| `RESET_HANDLER` + IVT | 0x9FFEE0–0x9FFFFF | `kn5000_table_data.s` |

The LZSS decoder is SLIDE4K (4 KB sliding window, 12-bit offset, 4-bit length) and is
invoked during flash firmware updates:

| Routine | Address | Size | Purpose |
|---------|---------|------|---------|
| `LZSS_ReadByte` | 0x9FC8C2 | 115 bytes | Read from compressed stream with sector buffering |
| `LZSS_OutputByte` | 0x9FC935 | 63 bytes | Write decompressed bytes with 32-bit batching |
| `LZSS_OutputByte_Alt` | 0x9FC974 | 63 bytes | Alternative output for flash update mode |
| `LZSS_ParseHeader` | 0x9FC9B3 | 157 bytes | Parse/validate firmware header, set up source |
| `LZSS_Decompress` | 0x9FCA50 | 474 bytes | Main decompression loop with sliding window |

(The 4 KB/8 KB *variant* dispatch lives in the main-CPU firmware, not here — see the help
database note above.)

**System update bitmaps (shared with the main CPU).** Eight 1-bit monochrome images
(224×22 px, 616 bytes each) at 0x9FA156, byte-identical to the main-CPU copies; both ROMs
`.incbin` the same files.

| Address | Image |
|---------|-------|
| 0x9FA156 | Flash Memory Update |
| 0x9FA3BE | Now Erasing |
| 0x9FA626 | FD to Flash Memory |
| 0x9FA88E | Completed |
| 0x9FAAF6 | Please Wait |
| 0x9FAD5E | Change FD 2 of 2 |
| 0x9FAFC6 | Illegal Disk |
| 0x9FB22E | Turn On AGAIN |

**Key discovery (still valid):** the interrupt vector table holds boot-time addresses
(0xFFxxxx) precisely because of the reset-time mapping described above.

### Shared source with the Main CPU

Several bootloader routines are byte-identical or semantically identical to main-CPU
utilities — both ROMs were built from common source. The disassembly now uses real shared
modules in `shared/`:

| File | Description |
|------|-------------|
| `shared/vga_constants.s` | VGA register addresses and constants |
| `shared/vga_init.s` | VGA initialization data + completion code |
| `shared/vga_io.s` | VGA register I/O routines (byte-identical between ROMs) |
| `shared/boot_call_init_handlers.s` | Init handler dispatch (conditional assembly) |
| `shared/boot_routines.s` | Boot initialization routines + LZSS decoder |
| `shared/macros.s`, `shared/sfr_tmp94c241.s` | Macros and SFR definitions |

**Shared routine mapping:**

| Table Data | Main CPU | Size | Routine |
|------------|----------|------|---------|
| 0x9FCDFC-0x9FCE1D | 0xEF5141-0xEF515F | 30-34 bytes | `Write_VGA_Register`, `Read_VGA_Register` |
| 0x9FB70A-0x9FB73F | 0xEF086F-0xEF08A3 | 53-54 bytes | `Boot_CallInitHandlers` |
| 0x9FCD9A-0x9FD7BD | 0xEF50DF-0xEF5B02 | 2,596 bytes | `VRAM_FillRect` and display routines |
| 0x9FBC3C-0x9FBECF | 0xEF3CE0-0xEF3F73 | 660 bytes | Boot utility routines |
| 0x9FB4F2-0x9FB622 | 0xEF03D0-0xEF0500 | 305 bytes | Boot initialization code |

Where the two ROMs differ in encoding (byte vs word compare, different helper addresses),
conditional assembly handles it — each ROM defines the required parameters before
including the shared file.

## Technical Notes

### TMP94C241F vs TMP96C141

Instructions unique to TMP94C241F that required macro workarounds under ASL:

- Memory-to-memory `LD` (not supported by TLCS-900)
- Certain shift/rotate variants
- Some MUL/DIV variants
- LDI, LDIR, LDD, LDDR block transfer instructions
- DMA control register access (`LDC` with DMAS/DMAD/DMAC/DMAM registers)

The LLVM backend encodes all of these natively; the macro tables below document the
archived ASL mirror, which is still built.

### ASL Macro Workarounds (tmp94c241.inc)

**DMA register macros:**

| Macro | Encoding | Description |
|-------|----------|-------------|
| `LDC_DMAS0_XWA` | `e8 2e 00` | Load DMA source 0 from XWA |
| `LDC_DMAS2_XDE` | `ea 2e 08` | Load DMA source 2 from XDE |
| `LDC_DMAS2_XHL` | `eb 2e 08` | Load DMA source 2 from XHL |
| `LDC_DMAD0_XWA` | `e8 2e 20` | Load DMA destination 0 from XWA |
| `LDC_DMAD0_XBC` | `e9 2e 20` | Load DMA destination 0 from XBC |
| `LDC_DMAD2_XWA` | `e8 2e 28` | Load DMA destination 2 from XWA |
| `LDC_DMAC0_WA` | `d8 2e 40` | Load DMA count 0 from WA |
| `LDC_DMAC0_A` | `c9 2e 42` | Load DMA count 0 from A |
| `LDC_DMAC2_A` | `c9 2e 4a` | Load DMA count 2 from A |
| `LDC_DMAC2_BC` | `d9 2e 48` | Load DMA count 2 from BC |
| `LDC_DMAC2_WA` | `d8 2e 48` | Load DMA count 2 from WA |

**Additional sub CPU boot ROM macros:**

| Macro | Encoding | Description |
|-------|----------|-------------|
| `INC_0_XBC` | `e9 60` | Increment XBC by 1 |
| `PUSH_WORD value` | `0b LL HH` | Push 16-bit immediate |
| `CP_pXWA_WORD value` | `90 3f LL HH` | Compare (XWA) with 16-bit immediate |
| `CP_pXBC_d_WORD d,val` | `99 dd 3f LL HH` | Compare (XBC+d) with 16-bit immediate |
| `LDA_XWA_IMM24 value` | `f2 LL MM HH 30` | Load 24-bit address into XWA |
| `CALR target` | `1e LL HH` | Call relative (3-byte encoding) |
| `CALL_ABS24 target` | `1d LL MM HH` | Call absolute with 24-bit address |
| `JRL_T target` | `78 LL HH` | Jump relative long (always true) |
| `LDIR_94` | `83 11` | Block copy (TMP94C241 encoding) |
| `LD_A value` | `21 nn` | Load immediate to A register |
| `LD_D value` | `24 nn` | Load immediate to D register |
| `LD_E value` | `25 nn` | Load immediate to E register |
| `LD_L value` | `27 nn` | Load immediate to L register |
| `LD_W value` | `20 nn` | Load immediate to W register |
| `LD_pXIX_IMM16 value` | `b4 02 LL HH` | Store 16-bit imm to (XIX) |
| `LD_pXHL_IMM16 value` | `b3 02 LL HH` | Store 16-bit imm to (XHL) |
| `LD_MEM24_IMM16 addr,val` | `f2 LL MM HH 02 VV WW` | Store 16-bit to 24-bit addr |

**Stack frame and register macros (DMA routines):**

| Macro | Encoding | Description |
|-------|----------|-------------|
| `DEC_6_XSP` | `ef 6e` | Decrement XSP by 6 (allocate stack frame) |
| `INC_6_XSP` | `ef 66` | Increment XSP by 6 (deallocate stack frame) |
| `LD_IZ_BC` | `d9 8e` | Load IZ from BC |
| `CP_IZ_imm16 val` | `de cf LL HH` | Compare IZ with 16-bit immediate |
| `SUB_IZ_imm16 val` | `de ca LL HH` | Subtract 16-bit immediate from IZ |
| `LD_C_IZL` | `c7 f8 8b` | Load C from low byte of IZ |
| `EXTZ_WA` | `d8 12` | Zero-extend A to WA |
| `EXTZ_BC` | `d9 12` | Zero-extend C to BC |

**Stack-relative addressing macros:**

| Macro | Encoding | Description |
|-------|----------|-------------|
| `LD_A_pXSP_d disp` | `8f dd 21` | Load A from (XSP+disp) |
| `LD_XDE_pXSP_d disp` | `af dd 22` | Load XDE from (XSP+disp) |
| `LD_XBC_pXSP_d disp` | `af dd 21` | Load XBC from (XSP+disp) |
| `LD_pXSP_d_A disp` | `bf dd 41` | Store A to (XSP+disp) |
| `LD_pXSP_d_XDE disp` | `bf dd 62` | Store XDE to (XSP+disp) |
| `ADD_pXSP_d_XWA disp` | `af dd 88` | Add XWA to (XSP+disp) |

### Encoding Differences

ASL sometimes chooses different (but functionally equivalent) encodings than the original ROM:

| Instruction | Original | ASL Default | Notes |
|-------------|----------|-------------|-------|
| `lda XWA, imm16` | 5-byte (24-bit addr) | 4-byte (16-bit) | Use `LDA_XWA_IMM24` macro |
| `call addr` | 3-byte `calr` | 4-byte `call` | Use `CALR` macro when target is within range |
| `jp addr` | 3-byte `jrl T` | 4-byte `jp` | Use `JRL_T` macro for relative long jump |
| `ldir` | `83 11` | `85 11` | Use `LDIR_94` macro for TMP94C241 encoding |
| `ld A, imm8` | `21 nn` | Different | Use `LD_A` macro |
| `ld D, imm8` | `24 nn` | Different | Use `LD_D` macro |

## Earlier Milestones

### March 2026: complete `LABEL_XXXXXX` elimination

Every address-based placeholder label was analysed and renamed to a descriptive name —
roughly 10,000 labels across the main-CPU sources alone, with zero `LABEL_XXXXXX`
remaining in any ROM directory. All renames were verified with a full
`make clean && make all` + `compare_roms.py`.

### March 2026: raw-byte code elimination

All executable code across the ROM set uses native TLCS-900 mnemonics; no code remains as
`.byte` sequences. Remaining `.byte` directives are data — tables, strings, bitmaps,
interpreter bytecode and padding. See
[Raw Byte Code Elimination]({{ site.baseurl }}/raw-byte-code-elimination/).

### March 2026: C struct conversion, R+d16 addressing, waveform ROM

15 sound-data files in `audio/sound_data/` were converted from raw byte arrays to typed C
structs with named fields and `_Static_assert` size checks; 357 `R+d16` `.byte` fallbacks
became native mnemonics once the LLVM backend gained SRI-prefix support; all 26 NAKA
widget C files moved to named-struct format with symbol-resolved pointer tables; and the
IC307 waveform ROM format was decoded (16-bit signed PCM at 32 kHz, 512-entry sample
table). See [Waveform ROM Format]({{ site.baseurl }}/waveform-rom-format/).

### Binary include splitting policy

Binary includes are split whenever code references an address inside them, so that
cross-references use symbolic labels instead of hardcoded addresses and structure
boundaries are explicit. Since the August 2026 waves the rule is stronger: a slice must
also carry a label, a length and a comment saying what it holds — an unnamed whole-file
`.incbin` is treated as an unfinished conversion.
