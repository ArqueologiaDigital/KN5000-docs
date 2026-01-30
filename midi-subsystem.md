---
layout: page
title: MIDI Subsystem
permalink: /midi-subsystem/
---

# MIDI Subsystem

The KN5000 has two distinct MIDI paths: external MIDI I/O (handled by Main CPU) and internal MIDI-like messages between Main CPU and Sub CPU for audio synthesis.

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │            MAIN CPU                      │
                    │                                          │
   MIDI IN ────────►│  ┌──────────────┐   ┌──────────────┐   │
   (5-pin DIN)      │  │ MIDI Parser  │──►│ MIDI Router  │   │
                    │  └──────────────┘   └──────┬───────┘   │
                    │                            │            │
   MIDI OUT ◄───────│  ┌──────────────┐         │            │
   (5-pin DIN)      │  │ MIDI Output  │◄────────┤            │
                    │  └──────────────┘         │            │
                    │                            │            │
   MIDI THRU ◄──────│  (Hardware echo)          │            │
   (5-pin DIN)      │                            ▼            │
                    │                   ┌──────────────┐      │
                    │                   │ Audio_DMA_   │      │
                    │                   │ Transfer     │      │
                    │                   └──────┬───────┘      │
                    └──────────────────────────┼──────────────┘
                                               │
                              Latch @ 0x120000 │
                                               ▼
                    ┌──────────────────────────────────────────┐
                    │             SUB CPU                       │
                    │                                           │
                    │  ┌────────────────────────────────────┐  │
                    │  │         MIDI_Dispatch              │  │
                    │  │         (0x034D93)                 │  │
                    │  │                                    │  │
                    │  │  Parse status byte (0x80-0xF0)     │  │
                    │  │  Route to voice parameter handlers │  │
                    │  └────────────────────────────────────┘  │
                    │                    │                      │
                    │     ┌──────────────┼──────────────┐      │
                    │     ▼              ▼              ▼      │
                    │  Voice_NoteOn  Voice_CtrlChange  ...     │
                    │  (0x02CF97)    (0x02A282)                │
                    └──────────────────────────────────────────┘
