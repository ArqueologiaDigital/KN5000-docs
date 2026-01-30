---
layout: page
title: Boot Sequence
permalink: /boot-sequence/
---

# KN5000 Boot Sequence

This page documents the complete boot sequence of the Technics KN5000, from power-on to a fully functional system. The KN5000 uses a dual-CPU architecture where the Main CPU orchestrates startup and loads firmware to the Sub CPU.

> **See Also**: [System Overview]({{ site.baseurl }}/system-overview/) for overall architecture and [CPU Subsystem]({{ site.baseurl }}/cpu-subsystem/) for detailed CPU specifications.

## Overview

```
Power On
    │
    ▼
┌─────────────────┐     ┌─────────────────┐
│   Main CPU      │     │    Sub CPU      │
│  TMP94C241F     │     │   TMP94C241F    │
│  (IC10)         │     │   (IC27)        │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │  1. Table Data ROM    │  1. Boot ROM
         │     First-stage boot  │     0xFF8290
         │                       │
         ▼                       ▼
    Memory Remap            Init Hardware
    Program ROM → 0xE00000  Wait for payload
         │                       │
         │  2. Program ROM       │
         │     RESET_HANDLER     │
         │                       │
         ▼                       ▼
    Init Hardware           Receive payload
    Load Sub CPU            at 0x0400
    Payload (192KB)              │
         │                       │
         │   ◄─── DMA ───►       │
         │   (0x120000 latch)    │
         │                       │
         ▼                       ▼
    Start Subsystems        Execute Payload
    (UI, MIDI, FDC...)      (Audio Engine)
         │                       │
         ▼                       ▼
    ┌─────────────────────────────┐
    │     System Ready            │
    └─────────────────────────────┘
```

## Main CPU Boot Sequence

### Discovery: Two-Stage Boot Process

**Important finding**: The Main CPU uses a **two-stage boot process**. On reset, the **Table Data ROM** is initially mapped at 0xE00000-0xFFFFFF and contains a first-stage bootloader. This bootloader configures the memory controller to remap the Program ROM to 0xE00000, then jumps to the main firmware.

### Stage 1: Table Data ROM Bootloader

> **Status**: The table_data boot code section (0xFFB4E8-0xFFFFFF, 19,224 bytes) is now **100% byte-matching**. See `table_data/kn5000_table_data.asm` and the reference disassembly at `original_ROMs/table_data_bootcode.unidasm`.

#### Reset Vector (0xFFFEE0)

On CPU reset, the Table Data ROM is mapped at 0xE00000-0xFFFFFF. The reset vector at 0xFFFEE0 (table_data offset 0x1FFEE0) contains:

```asm
JP 0x00FFB4E8    ; Jump to first-stage boot code
```

#### First-Stage Boot Code (0xFFB4E8)

The table_data bootloader at 0xFFB4E8 performs critical memory controller configuration:

```asm
; Memory Start Address Registers - define where each block appears
LD (MSAR0), 0x1E    ; Block 0 → 0x1E0000 (SRAM)
LD (MSAR1), 0x10    ; Block 1 → 0x100000 (I/O)
LD (MSAR2), 0xC0    ; Block 2 → 0xC00000
LD (MSAR3), 0x00    ; Block 3 → 0x000000 (DRAM)
LD (MSAR4), 0x80    ; Block 4 → 0x800000 (Table Data - NEW location)
LD (MSAR5), 0x00    ; Block 5 → 0x000000

; Memory Address Mask Registers - define block sizes
LD (MAMR0), 0x0F    ; Block 0 mask
LD (MAMR1), 0x3F    ; Block 1 mask
LD (MAMR2), 0x7F    ; Block 2 mask
LD (MAMR3), 0x1F    ; Block 3 mask
LD (MAMR4), 0xFF    ; Block 4 mask
LD (MAMR5), 0xFF    ; Block 5 mask

; DRAM Controller initialization
LD (DRAM1REF), 0x81
LD (DRAM1CRL), 0x8B
LD (DRAM1CRH), 0x58
LD (PMEMCR), 0xF1
```

After this configuration:
- **Table Data ROM** is remapped to 0x800000-0x9FFFFF
- **Program ROM** becomes visible at 0xE00000-0xFFFFFF
- The bootloader jumps to the Program ROM's `RESET_HANDLER` at 0xEF03C6

#### Boot_ClearRAM Routine (0xFFB740)

The first-stage bootloader calls `Boot_ClearRAM` to initialize RAM and copy essential data from ROM:

