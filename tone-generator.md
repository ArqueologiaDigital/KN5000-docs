---
layout: page
title: Tone Generator
permalink: /tone-generator/
---

# Tone Generator (IC303)

The KN5000's tone generator is a custom Matsushita LSI (TC183C230002, IC303) that provides 64-voice polyphonic wavetable synthesis. It is controlled by the Sub CPU via a register-indirect interface and reads waveform data from four 32Mbit ROMs (IC304-IC307).

> **Status:** Register map reverse-engineered from the SubCPU firmware; the tone generator now **makes
> sound in MAME** — real IC307 PCM, the firmware's software envelope, held-note sustain, per-semitone
> pitch, velocity and polyphony all work (July 2026). Remaining gap: waveform *selection* (every voice
> currently plays one fabricated sine). See [MAME Emulation Status](#mame-emulation-status) below and
> [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) for the overall audio architecture.

## Hardware Overview

| Property | Value |
|----------|-------|
| Chip | TC183C230002 (Matsushita custom) |
| Package Location | IC303 |
| Voice Count | 64 independent voices |
| Parameters per Voice | 32 registers (8 groups × 4 banks, 44-byte firmware struct) |
| Global Registers | 13 (system config + DSP/effects) |
| Interface | Memory-mapped register-indirect (address/data pair) |
| Address Lines | SubCPU memory bus + P6.7 chip-select |
| Waveform ROMs | IC304 (QS6GU3C32375), IC305 (QS6GT3C33A01), IC306 (QS6GU3C32374), IC307 (QS6GX3C32008) |
| Waveform RAM | *(none — see note)* IC303 has **no** external work RAM. IC308/IC309 are the two **effects DSPs'** delay DRAMs and are not connected to IC303 (corrected 2026-07-26 from the service-manual schematics). |

## Memory-Mapped Interface

The tone generator uses two separate memory regions with different purposes:

### Register Configuration Interface (0x100000)

Used by the SubCPU to configure voice parameters, system settings, and effects:

| Address | Width | Direction | Purpose |
|---------|-------|-----------|---------|
| 0x100000 | 16-bit | Write | Register address latch |
| 0x100002 | 16-bit | Write/Read | Register data port |

Every register write follows a strict bus protocol with chip-select timing:

```asm
RES 7, (P6)          ; Assert chip-select (active low)
LD (100000h), WA     ; Write register address
NOP                  ; Setup time
SET 7, (P6)          ; Deassert chip-select (latches address)
LD (100002h), data   ; Write data value
JR T, next           ; Delay (unconditional jump)
NOP; NOP; NOP        ; Hold time before next write
```

P6 bit 7 is the chip-select / address-latch strobe. The address is latched while CS is asserted, then data is written after CS is deasserted.

### Keyboard Input Interface (0x110000)

Used by the SubCPU to read voice events (note on/off) from the tone generator:

| Address | Width | Direction | Purpose |
|---------|-------|-----------|---------|
| 0x110002 | 16-bit | Read | Status register (bit 0 = data ready) |
| 0x110000 | 16-bit | Read | Voice data (low byte = note, high byte = velocity) |

P6.7 (A23 address line) also controls which port is accessed: status reads go to 0x110002, data reads go to 0x110000.

## Register Address Encoding

The 16-bit register address has a structured encoding:

```
Bits 15-8: Register Group (function selector)
Bits  7-6: Sub-bank (0-3, for multi-parameter per-voice registers)
Bits  5-0: Channel number (0-63)
```

This gives up to 256 register groups, each with 4 sub-banks of 64 channels.

## Per-Voice Registers

Each of the 64 voices has registers organized into groups. The register address for voice N is calculated as:
`base_offset + (bank * 0x40) + channel_number`

| Offset | Group | Banks | Struct Offset | Description |
|--------|-------|-------|---------------|-------------|
| +0x0000 | 0x00 | 0 | +0x00 | **Voice Control** -- key on/off/mode state machine |
| +0x0040 | 0x00 | 1 | +0x02 | **Pitch increment** (semitone table lookup from ROM 0x01217D) |
| +0x0080 | 0x00 | 2 | +0x04 | **Voice mode/velocity** (bit 15 = latch strobe; velocity OR'd in) |
| +0x00C0 | 0x00 | 3 | +0x06 | **Waveform control** (cleared on note-off) |
| +0x0100 | 0x01 | 0 | +0x08 | **Interpolated pitch** (16-bit signed, from portamento/legato) |
| +0x0140 | 0x01 | 1 | +0x0A | **Secondary pitch offset** (portamento/detune amount) |
| +0x0180 | 0x01 | 2 | +0x0C | **Velocity/expression coefficient** (8-bit signed, scaled) |
| +0x01C0 | 0x01 | 3 | +0x38 | **Key-on flag** (hard-coded 0x8100 by firmware) |
| +0x0400 | 0x04 | 0 | +0x0E | **Note key info** (note<<8, bit 15=active) |
| +0x0440 | 0x04 | 1 | +0x10 | Level/key parameter bank 1 |
| +0x0480 | 0x04 | 2 | +0x12 | Level/key parameter bank 2 |
| +0x04C0 | 0x04 | 3 | +0x14 | Level/key parameter bank 3 |
| +0x0500 | 0x05 | 0 | +0x16 | **Modulation param** (written just before KEY ON) |
| +0x0540 | 0x05 | 1 | +0x3A | **Extended param 1** (bit 15 = latch strobe) |
| +0x0580 | 0x05 | 2 | +0x3C | **Extended param 2** (bit 15 = latch strobe) |
| +0x05C0 | 0x05 | 3 | +0x3E | **Extended param 3** (bit 15 = latch strobe) |
| +0x0600 | 0x06 | 0 | +0x40 | **Aux routing param 0** |
| +0x0640 | 0x06 | 1 | +0x42 | **Aux routing param 1** |
| +0x0800 | 0x08 | 0 | +0x18 | **Main Volume** (0xFF80=mute, lower=louder) |
| +0x0840 | 0x08 | 1 | +0x1A | **Pan Left** (0x00=silent, 0x3C=center, 0x78=full) |
| +0x0880 | 0x08 | 2 | +0x1C | **Pan Right** (0x00=silent, 0x3C=center, 0x78=full) |
| +0x08C0 | 0x08 | 3 | +0x1E | **DSP/Effects Send Level** |
| +0x0900 | 0x09 | 0 | +0x20 | **DSP effects send 0** (4 independent aux sends) |
| +0x0940 | 0x09 | 1 | +0x22 | **DSP effects send 1** |
| +0x0980 | 0x09 | 2 | +0x24 | **DSP effects send 2** |
| +0x09C0 | 0x09 | 3 | +0x26 | **DSP effects send 3** |
| +0x0A00 | 0x0A | 0 | +0x28 | **Secondary aux param 0** (post-processing) |
| +0x0A40 | 0x0A | 1 | +0x2A | **Secondary aux param 1** |

### ToneGen_WriteVoiceParams Sequence

The firmware's `ToneGen_WriteVoiceParams` function (at subcpu 0x02D0FD) writes 23 register/data pairs per voice from a 44-byte parameter struct. The write order is:

| Step | Register | Struct Offset | Notes |
|------|----------|--------------|-------|
| 1 | +0x040 | +2 | **Pitch increment** (semitone table, 0x8000=1.0x) |
| 2 | +0x080 | +4 | **Voice mode/velocity** (bit 15 SET = latch strobe) |
| 3 | +0x0C0 | +6 | **Waveform control** (cleared on note-off) |
| 4 | +0x100 | +8 | Interpolated pitch (portamento/legato) |
| 5 | +0x140 | +10 | Secondary pitch offset (detune) |
| 6 | +0x180 | +12 | Velocity/expression coefficient |
| 7 | +0x400 | +14 | **Note key info** (note<<8, bit 15=active) |
| 8 | +0x440 | +16 | Level/key param bank 1 |
| 9 | +0x480 | +18 | Level/key param bank 2 |
| 10 | +0x4C0 | +20 | Level/key param bank 3 |
| 11 | +0x500 | +22 | **Modulation param** |
| 12 | +0x000 | — | Voice control = **0x8100** (KEY ON) |
| 13 | +0x840 | +26 | **Pan left** (0-0x78, center=0x3C) |
| 14 | +0x880 | +28 | **Pan right** (0-0x78, center=0x3C) |
| 15 | +0x8C0 | +30 | **DSP/effects send level** |
| 16 | +0x900 | +32 | DSP effects send 0 |
| 17 | +0x940 | +34 | DSP effects send 1 |
| 18 | +0x980 | +36 | DSP effects send 2 |
| 19 | +0x9C0 | +38 | DSP effects send 3 |
| 20 | +0xA00 | +40 | Secondary aux param 0 |
| 21 | +0xA40 | +42 | Secondary aux param 1 |
| 22 | +0x080 | +4 | Voice mode/velocity (bit 15 CLEAR = latch release) |

Note: Step 12 writes the constant 0x8100 (key-on) to the voice control register, NOT from the struct. Steps 2 and 22 form a SET/CLEAR strobe pair on register +0x080 bit 15.

### Voice Initialization Chain (Voice_Init_Type4)

When a voice is triggered, the firmware runs a 15-function initialization chain before writing registers:
1. `Voice_Pitch_InterpDispatch` — pitch interpolation
2. `Voice_Pitch_WriteOutputReg_Portamento` — portamento output
3. `Voice_Pitch_WriteOutputReg_Legato` — legato output
4. `Voice_Level_ComputeTriplet` — level computation
5. `Voice_PitchPack_Dispatch` — pitch packing
6. `Voice_PanReg_WriteDispatch` — pan register
7. `Voice_StereoLevel_Compute` — stereo balance
8. `Voice_PortaLevel_Compute` — portamento level
9. `Voice_Chan_ComputeParams` — channel parameters
10. `Voice_SubVoice_ComputeAndTrigger` — sub-voice trigger
11. `Voice2_UpdatePitch` — secondary pitch update
12. `Voice_ComputeExprPitchBend` — expression + pitch bend
13. `Voice_SetPitchWord_Muted` — initial pitch (muted)
14. `Voice_ComputeAndWritePan` — final pan
15. `Voice_ComputePitch` — final pitch computation

This chain runs at voice allocation time (from `Voice_Allocate_Typed`), computing all parameters from MIDI data, instrument definitions, and performance state before calling `ToneGen_WriteVoiceParams`.

### Voice Control State Machine

The voice control register at offset +0x0000 (group 0x00, bank 0) cycles through these states:

| Value | State | Description |
|-------|-------|-------------|
| 0x7E00 | Idle | Voice released / available |
| 0x8100 | Key-on | Bit 15 = active flag, bits 8-0 = voice mode |
| 0x1200 | Transition | Sound sustaining / decaying |

### Latched Parameter Updates

Several registers use bit 15 as a write strobe: the firmware writes the data value with bit 15 SET, then immediately rewrites the same value with bit 15 CLEAR. This SET-then-CLEAR pattern is used for registers at offsets +0x0080, +0x0540, +0x0580, and +0x05C0.

## Global Registers

These system-wide registers configure overall synthesis and effects:

| Register | Init Value | Description |
|----------|-----------|-------------|
| 0x0200 | 0x0060 | System config 0 (bit 3 conditionally set/cleared) |
| 0x0201 | 0x0993 | System config 1 |
| 0x0202 | 0x0001 | System config 2 |
| 0x0203 | 0x0004 | System config 3 |
| 0x0204 | 0x0004 | System config 4 |
| 0x0205 | 0x000C | System config 5 |
| 0x0C00 | 0x0000 | Effects config 0 |
| 0x0C01 | 0x0000 | Effects config 1 |
| 0x0C02 | 0x0000 | Effects config 2 |
| 0x0C03 | 0x0000 | Effects config 3 |
| 0x0C04 | 0x0020 | Effects config 4 |
| 0x0C05 | 0x0001 | Effects config 5 |
| 0x0E00 | 0x0000 | Master control |

## Initialization Sequence

The `ToneGen_Config_Init` routine (at `0x02DFCF`) performs the following sequence during boot:

1. **Write global config** -- 13 registers (0x0200-0x0205, 0x0C00-0x0C05, 0x0E00) from config struct at RAM 0xF8BB
2. **Copy voice template** -- 68 bytes from ROM 0xF8D5 to RAM 0x2AA4 (per-voice parameter template)
3. **For each of 64 channels** (0x00-0x3F):
   - Mute volume: register 0x0840 = 0xFF00, register 0x0800 = 0xFF80
   - Write 22 voice parameters from template struct
   - Re-mute volume
   - Set voice to idle: register 0x00C0 = 0x0000, register 0x0000 = 0x7E00
   - Write extended parameters (groups 0x01, 0x05, 0x06) with bit-15 strobe

This produces 2,317 register/data write pairs (confirmed in MAME log analysis).

After configuration, `ToneGen_Poll_Init` runs a polling sequence:
- For each of 16 hardware voice slots:
  - Delay loop (10,000 iterations)
  - Read status from 0x110002
  - Read data from 0x110000
  - Process as "note-off" events

## DSP Interface (0x130000)

A second register-indirect interface at 0x130000 controls DSP processing, accessed by the boot ROM during early initialization:

| Address | Width | Direction | Purpose |
|---------|-------|-----------|---------|
| 0x130000 | 8-bit | Write | DSP register address |
| 0x130002 | 8-bit | Write | DSP register data |

The DSP has 4 processing blocks at 0x20-byte spacing:

| Block | Register Range | Init Register | Init Value |
|-------|---------------|---------------|-----------|
| 0 | 0x00-0x1F | 0x1F | 0x01 |
| 1 | 0x20-0x3F | 0x3F | 0x01 |
| 2 | 0x40-0x5F | 0x5F | 0x01 |
| 3 | 0x60-0x7F | 0x7F | 0x01 |

Registers 0x50-0x57 are zeroed during boot for each block.

### DSP Command Protocol

DSP1 (IC311, uPD6383GF-3BA) uses an 8-bit parallel bus protocol, while DSP2 (IC310, MN19413) uses GPIO bit-bang serial. Both are controlled via Sub CPU GPIO pins:

| Pin | Port | Function |
|-----|------|----------|
| P7.3 | Port 7 bit 3 | Write strobe (active low) |
| P7.4 | Port 7 bit 4 | Read strobe (active low) |
| P7.5 | Port 7 bit 5 | CS1 — DSP1 chip select (IC311, uPD6383GF-3BA) |
| P7.6 | Port 7 bit 6 | Command/Data select (1=command, 0=data) |
| PE.6 | Port E bit 6 | CS2 — DSP2 chip select (IC310, MN19413) |
| PH.0 | Port H bit 0 | Status input (busy/ready) |
| PZ[7:0] | Port Z | 8-bit bidirectional data bus |

**Write handshake:**
1. Set Port Z = data byte
2. Set P7.6 high (command) or low (data)
3. Assert chip select (P7.5 or PE.6 low)
4. Assert write strobe (P7.3 low)
5. Poll PH.0 until ready
6. Deassert write strobe and chip select

### Known DSP Commands

| Command | Description |
|---------|-------------|
| 0x01 | Initialize / reset DSP |
| 0x03 | Set processing mode / algorithm |
| 0x30 | Parameter update (followed by data bytes) |
| 0x60 | Bulk transfer start |

See [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/#dsp-preset-structure) for the effect preset data format.

## Serial Port 1 ("SA" Interface)

The Sub CPU's serial port 1 (UART mode, ~500kHz clock) connects to an audio peripheral for control commands. The "SA" designation found in the service manual schematics refers to "Sub Address" bus lines, not a chip name. The serial device is likely the DAC (IC313, PCM69AU) or one of the DSP chips.

### Serial Configuration

| Parameter | Value |
|-----------|-------|
| Mode | 8-bit UART (SC1MOD = 0x29) |
| Clock | Internal baud rate generator |
| BR1CR | 0x0A (divisor = 10, clock = fCPU/4) |
| Baud Rate | ~500kHz serial clock (20MHz / 4 / 10) |

### Protocol

- **Sync byte**: 0xFE sent during initialization and periodically (every ~135 audio ticks)
- **TX ring buffer**: 1024 bytes at 0x0A00-0x0DFF
- **RX ring buffer**: 512 bytes at 0x0E16-0x1015
- **Special commands**: 0xF4 and 0xF5 trigger baud rate switching and RX enable

## Tone Generator Section IC Inventory

From the service manual schematics (Tone Generator Sections A and B):

| IC | Part Number | Function |
|----|-------------|----------|
| IC303 | TC183C230002 | **Tone Generator LSI** (custom Matsushita) |
| IC304 | QS6GU3C32375 | 32Mbit Waveform ROM |
| IC305 | QS6GT3C33A01 | 32Mbit Waveform ROM |
| IC306 | QS6GU3C32374 | 32Mbit Waveform ROM |
| IC307 | QS6GX3C32008 | 32Mbit Waveform ROM |
| IC308 | M5M418128AJ-6 | 1Mbit DRAM — delay memory for **DSP2 (IC310, MN19413)** |
| IC309 | M5M44260AJ-7S | 4Mbit DRAM — delay memory for **DSP1 (IC311, uPD6383GF)**. Only address lines A0–A8 reach it; A9–A16 are unconnected. |
| IC310 | MN19413 | **DSP2** (Matsushita, serial interface) |
| IC311 | uPD6383GF-3BA | **DSP1** (parallel + memory-mapped) |
| IC312 | M5218AFP | Dual op-amp (DAC output buffer) |
| IC313 | PCM69AU | **D-A Converter** (18-bit stereo, Burr-Brown) |
| IC314 | M5218AFP | Dual op-amp (output buffer) |
| IC315 | D74HC244GS | 3-state buffer |

## Audio Signal Chain

```
Waveform ROMs (IC304-307) ──> Tone Generator LSI (IC303)
                                      │
                                [Memory bus]
                                      │
                                Sub CPU (IC27, TMP94C241F)
                                      │
                        ┌─────────────┼─────────────┐
                        │             │             │
                   [0x100000]     [Serial1]    [0x130000]
                    Register        UART           DSP
                     Config        Control       Config
                        │             │             │
                        v             v             v
                    Tone Gen       DAC/DSP      DSP1/DSP2
                     (IC303)       (IC313?)    (IC310/311)
                                      │
                            [Serial Audio: BCK, SDOR/SDOF]
                                      │
                                      v
                                DAC (IC313, PCM69AU)
                                      │
                                Op-amps (IC312, IC314)
                                      │
                                FAJ board (mixing, LPF)
                                      │
                                Power amp ──> Speakers
```

## MAME Emulation Status

The KN5000 tone generator **makes sound** in MAME: a keyed note plays real PCM from the one
dumped wave ROM (IC307), shaped by the firmware's own envelope, sustains while held, and responds
to velocity — verified in July 2026. The sub-CPU runs its **dumped ROM**, so the envelope, voice
lifecycle and pitch math are executed as real firmware, not re-implemented; the emulation's job is
to model the IC303 chip faithfully enough that those firmware writes produce the right audio.

| Component | Address | Status |
|-----------|---------|--------|
| Register Config (0x100000) | Write **+ Read** | **Tone gen device** — register-address latch on write; **active-voice bitmap on read** (see below) |
| Register Data (0x100002) | Read/Write | **Tone gen device** — data port, voice status readback |
| Keyboard Input (0x110000) | Read-only | **Tone gen device** — keybed event queue (note/velocity) |
| DSP Config (0x130000) | Read/Write | **DSP1 device** — `kn5000_dsp1_device`, 4 channels × 0x20 registers |
| Serial1 (SA interface) | UART | **No receiver** — TX sends into void |
| Waveform RAM (0x1E0000) | Read/Write | **Stub (`noprw`)** — no sample storage |
| Sound output | Stereo 48kHz | **Audible PCM playback** — real IC307 samples, software envelope, sustain, per-semitone pitch, velocity, polyphony |

The `kn5000_tonegen_device` (in `kn5000_tonegen.cpp`) implements:
- Register-indirect interface matching the hardware protocol (address latch at 0x100000, data at 0x100002)
- 64 voice states with 32 registers each (8 groups × 4 banks, including group 0xA)
- 13 global configuration registers; voice control state machine (key on/off via group 0 bank 0)
- Waveform ROM reading from the `waveform` region (IC304-IC307, 16 MB); stereo 48 kHz stream with linear interpolation

### Sound generation

- **Real IC307 PCM is audible.** ⚠ A "does this voice have sample data?" test must probe a
  *window* of samples, never the first byte alone: real waveforms routinely start at a
  zero-crossing — IC307 index 0 is a sine beginning at sample 0 — so a first-byte test
  rejects them and the voice falls silent.
- **The software envelope is honored.** The KN5000 has **no hardware EG** — the envelope is a *per-note,
  multi-stage software* generator running in the SUB CPU (steppers `LABEL_026E5B`/`026EC3`), clocked by
  the audio tick, that rewrites the voice's amplitude every tick to group 0/bank 0 as `0xF000|magnitude`
  (low 9 bits = level). MAME now latches that per-tick magnitude and applies it, and gates key-on strictly
  on the `0x8100` note-on command so the envelope writes no longer retrigger the voice. GUI editors
  `SEAMPENV/SEPITENV/SEFILENV` = amplitude/pitch/filter envelopes (same three domains as the KN7000).
- **Held notes sustain.** The firmware polls an **active-voice bitmap by *reading* 0x100000** (it writes a
  bank index 0-3, then reads back a 16-bit "which voices are sounding" word); its software voice-manager
  frees any voice commanded ON but reported silent. The address had been modelled write-only, so the read
  returned 0 and every held note was released after ~45 ms. A `status_r()` handler now returns the
  active-voice bitmap, and note-off is detected from the firmware's release-envelope burst (a real key-up
  programs a release ramp rather than writing `0x7E00`).
- **Per-semitone pitch.** The IC303 is a PCM **multisample** chip: `reg[8]` (group 4/bank 0) steps +0x100
  per semitone *within* a sample zone and resets at zone boundaries, and `reg[1]`'s low nibble selects the
  zone — so no single register holds an absolute note, and the per-zone sample roots are not in the chip
  registers. An earlier "reg[1] = semitone ratio, reg[8] = octave" model was wrong (every semitone
  collapsed to one pitch). Because every voice currently renders the same fabricated sine (see wave-number
  limitation below), MAME recovers the true played note from the input FIFO and drives equal temperament
  directly — a faithful stand-in until real multisample tuning is wired in. Verified: a chromatic scale
  produces 12 distinct rising pitches; octaves double.
- **Velocity.** The firmware's per-voice loudness is a **log-domain attenuation** in the high byte of
  reg[20] (lower value = louder), velocity-scaled through a log table (`0x0118FE`). MAME expands it
  log→linear, giving a proper dynamic range (soft-vs-hard ≈ 6.5×). Panel Touch-Sensitivity scaling happens
  upstream in the sub-CPU curve, so this widens whatever curve the setting selects.
- **Polyphony.** Simultaneous chord notes share one keybed-scan timestamp, so a naive "most-recent note"
  correlation gave every voice the same note (a chord played as three copies of the root). Fixed with a
  register-anchored pairing: the voices of one chord are distinguished by a monotonic pitch index built
  from `reg[1]` (zone) and `reg[8]` (within-zone offset) and paired in order to the chord's input notes —
  so C-E-G rings as C-E-G, and dual-layer voices (identical index) collapse to the same note.
- **MIDI → internal keybed bridge (velocity).** A host MIDI controller can play the machine's own 61-key
  bed with velocity (`-kbdmidi midiin`), separate from the rear MIDI jacks — a MIDI UART deserializes to
  `kbd_midi_rx()`, which pushes note-on/off events in the same wire format the physical keybed scanner
  uses. See [Keybed Scanning]({{ site.baseurl }}/keybed-scanning/).

**Open / honest limitations:**
- **Waveform selection is unresolved** — *every* voice currently resolves to IC307 index 0 (a fabricated
  sine), so notes are correctly *pitched* and *voiced* but timbrally identical. Which register selects the
  waveform, and how it indexes IC307's 198-entry table, is under active investigation (an earlier static
  guess of reg[9] was falsified by a live capture showing reg[9] = 0). A real KN5000's Piano/Guitar/etc.
  sound different; this is the main remaining faithfulness gap.
  One lead worth following: the [Tone Database]({{ site.baseurl }}/tone-database/) carries three
  **wave-source name catalogues** (`ToneDB_SourceNameList1/2`, `ToneDB_DrumSourceNameList` — 333, 339 and
  424 rows of a 13-character PCM source name plus three id/flag bytes), each reached from a tone record
  through 1024-entry index maps. The id/flag bytes are not yet decoded, so this is a hypothesis about
  where the real wave index lives, not a result.
- **Waveform ROMs IC304-IC306 are NO_DUMP** (only IC307 is dumped). Whether per-waveform root note / tuning
  / loop points live in IC307's dumped parameter records or elsewhere is being decoded — *not* assumed to
  be in the undumped ROMs.
  - **No CPU wave-read port.** IC303's CPU-facing ports (`0x100000`/`0x100002` register+voice-status,
    `0x110000` keybed events) do not let the CPU address a wave-ROM location and read the sample back. The
    service-mode Wave ROM Check is an *acoustic* test (sine playback, listen for distortion), not a
    checksum. This is unlike the KN7000, whose tone generators expose a wave-memory read port that its
    §8.9 test sweeps digitally — so the KN7000's clean software dump route does **not** transfer here.
    See [KN7000 Expansion Bus & Wave-ROM Dump Routes]({{ site.baseurl }}/kn7000-expansion-and-wave-dump/).
