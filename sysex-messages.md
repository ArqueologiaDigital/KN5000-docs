---
layout: page
title: SysEx Messages
permalink: /sysex-messages/
---

# MIDI System Exclusive Messages

The KN5000 uses two distinct SysEx formats: **Roland GS** for incoming voice parameter control, and **Technics proprietary** for outgoing mode commands. It also implements a bulk data transfer system for panel memory, sound memory, composer data, sequences, and music style programmer (MSP) data.

## Outgoing: Technics SysEx

The KN5000 sends short proprietary SysEx messages via `MIDI_SendSysExCmd` (`0xFEBDA3`).

### Packet Format

```
F0 50 87 <param> F7
```

| Byte | Value | Meaning |
|------|-------|---------|
| `F0` | SysEx start | Standard MIDI SysEx header |
| `50` | Manufacturer ID | Technics/Panasonic (Matsushita) |
| `87` | Model ID | KN5000 identifier |
| `param` | Command byte | See table below |
| `F7` | SysEx end | (implicit, appended by `MIDI_SendCmdPacket`) |

### Known Command Bytes

| Param | Context | Description |
|-------|---------|-------------|
| `0x08` | Sequencer play/stop, drum voice changes, tempo changes, sound mode changes | Sound mode reset — signals downstream devices that the KN5000's sound configuration has changed |
| `0x10` | Panel button press (specific modes) | Mode change notification — sent when switching between certain operating modes |
| `0x68` | Sound initialization | Full sound reset — sent during major sound engine reconfiguration |

The `0x08` command is by far the most common, with 13 call sites across the firmware. It is sent after any operation that alters the active sound configuration (sequencer start/stop, drum kit selection, tempo changes, accompaniment mode switching).

### Implementation

`MIDI_SendSysExCmd` builds a 4-byte payload on the stack:

```
ld (xsp + 1), 0xF0    ; SysEx start
ld (xsp + 2), 0x50    ; Manufacturer: Technics
ld (xsp + 3), 0x87    ; Model: KN5000
ld (xsp + 4), a       ; Command byte (from A register)
```

It then calls `MIDI_SendCmdPacket` to transmit the packet through the MIDI output port, followed by `MIDI_PostSendStub` (likely a post-send flush or delay).

## Incoming: Roland GS SysEx

The KN5000 receives and processes **Roland GS** System Exclusive messages for real-time voice parameter control. This is validated by `SysEx_ValidateRolandHeader` (`0xFDAD57`).

### Expected Header

```
F0 41 42 12 40 01 <cmd> <data> F7
```

| Byte | Value | Meaning |
|------|-------|---------|
| `F0` | SysEx start | Standard MIDI SysEx header |
| `41` | Manufacturer ID | Roland |
| `42` | Device ID | Fixed device address |
| `12` | Command ID | DT1 (Data Transfer 1) |
| `40` | Model ID | GS (General Sound) |
| `01` | Sub-category | Address high byte |
| `cmd` | Address mid byte | Selects parameter group (see below) |
| `data` | Parameter value | Written to DSP configuration |
| `F7` | SysEx end | Standard MIDI SysEx terminator |

The firmware validates all 6 header bytes sequentially, returning immediately if any mismatch occurs. A maximum of 10 data bytes are accepted (checked via `cp c, 0xA` at entry).

### Command Dispatch

After header validation, the firmware reads the command byte and dispatches to one of four parameter handlers:

| Command | Handler | DSP Config | Voice Range | Description |
|---------|---------|------------|-------------|-------------|
| `0x30` | `SysEx_ApplyVoiceParam_4B` | `0x4B00` | 0-7 (8 voices) | Standard voice parameter, bank 4B |
| `0x33` | `SysEx_ApplyVoiceParam_4B_128` | `0x4B00` | 0-127 (128 voices) | Extended voice parameter, bank 4B |
| `0x38` | `SysEx_ApplyVoiceParam_49` | `0x4900` | 0-7 (8 voices) | Standard voice parameter, bank 49 |
| `0x3A` | `SysEx_ApplyVoiceParam_49_128` | `0x4900` | 0-127 (128 voices) | Extended voice parameter, bank 49 |

