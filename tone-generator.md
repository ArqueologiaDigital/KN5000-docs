---
layout: page
title: Tone Generator
permalink: /tone-generator/
---

# Tone Generator (IC303)

The KN5000's tone generator is a custom Matsushita LSI (TC183C230002, IC303) that provides 64-voice polyphonic wavetable synthesis. It is controlled by the Sub CPU via a register-indirect interface and reads waveform data from four 32Mbit ROMs (IC304-IC307).

> **Status:** Register map partially reverse-engineered from SubCPU firmware init sequence. See [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) for the overall audio architecture.

## Hardware Overview

| Property | Value |
|----------|-------|
| Chip | TC183C230002 (Matsushita custom) |
| Package Location | IC303 |
| Voice Count | 64 independent voices |
| Parameters per Voice | 28 registers (68-byte parameter struct) |
| Global Registers | 13 (system config + DSP/effects) |
| Interface | Memory-mapped register-indirect (address/data pair) |
| Address Lines | SubCPU memory bus + P6.7 chip-select |
| Waveform ROMs | IC304 (QS6GU3C32375), IC305 (QS6GT3C33A01), IC306 (QS6GU3C32374), IC307 (QS6GX3C32008) |
| Waveform RAM | IC308 (M5M44260AJ7S, 4Mbit DRAM), IC309 (M5M44260AJ7S, 4Mbit DRAM) |

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
| +0x0040 | 0x00 | 1 | +0x02 | Voice parameter 0, bank 1 |
| +0x0080 | 0x00 | 2 | +0x04 | Voice parameter 0, bank 2 (bit 15 = key-on flag) |
| +0x00C0 | 0x00 | 3 | +0x06 | Voice parameter 0, bank 3 |
| +0x0100 | 0x01 | 0 | +0x08 | Voice parameter 1, bank 0 |
| +0x0140 | 0x01 | 1 | +0x0A | Voice parameter 1, bank 1 |
| +0x0180 | 0x01 | 2 | +0x0C | Voice parameter 1, bank 2 |
| +0x01C0 | 0x01 | 3 | +0x38 | Voice parameter 1, bank 3 |
| +0x0400 | 0x04 | 0 | +0x0E | Voice parameter 4, bank 0 |
| +0x0440 | 0x04 | 1 | +0x10 | Voice parameter 4, bank 1 |
| +0x0480 | 0x04 | 2 | +0x12 | Voice parameter 4, bank 2 |
| +0x04C0 | 0x04 | 3 | +0x14 | Voice parameter 4, bank 3 |
| +0x0500 | 0x05 | 0 | +0x16 | Voice parameter 5, bank 0 |
| +0x0540 | 0x05 | 1 | +0x3A | Voice parameter 5, bank 1 (bit 15 = latch strobe) |
| +0x0580 | 0x05 | 2 | +0x3C | Voice parameter 5, bank 2 (bit 15 = latch strobe) |
| +0x05C0 | 0x05 | 3 | +0x3E | Voice parameter 5, bank 3 (bit 15 = latch strobe) |
| +0x0600 | 0x06 | 0 | +0x40 | Voice parameter 6, bank 0 |
| +0x0640 | 0x06 | 1 | +0x42 | Voice parameter 6, bank 1 |
| +0x0800 | 0x08 | 0 | +0x18 | **Volume/Level**, bank 0 |
| +0x0840 | 0x08 | 1 | +0x1A | **Volume/Level**, bank 1 |
| +0x0880 | 0x08 | 2 | +0x1C | **Volume/Level**, bank 2 |
| +0x08C0 | 0x08 | 3 | +0x1E | **Volume/Level**, bank 3 |
| +0x0900 | 0x09 | 0 | +0x20 | Aux level, bank 0 |
| +0x0940 | 0x09 | 1 | +0x22 | Aux level, bank 1 |
| +0x0980 | 0x09 | 2 | +0x24 | Aux level, bank 2 |
| +0x09C0 | 0x09 | 3 | +0x26 | Aux level, bank 3 |
| +0x0A00 | 0x0A | 0 | +0x28 | Aux parameter, bank 0 |
| +0x0A40 | 0x0A | 1 | +0x2A | Aux parameter, bank 1 |