```asm
Boot_ClearRAM:
    ; Clear 35,146 bytes at RAM 0x104E (general RAM area)
    LD XDE, 0x0000104E    ; Destination
    LD XBC, 0x0000894A    ; Count
    ; Uses LDIRW for efficient word-mode fill with zeros

    ; Clear 1,091 bytes at RAM 0x0C00 (boot variables)
    LD XDE, 0x00000C00
    LD XBC, 0x00000443

    ; Copy 10 bytes from ROM 0xFFB4D2 to RAM 0x1044
    ; Data: 00 40 20 08 10 04 02 00 01 00 (bit mask table)

    ; Copy 12 bytes from ROM 0xFFB4DC to RAM 0x9998
    ; Data: 7E 00 10 00 00 00 80 00 00 00 00 00 (init params)
```

The bit mask table at 0x1044 is used for bit manipulation operations throughout the firmware. The initialization parameters at 0x9998 appear to be related to stack/display setup.

#### LZSS Decompressor Suite (0xFFC8C2-0xFCCA4F)

The bootloader includes a complete LZSS decompression subsystem for handling compressed firmware data. This is the "SLIDE4K" format used by the firmware update system.

> **Status**: All LZSS routines (872 bytes total) are now **100% byte-matching** disassembly in `table_data/kn5000_table_data.asm`.

##### Decompressor Routines

| Routine | Address | Size | Purpose |
|---------|---------|------|---------|
| `LZSS_ReadByte` | 0xFFC8C2 | 115 bytes | Read from compressed stream with sector buffering |
| `LZSS_OutputByte` | 0xFFC935 | 63 bytes | Write decompressed bytes with 32-bit batching |
| `LZSS_OutputByte_Alt` | 0xFFC974 | 63 bytes | Alternative output for flash update mode |
| `LZSS_ParseHeader` | 0xFFC9B3 | 157 bytes | Parse/validate firmware header, setup source |
| `LZSS_Decompress` | 0xFFCA50 | 474 bytes | Main decompression loop with sliding window |

##### Format Characteristics

| Parameter | Value | Description |
|-----------|-------|-------------|
| Window Size | 4096 bytes (0x1000) | Standard SLIDE4K |
| Pre-fill | 0x00 for first 4078 bytes | Window positions 0-0x0FED |
| Initial Position | 0x0FEE | First write position |
| Offset Bits | 12 bits | Masked with 0x0FFF |
| Length Bits | 4 bits | Stored in high nibble of second byte |
| Flag Byte | High bit = sentinel | Bit 0: 1=literal, 0=back-ref |
| Header | "SLIDE4K" + size | 11+ byte header with magic and decompressed size |

##### RAM Variables (0x0C20-0x0C38)

| Address | Name | Purpose |
|---------|------|---------|
| 0x0C20 | Expected Size | Target decompressed size (3 bytes LE) |
| 0x0C24 | Output Position | Current output byte count |
| 0x0C28 | Dest Address | Destination pointer for decompressed data |
| 0x0C2C | Buffer Pointer | Sector read buffer (typically 0x0099A4) |
| 0x0C30 | Display X | Progress indicator X coordinate |
| 0x0C32 | Display Y | Progress indicator Y coordinate |
| 0x0C34 | Sector Offset | Current sector read offset |
| 0x0C36 | Byte Counter | Output byte counter (0-3 for 32-bit writes) |
| 0x0C38 | Source Address | Compressed data source pointer |

##### Decompression Algorithm

```
1. Allocate 4KB window buffer (via malloc at 0xFFFB56)
2. Pre-fill window[0..0xFED] with 0x00
3. Set window_pos = 0x0FEE
4. Read 8-byte header, then 3-byte size (little-endian)
5. Main Loop:
   a. Shift flag byte right
   b. If bit 8 clear, read new flag byte (set bit 8 as sentinel)
   c. If bit 0 = 1: read literal byte, output to dest and window
   d. If bit 0 = 0:
      - Read offset low byte (8 bits)
      - Read offset high + length byte
      - Offset = (high_nibble << 8) | low_byte (12 bits)
      - Length = low_nibble + 2
      - Copy (length) bytes from window[offset] to output
   e. Update window_pos (masked to 12 bits)
6. Continue until output_size reached
7. Free window buffer (via free at 0xFFFCDD)
```

##### Compressed Data Locations

| Location | Address | Contents | Header |
|----------|---------|----------|--------|
| **Table Data ROM** | 0x8E0000 | Compressed Sub CPU Program | `"SLIDE4K", 0x00, 0x00, 0x95...` |
| **Boot Headers** | 0x9FA000 | Update file type signatures | `"SLIDE"` markers |
| **Boot UI** | 0x9FA150 | Flash update UI bitmaps | `"SLIDE"` marker + bitmap |