- **No DSP effects** (reverb, chorus, EQ) — the effects DSP (IC311) is a separate subsystem.

The keybed scanner generates note-on/note-off events from MAME input ports. Events are queued in the tone
gen device and read by `ToneGen_Read_Voice_Data` at 0x110000/0x110002. The full bidirectional note flow
works: keybed (or MIDI bridge) → subcpu → maincpu (for display/chord detection) → subcpu → tone gen
registers. See [Keybed Scanning]({{ site.baseurl }}/keybed-scanning/) for the note encoding format.

## Related Pages

- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) -- Overall audio architecture
- [Tone Database]({{ site.baseurl }}/tone-database/) -- The factory tone/voice records these registers are loaded from
- [SubCPU Payload Loading]({{ site.baseurl }}/subcpu-payload-loading/) -- How firmware reaches the SubCPU
- [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) -- Latch communication details
- [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) -- Full system hardware

## Voice Setup Procedures

The SubCPU firmware provides two voice setup paths, both called via a dispatch table at `0x012159`:

### ToneGen_SetupPolyVoice (Melodic Voices)

Called for standard polyphonic note-on events. Performs:

1. **Copy template**: Copies 34-byte (0x22) voice parameter template from ROM `0x012115` to working buffer at `0x3B1C`. Default values (uint16_t LE): `0x06FF` (header), then `0x0600, 0x0800, 0x0800, 0x0800, 0x0A00, 0x0A00, 0x0C00, 0x0C00, 0x0E00, 0x0E00, 0x0F00, 0x1100, 0x1300, 0x1300, 0x1500, 0x1700` (16 register defaults). An additional word `0x1900` at `+34` is read beyond the copied region.
2. **Compute pitch**: MIDI note lookup → octave calculation (`note / 12`), remainder used for fine pitch from table at `0x01217D`
3. **Apply velocity**: `DSP_VelocityToVolume` converts MIDI velocity to volume level, OR'd into struct offset +24 (volume bank 0)
4. **Apply effect routing**: `DSP_GetEffectRouting` determines reverb/chorus send levels, OR'd into struct offset +26
5. **Write all parameters**: Calls `ToneGen_WriteVoiceParams` (22 register writes + key-on)
6. **Write control register**: `ToneGen_WriteSingleReg` writes the voice control word

