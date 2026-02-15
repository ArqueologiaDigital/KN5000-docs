---
layout: page
title: Audio Subsystem
permalink: /audio-subsystem/
---

# Audio Subsystem

The KN5000 audio subsystem handles all sound generation, processing, and output. The Sub CPU runs dedicated audio firmware that processes MIDI-like commands from the Main CPU and drives the DSP and DAC hardware.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MAIN CPU (TMP94C241F)                          │
│                                                                     │
│  Audio_Lock_Acquire ──► Audio_DMA_Transfer ──► Audio_Lock_Release   │
│                              │                                      │
│              Latch @ 0x120000 (Inter-CPU Communication)             │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       SUB CPU (TMP94C241F)                          │
│                                                                     │
│  Boot ROM: 128KB @ 0xFE0000      Payload: 192KB (from Main CPU)     │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  AUDIO PROCESSING LOOP                       │   │
│  │                                                              │   │
│  │  ToneGen_Process_Notes ──► MIDI_Dispatch ──► Audio_Process_DSP │ │
│  │         │                       │                    │        │   │
│  │         ▼                       ▼                    ▼        │   │
│  │   [Keyboard Input]      [Ring Buffer]         [DSP State]     │   │
│  │   @ 0x110000            @ 0x2B0D              @ 0x3B60        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────┬─────────────────────┬──────────────────┬────────────────┘
           │                     │                  │
     [0x100000]            [Serial1]          [0x130000]
     Register               UART               DSP
     Config                Control             Config
           │                     │                  │
           ▼                     ▼                  ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  TONE GENERATOR │   │   DAC (IC313)   │   │   DUAL DSP      │
│  IC303          │   │   PCM69AU       │   │   IC310 + IC311  │
│                 │   │                 │   │                  │
│  64 voices      │   │  18-bit stereo  │   │  4 channels      │
│  28 params each │   │  (via serial)   │   │  0x20 bytes/ch   │
└────────┬────────┘   └────────┬────────┘   └──────────────────┘
         │                     │
   [0x110000]            [BCK/SDOR/SDOF]
   Keyboard Input        Serial Audio Bus
```

## Hardware Addresses

| Component | Address | Description |
|-----------|---------|-------------|
| Tone Gen Registers | 0x100000/0x100002 | Register-indirect config (64 voices, addr/data) |
| Tone Gen Keyboard | 0x110000/0x110002 | Voice events (status + note/velocity data) |
| Inter-CPU Latch | 0x120000 | Bidirectional data register |
| DSP Registers | 0x130000/0x130002 | Register-indirect config (4 channels, addr/data) |
| HDAE5000 PPI | 0x160000 | Parallel port interface (expansion) |

See [Tone Generator]({{ site.baseurl }}/tone-generator/) for the complete register map and chip inventory.

## Sub CPU Audio Processing

### Main Loop

The Sub CPU runs a continuous audio processing loop in the payload firmware:

```
Audio_System_Init:
    CALL InterCPU_Latch_Setup     ; Configure DMA channels
    CALL DSP_System_Init          ; Clear DSP state buffers
    CALL DSP2_Init                ; Initialize second DSP
    CALL DSP_Init_Channels        ; Configure 4 DSP channels
    CALL ToneGen_Init             ; Set tone generator mode

Main_Loop:
    CALL ToneGen_Process_Notes    ; Read keyboard input
    CALL MIDI_Dispatch            ; Process MIDI commands
    CALL Audio_Process_DSP        ; Update DSP state
    CALL Audio_Process_Final      ; Final audio update
    JR Main_Loop