##### Callers of LZSS Decoder

The LZSS decoder is invoked during flash firmware updates:

| Routine | Address | File Type | Source |
|---------|---------|-----------|--------|
| `HANDLE_UPDATE_FILE_TYPE_ID_007h` | 0xEF47FA | Program DATA FILE PCK | 0x3E0000, 0x3F0000 |
| `HANDLE_UPDATE_FILE_TYPE_ID_008h` | 0xEF481E | Table DATA FILE PCK | Table Data ROM |
| `LZSS_ParseHeader` | 0xFFC9B3 | Flash update mode | 0x3E0000 (boot context) |

##### Update File Types

The firmware update system recognizes these LZSS-compressed file types:

| ID | File Type String | Description |
|----|-----------------|-------------|
| 0x07 | `"Technics KN5000 Program  DATA FILE PCK"` | Compressed program ROM |
| 0x08 | `"Technics KN5000 Table    DATA FILE PCK"` | Compressed table data |
| - | `"Technics KN5000 CMPCUSTOMDATA FILE"` | Compressed custom data |

The `PCK` suffix indicates LZSS-compressed content using the SLIDE4K format.

#### Evidence

The table_data ROM contains a complete interrupt vector table at offset 0x1FFF00:

| Vector | Address | Target | Description |
|--------|---------|--------|-------------|
| 0 (Reset) | 0xFFFEE0 | 0xFFB4E8 | First-stage boot code |
| 1-7 | 0xFFB705 | Handler | Common interrupt handler |
| 11 | 0xFFEAB2 | Handler | Specific handler |

The memory controller values in the table_data bootloader are **identical** to those in the Program ROM boot code (lines 134224-134235 of `kn5000_v10_program.asm`), confirming this is the intended configuration.

### Stage 2: Program ROM Main Boot

#### Reset Handler (0xEF03C6)

After memory remapping, execution continues at `RESET_HANDLER` in the Program ROM. The TMP94C241F CPU now sees the Program ROM at 0xE00000-0xFFFFFF.

#### Hardware Initialization

The reset handler performs additional hardware setup (note: memory controller is already configured by Stage 1):

| Step | Description | Key Registers |
|------|-------------|---------------|
| 1 | Disable watchdog | WDMOD, WDCR |
| 2 | Configure clock | CLKMOD |
| 3 | Initialize ports | P0-PZ, PxCR, PxFC |
| 4 | Set up memory controller | MSARx, MAMRx, BxCS |
| 5 | Initialize DRAM | DREFCR, DMEMCR |
| 6 | Configure timers | T01MOD, T4MOD, etc. |
| 7 | Initialize stack | XSP = stack address |

#### Sub CPU Payload Loading

After hardware initialization, the main CPU loads a 192KB firmware payload to the sub CPU via DMA through the inter-CPU latch at `0x140000` (main CPU side) / `0x120000` (sub CPU side).

**Main CPU Boot Sequence:**
```
RESET_HANDLER (0xEF03C6)
    │
    ├── LD (PA), 0xFE         ; Hold Sub CPU in reset (bit 0 = 0)
    │
    ├── ... hardware init ...
    │
    ├── SET 0, (PA)           ; Release Sub CPU from reset (0xEF05F3)
    │
    ├── CALL SubCPU_Init_DMA_Channels  ; Set up DMA at 0xEF329E
    │
    ├── EI 0                  ; Enable interrupts
    │
    └── CALR SubCPU_Send_Payload       ; Send 192KB payload at 0xEF068A
```

**E1 Transfer Protocol:**
1. Main CPU waits for SSTAT1 high (Sub CPU ready)
2. Main CPU sends E1 command byte (0xE1) to latch
3. Main CPU sends 6-byte header (destination address + byte count)
4. Main CPU sends actual data via DMA
5. Repeat for each 64KB chunk
6. Sub CPU receives E3 command, sets bit 6 of PAYLOAD_LOADED_FLAG
7. Sub CPU boot ROM calls payload at 0x000400

See [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) for detailed protocol documentation.

#### Subsystem Initialization

After the sub CPU payload is loaded:

| Subsystem | Description |
|-----------|-------------|
| Display | VGA-compatible LCD controller at 0x1A0000 |
| Control Panel | Serial communication with MCU (SC1, 250kHz) |
| FDC | Floppy disk controller at 0x110000 |
| MIDI | External MIDI I/O |
| HDAE5000 | Hard disk expansion (if present) at 0x160000 |

