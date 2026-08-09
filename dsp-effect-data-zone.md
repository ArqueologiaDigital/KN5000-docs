---
layout: page
title: DSP Effect Data Zone (Sub-CPU ROM)
permalink: /dsp-effect-data-zone/
---

# DSP Effect Data Zone (Sub-CPU ROM)

The Sub-CPU payload (`kn5000_subprogram_v142.rom`) carries a 39,372-byte data zone at
Sub-CPU addresses **0x0147B3-0x01E17E** holding the complete per-effect upload material
for all 100 effect-algorithm numbers: the DSP microprogram/coefficient **bytecode
streams** and the runtime **parameter record tables**. This page documents the zone's
layout and grammars, as carved in `v142/subcpu/subcpu_data_tables.s` (every block is
individually labeled; the reconstruction is byte-identical).

Companion pages: [Effects DSP (NEC uPD6383GF)]({{ site.baseurl }}/effects-dsp/) for the
DSP chip itself, [DSP Bytecode Interpreter]({{ site.baseurl }}/dsp-bytecode-interpreter/)
for the Sub-CPU-side interpreter that consumes this zone, and
[DSP Name Tables (Main CPU)]({{ site.baseurl }}/dsp-name-tables/) for the main-CPU tables
that supply the effect and parameter *names* quoted throughout this page.

## Indexing: four parallel pointer arrays

Everything is reached through four 100-entry `u32` arrays indexed by effect number
0..99 (Sub-CPU addresses; they live just after the zone):

| array | address | consumer |
|-------|---------|----------|
| algorithm bytecode | `0x01ED7C` | `EFF_Change_WithDebug` -> `DSP_WriteEFFConfig` -> `DSP_BytecodeInterpreter_Init` |
| coefficient bytecode | `0x01EF0C` | same path, uploaded after the algorithm |
| parameter VALUE tables | `0x01F09C` | `DSP_WriteParam_Generic` -> `DSP_ParameterWriteEngine` |
| parameter DESCRIPTOR tables | `0x01F22C` | passed in XDE to `DSP_ParameterWriteEngine` |

Slot-1 effects 9/10 bypass the arrays with hard-coded streams (`DSP_Eff09_Slot1_*`,
`0x01E1DE`/`0x01E342`) and the fixed `DSP_Eff9_*`/`DSP_EffA_*` pairs after the zone.

## Grammar 1: bytecode streams

A stream is a sequence of variable-length instructions `[b0, b1, payload...]`:

* opcode = `b0 >> 4`; total length (header included) = `((b0 & 0x0F) << 8) | b1`
* opcodes 0-5 dispatch through the word-offset table at `0x014739` into six upload
  handlers (I-RAM / C-RAM group writes); `0xD` = SPI bus-idle + task yield; `0xE` =
  payload[0] as COMMAND, rest as DATA words
* the stream ends when the *peeked* next byte has high nibble `0xF`

## Grammar 2: parameter record tables

A table is a run of records `[len_hi, len_lo, id, payload...]` (big-endian length counts
the whole record; a first byte of `0xF0` is the end-of-table sentinel).

* **Value records** are translator opstreams ending `0x7A`: the id byte is dispatched as
  an opcode (`0x21`/`0x24`/`0x40` have dedicated arms, `0x61..0x79` go through the offset
  table at `0x014745`), then `{ id, field-index, curve operands }` repeat until `0x7A`.
* **Descriptor records** with the same id list the DSP register (cell) numbers the value
  stream's field-index bytes select.

Settled translator-opcode semantics (measured; `kn7000_mame/tools/kn5000_dsp_params.py`):

