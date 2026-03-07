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
│                                 │                                   │
│              Latch @ 0x120000 (Inter-CPU Communication)             │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  v
┌───────────────────────────────────────────────────────────────────────┐
│                       SUB CPU (TMP94C241F)                            │
│                                                                       │
│  Boot ROM: 128KB @ 0xFE0000      Payload: 192KB (from Main CPU)       │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │                  AUDIO PROCESSING LOOP                         │   │
│  │                                                                │   │
│  │  ToneGen_Process_Notes ──> MIDI_Dispatch ──> Audio_Process_DSP │   │
│  │         │                       │                    │         │   │
│  │         v                       v                    v         │   │
│  │   [Keyboard Input]        [Ring Buffer]         [DSP State]    │   │
│  │      @ 0x110000             @ 0x2B0D             @ 0x3B60      │   │
│  └────────────────────────────────────────────────────────────────┘   │
└──────────┬─────────────────────┬─────────────────────┬────────────────┘
           │                     │                     │
      [0x100000]             [Serial1]            [0x130000]
       Register                UART                   DSP
        Config                Control               Config
           │                     │                     │
           v                     v                     v
  ┌─────────────────┐   ┌─────────────────┐   ┌──────────────────┐
  │  TONE GENERATOR │   │   DAC (IC313)   │   │   DUAL DSP       │
  │  IC303          │   │   PCM69AU       │   │   IC310 + IC311  │
  │                 │   │                 │   │                  │
  │  64 voices      │   │  18-bit stereo  │   │  4 channels      │
  │  28 params each │   │  (via serial)   │   │  0x20 bytes/ch   │
  └────────┬────────┘   └────────┬────────┘   └──────────────────┘
           │                     │
       [0x110000]          [BCK/SDOR/SDOF]
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
- `DSP_Init_Channels` - Initialize all 4 channels with test pattern
- `DSP_Write_Channel` - Write 8 bytes of config to a channel (loop)
- `DSP_WriteAllChannelRegs` - Write register data to all 4 channels
- `DSP_WriteChannelRegs_Inner` - Write 8 sequential registers to one channel
- `DSP_Send_Command` - Send command byte to DSP
- `DSP_Send_Data` - Send data byte to DSP

### DSP Voice Coefficient Routing

The Sub CPU firmware includes a coefficient routing subsystem that maps voice parameters to DSP coefficient buffers. This system sits between the voice parameter tables and the DSP hardware, computing which coefficient set to apply based on voice allocation and routing type.

**Memory Layout:**

| Address | Size | Purpose |
|---------|------|---------|
| 0x041368 | 7462 bytes | Voice allocation table (26 channels × 287 bytes/channel) |
| 0x045210 | variable | DSP coefficient output buffer (written by routing functions) |
| 0x045310 | 4 bytes | Base pointer for routing table computation |
| 0x045314 | 4 bytes | Pointer to routing configuration structure |

The routing configuration structure (pointed to by 0x045314) contains pointers to coefficient source tables at various offsets:

| Offset | Purpose |
|--------|---------|
| +0x44 | Type-A coefficient table (group 0, default) |
| +0x48 | Type-A coefficient table (group 2, 128-191) |
| +0x4C | Type-A coefficient table (group 1, 64-127) |
| +0x50 | Type-A output pointer table |
| +0x54 | Algorithm coefficient table (default) |
| +0x58 | Type-B coefficient table (group 0, default) |
| +0x5C | Type-B coefficient table (group 2) |
| +0x60 | Type-B coefficient table (group 1) |
| +0x64 | Type-B output pointer table |
| +0x70 | Algorithm table (type 1) |
| +0x7C | Algorithm table (type 2) |
| +0x80-0x98 | Extended algorithm tables (types 3-4) |

**Routing Algorithm:**

The routing functions share a common pattern:

1. **Extract parameters**: Mask voice number to 7 bits, extract channel (low 4 bits of BC) and type (bits 6-7 of BC)
2. **Type dispatch**: 4-way branch based on type bits (0/64/128/192) to select coefficient source table
3. **Compute index**: `index = (channel << 7 + voice) × 2`, used as offset into the selected table
4. **Load source pointer**: Read 32-bit pointer from `table_base + index + (0x45310)`
5. **Copy coefficients**: Copy 13 bytes from source to DSP coefficient buffer at 0x45210

**Voice-specific routing** (`DSP_VoiceCoeffRoute`) adds a nested lookup:
1. Compute voice allocation index: `voice × 287 + channel × 37 + 110`
2. Read routing type from allocation entry at `0x41368 + index`
3. Use routing type bits to select coefficient source
4. Copy 13 coefficient bytes plus 3 extra configuration bytes

**Routing Functions (Sub CPU):**

| Function | Purpose |
|----------|---------|
| `DSP_RouteCoeffs_TypeA` | Route coefficients via type-A tables (offsets 0x44-0x50) |
| `DSP_RouteCoeffs_TypeB` | Route coefficients via type-B tables (offsets 0x58-0x64) |
| `DSP_CopyCoeffs_TypeA` | Direct coefficient copy (offset 0x50, no type dispatch) |
| `DSP_CopyCoeffs_TypeB` | Direct coefficient copy (offset 0x64, no type dispatch) |
| `DSP_VoiceCoeffRoute` | Voice-specific routing with allocation table lookup |
| `DSP_VoiceCoeffRoute2` | Extended voice routing with filter/vibrato coefficients |
| `DSP_AlgoCoeffLookup` | Algorithm-based coefficient selection (5-way dispatch, algo 0-4) |

### DSP Register Write Protocol

The `DSP_WriteChannelRegs_Inner` function reveals the register-level protocol for writing to DSP channels via 0x130000:

```
Register address = channel_number × 32 + 0x10

For each of 8 registers (sequential):
  1. Write register address byte to (0x130000)   ; select register
  2. Write data byte to (0x130002)               ; write value
  3. Increment register address

Data sources for 8 registers:
  Reg 0-1: From BC (caller's direct parameters)
  Reg 2-3: From prevbank QBC (alternate register bank)
  Reg 4-5: From DE (caller's direct parameters)
  Reg 6-7: From prevbank QDE (alternate register bank)
```

The prevbank register usage allows passing 8 bytes of data using only 4 register pairs, by using the TLCS-900/H2's alternate register bank.

**Utility Functions (Sub CPU):**

| Function | Purpose |
|----------|---------|
| `DSP_BlockCopyWords` | Block copy words via `ldirw` instruction |
| `DSP_FillMemWords` | Fill memory with repeated word value |
| `DSP_ChecksumRange` | Compute one's complement checksum of 32-bit word range |

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

The master dispatcher (`DSP_State_Dispatcher`) takes a pointer to a state structure in XWA:

```
State structure (at RAM, passed via XWA → XIZ):
  +0: (base)
  +2: algorithm change flag (1 = needs algorithm change)
  +4: mode flag (1 = reset/disconnect mode, other = normal)
  +6: algorithm number
```

The dispatcher follows a conditional 11-step pipeline:

| Step | Routine | Condition | Description |
|------|---------|-----------|-------------|
| 1a | `DSP_ResetLoop` | mode == 1 | Reset both DSP chips (assert/deassert reset lines) |
| 1b | `EFF_MuteLoop` | mode != 1 | Mute all 5 EFF channels via `DSP_WriteEFFConfig` |
| 2 | `DSP_MuteLoop` | always | Mute DSP hardware chips 0-1 via `DSP_WriteGlobalConfig` |
| 3 | `DSP_AlgorithmChangeCheck` | always | If global algo-change flag set, call `DSP_AlgorithmChange` |
| 4a | `EFF_WriteHeader` | mode==1 or algo_change | Write EFF header config for channel 0 |
| 4b | `EFF_DisconnectLoop` | mode==1 or algo_change | Disconnect all effect slots (iterate 4→0) |
| 5 | `DSP_UnmuteLoop` | always | Unmute DSP hardware chips 0-1 via `DSP_WriteGlobalConfig` |
| 6 | `EFF_HeaderChangeDataLoop` | always | Process per-slot header changes + parameter changes (5 slots) |
| 7 | `EFF_LinkLoop` | always | Re-link connected effect slots (iterate 4→0) |
| 8 | `EFF_VolumeLoop` | always | Update volume parameters for all effect slots (iterate 4→0) |
| 9 | `EFF_SecondaryLinkPath` | always | Two-pass: compute max delay, then re-link secondary paths |
| 10 | Algo state update loop | always | Iterate slots 4→0, update algorithm state at 0x12226 |

**EFF_MuteLoop Detail (Step 1b):**
Iterates EFF slots 0-4. For each slot with its mute flag set (at RAM 18736 + slot×2), sends mute config from pointer table at 0x1F3BC via `DSP_WriteEFFConfig`. If any slot was muted, schedules a 20-unit delay via `DSP_ScheduleDelay`.

**DSP_AlgorithmChange Detail (Step 3):**
When the DSP algorithm changes, loads 7 configuration blocks sequentially from ROM:

| Order | ROM Address | Channel | Purpose |
|-------|------------|---------|---------|
| 1 | 0x01E63C | 0 | Initial global config |
| 2 | 0x01E6BE | 0 | Channel 0 config |
| 3 | 0x01E996 | 1 | Channel 1 config A |
| 4 | 0x01EA12 | 1 | Channel 1 config B |
| — | (1-unit delay) | — | Wait for DSP to settle |
| 5 | 0x01E7C5 | 1 | Channel 1 post-delay A |
| 6 | 0x01E8A7 | 1 | Channel 1 post-delay B |
| 7 | 0x01E891 | 1 | Channel 1 post-delay C |
| 8 | 0x01E947 | 1 | Channel 1 post-delay D |

If mode == 1, de-asserts DSP2 reset before loading channel configs.

**EFF_HeaderChangeDataLoop Detail (Step 6):**
Calls `EFF_Change_Handler` for each dirty slot. The handler dispatches by slot number:
- Slots 0-1: Standard EFF change path → `EFF_Change_WithDebug`
- Slots 2-4: Algorithm-dependent path (mode==1 uses `EFF_Change_WithDebug`, otherwise `EFF_DataChange_WithDebug`)

`EFF_Change_WithDebug` writes two config blocks per change: a primary config from table at 0x1ED7C and a secondary from 0x1EF0C, both indexed by the change type. Special handling for channel 1 with types 0x9 and 0xA (hardcoded reverb/chorus ROM addresses).

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

### DSP Bytecode Interpreter

The Sub CPU uses a bytecode interpreter to batch-write DSP register configurations. This is **not** DSP microcode — it's a Sub CPU-side interpreter that translates compact ROM-resident programs into sequences of hardware register writes to the DSP chips.

**Entry Points:**

| Routine | Address | Config Table | Purpose |
|---------|---------|-------------|---------|
| `DSP_WriteEFFConfig` | 0x03C161 | 0x14777 | Per-effect channel writes (looks up DSP chip from channel mapping at 0x1ED6D) |
| `DSP_WriteGlobalConfig` | 0x03C181 | 0x147B3 | Global DSP writes (always targets DSP chip 0) |

Both call `DSP_BytecodeInterpreter_Init` (0x03C266) which loads a 12-byte config entry from the table and begins execution.

**Config Entry Format (12 bytes per entry, indexed by channel/slot):**

```
Offset  Size  Description
+0      word  Config parameter 0 (passed to handlers via stack)
+2      word  Config parameter 1
+4      word  Config parameter 2
+6      word  Config parameter 3
+8      long  Pointer to bytecode program data in ROM
```

Entries are indexed by channel number: entry address = table_base + channel × 12.

**Bytecode Format:**

Each instruction has a 2-byte header followed by data bytes:

```
Byte 0: [opcode:4][count_high:4]
Byte 1: [count_low:8]

count = (count_high << 8) | count_low - 2
```

The `count` field gives the number of data bytes following the header (after subtracting 2 for the header itself).

**Opcode Set:**

| Opcode | Name | Description |
|--------|------|-------------|
| 0x0 | DSP Write Type 0 | Basic DSP register write (offset 0x000 in handler table) |
| 0x1 | DSP Write Type 1 | Extended parameter write (offset 0x23A) |
| 0x2 | DSP Write Type 2 | Multi-register write variant (offset 0x333) |
| 0x3 | DSP Write Type 3 | Complex routing write (offset 0x3DA) |
| 0x4 | DSP Write Type 4 | Short parameter write (offset 0x473) |
| 0x5 | DSP Write Type 5 | Short config write (offset 0x48D) |
| 0x6-0xC | — | Invalid (skipped) |
| 0xD | State Change | Yields to task scheduler (`TaskSched_PreemptiveYield_INT`), then continues |
| 0xE | Send Command | Sends command byte + data bytes directly to DSP hardware |
| 0xF | End | Terminates bytecode execution |

**Opcode 0xE Detail (Send Command):**

```
[0xE | count] [cmd_byte] [data_byte_1] ... [data_byte_N]
```

1. First data byte sent via `DSP_DispatchCommand` (sets command register)
2. Remaining bytes sent via `DSP_DispatchData` (writes data to selected register)
3. `DSP_DispatchCommand`/`DSP_DispatchData` route to DSP1 or DSP2 based on the channel parameter

**Opcodes 0-5 Detail (Native Code Handlers):**

Opcodes 0-5 dispatch to native TLCS-900 machine code subroutines within the `DSP_Bytecode_Programs` block at 0x03C32E. The dispatch table at `OFFSETS_14739` (0x014739) contains 16-bit offsets from 0x03C32E:

| Opcode | Offset | Handler Address | Approximate Size |
|--------|--------|----------------|-----------------|
| 0 | 0x000 | 0x03C32E | 570 bytes |
| 1 | 0x23A | 0x03C568 | 249 bytes |
| 2 | 0x333 | 0x03C661 | 167 bytes |
| 3 | 0x3DA | 0x03C708 | 153 bytes |
| 4 | 0x473 | 0x03C7A1 | 26 bytes |
| 5 | 0x48D | 0x03C7BB | ~70 bytes |

These handlers use prevbank registers (D7 prefix), auto-increment addressing `(xRR+)`, and register-indirect compact forms to efficiently write multiple DSP registers in sequence. They read data bytes from the bytecode stream and route them to the DSP hardware via the parallel bus protocol. After completing, each handler jumps to `DSP_BytecodeInterpreter_CheckEnd` to continue the interpreter loop.

A secondary offset table at `OFFSETS_14745` (0x014745) provides shorter offsets for a variant dispatch path, suggesting some handlers have fast-path entry points.

**Common Handler Idiom:**

All opcode 0-5 handlers share this recurring pattern for reading and sending bytes:
```
ld XWA,(XSP+0x1a)     ; load bytecode program pointer
ld C,(XWA+)            ; read next byte (auto-increment pointer)
ld (XSP+0x1a),XWA     ; store updated pointer
ld A,C                 ; copy byte to A
extz WA                ; zero-extend to 16-bit
ld BC,(XSP+0x14)       ; load DSP channel number from stack
call DSP_DispatchCommand ; or DSP_DispatchData
ld QIZ,HL              ; save result to prevbank register
```

**Handler Parameter Packing:**

Different handlers use different parameter widths for DSP register values:

| Opcode | Packing | Shift | Config Param Used | Description |
|--------|---------|-------|-------------------|-------------|
| 0 | 12-bit | `srl 4` / `sll 4` | stack[10] (word 1) | Complex multi-path: branches on data byte value (0x00, 0x0A, or other) |
| 1 | 12-bit | `srl 4` / `sll 4` | stack[10] | Extended write with different branching |
| 2 | 12-bit | `srl 4` / `sll 4` | stack[10] | Multi-register variant |
| 3 | 16-bit | `srl 8` / `sll 8` | stack[14] (word 3) | Full 16-bit parameter values |
| 4 | — | — | — | Command-only: sends 1 byte as command, then returns |
| 5 | — | — | — | Command + data: sends command byte then data byte |

For 12-bit parameters, the value is packed across 2 bytecode bytes as `byte0[7:0] << 4 | byte1[7:4]`. This is split into two DSP data writes: high byte (`value >> 4`) and low byte (`(value << 4) & 0xFF`). This indicates **DSP registers use 12-bit parameter values** for most effect parameters.

For 16-bit parameters (opcode 3), the full 16-bit value is packed as `byte0[7:0] << 8 | byte1[7:0]`, split into high byte and low byte data writes.

**Execution Flow Example:**

When `DSP_WriteGlobalConfig` is called to mute DSP chip 0:

```
1. DSP_WriteGlobalConfig called with WA=0 (channel 0), XBC=pointer to mute config
2. Sets DE=0 (fixed for global writes)
3. Pushes XBC (config pointer), loads bytecode table pointer 0x147B3
4. Calls DSP_BytecodeInterpreter_Init:
   a. Loads 12-byte entry from 0x147B3 + 0*12 (channel 0)
   b. Copies 4 config words + 1 program pointer to stack frame
   c. Falls through to BytecodeInterpreter_CheckEnd
5. Interpreter reads first bytecode header from program pointer
6. Dispatches on opcode:
   - 0xE → sends command+data to DSP hardware
   - 0x0-0x5 → jumps to native handler for bulk register writes
   - 0xD → yields to scheduler, then continues
   - 0xF → terminates
7. Repeats until 0xF terminator encountered
```

### DSP Coefficient Setup Pipeline

The coefficient setup subsystem configures DSP processing parameters through a multi-stage pipeline. Eight functions handle different aspects of coefficient configuration:

| Function | Size | Purpose |
|----------|------|---------|
| `DSP_SetCoeff_CopyDirect` | 69B | Direct coefficient copy from routing tables |
| `DSP_SetCoeff_CopyDirect2` | 69B | Direct copy variant 2 |
| `DSP_SetCoeff_RouteComplex` | 344B | Complex routing with multi-table lookup |
| `DSP_SetCoeff_RouteWithCallback` | 291B | Routing with callback (calls 0x032AE0) |
| `DSP_SetCoeff_FullPipeline` | 384B | Multi-stage processing (0x032AE0 + 0x032682) |
| `DSP_SetCoeff_WithDispatch` | 135B | Type-dispatched coefficient selection |
| `DSP_SetCoeff_WriteParams` | 90B | Individual parameter writes to 0x045216/17 |
| `DSP_SetCoeff_MasterConfig` | 706B | Master configuration (calls 0x02B014) |

### Voice-to-DSP Output Configuration

The voice output configuration functions map synthesized voices to DSP effect channels:

| Function | Size | Purpose |
|----------|------|---------|
| `Voice_DSP_OutputConfig` | 237B | Configure voice→DSP routing (type 1) |
| `Voice_DSP_OutputConfig2` | 237B | Configure voice→DSP routing (type 2) |
| `Voice_DSP_SimpleCopy` | 91B | Simple voice parameter copy to DSP |
| `Voice_DSP_SimpleCopy2` | 91B | Simple copy variant 2 |
| `DSP_VoiceParam_Dispatch` | 155B | Voice parameter dispatch with bit-5 routing |

These functions implement the voice→DSP routing pipeline:
1. Call `DSP_AlgoType_Dispatch1` to determine the algorithm type for the voice
2. Store result to DSP state (0x04520E or 0x04520C)
3. Call `Voice_BuildOutputList` to enumerate active voice outputs
4. Iterate the output list, configuring each via `ToneGen_ExtParams56b_DataTable`
5. Loop until all voices processed (up to 128 for full config, 64 for simple copy)

## Synthesis Architecture

The KN5000 implements a **hardware wavetable synthesis** architecture: the Sub CPU firmware handles MIDI event processing, voice allocation, and parameter management, while the actual sound generation is performed entirely by the tone generator hardware (IC303, TC183C230002).

### Polyphony and Voice Management

| Parameter | Value |
|-----------|-------|
| MIDI Channels | 26 (channels 0-25) |
| Hardware Voices | 64 simultaneous |
| Voice Parameter Size | 287 bytes per MIDI channel (0x11F) |
| Hardware Voice Size | 71 bytes per voice (0x47) |
| Voice Template | 68 bytes at ROM 0xF8D5 (34 × 16-bit words) |
| Channel Parameter Base | 0x04136E (Sub CPU RAM) |
| Hardware Voice Pool | 0x04308E (Sub CPU RAM, 64 × 71 = 4544 bytes) |
| Voice Slot Table | 0x4A4C (16 active voice tracking slots) |

**Channel address formula:** `0x04136E + (channel_number × 0x11F)`

The firmware implements **dynamic voice allocation**: any of the 26 MIDI channels can be assigned to any of the 64 hardware voices on demand. When a Note On arrives, `Voice_Allocate` (0x02C9DF) acquires a free voice from a pool-based allocator at 0x2A4E with voice stealing for polyphony overflow.

### Voice Parameter Structure (287 bytes per MIDI channel)

Each MIDI channel maintains a 287-byte parameter block:

| Offset | Size | Parameter | Set By |
|--------|------|-----------|--------|
| +0x00 | 4 | Pitch base | Note On |
| +0x04 | 2 | Portamento flag | CC 0x95 |
| +0x06 | 2 | Volume (scaled) | CC 0x07 |
| +0x08 | 2 | Pan | CC 0x0A |
| +0x0A | 2 | Expression (scaled) | CC 0x0B |
| +0x11 | 1 | Frequency multiplier | CC 0x91 |
| +0x12 | 1 | Fine pitch tuning | CC 0x97 |
| +0x1F | 1 | Vibrato depth | CC 0x9B |
| +0x20 | 1 | Tremolo/AM depth | CC 0x9D |
| +0x67 | var | Extended parameter refs | Program Change |

### Note-On Processing Pipeline

When a MIDI Note On arrives at `Voice_NoteOn` (0x02CF97):

```
MIDI Note On (channel, note, velocity)
  │
  ├─ velocity = 0? ──yes──> Voice_NoteOff (release voice)
  │
  ├─ Voice_Allocate (0x02C9DF)
  │     └─ Pool-based allocation from 64 hardware voices
  │     └─ Voice stealing if pool exhausted
  │
  ├─ Voice_SetVelocity
  │     └─ Scale velocity via lookup table at 0x011D16
  │     └─ Write to amplitude parameter
  │
  ├─ Voice_SetPitch / ToneGen_Calc_Pitch (0x03D11F)
  │     └─ note + 0x24 (transpose by +36 semitones)
  │     └─ Semitone-specific adjustments (A#, G#, F#, E#)
  │     └─ Mode-dependent pitch offset (tone gen mode at 0x4A48)
  │     └─ Clamp to 0-255 range
  │
  └─ ToneGen_WriteVoiceParams
        └─ Write 21 register pairs to 0x100000/0x100002
        └─ Set key-on flag (bit 15 at register offset 0x0080)
```

### Pitch Calculation

`ToneGen_Calc_Pitch` (0x03D11F) converts MIDI note numbers to tone generator pitch values:

1. Add base offset: `note + 0x24` (transpose up 3 octaves)
2. Apply semitone-specific corrections for A#, G#, F#, E# (chromatic tuning compensation)
3. Apply mode-dependent offset from lookup tables at 0x01F420-0x01F422
4. Clamp final pitch to 0-255 range
5. Look up velocity curve from table at 0x01F53E

