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
│  Audio_Lock_Acquire ──> Audio_DMA_Transfer ──> Audio_Lock_Release   │
│                              │                                      │
│              Latch @ 0x120000 (Inter-CPU Communication)             │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  v
┌─────────────────────────────────────────────────────────────────────┐
│                       SUB CPU (TMP94C241F)                          │
│                                                                     │
│  Boot ROM: 128KB @ 0xFE0000      Payload: 192KB (from Main CPU)     │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  AUDIO PROCESSING LOOP                       │   │
│  │                                                              │   │
│  │  ToneGen_Process_Notes ──> MIDI_Dispatch ──> Audio_Process_DSP │ │
│  │         │                       │                    │        │   │
│  │         v                       v                    v        │   │
│  │   [Keyboard Input]      [Ring Buffer]         [DSP State]     │   │
│  │   @ 0x110000            @ 0x2B0D              @ 0x3B60        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────┬─────────────────────┬──────────────────┬────────────────┘
           │                     │                  │
     [0x100000]            [Serial1]          [0x130000]
     Register               UART               DSP
     Config                Control             Config
           │                     │                  │
           v                     v                  v
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
| DSP Ring Buffer | 0x3B60-64 | 6 bytes | Command ring buffer for DSP |
| EFF Mute Flags | 0x493A | 10 bytes | Per-DSP/EFF mute status (5 words) |
| EFF State | 0x4940 | variable | Per-EFF dirty/change flags |
| EFF Params | 0x4944 | variable | Per-EFF parameter dirty flags |
| Argo Change Flag | 0x493E | 2 bytes | Algorithm/routing change pending |
| EFF Type Table | 0x1ED6D | 5 bytes | Current effect type per EFF slot |

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

### DSP State Dispatcher Architecture

The Sub CPU firmware contains a master DSP state dispatcher at `DSP_State_Dispatcher` that orchestrates all DSP configuration changes. It is called via this chain:

```
Audio_System_Init (0x01FACB)        -- on boot
  -> DSP_System_Init (0x034C45)
    -> DSP_Reset (0x0360A3)
      -> LABEL_038E6E               -- full DSP reconfigure
        -> LABEL_036E3D              -- DSP state apply orchestrator
          -> DSP_State_Dispatcher    -- master DSP state dispatcher

Audio_Main_Loop (0x01FAEB)          -- at runtime
  -> Audio_Process_DSP (0x035A7D)   -- reads ring buffer at 0x3B60
    -> command 0x2D dispatch
      -> LABEL_035F32                -- sub-command router
        -> ... -> LABEL_036E3D -> DSP_State_Dispatcher (same chain)
```

The master dispatcher (`DSP_State_Dispatcher`) calls 11 sub-routines sequentially:

| Step | Routine | Description | Debug String |
|------|---------|-------------|--------------|
| 1 | `DSP_ResetLoop` | DSP reset loop (DSP 0,1) | "DSP %d reset." |
| 2 | `EFF_MuteLoop` | EFF mute loop (EFF 0-4) | "EFF %d mute." |
| 3 | `DSP_MuteLoop` | DSP mute loop (DSP 0,1) | "DSP %d mute." |
| 4 | `DSP_AlgorithmChangeCheck` | Argo change check | "argo change %d" |
| 5 | `EFF_WriteHeader` | EFF header (for EFF 0) | "EFF %d headder" |
| 6 | `EFF_DisconnectLoop` | EFF disconnect loop | "EFF %d disconnect." |
| 7 | `DSP_UnmuteLoop` | DSP antimute loop | "DSP %d antimute." |
| 8 | `EFF_HeaderChangeDataLoop` | EFF header+change+data | "EFF %d change %d", "EFF %d data change %d" |
| 9 | `EFF_LinkLoop` | EFF link loop | "EFF %d link." |
| 10 | `EFF_VolumeLoop` | EFF volume loop | "EFF %d vol %d", "EFF %d para%d edit %d" |
| 11 | `EFF_SecondaryLinkPath` | Secondary EFF link | "EFF %d disconnect." |