#### Main Loop

The main CPU enters its event loop, handling:
- User interface events
- Control panel button/encoder input
- MIDI I/O
- Disk operations
- Display updates

### Complete Boot Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         POWER ON / RESET                              │
│                                                                       │
│  Initial Memory Map:                                                  │
│    0xE00000-0xFFFFFF = Table Data ROM (contains first-stage boot)    │
│    Program ROM not yet visible                                        │
└──────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   STAGE 1: TABLE DATA BOOTLOADER                      │
│                                                                       │
│  1. CPU fetches reset vector from 0xFFFF00 (table_data @ 0x1FFF00)   │
│  2. Vector points to 0xFFFEE0 → JP 0xFFB4E8                          │
│  3. Boot code configures MSAR0-5, MAMR0-5, DRAM controller           │
│  4. Memory remap: Table Data → 0x800000, Program ROM → 0xE00000      │
│  5. Jump to Program ROM entry point (0xEF03C6)                        │
└──────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    STAGE 2: PROGRAM ROM BOOT                          │
│                                                                       │
│  Final Memory Map:                                                    │
│    0x000000-0x0FFFFF = DRAM (1MB)                                    │
│    0x100000-0x1FFFFF = I/O (FDC, latches, VGA, SRAM)                 │
│    0x300000-0x3FFFFF = Custom Data Flash                              │
│    0x400000-0x7FFFFF = Rhythm Data ROM                                │
│    0x800000-0x9FFFFF = Table Data ROM (remapped)                      │
│    0xE00000-0xFFFFFF = Program ROM (now visible)                      │
│                                                                       │
│  1. RESET_HANDLER at 0xEF03C6                                         │
│  2. Hardware initialization (redundant memory controller setup)       │
│  3. Release Sub CPU from reset                                        │
│  4. Send 192KB payload to Sub CPU                                     │
│  5. Initialize subsystems and enter main loop                         │
└──────────────────────────────────────────────────────────────────────┘
```

### Implications for MAME Emulation

The discovery of the two-stage boot process has significant implications for accurate MAME emulation:

#### Current Driver (Incorrect)

The current MAME driver uses a static memory map:
```cpp
map(0x800000, 0x9fffff).rom().region("table_data", 0);
map(0xe00000, 0xffffff).rom().region("program", 0);
```

This assumes the Program ROM is always at 0xE00000, which is only true **after** the memory controller is configured.

#### Required Fix

For accurate emulation, the MAME driver needs to:

1. **On reset**: Map Table Data ROM at 0xE00000-0xFFFFFF
2. **Emulate MSAR/MAMR register writes**: When the bootloader writes to memory controller registers (0x0142-0x0157), update the address mapping dynamically
3. **After reconfiguration**: Program ROM becomes visible at 0xE00000, Table Data at 0x800000

#### Workaround

If implementing dynamic remapping is complex, a workaround might be to:
- Pre-configure the memory map to the final state
- Patch the table_data reset vector to jump directly to Program ROM's RESET_HANDLER

However, this violates the project's strict accuracy policy and may cause issues with code that expects the original boot sequence.

### Subprogram Storage Location (RESOLVED)

The Sub CPU payload storage has been identified:

**Primary Location: Table Data ROM at 0x8E0000**

The compressed Sub CPU program is stored in the Table Data ROM at offset 0x0E0000 (address 0x8E0000 after remap). It uses the SLIDE4K LZSS compression format:

```
Address: 0x8E0000 (Table Data ROM)
Header:  "SLIDE4K" + 0x00 + 0x00 + 0x95 + 0x00 + "}Z" + 0xEE + 0xF0
Format:  LZSS SLIDE4K compressed
Content: kn5000_subprogram_v142 (192KB uncompressed)
```

**Why Previous Search Failed:**

- During Stage 1 boot, table_data is at 0xE00000
- Offset 0x30000 would be address 0xE30000 (table_data's own code)
- The actual subprogram is at offset 0x0E0000, not 0x030000
- After remap, 0x8E0000 points to the compressed payload

**Decompression Flow:**

1. Flash update handler sets source address to 0x3E0000 (boot context) or 0x8E0000 (runtime)
2. `LZSS_ParseHeader` validates the "SLIDE4K" header
3. `LZSS_Decompress` decompresses to destination buffer
4. Decompressed payload is written to flash or loaded to Sub CPU RAM

The label `Compressed_data` at 0x8E0000 in `table_data/kn5000_table_data.asm` marks this location.

---

## Sub CPU Boot Sequence

The sub CPU has a dedicated 128KB boot ROM (`kn5000_subcpu_boot.ic30`) that initializes hardware and waits for the payload.

### 1. Reset Vector (0xFFFEE0)

The sub CPU's reset vector jumps to `BOOT_INIT` at `0xFF8290`.

### 2. Hardware Initialization (BOOT_INIT)

```
Address: 0xFF8290
Size: ~400 bytes
```

**Initialization steps:**

| Step | Registers | Values | Purpose |
|------|-----------|--------|---------|
| 1 | WDMOD_REAL | 0x00 | Disable watchdog |
| 2 | INT_CTRL | 0x04 | Configure interrupts |
| 3 | P0FC-P2FC | 0xFF | Port 0-2 all function mode |
| 4 | P7, P7FC, P7CR | Various | Port 7 configuration |
| 5 | P8, P8FC, P8CR | Various | Port 8 (chip select) |
| 6 | PA, PAFC, PB, PBFC | Various | DRAM signals |
| 7 | INTTC01 | 0x03 | Timer interrupt control |
| 8 | SC0/SC1 registers | Various | Serial configuration |
| 9 | T01MOD, T23MOD | Various | Timer modes |
| 10 | MSARx, MAMRx | Various | Memory controller |
| 11 | SER0/SER1 | Various | Serial channels |
| 12 | DRAM_* | Various | DRAM refresh/timing |
| 13 | BxCSL, BxCSH | Various | Bus chip select |

### 3. Copy Interrupt Vectors (Boot_Copy_Vectors)

```
Address: 0xFF846D
Source: 0xFF8F6C (ROM)
Destination: 0x0400 (RAM)
Size: 225 bytes (0xE1 bytes)
```

The boot ROM copies interrupt vector trampolines from ROM to RAM. These are placeholder handlers that jump back to boot ROM until the actual payload overwrites them:

```asm
Boot_Copy_Vectors:             ; 0xFF846D
    LD   XDE, 0x00000400       ; Destination: RAM at 0x0400
    LD   XHL, 0x00FF8F6C       ; Source: ROM stub table
    LD   XBC, 0x000000E1       ; Count: 225 bytes
    LDIR                       ; Block copy
    RET