### Volume and Expression

Volume (CC 0x07) and Expression (CC 0x0B) both use a shared **scaling lookup table** at ROM 0x011D16. The final output level is the product of volume and expression, applied to the tone generator's volume registers (groups 0x08-0x09).

Pan (CC 0x0A) is a direct value (0-127) written to channel offset +0x08 and translated to left/right balance via `LABEL_032E1E`.

### Envelope Processing

The KN5000 uses **hardware envelopes** in the tone generator IC303 — the Sub CPU firmware does not implement software ADSR:

- **Key-on** (Note On): Sets bit 15 at tone gen register 0x0080, which triggers the hardware's internal attack phase
- **Key-off** (Note Off): Clears the enable flag, triggering hardware release
- **Sustain pedal** (CC 0x40): `Voice_CC_Sustain` (0x028962) defers note-off processing while held — notes sustain until pedal released
- **Sostenuto** (CC 0x5B): Similar hold behavior for notes already sounding
- **Soft pedal** (CC 0x5D): Reduces velocity/volume scaling

Attack, decay, sustain level, and release times are determined by the tone generator hardware and the per-voice register template, not by CPU-side envelope generators.

### LFO and Modulation

The Mod Wheel (CC 0x01) controls LFO modulation via `Voice_ModWheel_Apply` (0x024565). The modulation type is selected by bits [7:6] of voice parameter offset +16:

| Bits [7:6] | Mode | Effect |
|------------|------|--------|
| 0x00 | Off | No modulation |
| 0x40 | Vibrato | Pitch modulation (frequency wobble) |
| 0x80 | Tremolo | Amplitude modulation (volume pulse) |
| 0xC0 | Auto-pan | Stereo position modulation |

Additional modulation parameters via proprietary CCs:

| CC | Offset | Parameter |
|----|--------|-----------|
| 0x9B | +0x1F | Vibrato depth |
| 0x9C | — | Vibrato enable/disable (bit 8 toggle) |
| 0x9D | +0x20 | Tremolo/AM depth |

The actual LFO oscillator runs inside the tone generator hardware; the firmware only sets depth and mode parameters.

### Filter Control

No explicit filter envelope or cutoff sweep exists in the CPU firmware. The tone generator hardware likely contains internal filters controlled by:

- **CC 0x9B** (offset +0x1F): May modulate filter cutoff depth in addition to vibrato
- **Tone gen registers 0x0800-0x08C0** (Volume/Level group): Likely include filter-related parameters
- **Tone gen registers 0x09C0-0x0A40** (Aux group): Extended parameters potentially including resonance

Filter behavior is fixed per voice preset — no real-time filter sweeps are implemented in firmware.

### Proprietary Control Changes (0x91-0x9D)

| CC | Handler | Channel Offset | Function |
|----|---------|---------------|----------|
| 0x91 | LABEL_028A44 | +0x11 | Frequency multiplier (via lookup table) |
| 0x95 | LABEL_028A55 | +0x04 | Portamento enable/disable (boolean flag) |
| 0x97 | LABEL_028A7F | +0x12 | Fine pitch tuning (semitone-level adjustment) |
| 0x9B | LABEL_028A90 | +0x1F | Vibrato depth (via lookup table) |
| 0x9C | LABEL_028AA1 | — | Vibrato enable/disable (bit 8 toggle) |
| 0x9D | LABEL_028ACB | +0x20 | Tremolo/AM depth (via lookup table) |

All proprietary CCs use `channel × 0x11F + base_offset` to access per-channel data. CCs 0x91, 0x97, 0x9B, and 0x9D read values from a shared lookup table at 0x011D16. CCs 0x95 and 0x9C are boolean toggles using OR/AND bit masks.

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

## Feature Demo

The Feature Demo plays pre-recorded MIDI sequences to demonstrate the keyboard's capabilities. Pressing the DEMO button triggers a complex initialization and playback sequence.

### Demo Initialization Flow

```
DemoModeFunc (entry point)
  ├─ First call → DemoMode_Initialize
  │     ├─ Demo_PreSetup (general preparation)
  │     ├─ Audio_WaitForReady (poll bit 2 of 0x0420)
  │     ├─ Voice_SavePreset (save current voice state)
  │     ├─ SeqInit_PostEventSequence (post events 0xE1, 0xE2, 0xE3)
  │     └─ Seq_StartMainControlAlt (enter main control with event 0x01E1000D)
  └─ Subsequent calls → DemoMode_Main_Operation
        ├─ Voice_InitializeAll (allocates 0x1F0 bytes, inits 16 voices × 26 params)
        ├─ Audio_ConfigureDSP (DSP and hardware setup)
        ├─ Voice_LoadVoiceTable (load 16 voice presets)
        ├─ Demo_PreSetup
        ├─ Voice_CopyPreset (restore voice data)
        ├─ Timer7_DisableInterrupt
        ├─ Audio_CheckSubsystemReady
        ├─ SeqInit_PostEventSequence
        ├─ SeqInit_FinalEvent (post event 0x1B with 0xFFFFFFFF)
        └─ Seq_StartMainControl (enter main control with event 0x01E1000C)
```

### Sequencer Event Processing

The sequencer reads song events from an internal buffer and dispatches them via inter-CPU latch:

| Routine | Address | Purpose |
|---------|---------|---------|
| `Seq_ProcessEventLoop` | 0xEF14CA | Main event processing loop |
| `Seq_CheckSongEnd` | 0xEF27A5 | Checks if song position (0x01F377) == end position (0x01F373) |
| `Seq_ProcessMidiEvent` | 0xEF13CD | Processes individual MIDI events (0x90=NoteOn, 0x80=NoteOff, 0xB0=CC) |

### Demo Song Data

The demo's style/rhythm preset data is at `Demo_StyleRhythmData` (0xF5CFCC), which contains:
- Rhythm/style parameter bytes (96 bytes)
- ASCII variation names: "a-variation1" through "c-variation4" (12 variations)
- Section names: "a-intro 1", "a-fill in 1", "a-ending 1", etc. (24 sections)
- Additional parameter data