All 13 diagnostic format strings (at ROM 0x0122CC-0x012397) are triggered through this dispatcher. The strings are output via `Debug_Print_String` (0x038365) which sends characters through boot ROM serial output at `0xFFFEA1`.

### Inter-CPU Command Protocol (Command 0x2D — DSP Configuration)

The Main CPU sends DSP effect configuration changes to the Sub CPU via a layered protocol:

**Layer 1 — Latch Protocol:**

The Main CPU writes bytes to the inter-CPU latch at `0x120000`. The first byte is a header:

| Bits | Meaning |
|------|---------|
| 7-5 | Handler index (0-7 into `CMD_DISPATCH_TABLE` at `0xF428`) |
| 4-0 | Payload length minus 1 (DMA count = value + 1) |

For DSP config changes, header byte `0x7F` is used:
- Handler index = 3 → `Audio_CmdHandler_60_7F` (line 39422)
- Payload = 32 bytes (0x1F + 1)

The `INT0_HANDLER` (line 11247) reads the header byte directly, then sets up HDMA channel 0 to transfer the payload to buffer at `0x10F0`. After DMA completion, `MICRODMA_CH0_HANDLER` (line 11338) dispatches to the handler.

| Handler | Range | Routine | Purpose |
|---------|-------|---------|---------|
| 0 | 0x00-0x1F | `Audio_CmdHandler_00_1F` | MIDI/note commands → ring buffer at `0x2B0D` |
| 1 | 0x20-0x3F | `Audio_CmdHandler_20_3F` | Stub (unused) |
| 2 | 0x40-0x5F | `Audio_CmdHandler_40_5F` | (function at line 9619) |
| 3 | 0x60-0x7F | `Audio_CmdHandler_60_7F` | Audio/DSP commands → ring buffer at `0x3B60` |
| 4 | 0x80-0x9F | `Serial1_DataTransmit_Loop` | Serial port 1 data |
| 5 | 0xA0-0xBF | `Audio_CmdHandler_A0_BF` | (function at line 51502) |
| 6 | 0xC0-0xDF | `Audio_CmdHandler_C0_FF` | (function at line 10951) |
| 7 | 0xE0-0xFF | `Audio_CmdHandler_C0_FF` | Same as handler 6 |

**Layer 2 — Ring Buffer:**

`Audio_CmdHandler_60_7F` copies the 32-byte payload into a ring buffer at `0x3B60`:
- Write pointer: `(3B60h)` — 11-bit, wraps at 0x800 (2KB)
- Available count: `(3B64h)` — number of bytes queued
- Buffer base: `(3B66h)` — pointer to actual data area

Two consecutive 32-byte payloads give 64 bytes in the ring buffer for a single DSP config command.

**Layer 3 — Command Processing:**

`Audio_Process_DSP` (called from main loop) reads from the ring buffer. `DSP_Cmd_DequeueHeader` reads 7 header bytes into RAM `4369h`-`436Fh`, plus the command byte at `4368h`.

For command `0x2D` (DSP configuration), the 8-byte header is:

| Byte | RAM Address | Description |
|------|-------------|-------------|
| 0 | 4368h | Command byte = `0x2D` |
| 1 | 4369h | Sub-command (0 = normal config) |
| 2 | 436Ah | EFF slot selector (0x0A-0x0E → slot 0-4) |
| 3 | 436Bh | Reserved |
| 4 | 436Ch | Reserved |
| 5 | 436Dh | Reserved |
| 6 | 436Eh | Data length (0x38 = 56 bytes) |
| 7 | 436Fh | Update mode (0x00 = partial, 0xFF = full) |

Then `DSP_RingBuf_ReadAndCompare` (at 0x035A7E) reads 56 data bytes from the ring buffer into `4370h`-`43A7h`, comparing each byte with the existing slot buffer and counting changes.

**Layer 4 — EFF Slot Storage:**

The 56-byte parameter block is compared against the current slot buffer at `4496h + slot × 0x38`:

| EFF Slot | Buffer Address |
|----------|---------------|
| 0 | 0x4496 |
| 1 | 0x44CE |
| 2 | 0x4506 |
| 3 | 0x453E |
| 4 | 0x4576 |

Each slot contains 28 word-sized parameters. Word[0] is the **algorithm ID** (e.g., 0x0014 = algorithm 20 = CONCERT REVERB 1). The remaining words are effect-type-specific parameter values.

If any parameters changed, `DSP_ApplyConfig` (at 0x03616A) copies the full 290-byte DSP state (8-byte header + 5 × 56-byte slots) from `0x448E` to an allocated work buffer via `LABEL_038E31` (at 0x038E31), which marks it as dirty and triggers processing by the DSP state dispatcher.

### DSP Data Tables

The Sub CPU uses several lookup tables for DSP configuration:

| Address | Size | Description |
|---------|------|-------------|
| 0x1E496 | variable | EFF header config table |
| 0x1ED6D | 5 bytes | Per-EFF-slot DSP channel byte |
| 0x1ED72 | 5 bytes | Per-EFF-slot parameter count limit |
| 0x1ED7C | variable | EFF change config table (per sub-change) |
| 0x1EF0C | variable | EFF data change config table |
| 0x1F09C | N × 4 bytes | Per-algorithm register address table (pointers to register maps) |
| 0x1F22C | N × 4 bytes | Per-algorithm parameter mapping table (pointers to param data) |
| 0x1F3BC | variable | EFF mute config table |
| 0x1F3D0 | variable | DSP mute config table |
| 0x1F3E0 | variable | DSP unmute config table |
| 0x1F3F0 | variable | EFF disconnect config table |
| 0x1F404 | variable | EFF link config table |
| 0x122A6 | 2 × 11 bytes | Sparse parameter update sequences (for algorithms 0x0F and 0x35) |
| 0x12226 | variable | Per-algorithm byte (DSP channel assignment lookup) |

**Parameter Translation Chain:**

`DSP_WriteParameter` (at 0x03C190) translates a parameter index + algorithm ID into DSP register writes:

1. Look up `0x1F22C[algo_id]` → pointer to parameter mapping data (XDE)
2. Look up `0x1F09C[algo_id]` → pointer to register address data (XBC)
3. Call `DSP_ParameterWriteEngine` (at 0x03C9E6) which uses 12-byte stride tables at those pointers
4. The inner loop reads 3 words per parameter from the mapping data
5. Final DSP register writes go through tone generator at `0x130000`

Special cases: algorithms 9 and 10 for EFF slot 1 use hardcoded tables at `0x1E17F`/`0x1E19E` and `0x1E40A`/`0x1E42D` respectively.

The DSP write routines used by the dispatcher:

| Routine | Address | Description |
|---------|---------|-------------|
| `DSP_WriteEFFConfig` | 0x03C161 | Per-EFF DSP write (uses EFF-specific bytecode tables) |
| `DSP_WriteGlobalConfig` | 0x03C181 | Global DSP write (direct bytecode config) |
| `DSP_WriteParameter` | 0x03C190 | Parameter-specific DSP write (algo-indexed tables) |
| `DSP_ParameterWriteEngine` | 0x03C9E6 | Core DSP parameter write engine |
| `DSP_BytecodeInterpreter_Init` | 0x03C266 | Bytecode interpreter entry point |

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

## DSP Chip Identification

The KN5000 uses two custom DSP chips for effects processing:

| IC | Part Number | Manufacturer | Notes |
|----|-------------|-------------|-------|
| IC310 | MN19413 | Matsushita (Panasonic) | Custom ASIC, no public documentation |
| IC311 | DS3613GF-3BA | Unknown origin | Custom ASIC, no public documentation |

Both DSPs use an identical 8-bit parallel bus protocol with shared data lines but separate chip-select signals. They are NOT general-purpose DSPs — they are dedicated effects processors with a fixed command interface.

### DSP Control Pin Mapping

The Sub CPU controls both DSPs via GPIO pins:

| Pin | Port | Function |
|-----|------|----------|
| P7.3 | Port 7 bit 3 | Write strobe (active low) |
| P7.4 | Port 7 bit 4 | Read strobe (active low) |
| P7.5 | Port 7 bit 5 | CS1 — DSP1 chip select (IC310, MN19413) |
| P7.6 | Port 7 bit 6 | Command/Data select (1=command, 0=data) |
| PE.6 | Port E bit 6 | CS2 — DSP2 chip select (IC311, DS3613GF-3BA) |
| PH.0 | Port H bit 0 | Status input (busy/ready) |
| PZ[7:0] | Port Z | 8-bit bidirectional data bus |

**Handshake sequence** (DSP command write):
1. Set PZ = data byte
2. Set P7.6 = 1 (command mode) or 0 (data mode)
3. Assert CS (P7.5 or PE.6 low)
4. Assert write strobe (P7.3 low)
5. Wait for PH.0 ready
6. Deassert write/CS

### DSP Firmware / Microcode Loading

**The DSP chips do NOT receive external microcode from the Sub CPU.** Investigation of the SubCPU firmware reveals that no large code blocks are ever uploaded to the DSPs. Instead:

1. **DSPs are pre-programmed at manufacture** — The MN19413 (IC310) and DS3613GF-3BA (IC311) contain internal ROM with their instruction set already loaded. They are dedicated effects processors with a fixed command interface, not general-purpose programmable DSPs.

2. **Sub CPU controls DSPs via register writes only** — All communication uses the 8-bit parallel bus handshake protocol (Port PZ data, Port P7 control lines). The Sub CPU sends:
   - **Command bytes** (P7.6=1): Select DSP register or operation mode
   - **Data bytes** (P7.6=0): Write parameter values to selected register

3. **Configuration via bytecode interpreter** — The Sub CPU has a bytecode interpreter (`DSP_BytecodeInterpreter_Init` at 0x03C266) that reads compact bytecode programs from ROM and translates them into sequences of DSP command+data writes. This is a **Sub CPU-side** interpreter, not DSP microcode.

**Evidence:** The `DSP_WriteEFFConfig` and `DSP_WriteGlobalConfig` routines both call `DSP_BytecodeInterpreter_Init` with ROM pointers to bytecode tables (at 0x14777 for EFF configs, 0x147B3 for global configs). These tables contain opcodes like:
- `0x0-0x4`: DSP register write operations
- `0x0D`: State change notification
- `0x0E`: Send command+data sequence
- `0x0F`: End of program

**Implication for emulation:** The DSP chips must be emulated with their internal behavior intact. Since no dumps of the DSP internal ROMs exist, the DSP behavior must be reverse-engineered from the register interface (what the SubCPU writes) and the resulting audio output. This is the primary remaining challenge for accurate sound emulation.

### DSP Preset Structure

The 0x91-word (290-byte) block at SubCPU RAM address 0xF01E contains **effect parameter presets**, not DSP microcode. The structure is:

| Offset | Size | Content |
|--------|------|---------|
| +0x00 | 20 words | Header / global effect config |
| +0x28 | 5 × ~24 words | Effect parameter blocks |

Each effect block contains parameters:
- **Type** (effect algorithm selector: 1, 3, 4, 8)
- **Level** (0-99)
- **Depth** (0-99)
- **Time** (0-99)
- **Rate** (0-99)
- **Mix** (dry/wet balance, 0-99)
- **Feedback** (0-99)

### Effect Type Name Table

The Main CPU ROM contains a 128-entry effect type name table at address `0xE32A7A` (pointer table) with 16-character padded strings at `0xE32C7A`-`0xE33579`. 100 entries are named; the rest are unused (`----------`).

**Modulation Effects (0-6):**

| Index | Name |
|-------|------|
| 0 | NO OPERATION |
| 1 | CHORUS |
| 2 | MODULATED CHORUS |
| 3 | ENHANCER |
| 4 | FLANGER |
| 5 | PHASER |
| 6 | ENSEMBLE |

**Delay & Gated Effects (8-11):**