### ToneGen_WriteVoiceParams Sequence

The firmware's `ToneGen_WriteVoiceParams` function (at subcpu 0x02D0FD) writes 23 register/data pairs per voice from a 44-byte parameter struct. The write order is:

| Step | Register | Struct Offset | Notes |
|------|----------|--------------|-------|
| 1 | +0x040 | +2 | Group 0, bank 1 |
| 2 | +0x080 | +4 | Group 0, bank 2 (bit 15 SET = strobe) |
| 3 | +0x0C0 | +6 | Group 0, bank 3 |
| 4 | +0x100 | +8 | Group 1, bank 0 |
| 5 | +0x140 | +10 | Group 1, bank 1 |
| 6 | +0x180 | +12 | Group 1, bank 2 |
| 7 | +0x400 | +14 | Group 4, bank 0 (pan) |
| 8 | +0x440 | +16 | Group 4, bank 1 |
| 9 | +0x480 | +18 | Group 4, bank 2 |
| 10 | +0x4C0 | +20 | Group 4, bank 3 |
| 11 | +0x500 | +22 | Group 5, bank 0 |
| 12 | +0x000 | — | Voice control = 0x8100 (KEY ON) |
| 13 | +0x840 | +26 | Volume, bank 1 |
| 14 | +0x880 | +28 | Volume, bank 2 |
| 15 | +0x8C0 | +30 | Volume, bank 3 |
| 16 | +0x900 | +32 | Aux level, bank 0 |
| 17 | +0x940 | +34 | Aux level, bank 1 |
| 18 | +0x980 | +36 | Aux level, bank 2 |
| 19 | +0x9C0 | +38 | Aux level, bank 3 |
| 20 | +0xA00 | +40 | Aux param, bank 0 |
| 21 | +0xA40 | +42 | Aux param, bank 1 |
| 22 | +0x080 | +4 | Group 0, bank 2 (bit 15 CLEAR = complete strobe) |

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

DSP1 (IC311, DS3613GF-3BA) uses an 8-bit parallel bus protocol, while DSP2 (IC310, MN19413) uses GPIO bit-bang serial. Both are controlled via Sub CPU GPIO pins:

| Pin | Port | Function |
|-----|------|----------|
| P7.3 | Port 7 bit 3 | Write strobe (active low) |
| P7.4 | Port 7 bit 4 | Read strobe (active low) |
| P7.5 | Port 7 bit 5 | CS1 — DSP1 chip select (IC311, DS3613GF-3BA) |
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
| IC308 | M5M44260AJ7S | 4Mbit DRAM (DSP1 work RAM) |
| IC309 | M5M44260AJ7S | 4Mbit DRAM (DSP2 work RAM) |
| IC310 | MN19413 | **DSP2** (Matsushita, serial interface) |
| IC311 | DS3613GF-3BA | **DSP1** (parallel + memory-mapped) |
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

| Component | Address | Status |
|-----------|---------|--------|
| Register Config (0x100000) | Write-only | **Tone gen device** — accepts register writes, tracks 64-voice state |
| Register Data (0x100002) | Read/Write | **Tone gen device** — data port, voice status readback |
| Keyboard Input (0x110000) | Read-only | **Tone gen device** — keybed event queue |
| DSP Config (0x130000) | Write-only | **Stub (`noprw`)** — writes harmlessly discarded |
| Serial1 (SA interface) | UART | **No receiver** — TX sends into void |
| Waveform RAM (0x1E0000) | Read/Write | **Stub (`noprw`)** — no sample storage |
| Sound output | Stereo 48kHz | **PCM playback** — pitch control, linear interpolation, release envelope |