The data loading uses LDIR block copy loops at `Demo_LoadVariationData` (0xF5CF8B) and `Demo_LoadVariationC_Data` (0xF5CFAE).

### Current Emulation Behavior

When the DEMO button is pressed in MAME, the Feature Demo enters its playback loop but **only sends configuration commands** (Control Change, Pitch Bend, Channel Pressure, SysEx). No Note On (0x90) or Note Off (0x80) events are ever dispatched. Analysis of a test session showed:

| Command Type | Count | Description |
|-------------|-------|-------------|
| 0xB0 (CC) | 2,555 | Control Change — Pan (1109), Expression (1099), Volume (73), others |
| 0xF0 (SysEx) | 36 | System Exclusive messages |
| 0xE0 (Pitch Bend) | 19 | Pitch Bend changes |
| 0xD0 (Chan Pressure) | 15 | Channel Pressure (aftertouch) |
| **0x90 (Note On)** | **0** | **No note events sent** |
| **0x80 (Note Off)** | **0** | **No note events sent** |

### Diagnostic Log Analysis

Detailed MAME logging with sequencer state instrumentation reveals:

**Rhythm ROM validation passes:**
- `rhy_ofs=00000000` at RAM `(3277h)` — NOT 0xFFFFFFFF, so `RhythmROM_CheckValid` returns success
- Rhythm ROM reads occur during demo mode (1800-3800 reads/second from 0x400000+ addresses)
- First rhythm ROM read at t=5.5s from 0x400000, PC=0xF5465E (inside `RhythmROM_ValidateHeader`)

**Sequencer state machine transitions:**

| Time | State | Event |
|------|-------|-------|
| Boot | 0x00 | Initial idle state |
| ~5s | 0x01 | Transition during initialization |
| ~21s | 0xE0 | `DemoMode_Main_Operation` entered |
| ~22.6s | 0xE4 | `DemoMode_Initialize` completed |

All observed states (0x00, 0x01, 0xE0, 0xE4) are outside the 0x10-0x16 skip range, confirming the sequencer dispatcher is NOT blocked by state checks.

**Ring buffer never written:**
- `putc_mrx=0` in every heartbeat — the function that writes MIDI events to the main sequencer ring buffer (`SeqMain_WriteByte` at 0xEF276D) has ZERO execution hits
- `SeqBuf wr=0000 rd=0000` — write and read positions are always equal (buffer empty)
- `Seq_CheckSongEnd` always returns 0 (no events to process)

**Startup flag always zero:**
- `startflag=0000` at RAM `(0x0251D8)` — never set to a non-zero value
- This flag controls whether `Seq_StartMainControlAlt` (called from `DemoMode_Initialize`) configures audio hardware at 0xF42EA4
- On real hardware, something sets this flag during boot or demo initialization

**Event loop rate drops 60x after demo init:**
- Before demo: ~11,500 event loop iterations/sec
- After demo init (state=0xE4): ~168-180 iterations/sec
- This indicates the sequencer dispatcher IS running heavier processing (rhythm ROM reads, pattern loading), consuming CPU time, but never producing MIDI events into the ring buffer

**Sequencer processing PC addresses during demo:**
- PCs in range F5CFxx-F641xx confirm rhythm/sequencer processing code is executing
- This range covers `Seq_RhythmProcessor` through `RhythmROM_CalcPatternAddr`

### Root Cause Analysis

The pipeline breaks between "rhythm data loaded from ROM" and "MIDI events generated into ring buffer":

```
Rhythm ROM (4MB) ──read──> Pattern Data in RAM ──???──> Ring Buffer (0x01F37B)
     ✓ working              ✓ executing                  ✗ NEVER written
```

Possible causes under investigation:
1. **Startup flag (0x0251D8)** is never set, potentially skipping a critical initialization step
2. A missing Timer7 tick or other timing mechanism that drives MIDI event generation
3. An inter-CPU response or hardware register that gates the final event write stage

## Code References

### Main CPU (`maincpu/kn5000_v10_program.asm`)

| Routine | Address | Description |
|---------|---------|-------------|
| `Audio_Lock_Acquire` | 0xEF1FEE | Acquire inter-CPU lock |
| `Audio_Lock_Release` | 0xEF1F0F | Release inter-CPU lock |
| `Audio_DMA_Transfer` | 0xEF341B | Core DMA transfer |
| `Audio_InitDMAChannels` | 0xEF329E | Initialize DMA channels |
| `sendCOMM` | 0xEF32F4 | Send command/audio data to Sub CPU (chunks 32-byte blocks) |
| `InterCPU_Send_Data_Block` | 0xEF3350 | Send 1-32 byte packet via inter-CPU latch |
| `Audio_CheckSubsystemReady` | 0xFDDE6F | Check if audio subsystem is ready for commands |
| `Audio_CheckInitStatus` | 0xFDF08A | Verify audio init state (checks 0xF19E) |
| `Voice_InitializeAll` | 0xFE0E75 | Initialize all 16 voices (26 params each) |
| `Audio_ConfigureDSP` | 0xFDBD52 | Configure DSP hardware and state |
| `DemoMode_Initialize` | 0xF869E3 | Feature Demo first-time initialization |
| `DemoMode_Main_Operation` | 0xF8696F | Feature Demo normal playback handler |

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

The Sub CPU's serial port 1 is used as a **Computer Interface** (TO HOST connector). The "SA" designation in the service manual schematics refers to "Sub Address" bus lines, not a chip name.

| Parameter | Value |
|-----------|-------|
| Mode | 8-bit UART (SC1MOD = 0x29) |
| Baud Rate | ~500kHz (20MHz / 4 / 10) |
| Sync Byte | 0xFE (sent at init and periodically) |
| TX Buffer | 1024 bytes at 0x0A00-0x0DFF |
| RX Buffer | 512 bytes at 0x0E16-0x1015 |