Commands `0x30`/`0x33` control DSP parameter bank `0x4B` (likely mixer/effects), while `0x38`/`0x3A` control bank `0x49` (likely oscillator/filter). The `_128` variants allow addressing up to 128 voice slots instead of the standard 8.

### Channel Routing

The header's implicit channel (derived from the SysEx stream position) determines the target voice data base address:

- **Channel 0:** Base at `0x00F180 + 0x2E0` — main voice parameter area
- **Channels 1-15:** Base at `0x0AB000 + (channel - 1) * 0x800 + 0x2E0` — per-channel voice areas (each channel gets a 2KB block)

### Voice Parameter Application

Each handler follows the same pattern:

1. **Clamp** the voice index to valid range (0-7 or 0-127) via `SysEx_ClampVoiceIndex*`
2. **Look up** the voice slot from a table (at `0xEE33A4` for 8-voice, `0xEE33AC` for 128-voice)
3. **Write** the parameter value via `DSPCfg_WriteParamSimple`
4. **Iterate** active voice slots (from `DSPCfg_ReadParam_Map0` at `0x4B04`/`0x4904`), applying the same parameter to all matching slots
5. **Restore** the original slot ID if the base address was temporarily modified

The per-channel dispatch tables (`SysEx_DispatchByChannel` at `0xFDAD71`, `SysEx_DispatchByChannel_49` at `0xFDADA0`) route parameters to up to 8 hardware channels, using jump tables at `0xEE3520`.

## SysEx Parser State Machine

`SysEx_ParserLoop` (`0xFD8D2B`) implements a 3-state parser for incoming SysEx streams read from the sequencer buffer:

### States (stored at DRAM address 48414)

| State | Action | Transition |
|-------|--------|------------|
| 0 | Wait for `0xF0` (SysEx start) | → State 1 on match |
| 1 | Check manufacturer ID | → State 2 if `0x50`, `0x7E`, or `0x41`; → State 0 otherwise |
| 2+ | Accumulate data bytes | → Process on `0xF7` (SysEx end); → State 0 on invalid |

### Accepted Manufacturer IDs

| ID | Manufacturer | Usage |
|----|-------------|-------|
| `0x41` | Roland | GS voice parameter commands |
| `0x50` | Technics (Panasonic) | Proprietary mode commands |
| `0x7E` | Universal Non-Realtime | Standard MIDI extensions (GM System On, etc.) |

Data bytes (bit 7 clear) are accumulated via `VoiceQueue_Append`. The buffer limit is checked against address 48212 (if the 16-bit value at that address reaches `0xFF`, further data is rejected). When `0xF7` is received, the accumulated message is processed by `SeqData_InitPlaybackFromField`.

## Bulk Data Transfer (SysEx Exclusive Functions)

The KN5000 supports bulk data transfer for six data types, each with a named handler function (names stored as ROM strings at `0xE555A4`-`0xE555EC`):

| Function | ROM String | Data Type | Jump Table Base |
|----------|-----------|-----------|-----------------|
| `ExcSendFunc` | "ExcSendFunc" | Main send dispatch | N/A (dispatches to others) |
| `ExcDotFunc` | "ExcDotFunc" | Data Object Transfer | `0xE7FD8A` |
| `ExcPmemFunc` | "ExcPmemFunc" | Panel Memory (PM1-PM8) | `0xE7FDD6` |
| `ExcSmemFunc` | "ExcSmemFunc" | Sound Memory banks | `0xE7FDEA` |
| `ExcCompFunc` | "ExcCompFunc" | Composer/arranger data | `0xE7FDFE` |
| `ExcSeqFunc` | "ExcSeqFunc" | Sequencer song data | `0xE7FE12` |
| `ExcMspFunc` | "ExcMspFunc" | Music Style Programmer | `0xE7FE26` |

### Handler Architecture

Each `Exc*Func` handler (except `ExcSendFunc`) follows an identical pattern:

1. Subtract `0x1E0003E` from the index parameter (XBC) to normalize
2. Validate range 0-9
3. Look up a 16-bit handler offset from the type-specific jump table
4. Dispatch via `jp_dri` (jump through indexed table)

The handlers support 10 sub-operations (indices 0-9) per data type, covering operations like initiate transfer, send data block, receive data block, verify checksum, and complete transfer.

### ExcSendFunc

