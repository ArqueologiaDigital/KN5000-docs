---
layout: page
title: Keybed Scanning
permalink: /keybed-scanning/
---

# Keybed Scanning

The KN5000's 61-key velocity-sensitive keyboard connects directly to the tone generator IC303 (TC183C230002), which performs hardware key scanning internally. The Sub CPU reads completed note events from IC303's keyboard output interface — the CPU does **not** scan the keyboard matrix itself.

> **Status:** Note encoding and voice slot management fully reverse-engineered from SubCPU firmware. HLE keybed device implemented in MAME driver.

## Architecture

The note flow is bidirectional — keybed events travel through the Sub CPU to the Main CPU (for display and MIDI output), then note-on commands travel back from the Main CPU through the Sub CPU to IC303 (for sound generation):

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        NOTE EVENT FLOW                                  │
│                                                                         │
│  ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ KEYBED  │───>│  IC303   │───>│ SUB CPU  │───>│ MAIN CPU │          │
│  │ (keys)  │    │ ToneGen  │    │ firmware │    │ firmware │          │
│  └─────────┘    └──────────┘    └──────────┘    └──────────┘          │
│                  0x110000         DMA latch       Display,             │
│                  (HW scan)       @ 0x120000       MIDI out             │
│                                                                         │
│                 ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│                 │  IC303   │<───│ SUB CPU  │<───│ MAIN CPU │          │
│                 │ ToneGen  │    │ firmware │    │ firmware │          │
│                 └──────────┘    └──────────┘    └──────────┘          │
│                  0x100000         DMA latch       Sound select,        │
│                  (voice cfg)     @ 0x120000       note routing         │
└──────────────────────────────────────────────────────────────────────────┘
```

**Forward path** (keybed to display):
1. Physical key press detected by IC303 hardware scanner
2. IC303 presents note/velocity at 0x110000, sets status bit at 0x110002
3. `ToneGen_Read_Voice_Data` reads the event and allocates a voice slot
4. `InterCPU_DMA_Send` transmits `[0x90, note, velocity]` to Main CPU via latch
5. Main CPU updates display (key indicators, voice allocation) and emits MIDI

**Return path** (sound generation):
1. Main CPU sends note-on command via latch to Sub CPU
2. Sub CPU `Voice_NoteOn` configures IC303 voice parameters at 0x100000
3. IC303 begins waveform playback from ROMs IC304-IC307

## Hardware Interface

| Address | Width | Direction | Purpose |
|---------|-------|-----------|---------|
| 0x110002 | 16-bit | Read | Status register |
| 0x110000 | 16-bit | Read | Voice data (note + velocity) |

### Status Register (0x110002)

| Bit | Name | Description |
|-----|------|-------------|
| 0 | DATA_READY | 1 = note event available for reading |
| 1 | MODE | 0 = note-on context (normal operation) |
| 15:2 | — | Reserved / unused |

### Data Register (0x110000)

| Bits | Name | Description |
|------|------|-------------|
| 7:0 | RAW_NOTE | Note number (see encoding below). Bit 7 = "has velocity" flag |
| 15:8 | VELOCITY | Velocity value. 0xFF = note-off |

## Note Encoding

### Raw Note to MIDI Note

`ToneGen_Calc_Pitch` (at 0x03D11F) adds a fixed offset of **0x24 (36)** to convert the raw note number to a MIDI note:

```
MIDI_note = raw_note + 0x24
```

| Raw Note | MIDI Note | Name | Octave |
|----------|-----------|------|--------|
| 0 | 36 | C2 | 2 |
| 12 | 48 | C3 | 3 |
| 24 | 60 | C4 (Middle C) | 4 |
| 36 | 72 | C5 | 5 |
| 48 | 84 | C6 | 6 |
| 60 | 96 | C7 | 7 |

The KN5000 has 61 keys: C2 (raw 0) through C7 (raw 60).

### Note-On Event Format

When a key is pressed with measurable velocity:

```
data_word = (velocity << 8) | (raw_note | 0x80)
status: bit 0 = 1 (data ready), bit 1 = 0 (note-on context)
```

- Bit 7 of the low byte is SET (0x80 OR'd in), indicating "has velocity data"
- Velocity range: 0x01-0xFE (1-254), where higher = harder press

### Note-Off Event Format

When a key is released:

```
data_word = (0xFF << 8) | raw_note
status: bit 0 = 1 (data ready)
```

- Bit 7 of the low byte is CLEAR (raw note value only)
- Velocity byte = 0xFF triggers the note-off code path in `ToneGen_Read_Voice_Data`

## Voice Slot Table

The Sub CPU maintains a 16-entry voice slot table at RAM address **0x4A4C**:

| Address | Size | Description |
|---------|------|-------------|
| 0x4A4A | 2 bytes | DMA enable flag (non-zero = DMA relay active) |
| 0x4A4C | 16 bytes | Voice slot states (one byte per slot) |

Each slot byte:
- **0xFF** = note active (slot in use)
- **0x00** = slot available

When a note-on event arrives, `ToneGen_Read_Voice_Data` scans the 16 slots for an available one. When a note-off arrives, the corresponding slot is freed.

## DMA Packet Format

After processing a note event, the Sub CPU relays it to the Main CPU via the inter-CPU latch using `InterCPU_DMA_Send`:

### Note-On Packet

```
Byte 0: 0x90 (MIDI Note On status)
Byte 1: MIDI note number (raw_note + 0x24)
Byte 2: velocity (0x01-0xFE)
```

### Note-Off Packet

```
Byte 0: 0x90 (MIDI Note On status — velocity 0 = note off per MIDI convention)
Byte 1: MIDI note number (raw_note + 0x24)
Byte 2: 0x00 (zero velocity = note off)
```

## Key Firmware Routines

| Routine | Address | Description |
|---------|---------|-------------|
| `ToneGen_Init` | 0x03D016 | Set tone generator mode to 6, begin polling |
| `ToneGen_Process_Notes` | 0x03D01E | Main loop: read and process all pending events |
| `ToneGen_Read_Voice_Data` | 0x03D0C5 | Read one event from 0x110000, manage voice slots |
| `ToneGen_Calc_Pitch` | 0x03D11F | Convert raw note to pitch value (adds 0x24) |
| `ToneGen_Poll_Init` | 0x03D227 | Initial polling: read 16 slots with delay loops |
| `ToneGen_Config_Init` | 0x02DFCF | Configure all 64 IC303 voices and global registers |
| `InterCPU_DMA_Send` | (varies) | Send 3-byte note packet to Main CPU via latch |

## MAME HLE Implementation

Since IC303 is a custom ASIC with no public documentation, the MAME driver uses an HLE (High-Level Emulation) device to inject keybed events:

- **6 input ports** (KEY0-KEY5) map PC keyboard keys to 61 piano notes
- A **1ms scan timer** compares current key states against previous states
- Key press/release transitions generate events in the IC303 output format
- Events are queued and served when the SubCPU reads 0x110000/0x110002

The HLE produces no sound (IC303 voice parameter writes at 0x100000 are discarded), but the full note event pipeline works end-to-end.

### PC Keyboard Mapping

The keybed notes are available as MAME input entries (visible in the Tab menu under "Input (This Machine)") but have **no default PC keyboard assignments** because all candidate keys conflict with control panel button mappings.

To play notes, use MAME's input configuration UI (Tab menu) to assign keys. A suggested piano layout:

**Lower octave (Z row — assign to KEY2 / C4-B4):**

| Suggested Key | Note | MAME Input Name |
|---------------|------|-----------------|
| Z | C4 | C4 |
| S | C#4 | C#4 |
| X | D4 | D4 |
| D | D#4 | D#4 |
| C | E4 | E4 |
| V | F4 | F4 |
| G | F#4 | F#4 |
| B | G4 | G4 |
| H | G#4 | G#4 |
| N | A4 | A4 |
| J | A#4 | A#4 |
| M | B4 | B4 |

**Upper octave (Q row — assign to KEY3 / C5-B5):**

| Suggested Key | Note | MAME Input Name |
|---------------|------|-----------------|
| Q | C5 | C5 |
| 2 | C#5 | C#5 |
| W | D5 | D5 |
| 3 | D#5 | D#5 |
| E | E5 | E5 |
| R | F5 | F5 |
| 5 | F#5 | F#5 |
| T | G5 | G5 |
| 6 | G#5 | G#5 |
| Y | A5 | A5 |
| 7 | A#5 | A#5 |
| U | B5 | B5 |

**Note:** Assigning these keys will also trigger control panel buttons that share the same keys. This is a known limitation — the control panel and keybed share the same physical keyboard namespace.

Fixed velocity of **100** for all key presses (PC keyboards have no velocity sensitivity).

## Related Pages

- [Tone Generator]({{ site.baseurl }}/tone-generator/) — IC303 register map and voice configuration
- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) — Overall audio architecture and DSP details
- [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) — Latch communication for note relay
- [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) — Physical keyboard and PCB layout
