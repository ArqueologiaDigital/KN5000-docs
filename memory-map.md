---
layout: page
title: Memory Map
permalink: /memory-map/
---

# KN5000 Memory Map

## Main CPU Address Space

| Address Range | Size | Description |
|---------------|------|-------------|
| `0x000000 - 0x0FFFFF` | 1MB | Internal RAM / SFRs |
| `0x110000` | - | Floppy Disk Controller |
| `0x120000` | - | Inter-CPU Communication Latches |
| `0x160000 - 0x160006` | 8B | HDAE5000 PPI (8255) |
| `0x1A0000 - 0x1A7FFF` | 512KB | Video RAM (IC207 M5M44265CJ8S) |
| `0x280000` | 512KB | HDAE5000 ROM |
| `0x300000` | 1MB | Custom Data Flash (User Storage) |
| `0x3C0 - 0x3DA` | - | VGA Registers (LCD Controller IC206) |
| `0x400000` | - | Rhythm Data ROM |
| `0x800000` | 2MB | Table Data ROM |
| `0xE00000` | 2MB | Program Flash (Main ROM) |

## Special Function Registers (TMP94C241F)

### Serial Channels

| Register | Address | Description |
|----------|---------|-------------|
| `SC0BUF` | - | Serial Channel 0 Buffer |
| `SC0CR` | - | Serial Channel 0 Control |
| `SC0MOD` | - | Serial Channel 0 Mode |
| `SC1BUF` | - | Serial Channel 1 Buffer |
| `SC1CR` | - | Serial Channel 1 Control |
| `SC1MOD` | - | Serial Channel 1 Mode |

### Timers

| Register | Address | Description |
|----------|---------|-------------|
| `T0` - `T7` | - | 8-bit Timers |
| `T8` - `TB` | - | 16-bit Timers |

### Interrupts

| Vector | Handler | Description |
|--------|---------|-------------|
| `INTA` | `INTA_HANDLER` | Interrupt A (includes serial) |
| `INT0` | `INT0_HANDLER` | External Interrupt 0 |

## Control Panel Memory

### Button State

| Address | Variable | Description |
|---------|----------|-------------|
| `0x8E4A` | `STATE_OF_CPANEL_BUTTONS` | Button state array (Right panel) |
| `0x8E5A` | `STATE_OF_CPANEL_BUTTONS_LEFT` | Button state array (Left panel) |
| `0x8E55` | `STATE_OF_CPANEL_BUTTONS + 11` | Bits 6,7 select value 0x0c/0x0d/0x0e |

### LED State

| Address | Variable | Description |
|---------|----------|-------------|
| `0x8DFD` | `CPANEL_LED_READ_PTR` | LED TX buffer read pointer (word) |
| `0x8DFF` | `CPANEL_LED_WRITE_PTR` | LED TX buffer write pointer (word) |
| `0x8E01` | `CPANEL_LED_TX_BUFFER` | LED state TX buffer (60 bytes) |

### Protocol State

| Address | Variable | Description |
|---------|----------|-------------|
| `0x8D8A` | `CPANEL_STATE_MACHINE_INDEX` | State machine index (byte, values 0-10) |
| `0x8D8B` | `CPANEL_PACKET_BYTE_COUNT` | Packet byte counter (byte, values 0-17) |
| `0x8D9D` | `CPANEL_RX_READ_PTR` | RX buffer read pointer (word) |
| `0x8D9F` | `CPANEL_RX_WRITE_PTR` | RX buffer write pointer (word) |

### Status Flags

| Address | Variable | Description |
|---------|----------|-------------|
| `0x8D8C` | `CPANEL_TX_RX_FLAGS` | TX/RX protocol flags (byte) |
| `0x8D92` | `CPANEL_PROTOCOL_FLAGS` | Protocol state flags (byte) |
| `0x8D93` | `CPANEL_PANEL_DETECT_FLAGS` | Panel detection flags (byte) |

### Encoder Raw Input Storage

| Address | Variable | Description |
|---------|----------|-------------|
| `0x8ECA` | `ENCODER_RAW_MODWHEEL` | Raw modulation wheel input |
| `0x8ECC` | `ENCODER_RAW_VOLUME` | Raw volume slider input |
| `0x8ED4` | `ENCODER_RAW_BREATH` | Raw breath controller input |
| `0x8ED6` | `ENCODER_RAW_FOOT` | Raw foot controller input |
| `0x8ED8` | `ENCODER_RAW_EXPRESSION` | Raw expression pedal input |
| `0x8EDA` | `ENCODER_BREATH_MODE` | Breath controller mode/enable |
| `0x8EDC` | `ENCODER_VOLUME_MODE` | Volume mode configuration |
| `0x8EDE` | `ENCODER_RANGE_LIMIT` | Encoder range limit value |