```

### Command Dispatch Table

Commands from the Main CPU are dispatched based on the upper 3 bits:

| Cmd Range | Handler | Purpose |
|-----------|---------|---------|
| 0x00-0x1F | `Audio_CmdHandler_00_1F` | DSP/audio control - writes to ring buffer |
| 0x20-0x3F | `Audio_CmdHandler_20_3F` | Extended audio control |
| 0x40-0x5F | `Audio_CmdHandler_40_5F` | Audio parameters |
| 0x60-0x7F | `Audio_CmdHandler_60_7F` | Voice/DSP configuration |
| 0x80-0x9F | (Serial port setup) | 38400 baud configuration |
| 0xA0-0xBF | `Audio_CmdHandler_A0_BF` | System audio commands |
| 0xC0-0xFF | `Audio_CmdHandler_C0_FF` | Extended system commands |

### Ring Buffer

Audio commands use a 4KB circular ring buffer:

| Variable | Address | Description |
|----------|---------|-------------|
| Write Pointer | 0x2B0D | 12-bit circular index |
| Read Pointer | 0x2B0F | Current read position |
| Byte Count | 0x2B11 | Bytes available |
| Base Address | 0x2B13 | Buffer start |

**Key Routines:**
- `RingBuf_ReadByte` - Read single byte (returns 0xFFFF if empty)
- `RingBuf_SkipToEnd` - Skip remaining bytes in current message

## MIDI Message Processing

The `MIDI_Dispatch` routine parses MIDI-like status bytes and routes to handlers:

| Status | Handler | Voice Handler | Description |
|--------|---------|---------------|-------------|
| 0x80/0x90 | `MIDI_Status_NoteOn` | `Voice_NoteOn` | Note On/Off (velocity 0 = off) |
| 0xB0 | `MIDI_Status_CtrlChange` | `Voice_CtrlChange` | Control Change |
| 0xC0 | `MIDI_Status_ProgChange` | `Voice_ProgChange` | Program Change |
| 0xD0 | `MIDI_Status_ChanPressure` | `Voice_ChanPressure` | Channel Aftertouch |
| 0xE0 | `MIDI_Status_PitchBend` | `Voice_PitchBend` | Pitch Bend |
| 0xF0 | `MIDI_Status_System` | `Voice_SystemMsg` | System messages |

### Control Change Sub-handlers

The `Voice_CtrlChange` handler supports these controllers:

| CC# | Handler | Parameter |
|-----|---------|-----------|
| 0x01 | `Voice_CC_ModWheel` | Modulation Wheel |
| 0x07 | `Voice_CC_Volume` | Main Volume |
| 0x0A | `Voice_CC_Pan` | Pan/Balance |
| 0x0B | `Voice_CC_Expression` | Expression |
| 0x40 | `Voice_CC_Sustain` | Sustain Pedal |
| 0x5B | `Voice_CC_Sostenuto` | Sostenuto Pedal |
| 0x5D | `Voice_CC_Soft` | Soft Pedal |
| 0x5E | `Voice_CC_Portamento` | Portamento |
| 0x91 | `Voice_CC_91` | Reverb Depth |
| 0x95 | `Voice_CC_95` | Chorus Depth |
| 0x97-0x9D | `Voice_CC_97`-`Voice_CC_9D` | Proprietary effects |

## DSP Configuration

### Dual DSP Architecture

The Sub CPU controls two DSP chips:

- **DSP1**: Primary sound synthesis (initialized by `DSP_System_Init`)
- **DSP2**: Additional processing (initialized by `DSP2_Init`)

### DSP State Buffers

| Buffer | Address | Size | Purpose |
|--------|---------|------|---------|
| DSP State 1 | 0x041342 | 38 bytes | Primary DSP state |
| DSP State 2 | 0x041368 | 7462 bytes | Extended DSP state |
| DSP Config | 0x045310-18 | 12 bytes | Configuration parameters |
| DSP2 State | 0x3B60-64 | 6 bytes | Second DSP control |

### DSP Channel Configuration

Each of the 4 DSP channels has 0x20 bytes of register space at 0x130000:

```
Channel 0: 0x130000 - 0x13001F
Channel 1: 0x130020 - 0x13003F
Channel 2: 0x130040 - 0x13005F
Channel 3: 0x130060 - 0x13007F
```

**Key Routines:**
- `DSP_Init_Channels` - Initialize all 4 channels
- `DSP_Write_Channel` - Write 8 bytes of config to a channel
- `DSP_Send_Command` - Send command byte to DSP
- `DSP_Send_Data` - Send data byte to DSP

## Tone Generator

The tone generator (IC303, TC183C230002) is a custom Matsushita 64-voice wavetable synthesis LSI. It has two interfaces:

- **Register config** at 0x100000/0x100002: Write voice parameters and global settings via register-indirect addressing (28 params per voice, 13 global registers)
- **Keyboard input** at 0x110000/0x110002: Read voice events (note on/off with velocity)

See [Tone Generator]({{ site.baseurl }}/tone-generator/) for the complete register map, initialization sequence, and chip inventory.

### Voice Slot Table

16 voice slots at 0x4A4C-0x4A5C track active notes:
- 0xFF = note active
- 0x00 = slot available

### Key Routines

| Routine | Address | Description |
|---------|---------|-------------|
| `ToneGen_Config_Init` | 0x02DFCF | Configure all 64 voices and global registers |
| `ToneGen_Init` | 0x03D016 | Set mode to 6, start polling |
| `ToneGen_Poll_Init` | 0x03D227 | Read initial voice state (16 slots) |
| `ToneGen_Process_Notes` | 0x03D01E | Process keyboard events in main loop |
| `ToneGen_Read_Voice_Data` | 0x03D0C5 | Read note/velocity from hardware |
| `ToneGen_Calc_Pitch` | 0x03D11F | Calculate pitch value |

### Hardware Access

- P6.7 controls A23 address line for tone generator access
- Status read: 0x110002 (bit 0 = data ready)
- Data read: 0x110000 (16-bit: low byte = note, high byte = velocity)
- Register write: 0x100000 (address), 0x100002 (data) with P6.7 chip-select protocol

## Sound Categories

The Main CPU organizes sounds into 16 categories with pointers at 0xE023B0:

| Index | Category |
|-------|----------|
| 0 | PIANO |
| 1 | GUITAR |
| 2 | STRINGS & VOCAL |
| 3 | BRASS |
| 4 | FLUTE |
| 5 | SAX & REED |
| 6 | MALLET & ORCH PERC |
| 7 | WORLD PERC |
| 8 | ORGAN & ACCORDION |
| 9 | ORCHESTRAL PAD |
| 10 | SYNTH |
| 11 | BASS |
| 12 | DIGITAL DRAWBAR |
| 13 | ACCORDION REG. |
| 14 | GM SPECIAL |
| 15 | DRUM KITS |

## Code References

### Main CPU (`maincpu/kn5000_v10_program.asm`)

| Routine | Address | Description |
|---------|---------|-------------|
| `Audio_Lock_Acquire` | 0xEF1FEE | Acquire inter-CPU lock |
| `Audio_Lock_Release` | 0xEF1F0F | Release inter-CPU lock |
| `Audio_DMA_Transfer` | 0xEF341B | Core DMA transfer |
| `Audio_InitDMAChannels` | 0xEF329E | Initialize DMA channels |

### Sub CPU (`subcpu/kn5000_subprogram_v142.asm`)

| Routine | Address | Description |
|---------|---------|-------------|
| `Audio_System_Init` | 0x01FACB | Master audio initialization |
| `MIDI_Dispatch` | 0x034D93 | MIDI message dispatcher |
| `Audio_CmdHandler_00_1F` | 0x034D5F | Audio command handler |
| `Voice_NoteOn` | 0x02CF97 | Note On processing |
| `Voice_CtrlChange` | 0x02A282 | Control Change processing |
| `DSP_System_Init` | 0x034C45 | DSP initialization |
| `ToneGen_Init` | 0x03D016 | Tone generator init |

## Related Pages

- [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) - Communication details
- [MIDI Subsystem]({{ site.baseurl }}/midi-subsystem/) - External MIDI handling
- [CPU Subsystem]({{ site.baseurl }}/cpu-subsystem/) - Main and Sub CPU details
- [System Overview]({{ site.baseurl }}/system-overview/) - Overall architecture

## Serial Port 1 Interface

The Sub CPU's serial port 1 connects to an audio peripheral (likely the DAC IC313 or one of the DSPs) for control commands. The "SA" designation in the service manual schematics refers to "Sub Address" bus lines, not a chip name.

| Parameter | Value |
|-----------|-------|
| Mode | 8-bit UART (SC1MOD = 0x29) |
| Baud Rate | ~500kHz (20MHz / 4 / 10) |
| Sync Byte | 0xFE (sent at init and periodically) |
| TX Buffer | 1024 bytes at 0x0A00-0x0DFF |
| RX Buffer | 512 bytes at 0x0E16-0x1015 |

See [Tone Generator]({{ site.baseurl }}/tone-generator/#serial-port-1-sa-interface) for details.

## Related Pages

- [Tone Generator]({{ site.baseurl }}/tone-generator/) -- Register map and chip inventory
- [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) -- Communication details
- [SubCPU Payload Loading]({{ site.baseurl }}/subcpu-payload-loading/) -- How firmware reaches the SubCPU
- [MIDI Subsystem]({{ site.baseurl }}/midi-subsystem/) -- External MIDI handling
- [CPU Subsystem]({{ site.baseurl }}/cpu-subsystem/) -- Main and Sub CPU details
- [System Overview]({{ site.baseurl }}/system-overview/) -- Overall architecture

## Research Needed

- [ ] Document waveform ROM format and sample layout
- [ ] Analyze DSP effects processing algorithms
- [ ] Map remaining proprietary CC handlers (0x97-0x9D)
- [ ] Identify exact device on Serial Port 1 (trace PCB connections)
- [ ] Decode tone generator register semantics (pitch, envelope, filter, etc.)
- [ ] Analyze DSP1/DSP2 command sets