The `kn5000_tonegen_device` (in `kn5000_tonegen.cpp`) implements:
- Register-indirect interface matching the hardware protocol (address latch at 0x100000, data at 0x100002)
- 64 voice states with 32 registers each (8 groups × 4 banks, including group 0xA)
- 13 global configuration registers
- Voice control state machine (key on/off via group 0 bank 0)
- Waveform ROM reading from the `waveform` region (IC304-IC307, 16MB total)
- Stereo output via MAME sound stream (48kHz) with linear interpolation
- Pitch control from group 1 registers (16-bit pitch increment scaling)
- Volume and pan from group 8 / group 4 registers
- Release envelope (50ms fade-out on key-off)
- 2-second hold timer for voice status readback (firmware compatibility)
- Waveform latch strobe protocol (group 0, bank 2, bit 15 SET/CLEAR)

**Limitations:** Waveform ROMs IC304-IC306 are NO_DUMP (synthetic approximations available: sine, sawtooth, square/triangle). Pitch register encoding is approximate — the exact firmware-to-hardware pitch mapping is not fully decoded. No DSP effects (reverb, chorus, EQ). Envelope is a simple linear fade, not the hardware's multi-stage envelope. Loop points from parameter records not yet implemented.

The keybed scanner generates note-on/note-off events from MAME input ports (PC keyboard mapped to a 2-octave piano layout). Events are queued in the tone gen device and read by `ToneGen_Read_Voice_Data` at 0x110000/0x110002. The full bidirectional note flow works: keybed → subcpu → maincpu (for display/MIDI) → subcpu → tone gen registers.

See [Keybed Scanning]({{ site.baseurl }}/keybed-scanning/) for the note encoding format and signal flow.

## Related Pages

- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) -- Overall audio architecture
- [SubCPU Payload Loading]({{ site.baseurl }}/subcpu-payload-loading/) -- How firmware reaches the SubCPU
- [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) -- Latch communication details
- [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) -- Full system hardware

## Voice Setup Procedures

The SubCPU firmware provides two voice setup paths, both called via a dispatch table at `0x012159`:

### ToneGen_SetupPolyVoice (Melodic Voices)

Called for standard polyphonic note-on events. Performs:

1. **Copy template**: Copies 34-byte (0x22) voice parameter template from ROM `0x012115` to working buffer at `0x3B1C`
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
| 1 | +0x0040 | +2 | 0 | 1 | Waveform pointer low |
| 2 | +0x0080 | +4 | 0 | 2 | Waveform pointer high (**bit 15 SET** = latch strobe) |
| 3 | +0x00C0 | +6 | 0 | 3 | Waveform control |
| 4 | +0x0100 | +8 | 1 | 0 | Envelope param 0 |
| 5 | +0x0140 | +10 | 1 | 1 | Envelope param 1 |
| 6 | +0x0180 | +12 | 1 | 2 | Envelope param 2 |
| 7 | +0x0400 | +14 | 4 | 0 | Filter/pitch param 0 |
| 8 | +0x0440 | +16 | 4 | 1 | Filter/pitch param 1 |
| 9 | +0x0480 | +18 | 4 | 2 | Filter/pitch param 2 |
| 10 | +0x04C0 | +20 | 4 | 3 | Filter/pitch param 3 |
| 11 | +0x0500 | +22 | 5 | 0 | Modulation param 0 |
| 12 | +0x0800 | +24 | 8 | 0 | **Volume level** (main) |
| **KEY-ON** | +0x0000 | — | 0 | 0 | **0x8100** (active flag set) |
| 13 | +0x0840 | +26 | 8 | 1 | Volume/pan param 1 |
| 14 | +0x0880 | +28 | 8 | 2 | Volume/pan param 2 |
| 15 | +0x08C0 | +30 | 8 | 3 | Volume/pan param 3 |
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