### ToneGen_SetupPercussionVoice (Drum Voices)

Similar to poly but with percussion-specific pitch handling:

1. **Copy template**: Same 34-byte template from `0x012115` to `0x3B1C`
2. **Percussion pitch**: Uses `note / 12` for octave, `note % 12` as drum index (bit 7 cleared). Shifted left 8 bits and OR'd with key-on flag
3. **Octave lookup**: Uses separate table at `0x012195` (vs `0x01217D` for melodic)
4. **Effect routing**: Same `DSP_GetEffectRouting` call
5. **Fixed velocity**: Volume set to 0x0FFF (maximum)
6. **Write parameters**: Same `ToneGen_WriteVoiceParams` + `ToneGen_WriteSingleReg` sequence

### ToneGen_WriteVoiceParams — Full Register Sequence

This routine writes 22 voice parameters from a 44-byte struct, in this exact order:

| Step | Register Offset | Struct Offset | Group | Bank | Notes |
|------|----------------|---------------|-------|------|-------|
| 1 | +0x0040 | +2 | 0 | 1 | **Pitch increment** (semitone table lookup) |
| 2 | +0x0080 | +4 | 0 | 2 | **Voice mode/velocity** (**bit 15 SET** = latch strobe) |
| 3 | +0x00C0 | +6 | 0 | 3 | **Waveform control** (cleared on note-off) |
| 4 | +0x0100 | +8 | 1 | 0 | **Interpolated pitch** (portamento/legato) |
| 5 | +0x0140 | +10 | 1 | 1 | **Secondary pitch offset** (detune) |
| 6 | +0x0180 | +12 | 1 | 2 | **Velocity/expression coefficient** |
| 7 | +0x0400 | +14 | 4 | 0 | **Note key info** (note value << 8, bit 15=active) |
| 8 | +0x0440 | +16 | 4 | 1 | Filter/pitch param 1 |
| 9 | +0x0480 | +18 | 4 | 2 | Filter/pitch param 2 |
| 10 | +0x04C0 | +20 | 4 | 3 | Filter/pitch param 3 |
| 11 | +0x0500 | +22 | 5 | 0 | Modulation param 0 |
| 12 | +0x0800 | +24 | 8 | 0 | **Main volume** (0xFF80=mute, lower=louder) |
| **KEY-ON** | +0x0000 | — | 0 | 0 | **0x8100** (active flag set) |
| 13 | +0x0840 | +26 | 8 | 1 | **Pan left** (0-0x78, center=0x3C) |
| 14 | +0x0880 | +28 | 8 | 2 | **Pan right** (0-0x78, center=0x3C) |
| 15 | +0x08C0 | +30 | 8 | 3 | **DSP/effects send level** |
| 16 | +0x0900 | +32 | 9 | 0 | Aux/send level 0 |
| 17 | +0x0940 | +34 | 9 | 1 | Aux/send level 1 |
| 18 | +0x0980 | +36 | 9 | 2 | Aux/send level 2 |
| 19 | +0x09C0 | +38 | 9 | 3 | Aux/send level 3 |
| 20 | +0x0A00 | +40 | A | 0 | Aux parameter 0 |
| 21 | +0x0A40 | +42 | A | 1 | Aux parameter 1 |
| 22 | +0x0080 | +4 | 0 | 2 | Same as step 2, **bit 15 CLEAR** (latch release) |