### MIDI Active Sensing

MAME emulation confirms that the Sub CPU transmits **0xFE (MIDI Active Sensing)** on this port approximately every 276ms. This is a standard MIDI heartbeat message indicating the device is alive and ready for communication. No other data has been observed on this port during normal operation or Feature Demo playback.

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

These are the hardware command bytes sent to the DSP chips via the parallel bus (P7.6=1 for command, P7.6=0 for subsequent data). They are sent by bytecode opcode 0xE and by direct calls to `DSP_DispatchCommand`/`DSP_DispatchData`.

| Command | Direction | Via | Description |
|---------|-----------|-----|-------------|
| 0x01 | Write | OP3 (16-bit) | **Bulk initialization** — uploads full DSP state (150-350 data bytes). Used for EFF header (302B), reverb (272B), chorus (352B), algorithm init (117B). |
| 0x03 | Write | OP4 (cmd only) | **Algorithm select** — sent before coefficient data blocks (OP1/OP2). No data bytes. |
| 0x0F | Write | OP4 (cmd only) | **Disable/flush** — sent during algorithm init cleanup. No data bytes. |
| 0x10 | Write | OP4 (cmd only) | **Enable/start** — sent during algorithm init sequence. No data bytes. |
| 0x30 | Write | SEND_CMD (0xE) | **Parameter write** — sub-addressed, large data blocks (up to 190 bytes). Format: `0x30 [sub_addr] [data...]`. Sub-addresses 0x00, 0x03, 0x05, 0x0D seen. |
| 0x60 | Write | OP0 | **Bulk transfer** — used in standard parameter write sequences via opcode 0 handler. |

**Algorithm Configuration Sequence (from `DSP_AlgorithmChange`):**

The complete algorithm change writes 8 bytecode programs to the DSPs in order:

```
1. AlgoChange_Init (0x01E63C):
   - OP3: cmd=0x01, 117 bytes (16-bit packed DSP state init)
   - OP4: cmd=0x10 (enable)
   - OP4: cmd=0x10 (enable again)
   - OP4: cmd=0x0F (flush)

2. AlgoChange_Ch0 (0x01E6BE):
   - OP0: cmd=0x01, 23 bytes (12-bit packed init)
   - OP4: cmd=0x03 (select algorithm)
   - OP1: 8 bytes (algorithm header)
   - OP2: 93 bytes (coefficient data block 1)
   - OP4: cmd=0x03 (select algorithm)
   - OP1: 8 bytes (algorithm header 2)
   - OP2: 93 bytes (coefficient data block 2)

3-8. AlgoChange_Ch1 (4 programs with delay):
   - SEND_CMD: cmd=0x30 sub=0x03 + 2 data bytes (mode select)
   - STATE_CHANGE (yield to scheduler)
   - SEND_CMD: cmd=0x30 sub=0x05 + 100-189 data bytes (coefficients)
   - SEND_CMD: cmd=0x30 sub=0x00 + variable data (parameters)
   - SEND_CMD: cmd=0x30 sub=0x0D + variable data (delay line config)
```

**Parameter Data Formats:**

Reverb and chorus configs share a common 28-byte header (first 14 word pairs) starting with `0x00C8 0x0880 0x1300 0x0B00 0x0028 0x9415 0x0212...`, suggesting a common DSP state initialization structure where effect-specific parameters follow.

The `DSP_DispatchCommand` function (0x036454) routes commands to DSP1 (`DSP_Send_Command`) or DSP2 (`DSP2_Send_Command`) based on the chip number in BC. Both use the same handshake protocol: poll PH.0 for ready, then write via Port PZ with appropriate chip-select and command/data strobes.

## Keybed Architecture

The physical keyboard (keybed) connects **directly** to the tone generator IC303, NOT to the Sub CPU. IC303 performs hardware key scanning internally and presents note events to the Sub CPU via the keyboard input interface at 0x110000.

This means:
- The CPU does **not** scan the keyboard matrix
- IC303 handles debouncing, velocity detection, and polyphony assignment
- The Sub CPU simply reads completed note events from IC303's output register

See [Keybed Scanning]({{ site.baseurl }}/keybed-scanning/) for the complete note flow, encoding format, and voice slot management.

## MAME Emulation Status

The MAME driver (`kn5000.cpp`) includes device stubs for all three audio chips. These provide logging of firmware-driven register writes, enabling reverse engineering of the audio pipeline. No audio output is produced yet — the DSP internal ROMs have not been dumped.

### Audio Chip Device Classes

| Device | Chip | IC | Interface | MAME Class | Status |
|--------|------|----|-----------|------------|--------|
| Tone Generator | TC183C230002 | IC303 | Memory-mapped (0x100000) | `tc183c230002_device` | Stub with config register logging, keybed event injection |
| DSP1 | DS3613GF-3BA | IC311 | Memory-mapped (0x130000) | `ds3613gf3ba_device` | Stub with per-channel register logging, effect type/parameter name tables |
| DSP2 | MN19413 | IC310 | Serial (GPIO bit-bang) | `mn19413_device` | Stub with serial bit sampling, command context tracking |

**Tone Generator (TC183C230002):**
- Register-indirect config interface (address port + data port)
- 64 voices tracked with per-voice state (group, bank, channel, register, data)
- Keyboard input interface with `inject_key_event()` for MAME input port integration
- Logs all register writes with voice/register/data breakdown

**DSP1 (DS3613GF-3BA):**
- 4 channels × 32 registers (0x80 bytes total address space)
- Logs register writes with channel, register offset, and semantic descriptions
- Contains effect type name table (100 entries) and parameter name table (84 entries)
- Tracks current effect type per channel for context-aware logging

**DSP2 (MN19413):**
- Serial interface via SubCPU GPIO (Port PF bit 0 = SDA, bit 2 = SCLK)
- MSB-first serial data sampling on SCLK rising edge
- Logs received commands with bit count and shift register state