`ExcSendFunc` (`0xF76688`) is the top-level entry point. It validates the message type (`0x1C00007`), then calls `MainExcSend`, which dispatches to `SysEx_InitiateSend` based on an index (0-5) looked up from a table at `0xE7FD84`.

### SysEx_InitiateSend

`SysEx_InitiateSend` (`0xFD8C7F`) configures the SysEx send mode:

1. Sets bit 7 of the mode byte (DRAM 48380)
2. Sets the SysEx active flag (bit 6 of DRAM 48408)
3. Clears all MIDI channel states (`MidiChan_ClearAllStates`)
4. Dispatches to one of 6 mode-specific handlers via a jump table at `0xEE2F7E`

When the mode is deactivated (bit 7 clear), it clears the SysEx flag and calls `SoundMode_ResetAllParams`.

## Roland GS Compatibility

The KN5000's acceptance of Roland GS SysEx (manufacturer `0x41`) provides compatibility with Roland-format MIDI files and sequencers. This allows:

- **External sequencers** using Roland GS protocol to control the KN5000's voice parameters in real time
- **GS-format MIDI files** to play back with correct voice assignments
- **MIDI accompaniment files** that embed GS SysEx for voice setup

The command mapping (`0x30`/`0x33` → bank 4B, `0x38`/`0x3A` → bank 49) corresponds to Roland GS address space `40 01 3x`, which covers Part parameters in the GS specification:

| GS Address | Meaning |
|-----------|---------|
| `40 01 30` | Tone number (instrument) |
| `40 01 33` | Rx. Note On |
| `40 01 38` | Scale tuning |
| `40 01 3A` | CAf Pitch Control |

## Code References

| Symbol | Address | Purpose |
|--------|---------|---------|
| `MIDI_SendSysExCmd` | `0xFEBDA3` | Send Technics SysEx (F0 50 87 param) |
| `MIDI_SendCmdPacket` | `0xFEB55F` | Low-level MIDI packet transmit |
| `SysEx_ValidateRolandHeader` | `0xFDAD57` | Validate incoming Roland GS header |
| `SysEx_ApplyVoiceParam_4B` | `0xFDAD9A` | Apply voice param, bank 4B, 8 voices |
| `SysEx_ApplyVoiceParam_4B_128` | `0xFDADF2` | Apply voice param, bank 4B, 128 voices |
| `SysEx_ApplyVoiceParam_49` | `0xFDAE58` | Apply voice param, bank 49, 8 voices |
| `SysEx_ApplyVoiceParam_49_128` | `0xFDAEC4` | Apply voice param, bank 49, 128 voices |
| `SysEx_DispatchByChannel` | `0xFDAD71` | Route param to channel (bank 4B) |
| `SysEx_DispatchByChannel_49` | `0xFDADA0` | Route param to channel (bank 49) |
| `SysEx_ClampVoiceIndex8` | `0xFDACD4` | Clamp voice index to 0-7 |
| `SysEx_ClampVoiceIndex128` | `0xFDAD07` | Clamp voice index to 0-127 |
| `SysEx_ParserLoop` | `0xFD8D2B` | SysEx stream parser state machine |
| `SysEx_InitiateSend` | `0xFD8C7F` | Initiate bulk SysEx send |
| `MidiSysEx_CmdDispatchLoop` | `0xF24171` | MIDI status byte dispatcher (0x81-0xF0) |
| `ExcSendFunc` | `0xF76688` | Main SysEx send handler |
| `ExcDotFunc` | `0xF766A6` | Data Object Transfer handler |
| `ExcPmemFunc` | `0xF76706` | Panel Memory SysEx handler |
| `ExcSmemFunc` | `0xF76764` | Sound Memory SysEx handler |
| `ExcCompFunc` | `0xF767C2` | Composer SysEx handler |
| `ExcSeqFunc` | `0xF76820` | Sequence SysEx handler |
| `ExcMspFunc` | `0xF7687E` | MSP SysEx handler |

## References

- [MIDI Subsystem](/midi-subsystem/) — MIDI dispatch and channel handling
- [Audio Subsystem](/audio-subsystem/) — Sound generation and DSP configuration
- [Sequencer](/sequencer/) — MIDI recording and playback
- [Inter-CPU Protocol](/inter-cpu-protocol/) — Main/Sub CPU MIDI routing

---

*Last updated: March 2026*