Key design points:
- **Key-on is in the middle** (after volume, before pan/aux) — ensures volume is set before the voice starts sounding
- **Latch strobe protocol**: Register +0x0080 is written twice — first with bit 15 SET to load waveform data, last with bit 15 CLEAR to release the latch
- **NOP timing**: 3 NOPs between each register write for bus setup/hold times

## Pitch Calculation

`ToneGen_Calc_Pitch` (at `0x03D11F`) converts MIDI note numbers to tone generator pitch values:

### Algorithm

1. **Base pitch**: `pitch = (MIDI_note & 0x7F) + 36` — adds a 3-octave offset (0x24)
2. **Release check**: Bit 7 of the note byte indicates note-off; if set, velocity = 0 and return
3. **Velocity scaling**: MIDI velocity is processed through a multi-step lookup:
   - Index into velocity table at `0x01F43E` (mode × 3 lookup)
   - Compute delta from base reference at `0x01F418`
   - Multiply by mode-specific scaling factor from `0x01F420`
   - Divide by reference divisor at `0x01F41A`
4. **Octave division**: `pitch / 12` gives octave, remainder gives semitone
5. **Mode-specific adjustment**: For certain pitch modes (1, 3, 6, 8, 10), an additional offset from table `0x01F422` is subtracted
6. **Clamping**: Final value clamped to 0-255 range
7. **Velocity lookup**: Clamped value indexes into `0x01F53E` for final velocity byte