```

### 4. Enable Interrupts

```asm
ei 0    ; Enable interrupts at level 0
```

### 5. Initialization Routines

| Routine | Address | Size | Purpose |
|---------|---------|------|---------|
| INIT_MEMORY_TEST | 0xFF8956 | ~300B | RAM test, ROM checksum |
| INIT_DMA_SERIAL | 0xFF85AE | ~90B | DMA and serial setup |
| INIT_TONE_GEN | 0xFF84A8 | ~70B | Tone generator at 0x130000 |

### 6. Main Loop (Wait for Payload)

```
Address: 0xFF8405
```

The sub CPU enters a loop waiting for the payload ready flag:

```asm
MAIN_LOOP:
    res  6, (SUBCPU_STATUS_FLAGS)    ; Clear ready flag
.wait_loop:
    bit  6, (SUBCPU_STATUS_FLAGS)    ; Check if payload ready
    jr   Z, .check_status
    ei   6                            ; Enable interrupt level 6
    call PAYLOAD_ENTRY               ; Call payload at 0x0400
.check_status:
    ; Update serial status
    jr   .wait_loop
```

### 7. Payload Execution

Once `PAYLOAD_LOADED_FLAG` bit 6 is set (by E3 command), the sub CPU jumps to the payload entry point at `0x0400`. The payload takes over audio synthesis and tone generation duties.

---

## Inter-CPU Communication Protocol

The main CPU and sub CPU communicate via a single-byte latch at `0x120000`.

### Command Format

| Command | Description | Data Size | Buffer |
|---------|-------------|-----------|--------|
| 0x00-0x1F | Variable-length data | Low 5 bits + 1 | CMD_DATA_BUFFER |
| 0xE1 | Two-phase transfer setup | 6 bytes | CMD_E1_BUFFER |
| 0xE2 | Parameter block | 10 bytes | CMD_E2_BUFFER |
| 0xE3 | Payload complete | 0 bytes | - |

### Variable-Length Commands (0x00-0x1F)

```
Bits 7-5: Handler index (0-7) from jump table at 0xFF8000
Bits 4-0: Data length - 1 (so 0x00 = 1 byte, 0x1F = 32 bytes)
```

### Handshaking Signals (INTERCPU_STATUS at 0x34)

| Bit | Direction | Meaning |
|-----|-----------|---------|
| 0 | Sub → Main | Sub CPU ready flag |
| 1 | Internal | Completion signal from interrupt |
| 2 | Internal | Gate for command processing |
| 4 | Main → Sub | Main CPU ready flag |

### DMA State Machine (DMA_XFER_STATE at 0x0516)

| State | Meaning |
|-------|---------|
| 0 | Idle - no transfer in progress |
| 1 | Single transfer - waiting for completion |
| 2 | Two-phase transfer - phase 1 done, phase 2 pending |

### Transfer Flow

```
Main CPU                          Sub CPU
   │                                 │
   │  1. Write command to latch      │
   │  ─────────────────────────────► │
   │                                 │  2. InterCPU_RX_Handler
   │                                 │     triggered
   │                                 │
   │  3. Wait for sub ready          │  4. Set up DMA
   │  ◄───────────────────────────── │     destination
   │                                 │
   │  5. Send data bytes             │
   │  ─────────────────────────────► │  6. DMA receives data
   │                                 │
   │  7. Check completion            │  8. DMA_Complete_Handler
   │  ◄───────────────────────────── │     clears state
   │                                 │
