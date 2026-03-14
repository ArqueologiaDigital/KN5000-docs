---
layout: page
title: Sub CPU Command Format
permalink: /subcpu-command-format/
---

# Sub CPU Command Byte Format

The Main CPU sends commands to the Sub CPU via the inter-CPU latch at `0x120000`. Each command is received by the MicroDMA Channel 0 interrupt handler (`MICRODMA_CH0_HANDLER` at `0x020F1F`), which dispatches based on the command byte format.

## Command Byte Encoding

The command byte uses a split format:

```
  7   6   5   4   3   2   1   0
+---+---+---+---+---+---+---+---+
| Handler ID    | Payload Length    |
|  (bits 7-5)   |  (bits 4-0)       |
+---+---+---+---+---+---+---+---+
```

- **Bits 7-5:** Handler selector (0-7), indexes into `CMD_DISPATCH_TABLE`
- **Bits 4-0:** Payload length minus 1 (actual byte count = value + 1, range 1-32)

The handler receives:
- **Stack +4:** Byte count (the decoded payload length)
- **Stack +6:** Pointer to command data buffer at `0x10F0`

## CMD_DISPATCH_TABLE

The 8-entry jump table at `0x00F46C` dispatches commands to handlers:

| Index | Command Range | Handler | Purpose |
|-------|--------------|---------|---------|
| 0 | `0x00`-`0x1F` | `Audio_CmdHandler_00_1F` | MIDI/audio data to ring buffer |
| 1 | `0x20`-`0x3F` | `Audio_CmdHandler_20_3F` | No-op (returns immediately) |
| 2 | `0x40`-`0x5F` | `Audio_CmdHandler_40_5F` | Skip N bytes (data drain) |
| 3 | `0x60`-`0x7F` | `Audio_CmdHandler_60_7F` | DSP streaming data |
| 4 | `0x80`-`0x9F` | `Serial1_DataTransmit_Loop` | Serial port 1 (SC1) TX |
| 5 | `0xA0`-`0xBF` | `Audio_CmdHandler_A0_BF` | Tone generator control |
| 6 | `0xC0`-`0xDF` | `Audio_CmdHandler_C0_FF` | No-op (returns immediately) |
| 7 | `0xE0`-`0xFF` | `Audio_CmdHandler_C0_FF` | No-op (returns immediately) |

Note: Ranges 6 and 7 share the same no-op handler. Special E1/E2/E3 commands bypass this table entirely (see Special Commands below).

## Handler Details

### 0x00-0x1F: MIDI/Audio Ring Buffer (`Audio_CmdHandler_00_1F`)

**Purpose:** Writes incoming audio/MIDI data bytes to a 4KB circular ring buffer for processing by `MIDI_Dispatch`.

**Buffer Structure:**
- Control block at DRAM `0x2B0D`:
  - `+0` (16-bit): Write pointer
  - `+4` (16-bit): Byte count
  - `+6`: Data area start
- Buffer capacity: 4KB (12-bit index, masked with `0xFFF`)

**Algorithm:**
1. Read byte count from stack (bits 4-0 of command byte + 1)
2. For each byte in the payload:
   - Read write pointer from control block
   - Write byte to `base + (write_ptr & 0xFFF)`
   - Increment write pointer and byte count
3. Return HL = 0 (success)

**Usage:** This is the primary path for all MIDI messages from Main CPU to Sub CPU. The ring buffer is consumed by `MIDI_Dispatch` (`0x034D93`), which parses MIDI status bytes (0x80-0xF0) and routes to voice parameter handlers (Note On/Off, Control Change, Program Change, etc.).

**Payload Format:**
```
[cmd_byte] [midi_byte_1] [midi_byte_2] ... [midi_byte_N]
```

Where `cmd_byte & 0x1F` = N (number of MIDI bytes following). The MIDI bytes are standard MIDI protocol messages (status + data bytes).

### 0x20-0x3F: No-Op (`Audio_CmdHandler_20_3F`)