| op | semantics |
|----|-----------|
| `0x21` | lerp `0x000000..0x666666` = 0..0.8 full scale -> cell `0x90` (universal tail level) |
| `0x62` | CURVE_D volume law, 1.00 dB per UI step |
| `0x63` | A/B/C curve select -> cell `0x06` (second tail level) |
| `0x68` | ms x 44100 / 1000 -> DRAM word count (delay times; the 44.1 kHz rate is hard-coded) |
| `0x69` | value / 180 -> degrees (PHASE / PAN family) |
| `0x6D` | descriptor `+8` pair (compressor attack/release smoother coefficients) |
| `0x70` | parametric-EQ biquad coefficient + state block (5 bands) |
| `0x72` | compressor THRESHOLD (`0x04`) / RATIO (`0x0D`) cells |

The UI value range is 0..99 (lerp divisor `0x63`); the 100-entry curve tables
CURVE_A/B/C/D sit at `0x012483`/`0x012613`/`0x0127A3`/`0x012B33`. Those names are the
kn7000_mame tooling's; the assembly source labels them `DSP_FreqParamCurve_Algo0`
(`0x012483`), `DSP_FreqParamCurve_Algo1` (`0x012613`), `DSP_FreqParamCurve_Algo2`
(`0x0127A3`), `DSP_OscParamCurve` (`0x0129A3`) and `DSP_CoeffCurve_Op62` (`0x012B33`) —
five ladders, not four; the CURVE_x scheme skips `0x0129A3` entirely. The user-facing
parameter *names* live on the **main CPU**: an 86-slot × 17-byte name table at ROM
`0xE324C4` (file offset `0x0324C4`) with its 86-slot × 2-byte unit table at `0xE32418`
(`0x032418`), both now carved and labelled in source — see
[DSP Name Tables (Main CPU)]({{ site.baseurl }}/dsp-name-tables/). *(Earlier revisions of
this page gave `0x0324D5` / `0x03241A` and a count of 85; those addresses are slot **1**
of each table. Slot 0 and slot 85 are blank spares.)* The per-effect ordered name list
was captured live per effect
(`kn7000_mame/notes/kn5000-dsp-paramlist.md`) and is quoted in the per-effect banners of
`subcpu_data_tables.s`. The two trailing UI controls of every effect are VOLUME and
REV SEND, landing on cells `0x90`/`0x06` (which is which is not forced by record order).

## Chip partition: uPD6383 (IC311) vs MN19413 (IC310)

Nine effect numbers are **IC310 (MN19413, the second DSP)** programs: 57 STANDARD,
58 PERCUSSIVE, 59 SYMPHONIC, 60 DEEP SPACE (the ACOUSTIC ILLUSION types), 79 GEQ,
88 ROOM, 89 KARAOKE, 90 BATH ROOM, 91 STAGE. Their streams carry command-`0x30` records
(`dsp/analysis/second-dsp-and-ready.md` B1, proven by construction, and re-derived
independently during the carve enrichment). Their labels carry the **`DSP2_` prefix**;
their descriptor bytes are IC310 parameter-word addresses, *not* uPD6383 cell numbers.
Do not feed them to a uPD6383-shaped parser.

## The stub set

42 effect numbers point all three of algorithm/coefficient/descriptor at one shared
**NO OPERATION** trio (`DSP_Eff00_Algo_Bytecode` `0x017263` / `DSP_Eff00_Coef_Bytecode`
`0x01735E` / `DSP_Eff00_Param_Descriptors` `0x017425`) -- a dry pass-through program
(it still runs a level detector). Those 42 are 40 pure stubs plus two special cases:
effect 0, which *owns* the trio, and effect 37, which owns a parameter-value table but no
program of its own. The main-CPU name table now counts the same partition from the other
side -- 60 of the 100 effect numbers carry a cross-reference to at least one Sub-CPU
block, the other 40 are marked stubs (see
[DSP Name Tables (Main CPU)]({{ site.baseurl }}/dsp-name-tables/)).
Besides the `----------` placeholders, **twelve named
effects are stubs**: 11 MODULATION DELAY, 37 SLOW ATTACKER, 38 NOISE FLANGER, 44 CEL,
45 CELM, 49 PITCH SHIFTER, 51 PEDAL WAH, 55 HARS EFFECT, 63 STRING,
69 PEDAL WAH+DELAY, 80 DS_D, 81 OVER_D. Verified from the ROM: all twelve share the trio
by pointer identity and no second byte-identical copy of the program exists in the zone.