```

---

## Boot ROM Routines Reference

### DMA Transfer Routines (0xFF8604-0xFF881E)

| Routine | Address | Size | Description |
|---------|---------|------|-------------|
| SendData_Chunked | 0xFF8604 | 69B | Break large transfers into 32-byte chunks |
| SendData_Block | 0xFF8649 | 99B | Send single block with handshaking |
| SendCmd_E3 | 0xFF86AC | 48B | Signal payload complete |
| SendParams_E2 | 0xFF86DC | 112B | Send E2 parameter block |
| TwoPhase_Transfer | 0xFF874C | 211B | Execute E1 two-phase sequence |

### Interrupt Handlers

| Handler | Address | Description |
|---------|---------|-------------|
| InterCPU_RX_Handler | 0xFF881F | Receives commands from main CPU |
| DMA_Complete_Handler | 0xFF889A | Advances DMA state machine |
| CMD_Dispatch_Handler | 0xFF88B8 | Processes received commands |
| DEFAULT_HANDLER | 0xFF8432 | Default handler (just RETI) |

### Utility Routines

| Routine | Address | Description |
|---------|---------|-------------|
| COPY_VECTORS | 0xFF846D | Copy interrupt trampolines to RAM |
| INIT_TONE_GEN | 0xFF84A8 | Initialize tone generator |
| TONE_GEN_WRITE | 0xFF84F1 | Write to tone generator registers |
| CHECKSUM_CALC | 0xFF859B | Calculate memory checksum |
| MEM_TEST_ROUTINE | 0xFF89FC | RAM test with patterns |
| ROM_CHECKSUM | 0xFF8AB4 | Verify boot ROM integrity |

---

## Memory Map During Boot

### Sub CPU RAM Layout

| Address | Size | Symbol | Description |
|---------|------|--------|-------------|
| 0x0400 | 225B | PAYLOAD_ENTRY | Interrupt vector trampolines |
| 0x04FE | 1B | PAYLOAD_LOADED_FLAG | Payload ready flags |
| 0x0502 | 10B | DMA_SETUP_PARAMS | DMA parameter block |
| 0x050C | 6B | E1_XFER_PARAMS | E1 command parameters |
| 0x0512 | 4B | DMA_TARGET_ADDR | Current DMA destination |
| 0x0516 | 2B | DMA_XFER_STATE | DMA state machine |
| 0x0518 | 2B | CMD_PROCESSING_STATE | Command processing phase |
| 0x051A | 1B | LAST_CMD_BYTE | Last received command |
| 0x051E | 32B | CMD_DATA_BUFFER | Variable-length command data |
| 0x053E | 10B | E2_XFER_PARAMS | E2 command parameters |
| 0x0544 | 6B | CMD_E1_BUFFER | E1 command buffer |
| 0x054A | 10B | CMD_E2_BUFFER | E2 command buffer |
| 0x0556 | 1B | MEMTEST_RESULT | Memory test result |
| 0x0558 | 8B | SERIAL_STATUS | Serial status bytes |
| 0x05A2 | - | STACK_INIT | Initial stack pointer |

### Hardware Addresses

| Address | Description |
|---------|-------------|
| 0x100000 | Audio hardware registers (DSP/DAC) |
| 0x110000 | Tone generator data/status (P6.7 controlled) |
| 0x120000 | Inter-CPU communication latch |
| 0x130000 | Tone generator DSP control registers |

### Sub CPU Payload Command Dispatch

After payload loading, the `MICRODMA_CH0_HANDLER` at 0x020F1F processes commands using `CMD_DISPATCH_TABLE`:

| Handler | Command Range | Address | Purpose |
|---------|---------------|---------|---------|
| 0 | 0x00-0x1F | 0x034D5F | DSP/audio control |
| 1 | 0x20-0x3F | 0x01FC7C | Audio parameters |
| 2 | 0x40-0x5F | 0x01FC7F | Tone generator |
| 3 | 0x60-0x7F | 0x035893 | Effects processing |
| 4 | 0x80-0x9F | 0x01F890 | Serial port setup |
| 5 | 0xA0-0xBF | 0x03CFEE | Voice commands |
| 6-7 | 0xC0-0xFF | 0x020C12 | System commands |

---

## Timing Considerations

### Boot Time Estimates

| Phase | Duration | Notes |
|-------|----------|-------|
| Hardware init | ~1ms | SFR configuration |
| Memory test | ~10ms | RAM pattern test |
| ROM checksum | ~5ms | 4KB verification |
| Tone gen init | ~1ms | 4 channel setup |
| Payload load | ~100ms | 192KB via DMA |
| **Total** | **~120ms** | To payload execution |

### DMA Transfer Rates

- Latch clock: Tied to timer frequency
- Typical chunk size: 32 bytes
- Timeout: 60,000 iterations (~300ms at 20MHz)

---

## Error Handling

### Memory Test Errors (MEMTEST_RESULT)

| Bit | Meaning |
|-----|---------|
| 0-1 | Low word RAM errors |
| 2-3 | High word RAM errors |
| 3 | ROM checksum mismatch |

### DMA Timeouts

All DMA routines have 60,000 iteration timeouts (~300ms). On timeout:
- Transfer is abandoned
- Ready flag is set
- Control returns to caller

### HALT_LOOP (0xFF8490)

Fatal error handler that disables serial and halts the CPU:

```asm
HALT_LOOP:
    res  0, (SC0MOD)    ; Disable serial