| Index | Name |
|-------|------|
| 8 | GATED REVERB |
| 9 | SINGLE DELAY |
| 10 | MULTI TAP DELAY |
| 11 | MODULATION DELAY |

**Reverbs (15-27):**

| Index | Name |
|-------|------|
| 15 | ROCK ROTARY |
| 16 | ROOM REVERB 1 |
| 17 | ROOM REVERB 2 |
| 18 | PLATE REVERB 1 |
| 19 | PLATE REVERB 2 |
| 20 | CONCERT REVERB 1 |
| 21 | CONCERT REVERB 2 |
| 22 | DARK REVERB 1 |
| 23 | DARK REVERB 2 |
| 24 | BRIGHT REVERB 1 |
| 25 | BRIGHT REVERB 2 |
| 26 | WAVE REVERB 1 |
| 27 | WAVE REVERB 2 |

**Drive & Dynamics (32-39):**

| Index | Name |
|-------|------|
| 32 | DISTORTION |
| 33 | OVERDRIVE |
| 34 | FUZZ |
| 35 | EXCITER |
| 36 | COMPRESSOR |
| 37 | SLOW ATTACKER |
| 38 | NOISE FLANGER |
| 39 | PARAMETRIC EQ |

**Special Effects (44-60, 63):**

| Index | Name |
|-------|------|
| 44 | CEL |
| 45 | CELM |
| 48 | AUTO PAN |
| 49 | PITCH SHIFTER |
| 50 | VIBRATO |
| 51 | PEDAL WAH |
| 52 | AUTO WAH |
| 53 | ROTARY SPEAKER |
| 54 | RING MODULATOR |
| 55 | HARS EFFECT |
| 56 | MIX UP |
| 57 | STANDARD |
| 58 | PERCUSSIVE |
| 59 | SYMPHONIC |
| 60 | DEEP SPACE |
| 63 | STRING |

**Combination Effects (64-75, 79-81, 88-91, 96-99):**

| Index | Name |
|-------|------|
| 64 | S.DELAY+CHORUS |
| 65 | S.DELAY+S.DELAY |
| 66 | S.DELAY+FLANGER |
| 67 | S.DELAY+VIBRATO |
| 68 | S.DELAY+PHASER |
| 69 | PEDAL WAH+DELAY |
| 70 | AUTO WAH+S.DELAY |
| 71 | PEQ+CHORUS |
| 72 | PEQ+S.DELAY |
| 73 | PEQ+FLANGER |
| 74 | PEQ+VIBRATO |
| 75 | PEQ+COMPRESSOR |
| 79 | GEQ |
| 80 | DS_D |
| 81 | OVER_D |
| 88 | ROOM |
| 89 | KARAOKE |
| 90 | BATH ROOM |
| 91 | STAGE |
| 96 | PEQ+COMPR+DIST |
| 97 | PEQ+COMPR+OVERDR |
| 98 | PEQ+DIST+DELAY |
| 99 | PEQ+OVERDR+DELAY |

### Effect Parameter Names

84 effect parameter names are stored at Main CPU ROM `0xE324D0`-`0xE32A6A`:

| Index | Name | Index | Name |
|-------|------|-------|------|
| 0-1 | VOLUME | 33 | REVERB TIME |
| 2 | REV SEND | 34 | PRE DELAY |
| 3 | DRIVE | 35 | HIGH DAMP GAIN |
| 4 | ADJUST | 36 | ER.LEVEL |
| 5 | EMPHASIS GAIN | 37-38 | PITCH L/R |
| 6 | DEPTH | 39 | THRESHOLD |
| 7 | LFO SPEED | 40 | RATIO |
| 8 | SLOW LFO SPEED | 41-42 | ATTACK/RELEASE SENS. |
| 9 | FAST LFO BALANCE | 43-44 | ATTACK/RELEASE RATE |
| 10 | RESONANCE | 45-46 | GATE/MASK TIME |
| 11 | MANUAL | 47 | HARS TIME |
| 12 | SLOW/FAST | 48-49 | LFO/OSC WAVEFORM |
| 13 | TREBLE FAST | 50-52 | BAND EMPHASIS FC/Q/G |
| 14 | SLOW | 53-54 | LOW/HIGH MIX |
| 15-16 | WIND UP/DOWN | 55 | PHASE |
| 17-18 | BASS FAST/SLOW | 56 | FEEDBACK |
| 19 | VOLUME ADJUST | 57 | SWEEP RANGE |
| 20 | OSC SPEED | 58 | WAH CENTER FC |
| 21-22 | DELAY L/R | 59-60 | HARS TIME L/R |
| 23-24 | FEEDBACK L/R | 61-62 | BALANCE L/R |
| 25-28 | DRY/WET (various) | 63-64 | FAST LFO SPEED L/R |
| 29-32 | EMPHASIS FC/G | 65 | MODULATION DEPTH |
| 66-69 | DRY/WET (combos) | 82 | INTENSITY |
| 70 | FAST LFO SPEED | 83 | EXCITE |
| 71-73 | TREBLE/BASS DEPTH | 74-77 | DELAY 1-4 |
| 78-81 | PAN 1-4 | | |

### Known DSP Commands

| Command | Direction | Description |
|---------|-----------|-------------|
| 0x01 | Write | Initialize/reset |
| 0x03 | Write | Set mode/algorithm |
| 0x30 | Write | Parameter update (followed by data bytes) |
| 0x60 | Write | Bulk transfer start |

## Keybed Architecture

The physical keyboard (keybed) connects **directly** to the tone generator IC303, NOT to the Sub CPU. IC303 performs hardware key scanning internally and presents note events to the Sub CPU via the keyboard input interface at 0x110000.

This means:
- The CPU does **not** scan the keyboard matrix
- IC303 handles debouncing, velocity detection, and polyphony assignment
- The Sub CPU simply reads completed note events from IC303's output register

See [Keybed Scanning]({{ site.baseurl }}/keybed-scanning/) for the complete note flow, encoding format, and voice slot management.

## Research Needed

- [ ] Document waveform ROM format and sample layout
- [ ] Map remaining proprietary CC handlers (0x97-0x9D)
- [ ] Decode tone generator register semantics (pitch, envelope, filter, etc.)
- [ ] Decode per-algorithm parameter mapping tables at `0x1F22C`/`0x1F09C` (12-byte stride entries)
- [ ] Map MainCPU parameter indices (e.g., 33=REVERB TIME) to EFF block word positions per algorithm
- [ ] Decode DSP register semantics per channel (what registers 0x10-0x17 control)
- [ ] Document remaining inter-CPU command types (beyond 0x2D and 0xE1/E2/E3)
- [x] ~~Identify exact device on Serial Port 1~~ — Likely DAC IC313 control interface
- [x] ~~Analyze DSP1/DSP2 command sets~~ — Partial: 4 commands identified, preset structure decoded
- [x] ~~Extract effect type names from ROM~~ — Complete: 100 named effect types at MainCPU 0xE32A7A
- [x] ~~Extract effect parameter names from ROM~~ — Complete: 84 parameter names at MainCPU 0xE324D0
- [x] ~~Document DSP state dispatcher architecture~~ — Complete: `DSP_State_Dispatcher` and 11 sub-routines traced
- [x] ~~Trace inter-CPU command 0x2D protocol~~ — Complete: 4-layer protocol fully documented
- [x] ~~Map effect type indices to DSP register configurations~~ — Partial: translation chain traced through `DSP_WriteParameter` → `DSP_ParameterWriteEngine`, but per-algorithm ROM tables not yet decoded
- [x] ~~Determine if DSP microcode is loaded from ROM~~ — **No.** DSPs are pre-programmed; SubCPU only writes configuration via bytecode interpreter
- [ ] Reverse-engineer DSP register semantics by analyzing bytecode programs at 0x14777/0x147B3
- [ ] Determine if DSP internal ROM can be extracted (decapping, JTAG, etc.)
- [ ] Document bytecode interpreter opcode set completely (opcodes 0x0-0xF)