Effect **37 SLOW ATTACKER** is the curious one: it has its *own* live parameter value
table (`DSP_Eff37_Param_Values`, `0x0173F2`, and a real 5-slot UI page:
THRESHOLD / ATTACK RATE / RELEASE RATE / VOLUME / REV SEND) -- but the parameter writes
land on the dry pass-through program. Worth trying on real hardware.

## Effect record map

Named effects only (the 29 unnamed `----------` placeholders all share the stub trio and
are omitted). Addresses are Sub-CPU payload addresses. **Bold** = IC310 (MN19413).

| # | effect | algo bytecode | coef bytecode | param values | param descr | chip |
|---|--------|---------------|---------------|--------------|-------------|------|
| 0 | NO OPERATION *(stub)* | `0x017263` | `0x01735E` | `--` | `0x017425` | IC311 |
| 1 | CHORUS | `0x0153C1` | `0x015525` | `0x01561A` | `0x01564B` | IC311 |
| 2 | MODULATED CHORUS | `0x015664` | `0x015813` | `0x01591F` | `0x015969` | IC311 |
| 3 | ENHANCER | `0x015986` | `0x015B7B` | `0x015CD8` | `0x015D1B` | IC311 |
| 4 | FLANGER | `0x015D43` | `0x015E8E` | `0x015F6C` | `0x015FD3` | IC311 |
| 5 | PHASER | `0x015FFE` | `0x016216` | `0x01633B` | `0x0163A2` | IC311 |
| 6 | ENSEMBLE | `0x0177C3` | `0x0179A9` | `0x017A92` | `0x017AE3` | IC311 |
| 8 | GATED REVERB | `0x01743B` | `0x01763F` | `0x01776C` | `0x01779F` | IC311 |
| 9 | SINGLE DELAY | `0x017F1F` | `0x018015` | `0x0180D0` | `0x01811E` | IC311 |
| 10 | MULTI TAP DELAY | `0x018141` | `0x01829B` | `0x018359` | `0x0183CE` | IC311 |
| 11 | MODULATION DELAY *(stub)* | `0x017263` | `0x01735E` | `--` | `0x017425` | IC311 |
| 15 | ROCK ROTARY | `0x016ACF` | `0x016EAF` | `0x017044` | `0x016E85` | IC311 |
| 16 | ROOM REVERB 1 | `0x01C701` | `0x01C9A0` | `0x01CB3C` | `0x01CB72` | IC311 |
| 17 | ROOM REVERB 2 | `0x01C701` | `0x01CB9C` | `0x01CD38` | `0x01CB72` | IC311 |
| 18 | PLATE REVERB 1 | `0x01C701` | `0x01CD6E` | `0x01CF0A` | `0x01CB72` | IC311 |
| 19 | PLATE REVERB 2 | `0x01C701` | `0x01CF40` | `0x01D0DC` | `0x01CB72` | IC311 |
| 20 | CONCERT REVERB 1 | `0x01C701` | `0x01D112` | `0x01D2AE` | `0x01CB72` | IC311 |
| 21 | CONCERT REVERB 2 | `0x01C701` | `0x01D2E4` | `0x01D480` | `0x01CB72` | IC311 |
| 22 | DARK REVERB 1 | `0x01C701` | `0x01D4B6` | `0x01D652` | `0x01CB72` | IC311 |
| 23 | DARK REVERB 2 | `0x01C701` | `0x01D688` | `0x01D824` | `0x01CB72` | IC311 |
| 24 | BRIGHT REVERB 1 | `0x01C701` | `0x01D85A` | `0x01D9F6` | `0x01CB72` | IC311 |
| 25 | BRIGHT REVERB 2 | `0x01C701` | `0x01DA2C` | `0x01DBCB` | `0x01CB72` | IC311 |
| 26 | WAVE REVERB 1 | `0x01C701` | `0x01DC01` | `0x01DD9D` | `0x01CB72` | IC311 |
| 27 | WAVE REVERB 2 | `0x01C701` | `0x01DDD3` | `0x01DF6F` | `0x01CB72` | IC311 |
| 32 | DISTORTION | `0x0147EF` | `0x0148C7` | `0x014927` | `0x01494D` | IC311 |
| 33 | OVERDRIVE | `0x014967` | `0x014AA8` | `0x014B59` | `0x014B7F` | IC311 |
| 34 | FUZZ | `0x014B99` | `0x014C71` | `0x014CD1` | `0x014CF7` | IC311 |
| 35 | EXCITER | `0x014D11` | `0x014E70` | `0x014F2D` | `0x014F6F` | IC311 |
| 36 | COMPRESSOR | `0x017B00` | `0x017BCE` | `0x017C61` | `0x017C93` | IC311 |
| 37 | SLOW ATTACKER *(stub)* | `0x017263` | `0x01735E` | `0x0173F2` | `0x017425` | IC311 |
| 38 | NOISE FLANGER *(stub)* | `0x017263` | `0x01735E` | `--` | `0x017425` | IC311 |
| 39 | PARAMETRIC EQ | `0x014F93` | `0x0151A6` | `0x01533F` | `0x0153AB` | IC311 |
| 44 | CEL *(stub)* | `0x017263` | `0x01735E` | `--` | `0x017425` | IC311 |
| 45 | CELM *(stub)* | `0x017263` | `0x01735E` | `--` | `0x017425` | IC311 |
| 48 | AUTO PAN | `0x0163C8` | `0x0164C8` | `0x016547` | `0x016588` | IC311 |
| 49 | PITCH SHIFTER *(stub)* | `0x017263` | `0x01735E` | `--` | `0x017425` | IC311 |
| 50 | VIBRATO | `0x0165A7` | `0x0166B6` | `0x016773` | `0x0167B4` | IC311 |
| 51 | PEDAL WAH *(stub)* | `0x017263` | `0x01735E` | `--` | `0x017425` | IC311 |
| 52 | AUTO WAH | `0x0167D3` | `0x016941` | `0x016A18` | `0x016AB1` | IC311 |
| 53 | ROTARY SPEAKER | `0x016ACF` | `0x016C83` | `0x016E18` | `0x016E85` | IC311 |
| 54 | RING MODULATOR | `0x0170B1` | `0x01719D` | `0x01721B` | `0x017249` | IC311 |
| 55 | HARS EFFECT *(stub)* | `0x017263` | `0x01735E` | `--` | `0x017425` | IC311 |
| 56 | MIX UP | `0x017CA8` | `0x017DEE` | `0x017EB4` | `0x017EFE` | IC311 |
| 57 | **STANDARD** | `0x0183F5` | `0x0186C1` | `0x0187C4` | `0x018806` | IC310 |
| 58 | **PERCUSSIVE** | `0x0183F5` | `0x018815` | `0x018918` | `0x018806` | IC310 |
| 59 | **SYMPHONIC** | `0x0183F5` | `0x01895A` | `0x018A5D` | `0x018806` | IC310 |
| 60 | **DEEP SPACE** | `0x0183F5` | `0x018A9F` | `0x018BA2` | `0x018806` | IC310 |
| 63 | STRING *(stub)* | `0x017263` | `0x01735E` | `--` | `0x017425` | IC311 |
| 64 | S.DELAY+CHORUS | `0x01925D` | `0x01943E` | `0x01956C` | `0x0195E9` | IC311 |
| 65 | S.DELAY+S.DELAY | `0x019610` | `0x01976A` | `0x019833` | `0x0198B7` | IC311 |
| 66 | S.DELAY+FLANGER | `0x0198E0` | `0x019ADA` | `0x019BF9` | `0x019CAC` | IC311 |
| 67 | S.DELAY+VIBRATO | `0x019CE4` | `0x019E98` | `0x019F96` | `0x01A010` | IC311 |
| 68 | S.DELAY+PHASER | `0x01A03F` | `0x01A26B` | `0x01A399` | `0x01A44C` | IC311 |
| 69 | PEDAL WAH+DELAY *(stub)* | `0x017263` | `0x01735E` | `--` | `0x017425` | IC311 |
| 70 | AUTO WAH+S.DELAY | `0x01A47D` | `0x01A690` | `0x01A7A7` | `0x01A879` | IC311 |
| 71 | PEQ+CHORUS | `0x01A8A3` | `0x01AA7A` | `0x01ABD2` | `0x01AC34` | IC311 |
| 72 | PEQ+S.DELAY | `0x01AC54` | `0x01AD68` | `0x01AE42` | `0x01AEA8` | IC311 |
| 73 | PEQ+FLANGER | `0x01AECE` | `0x01B09B` | `0x01B1D8` | `0x01B26D` | IC311 |
| 74 | PEQ+VIBRATO | `0x01B29F` | `0x01B426` | `0x01B530` | `0x01B58C` | IC311 |
| 75 | PEQ+COMPRESSOR | `0x01B5B2` | `0x01B6DF` | `0x01B7E4` | `0x01B831` | IC311 |
| 79 | **GEQ** | `0x018BE4` | `0x018CDC` | `0x018D18` | `0x018D4F` | IC310 |
| 80 | DS_D *(stub)* | `0x017263` | `0x01735E` | `--` | `0x017425` | IC311 |
| 81 | OVER_D *(stub)* | `0x017263` | `0x01735E` | `--` | `0x017425` | IC311 |
| 88 | **ROOM** | `0x018D5E` | `0x018FFA` | `0x019067` | `0x01908E` | IC310 |
| 89 | **KARAOKE** | `0x018D5E` | `0x0190A1` | `0x01910E` | `0x01908E` | IC310 |
| 90 | **BATH ROOM** | `0x018D5E` | `0x019135` | `0x0191A2` | `0x01908E` | IC310 |
| 91 | **STAGE** | `0x018D5E` | `0x0191C9` | `0x019236` | `0x01908E` | IC310 |
| 96 | PEQ+COMPR+DIST | `0x01B852` | `0x01BA1A` | `0x01BB32` | `0x01BB9A` | IC311 |
| 97 | PEQ+COMPR+OVERDR | `0x01BBC5` | `0x01BDB0` | `0x01BEF3` | `0x01BF59` | IC311 |
| 98 | PEQ+DIST+DELAY | `0x01BF84` | `0x01C156` | `0x01C248` | `0x01C2C2` | IC311 |
| 99 | PEQ+OVERDR+DELAY | `0x01C2F4` | `0x01C502` | `0x01C652` | `0x01C6CF` | IC311 |

Shared blocks: the 12 reverb presets (16-27) share one microprogram and one descriptor
table; 15/53 share the rotary microprogram and descriptors; 57-60 and 88-91 each share
one IC310 microprogram and descriptor table; all stubs share the NO OPERATION trio.

## Provenance

* Carve + labels: `v142/subcpu/subcpu_data_tables.s` (zone header documents both
  grammars; per-effect banners quote the captured UI parameter lists).
* Grammar recovered from the dispatch code in `v142/subcpu/kn5000_subprogram_v142.s`
  (`DSP_BytecodeInterpreter_Loop`, `DSP_TableWalk_Search`, `DSP_ParameterWriteEngine`,
  `DSP_PerParameterTranslator`).
* Effect names: main CPU `DspEffectName_PtrTable` (`0xE32A7A`), whose entry *n* is
  `0xE33568 - 18*n` — ROM file offset `0x033568 - 18*n`, stride 18 descending. Now carved
  in source: [DSP Name Tables (Main CPU)]({{ site.baseurl }}/dsp-name-tables/).
* UI parameter lists: measured live (`kn7000_mame/notes/kn5000-dsp-paramlist.md`).
* IC310 partition: `dsp/analysis/second-dsp-and-ready.md` finding B1.