.halt:
    halt                ; Halt CPU
    jr   T, .halt       ; Loop forever
```

---

## HD-AE5000 Initialization (Optional)

If the HD-AE5000 hard disk expansion is detected (PE port bit 0 = 0), the main CPU calls its initialization routines.

### Detection and Entry

```
Main CPU checks PE.0
    │
    ├─► PE.0 = 1: No HD-AE5000, skip
    │
    └─► PE.0 = 0: HD-AE5000 present
            │
            ▼
        Validate ROM header at 0x280000
        Check for "XAPR" magic string
            │
            ▼
        CALL 0x280008 (Boot Init entry)
```

### HDAE5000_Boot_Init (0x28F576)

The boot initialization performs these steps:

| Step | Action | Details |
|------|--------|---------|
| 1 | Store workspace | Save main CPU workspace pointer at 0x23A1A2 |
| 2 | Clear work buffer | Zero 62KB at 0x22A000 |
| 3 | Register handlers | Register 12 callback handlers with main CPU |
| 4 | Load palette | Load 256-entry VGA palette from ROM |
| 5 | Copy VRAM data | Copy 76,800 bytes to 0x1A0000 and 0x1A9600 |
| 6 | Init handler pointers | Store function pointers at 0x230ECC/ED2/ED6 |
| 7 | RAM test | Fill/verify 32KB at 0x230F1C-0x238F1C |
| 8 | Check HD presence | Detect hard disk, store result at 0x230EDA |
| 9 | Register frame handler | Set up periodic update callback |

### Workspace Dispatch System

The main CPU provides a callback registration system that HDAE5000 uses to integrate with the UI framework:

```
WORKSPACE_PTR (0x23A1A2)
    │
    └──► Handler Table A (offset +0x0E0A)
              │
              ├──► Registration func (offset +0x00E4)
              ├──► Display callback (offset +0x0124)
              ├──► UI callbacks (offsets +0x0244, +0x0248, etc.)
              │
    └──► Handler Table B (offset +0x0E88)
              │
              └──► Audio/system callbacks
```

HDAE5000 registers 12 handlers using this system, each identified by a port address (0x0160000x) and handler ID.

### Frame Handler (0x28F662)

After initialization, the main CPU calls the frame handler periodically:

1. Calculate display offset from handler states
2. Check for state changes via callback dispatch
3. Monitor status bit 2 for display refresh triggers
4. Jump to PPORT handler for parallel port polling

---

## Subsystem Initialization Order

After boot completes, subsystems initialize in this order:

```
Sub CPU Payload Loaded (E3 command)
    │
    ▼