### MIDI Controller Values

| Address | Variable | Description |
|---------|----------|-------------|
| `0x8EE0` | `MIDI_CC_MODWHEEL_PENDING` | Modulation value with change flag (bit 7) |
| `0x8EE2` | `MIDI_CC_EXPRESSION_PENDING` | Expression value with change flag (bit 7) |
| `0x8EE4` | `MIDI_CC_MODWHEEL_VALUE` | Current modulation wheel value (CC#1) |
| `0x8EE6` | `MIDI_CC_EXPRESSION_VALUE` | Current expression value (CC#0) |
| `0x8EE8` | `MIDI_CC_BREATH_VALUE` | Breath controller value (CC#2) |
| `0x8EEA` | `MIDI_CC_FOOT_VALUE` | Foot controller value (CC#4) |
| `0x8EF4` | `MIDI_CC_VOLUME_VALUE` | Volume controller value (CC#7) |

### Encoder State

| Address | Variable | Description |
|---------|----------|-------------|
| `0x8EFC` | `ENCODER_0_LAST_VALUE` | Previous encoder 0 reading (for delta) |
| `0x8EFE` | `ENCODER_1_LAST_VALUE` | Previous encoder 1 reading (for delta) |
| `0x8F04` | `ENCODER_0_STATUS` | Encoder 0 status flags (bit 3 = changed) |
| `0x8F06` | `ENCODER_1_STATUS` | Encoder 1 status flags (bit 3 = changed) |
| `0x8F10` | `ENCODER_0_OUTPUT` | Encoder 0 output buffer (2 bytes) |
| `0x8F16` | `ENCODER_1_OUTPUT` | Encoder 1 output buffer (2 bytes) |
| `0x8F18` | `ENCODER_STATE_BASE` | Base of encoder state structure |

### Encoder Lookup Tables (ROM)

| Address | Variable | Description |
|---------|----------|-------------|
| `0xEDA13C` | `ENCODER_LUT_MODWHEEL` | Modulation wheel value lookup |
| `0xEDA1BC` | `ENCODER_LUT_VOLUME` | Volume slider value lookup |
| `0xEDA2BC` | `ENCODER_LUT_BREATH_INDEX` | Breath controller index lookup |
| `0xEDA2D2` | `ENCODER_LUT_BREATH_VALUE` | Breath controller value lookup |
| `0xEDA3D2` | `ENCODER_LUT_BREATH_MULT` | Breath controller multiplier table |
| `0xEDA3EA` | `ENCODER_LUT_BREATH_OFFSET` | Breath controller offset table |
| `0xEDA402` | `ENCODER_LUT_FOOT` | Foot controller value lookup |
| `0xEDA482` | `ENCODER_LUT_EXPRESSION` | Expression pedal value lookup |

## Sub CPU Address Space

The sub CPU (tone generator controller) has its own memory map, documented from boot ROM disassembly.

| Address Range | Size | Description |
|---------------|------|-------------|
| `0x0000 - 0x00FF` | 256B | Special Function Registers (SFR) |
| `0x0100 - 0x01FF` | 256B | Extended SFR / Memory Controller |
| `0x0400 - 0x04E0` | 225B | Interrupt vector trampolines (copied from boot ROM) |
| `0x04FE` | 1B | `DMA_READY_FLAG` - DMA ready indication (bit 7 set when DMA ready) |
| `0x0500 - 0x05A2` | ~160B | RAM / Stack area (stack init = 0x05A2) |
| `0x0502` | 12B | `DMA_PARAM_BLOCK` - DMA parameter storage (XWA, XDE, BC values) |
| `0x0512` | 4B | `DMA_TARGET_ADDR` - Current DMA destination address |
| `0x0516` | 2B | `DMA_SYNC_FLAG` - DMA synchronization (0=complete, 1=pending, 2=E1 mode) |
| `0x0518` | 2B | `CMD_PROCESSING_STATE` - Command processing state (0-4) |
| `0x051A` | 1B | `LAST_CMD_BYTE` - Last received command byte from main CPU |
| `0x051E` | 32B | `CMD_DATA_BUFFER` - Variable-length command data buffer |
| `0x0544` | 6B | `CMD_E1_BUFFER` - E1 command data buffer |
| `0x054A` | 10B | `CMD_E2_BUFFER` - E2 command data buffer |
| `0x0556` | 1B | `MEMTEST_RESULT` - Memory test result flags |
| `0x0558` | 8B | `SERIAL_STATUS` - Serial communication status bytes |
| `0x100000` | - | Audio Hardware Registers (DSP/DAC) |
| `0x110000` | - | Keyboard/Control Panel Interface Latches |
| `0x120000` | - | Inter-CPU Communication Latch (shared with main CPU) |
| `0x130000` | - | Tone Generator Registers |
| `0xFE0000 - 0xFFFFFF` | 128KB | Boot ROM |

### Sub CPU SFR Addresses (Confirmed from Boot ROM)

| Address | Register | Description |
|---------|----------|-------------|
| `0x07` | P0FC | Port 0 Function Control |
| `0x0B` | P1FC | Port 1 Function Control |
| `0x0F` | P2FC | Port 2 Function Control |
| `0x1C` | P7 | Port 7 Data |
| `0x1E` | P7CR | Port 7 Control |
| `0x1F` | P7FC | Port 7 Function Control |
| `0x20` | P8 | Port 8 Data |
| `0x22` | P8CR | Port 8 Control |
| `0x23` | P8FC | Port 8 Function Control |
| `0x28` | PA | Port A Data |
| `0x2B` | PAFC | Port A Function Control |
| `0x2C` | PB | Port B Data |
| `0x2F` | PBFC | Port B Function Control |
| `0x30` | INTTC01 | Interrupt Control (Timer 0/1) |
| `0x34` | INTERCPU_STATUS | Inter-CPU handshaking: bit 0=sub ready, bit 1=completion, bit 2=gate, bit 4=main ready |
| `0x36` | SC0CR | Serial Channel 0 Control |
| `0x38` | SC0MOD | Serial Channel 0 Mode |
| `0x3A` | SC1BUF | Serial Channel 1 Buffer |
| `0x3C` | SC1CR | Serial Channel 1 Control |
| `0x3E` | SC1MOD | Serial Channel 1 Mode |
| `0x80` | T01MOD | Timer 0/1 Mode (not watchdog - real WD at 0x110) |
| `0x81` | T01FFCR | Timer 0/1 Flip-Flop Control |
| `0x82` | T8RUN | 8-bit Timer Run Control |
| `0x102` | DMA_MODE_REG | DMA mode configuration register |

## Inter-CPU Communication

The main CPU and sub CPU communicate via latches at `0x120000`.

### Latch Address

| Address | Access | Description |
|---------|--------|-------------|
| `0x120000` | R/W | Inter-CPU Communication Latch |

The sub CPU boot ROM configures DMA to use this address for bidirectional communication with the main CPU.

### Command Protocol (Boot ROM)

The sub CPU boot ROM implements this command protocol:

| Command Byte | Action | Data Size | Buffer Address |
|--------------|--------|-----------|----------------|
| `0x00 - 0x1F` | Handler dispatch + data | 1-32 bytes | `0x051E` |
| `0xE1` | DMA transfer type 1 | 6 bytes | `0x0544` |
| `0xE2` | DMA transfer type 2 | 10 bytes | `0x054A` |
| `0xE3` | Signal payload ready | 0 bytes | - |

**Command Encoding (0x00-0x1F):**

For general commands, the byte encodes both handler and length:

```
Bits 7-5: Handler index (0-7) → selects from jump table at 0xFF8000
Bits 4-0: Data length minus 1 (0-31 → 1-32 bytes)
```

Example: Command `0x45` = handler 2 (`0x45 >> 5 = 2`), 6 bytes (`(0x45 & 0x1F) + 1 = 6`)

### Communication Flow

**Main CPU → Sub CPU (Command):**

```
1. Main CPU writes command byte to 0x120000
2. Sub CPU INT_HANDLER_9 triggered
3. Sub CPU reads command, initiates DMA for data bytes
4. DMA transfers remaining data to RAM buffer
5. INT_HANDLER_35 processes command based on state machine
```

**Sub CPU → Main CPU (Response):**

```
1. Sub CPU writes response to 0x120000
2. Sub CPU sets appropriate flag bits in VAR_04FE
3. Main CPU polls or receives interrupt
4. Main CPU reads response from latch
```

### Sub CPU State Variables

| Address | Symbol | Description |
|---------|--------|-------------|
| `0x04FE` | `SUBCPU_STATUS_FLAGS` | Bit 6: payload ready, Bit 7: transfer complete |
| `0x0512` | `DMA_TARGET_ADDR` | Current DMA destination address (4 bytes) |
| `0x0516` | `DMA_SYNC_FLAG` | 0=idle, 1=single xfer, 2=multi-stage (E1) |
| `0x0518` | `CMD_PROCESSING_STATE` | 0-4, tracks command processing phase |
| `0x051A` | `LAST_CMD_BYTE` | Most recent command byte received |
| `0x051E` | `CMD_DATA_BUFFER` | Variable-length command data (32 bytes) |
| `0x0544` | `CMD_E1_BUFFER` | E1 command data buffer (6 bytes) |
| `0x054A` | `CMD_E2_BUFFER` | E2 command data buffer (10 bytes) |
| `0x0556` | `MEMTEST_RESULT` | Memory test result flags |
| `0x0558` | `SERIAL_STATUS` | Serial status bytes (8 bytes) |

### DMA Configuration

The boot ROM configures DMA for the inter-CPU latch:

- **Source:** `0x120000` (latch)
- **Mode:** Controlled via undocumented LDC opcodes
- **Trigger:** Write `0x0A` to address `0x0100`

## Sub CPU Boot ROM Routines

Key routines identified in the boot ROM at 0xFF8000+:

| Address | Routine | Description |
|---------|---------|-------------|
| `0xFF8290` | `BOOT_INIT` | Hardware initialization entry point |
| `0xFF8432` | `DEFAULT_HANDLER` | Default interrupt handler (RETI) |
| `0xFF8433` | `RESET_ENTRY` | Alternative reset/NMI handler |
| `0xFF8437` | `SUB_8437` | Tone generator channel init loop |
| `0xFF846D` | `COPY_VECTORS` | Copy interrupt trampolines to RAM |
| `0xFF8490` | `HALT_LOOP` | Error handler (halt and loop) |
| `0xFF84A8` | `INIT_TONE_GEN` | Tone generator initialization |
| `0xFF84F1` | `TONE_GEN_WRITE` | Write data to tone generator |
| `0xFF850E` | `SUB_850E` | Multi-register push/call wrapper |
| `0xFF853A` | `SUB_853A` | Write register pairs to tone generator |
| `0xFF858B` | `COPY_WORDS` | Word block copy (ldirw) |
| `0xFF8594` | `FILL_WORDS` | Memory fill with word values |
| `0xFF859B` | `CHECKSUM_CALC` | Calculate checksum over memory range |
| `0xFF85AE` | `INIT_DMA_SERIAL` | DMA and serial initialization |
| `0xFF8604-0xFF881E` | *DMA routines* | 539 bytes, fully disassembled (5 routines) |
| `0xFF8956` | `INIT_MEMORY_TEST` | Memory test initialization |
| `0xFF881F` | `INT_HANDLER_9` | Serial receive interrupt |
| `0xFF889A` | `INT_HANDLER_37` | DMA complete interrupt |
| `0xFF88B8` | `INT_HANDLER_35` | Timer/processing interrupt |
| `0xFF89A9` | `DELAY_ROUTINE` | Variable delay loop |
| `0xFF89FC` | `MEM_TEST_ROUTINE` | RAM test routine |
| `0xFF8AB4` | `ROM_CHECKSUM` | Boot ROM integrity check |
| `0xFF8B07` | `SERIAL_INIT` | Serial communication init |
| `0xFF8F6C` | *Trampolines* | 45 interrupt vector trampolines (225 bytes) |
| `0xFFFF00` | *Vector Table* | Hardware interrupt vector table |

## Tone Generator

The tone generator hardware is accessed at `0x130000`.

| Address | Description |
|---------|-------------|
| `0x130000` | Tone Generator Base Address |

The sub CPU boot ROM initializes tone generator registers with patterns starting at this address. Each voice appears to use a 32-byte register block.

## HDAE5000 Hard Disk Expansion

The HD-AE5000 is a hard disk expansion system, not an audio processor. It serves as a data control center for managing large music file libraries beyond floppy disk capacity.

**Interface:** PPI at `0x160000`
**ROM:** `0x280000` (512KB)

### Firmware Versions

| Version | Release Date | Notes |
|---------|--------------|-------|
| v1.10i | 1998-07-06 | Initial release |
| v1.15i | 1998-10-13 | |
| v2.0i | 1999-01-15 | Added lyrics display |

All versions archived at [archive.org](https://archive.org/details/technics-kn5000-system-update-disks).

### Features

- Flash-ROM and Static RAM for quick directory access
- 2.5" Hard Disk Drive (1.08 GB storage)
- Parallel port for PC communication (HD-TechManager5000 software)
- Audio outputs with channel separation options

### Limitations

Files cannot be played directly from hard drive during performance - all file operations occur during breaks to protect the drive.

**Reference:** [keysoftservice.ch/hdae5000-e.htm](https://www.keysoftservice.ch/hdae5000-e.htm)
