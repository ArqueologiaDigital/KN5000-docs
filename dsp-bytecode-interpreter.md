---
layout: page
title: DSP Bytecode Interpreter
permalink: /dsp-bytecode-interpreter/
---

# DSP Bytecode Interpreter

The KN5000's dual DSP chips (IC310 MN19413 and IC311 NEC uPD6383GF) are programmed via a two-level bytecode interpreter running on the SubCPU. This page documents the interpreter architecture, opcodes, and register write protocol.

> **Status:** Architecture and opcode tables decoded from SubCPU firmware. Register-to-effect parameter mapping still incomplete.

> **Note:** This page predates the identification of IC311. It formerly called the chip
> "DS3613GF-3BA, a custom ASIC" — that was a transcription error; the part is the **NEC
> uPD6383GF-3BA**. Everything below about the *SubCPU-side* interpreter remains valid; for
> the DSP chip's own architecture, instruction word, decoded algorithms and the full
> effect/parameter catalogue, see the newer
> [Effects DSP (NEC uPD6383GF)]({{ site.baseurl }}/effects-dsp/) page.

## Architecture

The interpreter has two levels:

### Level 1 — Low-level Bytecode Interpreter

- **Entry:** `DSP_BytecodeInterpreter_Init` (subcpu line 42289)
- **Called by:** `DSP_WriteGlobalConfig` and `DSP_WriteEFFConfig`
- **Programs:** Stored in SubCPU DRAM (loaded from maincpu payload at boot)
- **Format:** 2 bytes per opcode — high nibble = opcode, remaining 12 bits = count field

### Level 2 — Translator (Parameter Descriptor Engine)

- **Entry:** `DSP_Translator_ReadOpcode` (subcpu line 42786)
- **Called by:** `DSP_ParameterWriteEngine` (subcpu line 42654)
- **Programs:** Parameter descriptors from maincpu program ROM (pointer table at 0xEE75F6)
- **Format:** Single-byte opcodes (0x61-0x78), each followed by variable parameter data

### Dispatch Router

`DSP_DispatchCommand(wa=cmd_byte, bc=chip_id)` routes to DSP1 (chip=0, parallel bus) or DSP2 (chip=1, SPI serial). `DSP_DispatchData` similarly routes data bytes.

## Level 1 Opcodes (Low-level)

| Opcode | Handler | Description |
|--------|---------|-------------|
| 0x0N | Handler 0 | CMD + preamble + groups-of-5 (3-way branch: 0x00=static, 0x0A=raw, else=param-modified) |
| 0x1N | Handler 1 | CMD + preamble + groups-of-5 (12-bit address computation) |
| 0x2N | Handler 2 | CMD + preamble + groups-of-3 (pure raw data writes) |
| 0x3N | Handler 3 | CMD + 16-bit address + raw tail |
| 0x4N | Handler 4 | Single command byte only |
| 0x5N | Handler 5 | CMD + preamble + groups-of-5 (variant with IZH mask) |
| 0x0D | Op0D | SPI bus idle + state change notification |
| 0x0E | Op0E | DispatchCommand + DispatchData loop (register write) |
| 0xFN | End | Terminate program |

Handler dispatch table: `OFFSETS_14739` (6 entries in `subcpu_data_tables.s`). Handler code: 1,613 bytes of embedded machine code at `DSP_Bytecode_Programs` (line 42404).

## Level 2 Opcodes (Translator)

| Opcode | Handler | Output | Purpose |
|--------|---------|--------|---------|
| 0x21 | ParamInterp_2Point | WriteOscParam | 2-point linear interpolation |
| 0x24 | ParamInterp_MultiStep | WriteOscParam | Multi-step interpolation |
| 0x40 | PanScale_Simple | WriteOscParam | Pan position scaling |
| 0x61 | ParamFetch_SingleTable | WriteOscParam | Direct parameter lookup |
| 0x62 | ParamFetch_AlgoTypeTable | WriteFreqParam_AlgoType | Algorithm-dependent freq param |
| 0x63 | AlgoParam_Decode | WriteOscParam | Algorithm parameter decode |
| 0x64 | PitchParam_Scale | WriteFreqParam | Pitch scaling with freq write |
| 0x65 | VolumeParam_Scale | WriteOscParam | Volume scaling |
| 0x66 | ParamInterp_2Point | WriteOscParam | 2-point interpolation (oscillator) |
| 0x67 | ParamInterp_FPScale | WriteOscParam_Offset | FP scale with offset |
| 0x68 | ParamInterp_Div0xB4 | WriteFreqParam | Frequency interp (divide by 0xB4) |
| 0x69 | VolumeCurve_FP | WriteOscParam | Fixed-point volume curve |
| 0x6A | FreqCurve_FP | WriteFreqParam | Fixed-point frequency curve |
| 0x6B | FreqInterp_2Point | WriteFreqParam | 2-point frequency interp |
| 0x6C | ParamInterp_3Point_WithOffset | WriteFreqParam | 3-point interp with offset |
| 0x6D | ReverbCurve_FP | WriteOscParam | Reverb-specific curve |
| 0x6E | ParamInterp_FPComplex | WriteOscParam | Complex FP interpolation |
| 0x6F | PanCurve_PiecewiseLin | WriteOscParam | Piecewise-linear pan curve |
| 0x70 | BiquadCoeff_Compute | (direct) | Biquad IIR filter coefficient |
| 0x71 | DetuneCurve_SignedFP | WriteOscParam | Signed FP detune curve |
| 0x72 | BiquadWarp_FP | (direct) | Bilinear transform warping |
| 0x73 | ParamInterp_Div0xC6 | WriteOscParam | Interpolation (divide by 0xC6) |
| 0x74 | WriteLUTParamSet | (direct) | Lookup table parameter set |
| 0x75 | ParamEQ_Curve_FP | WriteOscParam | Parametric EQ curve |
| 0x76 | SOS_Coeff_Compute | (direct) | Second-order section coefficient |
| 0x77 | ParamInterp_2Point_B | WriteOscParam | 2-point interp variant B |
| 0x78 | VolScale_B | WriteOscParam | Volume scaling variant B |
| 0x7A | (end) | — | Terminate bytecode block |
| 0xF0 | (separator) | — | Separator between parameter slots |