**Purpose:** Does nothing. Returns HL = 0 immediately.

This range is reserved/unused. The Main CPU may send these commands for padding or synchronization purposes.

### 0x40-0x5F: Data Drain (`Audio_CmdHandler_40_5F`)

**Purpose:** Skips (drains) N bytes from the command stream without processing them.

**Algorithm:**
1. Read byte count from stack
2. Decrement count to 0 in a loop (no data processing)
3. Return HL = 0

**Usage:** Used to discard unwanted data that was already committed to the DMA transfer. Acts as a "null sink" for payload bytes.

### 0x60-0x7F: DSP Streaming Data (`Audio_CmdHandler_60_7F`)

**Purpose:** Handles multi-packet DSP audio streaming with size tracking and ring buffer output.

**State Machine** (state stored at DRAM 17548):

| State | Condition | Action |
|-------|-----------|--------|
| 0 (Init) | Payload = 32 bytes | Extract 14-bit size from bytes 5-6, init stream counter |
| 0 (Init) | Payload != 32 bytes | Reset state, enqueue data |
| 1+ (Streaming) | Accumulated < total | Add to running count, enqueue data |
| 1+ (Streaming) | Accumulated >= total | Reset state (stream complete) |

**Stream Header** (first 32-byte packet):
- Byte 5: Size high (bits 10-4), encoded as `(value & 0x7FF)`
- Byte 6: Size low (bits 6-0)
- Total size = `(byte5 & 0x7FF) << 7 + (byte6 & 0x7F) + 8`

**Output:** Data bytes are written to a 2KB ring buffer:
- Control block at DRAM `0x3B60` (address 15200)
- 11-bit index (masked with `0x7FF`)

**State Variables:**
- DRAM 17544: Total expected stream size
- DRAM 17546: Accumulated byte count
- DRAM 17548: Stream state (0=waiting for header, 1+=streaming)

### 0x80-0x9F: Serial Port 1 TX (`Serial1_DataTransmit_Loop`)

**Purpose:** Transmits payload bytes via Serial Channel 1 (SC1), used for communication with tone generator hardware or external devices.

**Algorithm:**
1. For each byte in the payload:
   - If DRAM 4148 bit 2 is clear: call `Serial1_CommandHandler_RX_F4F5` directly (synchronous TX)
   - If DRAM 4148 bit 2 is set: write byte to SC1 ring buffer (`0x1016`) and enable TX interrupt (buffered TX)
2. Return HL = 0

**Two TX Modes:**
- **Direct mode** (bit 2 clear): Bytes are processed immediately by the serial command handler. Used during initialization or when real-time response is needed.
- **Buffered mode** (bit 2 set): Bytes are queued in a ring buffer and transmitted asynchronously via SC1 TX interrupts. Used during normal operation.

### 0xA0-0xBF: Tone Generator Control (`Audio_CmdHandler_A0_BF`)

**Purpose:** Controls the tone generator subsystem state.

**Payload Format:**
```
[cmd_byte] [sub_command] [parameter]
```

**Sub-commands:**

| Byte 0 | Byte 1 | Action |
|--------|--------|--------|
| `0x00` | `0x01` | Set tone gen enable flag (DRAM 19018 = 1) |
| `0x01` | `0x00`-`0x09` | Set tone gen mode (DRAM 19016 = byte 1) |
| other | any | Ignored |

**Tone Generator Modes** (DRAM 19016, aka address `0x4A48`):
- Values 0-9 are accepted
- Mode 6 is set during `ToneGen_Init`
- The mode value controls the tone generator's processing behavior

### 0xC0-0xFF: No-Op (`Audio_CmdHandler_C0_FF`)

**Purpose:** Does nothing. Returns HL = 0 immediately.

These ranges (0xC0-0xDF and 0xE0-0xFF) share the same no-op handler. However, the 0xE0-0xFF range is partially intercepted by the special command system before reaching this table (see below).