┌─────────────────────────────────────────────┐
│         Main CPU Subsystem Init             │
├─────────────────────────────────────────────┤
│  1. Display System (VGA controller)         │
│     - Configure MN89304 at 0x170000         │
│     - Set 320×240 resolution                │
│     - Load default palette                  │
│                                             │
│  2. Control Panel (Serial Channel 1)        │
│     - 250kHz clock, 8-bit mode              │
│     - Initialize button/encoder states      │
│     - Start polling loop                    │
│                                             │
│  3. Floppy Disk Controller (0x110000)       │
│     - Detect drive presence                 │
│     - Initialize FDC state machine          │
│                                             │
│  4. HDAE5000 (if present)                   │
│     - Call 0x280008 for initialization      │
│     - Register frame handler                │
│                                             │
│  5. MIDI I/O                                │
│     - Configure serial channels             │
│     - Initialize message buffers            │
└─────────────────────────────────────────────┘
    │
    ▼
    Main Event Loop
```

---

## System Runtime

### Main Event Loop

After all initialization completes, the main CPU enters its event loop:

```
┌──────────────────────────────────────────────────────────┐
│                    MAIN EVENT LOOP                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Control   │    │   Display   │    │    MIDI     │  │
│  │   Panel     │───►│   Update    │───►│  Processing │  │
│  │   Poll      │    │             │    │             │  │
│  └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                  │                  │          │
│         ▼                  ▼                  ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │    FDC      │    │  HDAE5000   │    │   Audio     │  │
│  │   Handler   │───►│   Frame     │───►│   Sync      │  │
│  │             │    │   Handler   │    │             │  │
│  └─────────────┘    └─────────────┘    └─────────────┘  │
│                           │                              │
│                           ▼                              │
│                    Loop continues                        │
└──────────────────────────────────────────────────────────┘
```

### Control Panel Communication

The control panel uses a serial protocol at 250kHz:

| Direction | Data | Purpose |
|-----------|------|---------|
| Main → Panel | Button LED states | Update indicator LEDs |
| Panel → Main | Button presses | User input events |
| Panel → Main | Encoder deltas | Rotary encoder changes |

See [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) for detailed protocol documentation.

### Inter-CPU Communication (Runtime)

During runtime, the main CPU sends commands to the sub CPU for audio operations:

| Command Range | Purpose |
|---------------|---------|
| 0x00-0x1F | DSP/audio control |
| 0x20-0x3F | Audio parameters |
| 0x40-0x5F | Tone generator |
| 0x60-0x7F | Effects processing |
| 0x80-0x9F | Serial port setup |
| 0xA0-0xBF | Voice commands |
| 0xC0-0xFF | System commands |

### HDAE5000 PPORT Polling

If HD-AE5000 is present, its frame handler checks for PC parallel port commands:

1. Check PPORT status register at 0x239000
2. If active, load parameters from 0x23900A-0x239010
3. Call PPORT_Setup (0x29511C) and PPORT_Dispatch (0x2950CC)
4. Process command from jump table at 0x2953E2

Available PPORT commands include file transfers, HD formatting, and PC communication.

---

## Complete Boot Timeline

```
Time    Event
─────   ─────────────────────────────────────────────────
0ms     Power On
        ├── Main CPU reset vector → hardware init
        └── Sub CPU reset vector → hardware init

1ms     Hardware configured
        ├── Main CPU: Ports, memory controller, timers
        └── Sub CPU: Serial, DMA, tone generator

10ms    Memory tests complete
        └── Sub CPU: RAM pattern test, ROM checksum

15ms    Sub CPU waiting for payload
        └── Main CPU: Begin payload transfer

115ms   Payload loaded (192KB via DMA)
        └── E3 command signals completion

120ms   Sub CPU executing payload
        ├── Audio engine active
        └── Command dispatch ready

150ms   Main CPU subsystem init
        ├── Display initialized
        ├── Control panel connected
        └── FDC ready

200ms   HDAE5000 init (if present)
        ├── 32KB RAM test
        ├── HD detection
        └── Frame handler registered

250ms   System Ready
        └── Main event loop running
```

---

## See Also

- [Memory Map]({{ site.baseurl }}/memory-map/) - Complete address space documentation
- [Reverse Engineering]({{ site.baseurl }}/reverse-engineering/) - Technical details
- [ROM Reconstruction]({{ site.baseurl }}/rom-reconstruction/) - Build status and known issues
- [HDAE5000 Hard Disk Expansion]({{ site.baseurl }}/hdae5000/) - HD-AE5000 firmware details
- [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) - Serial communication with control panel