### Key Emulation Challenges

1. **No DSP internal ROM dumps** — Both DSP chips contain internal ROM with their effects algorithms. Without dumps, audio processing cannot be accurately emulated.
2. **Tone generator wavetable ROM** — IC303 contains internal wavetable samples. Without a dump, synthesized audio output is not possible.
3. **Serial port 1 protocol** — The ~500kHz UART connection between SubCPU and the DAC/DSP control path is not yet fully decoded.

### What Works Now

- SubCPU firmware loads and executes (192KB payload transfer via HDMA)
- All inter-CPU audio commands (0x2D DSP config, 0x2B sound name query, etc.) are dispatched correctly
- DSP state dispatcher runs all 11 sub-routines, generating complete register write sequences
- Effect configurations flow from MainCPU → SubCPU → DSP device stubs
- Keybed input from MAME input ports reaches the tone generator device
- SubCPU Serial Port 1 (Computer Interface) wired with UART byte decoder and logging
- Feature Demo sends CC/pitch/sysex configuration commands correctly (2,625 commands observed)

### Known Issues

- **Feature Demo produces no note events** — The sequencer dispatcher runs and reads rhythm ROM data, but the song engine never writes MIDI events to the ring buffer. The pipeline breaks between pattern data loading and event generation. Rhythm ROM validation passes (rhy_ofs=0), state machine is correct (0xE0→0xE4), but `putc_mrx` (ring buffer write function) has zero executions. See [Feature Demo](#feature-demo) for detailed diagnostic analysis and [Sequencer]({{ site.baseurl }}/sequencer/) for the full architecture.
- **No audio output** — All three audio device classes are logging stubs; no sound synthesis or effects processing is implemented.

## Research Needed

- [ ] Document waveform ROM format and sample layout
- [ ] Decode per-algorithm parameter mapping tables at `0x1F22C`/`0x1F09C` (12-byte stride entries)
- [ ] Map MainCPU parameter indices (e.g., 33=REVERB TIME) to EFF block word positions per algorithm
- [ ] Decode DSP register semantics per channel (what registers 0x10-0x17 control)
- [ ] Document remaining inter-CPU command types (beyond 0x2D and 0xE1/E2/E3)
- [ ] Investigate why song engine never writes MIDI events to ring buffer (putc_mrx has zero hits)
- [ ] Determine what sets the startup flag at 0x0251D8 on real hardware
- [ ] Trace the path from rhythm ROM pattern data to ring buffer write calls
- [ ] Decode voice parameter template at ROM 0xF8D5 (34 words — which map to pitch, waveform select, envelope mode, etc.)
- [x] ~~Investigate why Feature Demo sequencer never reaches Note On events~~ — Ring buffer at 0x01F37B is never written; sequencer dispatcher and rhythm ROM reading work correctly but event generation stage never fires
- [x] ~~Identify the timing mechanism or subcpu response that advances the sequencer~~ — Partially resolved: Timer7, state machine, and dispatcher pipeline traced; the issue is in the song engine output stage, not the input/timing stage
- [x] ~~Identify exact device on Serial Port 1~~ — Computer Interface (TO HOST connector), sends 0xFE Active Sensing
- [x] ~~Analyze DSP1/DSP2 command sets~~ — Partial: 4 commands identified, preset structure decoded
- [x] ~~Extract effect type names from ROM~~ — Complete: 100 named effect types at MainCPU 0xE32A7A
- [x] ~~Extract effect parameter names from ROM~~ — Complete: 84 parameter names at MainCPU 0xE324D0
- [x] ~~Document DSP state dispatcher architecture~~ — Complete: `DSP_State_Dispatcher` and 11 sub-routines traced
- [x] ~~Trace inter-CPU command 0x2D protocol~~ — Complete: 4-layer protocol fully documented
- [x] ~~Map effect type indices to DSP register configurations~~ — Partial: translation chain traced through `DSP_WriteParameter` → `DSP_ParameterWriteEngine`, but per-algorithm ROM tables not yet decoded
- [x] ~~Determine if DSP microcode is loaded from ROM~~ — **No.** DSPs are pre-programmed; SubCPU only writes configuration via bytecode interpreter
- [x] ~~Map remaining proprietary CC handlers (0x97-0x9D)~~ — Complete: CC91=freq mult, CC95=portamento, CC97=fine pitch, CC9B=vibrato depth, CC9C=vibrato enable, CC9D=tremolo depth
- [x] ~~Decode tone generator register semantics~~ — Partial: voice control state machine, key-on/off flags, volume/level groups, latched parameter updates documented; pitch/envelope/filter register mapping still needs work
- [x] ~~Document synthesis architecture~~ — Complete: 64-voice wavetable, 26 MIDI channels, dynamic voice allocation, hardware ADSR, LFO modes, proprietary CCs
- [ ] Reverse-engineer DSP register semantics by tracing actual bytecode program data through the decoded handlers (need to decode config tables at 0x14777/0x147B3 entry-by-entry)
- [x] ~~Analyze native code handlers within DSP_Bytecode_Programs~~ — Complete: 6 handlers at 0x3C32E, opcodes 0-2 use 12-bit parameter packing (4-bit shift), opcode 3 uses 16-bit (8-bit shift), opcode 4=command-only, opcode 5=command+data. All share common read-from-stream idiom with prevbank result storage.
- [ ] Determine if DSP internal ROM can be extracted (decapping, JTAG, etc.)
- [x] ~~Document bytecode interpreter opcode set completely (opcodes 0x0-0xF)~~ — Complete: 2-byte header format, opcodes 0-5 (native code dispatch), 0xD (yield), 0xE (send command+data), 0xF (end). Config entries are 12 bytes (4 words + 1 pointer). Handlers at `DSP_Bytecode_Programs` (0x3C32E) are native TLCS-900 subroutines.