Translator dispatch table: `OFFSETS_14745` (25 entries in `subcpu_data_tables.s`).

## SPI Protocol (DSP2 Register Writes)

Physical layer: GPIO bit-banging on SubCPU ports.

| Signal | Port | Bit |
|--------|------|-----|
| SDA | Port F (0x3C) | bit 0 |
| SCLK | Port F (0x3C) | bit 2 |
| CS2 | Port E (0x38) | bit 6 |

Each SPI transaction produces **9 SCLK rising edges** (confirmed by `DSP2_Send_Command` at subcpu line 32980).

### CMD 0x30 Register Write Sequence

A register write sends 5 SPI transactions:

1. **Command** 0x30 (register write command)
2. **Data** 0x00 (constant preamble byte)
3. **Data** `register_address` (8-bit DSP register)
4. **Data** `value_high` (MSB of 16-bit value)
5. **Data** `value_low` (LSB of 16-bit value)

### Boot-time Writes

| Register | Value | Purpose |
|----------|-------|---------|
| 0xD0 | 0x0000 | Initialization |
| 0xD3 | 0x0000 | Initialization |
| 0x3C | 0x4000 | Configuration |

## DSP Register Address Space

Registers use a structured addressing scheme:

### Parametric EQ (detected from opcode 0x70 = BiquadCoeff_Compute)

5-band parametric EQ, each band with 3 coefficients:

| Band | Frequency | Q Factor | Gain |
|------|-----------|----------|------|
| 0 | 0x0000 | 0x0010 | 0x0020 |
| 1 | 0x0100 | 0x0110 | 0x0120 |
| 2 | 0x0200 | 0x0210 | 0x0220 |
| 3 | 0x0300 | 0x0310 | 0x0320 |
| 4 | 0x0400 | 0x0410 | 0x0420 |

### Effect Algorithm Types

The firmware supports 12 algorithm types (indices 0-11), dispatched through tables at SubCPU DRAM 0x33812 (`DSP_AlgoType_Dispatch1_TableData`). These correspond to different reverb/chorus/delay/EQ algorithm structures.

Effect configurations are loaded by `DSP_WriteEFFConfig`, which looks up the algorithm type from a table at `0x1ED6D[wa]` and passes it to the bytecode interpreter along with the appropriate bytecode program pointer.

## Key Functions (SubCPU)

| Function | Line | Purpose |
|----------|------|---------|
| `DSP_BytecodeInterpreter_Init` | 42289 | Low-level interpreter entry |
| `DSP_Bytecode_Programs` | 42404 | 1,613 bytes of handler machine code |
| `DSP_ParameterWriteEngine` | 42654 | Translator entry point |
| `DSP_Translator_ReadOpcode` | 42786 | Opcode decode + dispatch |
| `DSP_DispatchCommand` | 34044 | Route command to DSP1/DSP2 |
| `DSP_DispatchData` | — | Route data to DSP1/DSP2 |
| `DSP2_Send_Command` | 32980 | SPI bit-bang: 9 SCLK rising edges |
| `DSP2_SPI_BusIdle` | — | SPI CS deassert + state change |
| `DSP_WriteGlobalConfig` | — | Global config via bytecode |
| `DSP_WriteEFFConfig` | — | Effect config via bytecode (12 algo types) |
| `DSP_WriteParamCmd30` | — | CMD 0x30 register write (5 SPI transactions) |
| `DSP_WriteOscParam` | — | Write oscillator/effect parameter |
| `DSP_WriteFreqParam` | — | Write frequency parameter |

## Related Pages

- [Effects DSP (NEC uPD6383GF)]({{ site.baseurl }}/effects-dsp/) — the IC311 DSP chip itself: architecture, instruction word, decoded algorithms, effect/parameter catalogue
- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) — Overall audio architecture
- [Tone Generator]({{ site.baseurl }}/tone-generator/) — IC303 wavetable synth