### Note-Off Protocol

`ToneGen_WriteNoteKey` performs a two-step register write:
1. Write register `+0xC0` (group 0, bank 3) = `0x0000` — clear waveform control
2. Write register `+0x00` (group 0, bank 0) = `0x7E00` — set voice to idle state

## Note-On Voice Allocation

`Voice_Poly_NoteOn` uses **round-robin allocation** across 8 voice slots per channel:

1. **Counter**: RAM `15123` holds a 3-bit counter (0-7), incremented on each note-on, wrapping with `AND 0x7`
2. **Slot search**: The selected slot is checked for availability
3. **Mute existing**: If the slot is active, its current voice is muted:
   - Register `+0x840` = `0xFF00` (mute volume bank 1)
   - Register `+0x800` = `0xFF80` (mute volume bank 0)
4. **Dispatch**: The voice type (from bits 4-7 of the event) selects a setup function via the dispatch table at `0x012159`:
   - Entries include `ToneGen_SetupPolyVoice` (for standard melodic voices)
   - Different entries handle split, layer, and percussion voices
5. **Mark active**: The note number is stored in the voice allocation table (bit 7 set = active)

### Voice Processing Pipeline

After note-on, the ongoing voice processing (called from `Voice_Init_Type4`) runs a chain of 14 parameter computation functions:
- `Voice_Pitch_InterpDispatch` — pitch interpolation
- `Voice_Pitch_WriteOutputReg_Portamento` — portamento glide
- `Voice_Pitch_WriteOutputReg_Legato` — legato transitions
- `Voice_Level_ComputeTriplet` — 3-component level blending
- `Voice_PitchPack_Dispatch` — pitch word assembly
- `Voice_PanReg_WriteDispatch` — pan position
- `Voice_StereoLevel_Compute` — stereo balance
- `Voice_PortaLevel_Compute` — portamento level
- `Voice_Chan_ComputeParams` — channel parameter merge
- `Voice_SubVoice_ComputeAndTrigger` — sub-voice triggering (for layered sounds)
- `Voice2_UpdatePitch` — secondary pitch update
- `Voice_ComputeExprPitchBend` — expression + pitch bend
- `Voice_SetPitchWord_Muted` — muted pitch override
- `Voice_ComputeAndWritePan` — final pan write

## Research Needed

- [x] ~~Determine exact register semantics~~ — Partially: voice control, volume, aux sends documented from write sequence
- [x] ~~Decode voice parameter template at ROM 0xF8D5~~ — 34-word (68-byte) template at `0x012115`, copied to `0x3B1C` per voice setup
- [ ] Map remaining per-voice register semantics (groups 4/5 = filter? pitch? modulation?)
- [x] ~~Analyze waveform ROM format and sample addressing~~ -- Complete: IC307 format documented. See [Waveform ROM Format]({{ site.baseurl }}/waveform-rom-format/)
- [ ] Document DSP1/DSP2 command sets and processing algorithms
- [ ] Trace the PCM audio serial bus (BCK/SDOR/SDOF) connections
- [x] ~~Identify the exact device connected to Serial Port 1~~ — Computer Interface (TO HOST connector), sends 0xFE Active Sensing