```

## Internal MIDI Processing (Sub CPU)

The Sub CPU's `MIDI_Dispatch` routine processes MIDI-like messages from the Main CPU via a ring buffer.

### Status Byte Dispatch

| Status | Range | Handler | Voice Handler | Description |
|--------|-------|---------|---------------|-------------|
| 0x80 | Note Off | `MIDI_Status_NoteOn` | `Voice_NoteOn` | Handled as Note On with velocity 0 |
| 0x90 | Note On | `MIDI_Status_NoteOn` | `Voice_NoteOn` | Note On (3-6 bytes) |
| 0xB0 | Control Change | `MIDI_Status_CtrlChange` | `Voice_CtrlChange` | CC messages (3 bytes) |
| 0xC0 | Program Change | `MIDI_Status_ProgChange` | `Voice_ProgChange` | Patch selection (4 bytes) |
| 0xD0 | Channel Pressure | `MIDI_Status_ChanPressure` | `Voice_ChanPressure` | Aftertouch (3 bytes) |
| 0xE0 | Pitch Bend | `MIDI_Status_PitchBend` | `Voice_PitchBend` | Pitch wheel (3 bytes) |
| 0xF0 | System | `MIDI_Status_System` | `Voice_SystemMsg` | System messages (3 bytes) |

### Message Format

Messages are read from the ring buffer at 0x2B0D:

```
Note On (standard):     [status] [channel] [note] [velocity]
Note On (extended):     [status|0x08] [channel] [note] [vel] [param1] [param2]
Control Change:         [status] [channel] [cc#] [value]
Program Change:         [status] [channel] [program] [bank_lsb] [bank_msb]
Channel Pressure:       [status] [channel] [pressure] [param]
Pitch Bend:             [status] [channel] [lsb] [msb]
System:                 [status] [data1] [data2] [data3]
```

### Dispatch Flow

```asm
MIDI_Dispatch:
    PUSH XIZ
    LDA XIZ, 2B0Dh              ; Ring buffer control structure
    LD WA, (XIZ + 004h)         ; Get byte count
    CALL RingBuf_SetOffsetHi    ; Set read position
    JRL T, MIDI_Dispatch_NextByte

MIDI_Dispatch_ParseStatus:
    LD WA, HL
    AND WA, 00F0h               ; Mask to get status nibble
    CP WA, 00F0h
    JRL Z, MIDI_Status_System   ; 0xF0: System messages
    CP WA, 00E0h
    JRL Z, MIDI_Status_PitchBend ; 0xE0: Pitch Bend
    CP WA, 00D0h
    JRL Z, MIDI_Status_ChanPressure ; 0xD0: Channel Pressure
    ; ... continue for other status bytes
```

## Control Change Handlers

The `Voice_CtrlChange` routine dispatches to specific handlers based on CC number:

### Standard MIDI Controllers

| CC# | Handler | Parameter | Notes |
|-----|---------|-----------|-------|
| 0x01 | `Voice_CC_ModWheel` | Modulation Wheel | Vibrato depth |
| 0x07 | `Voice_CC_Volume` | Main Volume | Channel volume |
| 0x0A | `Voice_CC_Pan` | Pan | Stereo position |
| 0x0B | `Voice_CC_Expression` | Expression | Dynamics control |
| 0x40 | `Voice_CC_Sustain` | Sustain Pedal | Hold notes |
| 0x5B | `Voice_CC_Sostenuto` | Sostenuto | Selective sustain |
| 0x5D | `Voice_CC_Soft` | Soft Pedal | Reduce volume/brightness |
| 0x5E | `Voice_CC_Portamento` | Portamento | Glide control |

### Proprietary Controllers

| CC# | Handler | Parameter | Notes |
|-----|---------|-----------|-------|
| 0x91 | `Voice_CC_91` | Reverb Depth | Effect send level |
| 0x95 | `Voice_CC_95` | Chorus Depth | Effect send level |
| 0x97 | `Voice_CC_97` | Unknown | Proprietary effect |
| 0x9B | `Voice_CC_9B` | Unknown | Proprietary effect |
| 0x9C | `Voice_CC_9C` | Unknown | Proprietary effect |
| 0x9D | `Voice_CC_9D` | Unknown | Proprietary effect |

### CC Handler Structure

```asm
Voice_CtrlChange:
    ; Entry: XIZ = pointer to 4-byte message
    ;   XIZ+0 = status (0xBn)
    ;   XIZ+1 = channel (0-25)
    ;   XIZ+2 = CC number
    ;   XIZ+3 = CC value

    CP (XIZ + 001h), 01Ah       ; Channel must be < 26
    JRL NC, Voice_CC_Exit

    LD A, (XIZ + 002h)          ; Get CC number
    CP A, 09Dh
    JRL Z, Voice_CC_9D
    CP A, 09Ch
    JRL Z, Voice_CC_9C
    ; ... check other CC numbers
    CP A, 001h
    JR Z, Voice_CC_ModWheel
    ; etc.
```

## External MIDI (Main CPU)

The Main CPU handles external MIDI I/O via serial ports:

| Function | Description |
|----------|-------------|
| MIDI IN | Receives external MIDI, routes to internal synth or THRU |
| MIDI OUT | Transmits keyboard events, sequencer playback |
| MIDI THRU | Hardware echo of MIDI IN |

### MIDI Implementation

Based on KN5000 specifications:

| Feature | Support |
|---------|---------|
| Channels | 1-16 transmit and receive |
| Notes | Full 0-127 range |
| Velocity | Note On/Off |
| Aftertouch | Channel and polyphonic |
| Controllers | Standard + proprietary |
| Program Change | With bank select |
| System | Clock, Start/Stop/Continue |
| SysEx | Technics-specific messages |

## Code References

### Sub CPU (`subcpu/kn5000_subprogram_v142.asm`)

| Routine | Address | Description |
|---------|---------|-------------|
| `MIDI_Dispatch` | 0x034D93 | Main MIDI message dispatcher |
| `MIDI_Dispatch_ParseStatus` | 0x034DA2 | Parse status byte |
| `MIDI_Status_NoteOn` | 0x034E65 | Note On/Off handler |
| `MIDI_Status_CtrlChange` | 0x034EB2 | Control Change handler |
| `MIDI_Status_ProgChange` | 0x034EEB | Program Change handler |
| `MIDI_Status_ChanPressure` | 0x034F2D | Channel Pressure handler |
| `MIDI_Status_PitchBend` | 0x034F65 | Pitch Bend handler |
| `MIDI_Status_System` | 0x034F9C | System message handler |
| `Voice_NoteOn` | 0x02CF97 | Voice note-on processing |
| `Voice_CtrlChange` | 0x02A282 | Voice CC processing |
| `Voice_CC_ModWheel` | 0x02A306 | Mod wheel handler |
| `Voice_CC_Volume` | 0x02A31C | Volume handler |
| `Voice_CC_Pan` | 0x02A340 | Pan handler |

## Related Pages

- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) - Sound generation
- [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) - Main/Sub CPU communication
- [Sequencer]({{ site.baseurl }}/sequencer/) - MIDI recording/playback
- [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) - Local keyboard control

## Research Needed

- [ ] Document external MIDI serial port configuration
- [ ] Analyze MIDI routing logic in Main CPU
- [ ] Document Technics SysEx message format
- [ ] Map remaining proprietary CC handlers (0x97, 0x9B-0x9D)
- [ ] Document MIDI filter and channel assignment settings