## Special Commands (E1/E2/E3)

Commands `0xE1`, `0xE2`, and `0xE3` are handled by the `MICRODMA_CH0_HANDLER` state machine before the dispatch table is consulted. They use multi-phase DMA transfers:

### State Machine (CMD_PROCESSING_STATE at DRAM 4330)

| State | Trigger | Action |
|-------|---------|--------|
| 0 | Idle | Receive first byte, set state to 1 |
| 1 | Command byte received | Decode and dispatch via CMD_DISPATCH_TABLE |
| 2 | E1 phase 1 complete | Read DMA destination and byte count from buffer, start DMA transfer |
| 3 | E2 command | Set E2 pending flag, signal ready to Main CPU |
| 4 | E1 phase 2 complete | Clear transfer flag, signal completion |

### E1: Two-Phase DMA Transfer

**Purpose:** Large block data transfer (e.g., sample data, firmware updates, configuration blocks).

**Protocol:**
1. Main CPU sends E1 command
2. Sub CPU receives 6-byte setup: 4-byte destination address + 2-byte byte count (at DRAM 4374)
3. Sub CPU configures DMA Channel 2 with the destination/count and starts transfer
4. Main CPU streams data through latch
5. DMA completion triggers state 4, which signals ready for next command

### E2: Single-Phase Command

**Purpose:** Short command with acknowledgment.

**Protocol:**
1. Main CPU sends E2 command with payload
2. Sub CPU stores payload, sets pending flag (DRAM 4390 bit 7), signals ready
3. Payload is processed later by the main processing loop

### E3: Payload Ready Signal

Used as a handshake signal during multi-step transfers.

## Dispatch Flow

```
Main CPU writes to latch (0x120000)
    |
    v
MicroDMA Ch0 interrupt fires
    |
    v
CMD_PROCESSING_STATE check
    |
    +-- State 0: Store byte, set state=1, setup next DMA
    +-- State 1: Decode command byte
    |       |
    |       v
    |   bits 7-5 → CMD_DISPATCH_TABLE[index]
    |       |
    |       v
    |   Handler processes payload
    |       |
    |       v
    |   State → 0, ACK to Main CPU
    |
    +-- State 2: E1 phase 2 (start DMA)
    +-- State 3: E2 complete (set flag, ACK)
    +-- State 4: E1 complete (clear flag, ACK)
```

## Code References

| Symbol | Address | Purpose |
|--------|---------|---------|
| `CMD_DISPATCH_TABLE` | `0x00F46C` | 8-entry handler jump table |
| `MICRODMA_CH0_HANDLER` | `0x020F1F` | Main command dispatcher |
| `Audio_CmdHandler_00_1F` | `0x039640` | MIDI ring buffer writer |
| `Audio_CmdHandler_20_3F` | `0x01FC7B` | No-op |
| `Audio_CmdHandler_40_5F` | `0x01FC7F` | Data drain |
| `Audio_CmdHandler_60_7F` | `0x039896` | DSP streaming |
| `Serial1_DataTransmit_Loop` | `0x01F226` | SC1 serial TX |
| `Audio_CmdHandler_A0_BF` | `0x03D00D` | Tone gen control |
| `Audio_CmdHandler_C0_FF` | `0x0200C6` | No-op |
| `InterCPU_Latch_Setup` | `0x020B3B` | DMA and latch init |
| `MIDI_Dispatch` | `0x034D93` | MIDI message parser |
| `Audio_CmdHandler_ConstData` | `0x039622` | Ring buffer write helper |

## References

- [Inter-CPU Protocol](/inter-cpu-protocol/) — Latch communication mechanism
- [MIDI Subsystem](/midi-subsystem/) — MIDI message dispatch on Sub CPU
- [Audio Subsystem](/audio-subsystem/) — Sound generation and DSP
- [SysEx Messages](/sysex-messages/) — System Exclusive message handling

---

*Last updated: March 2026*
