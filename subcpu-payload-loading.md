---
layout: page
title: SubCPU Payload Loading
permalink: /subcpu-payload-loading/
---

# SubCPU Payload Loading Investigation

This page documents the investigation into why the SubCPU never receives its firmware payload in MAME emulation, resulting in "Sound Name Error" messages. The SubCPU firmware is stored compressed (LZSS SLIDE4K format) in the Custom Data Flash ROM (IC19) and must be decompressed and transferred to the SubCPU during boot.

> **Status:** Active investigation. See [Boot Sequence]({{ site.baseurl }}/boot-sequence/) for the overall boot flow and [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) for latch communication details.

## Background

After replacing the decompressed SubCPU payload ROMs with the compressed originals (LZSS SLIDE4K format at Custom Data Flash offset 0xE0000 = address 0x3E0000), the MAME driver shows "Sound Name Error" messages. This indicates the SubCPU never receives its firmware payload, so sound commands fail.

The firmware's `SubCPU_Send_Payload` function (address `0xEF068A`) is responsible for:

1. Sending 5 x 64KB of config data from Table Data ROM (`0x830000`-`0x870000`) to SubCPU RAM
2. Decompressing the compressed payload from `0x3E0000` to Main CPU RAM at `0x050000`
3. Sending the decompressed data (preset data + entry point code) to SubCPU via E1 bulk transfers
4. The SubCPU starts executing payload code when it receives a command byte of `0xE3`

## Boot Flow: Payload Transfer

The complete calling sequence during boot:

```
User_didnt_request_flash_mem_update (0xEF05E8)
  │
  ├── SET 0, (PA)              → Release Sub CPU from reset
  ├── SubCPU_Init_DMA_Channels → Initialize DMA for inter-CPU comm
  ├── EI 000h                  → Enable interrupts
  ├── SubCPU_Send_Payload      → Transfer 192KB firmware payload
  ├── SubCPU_Payload_Verify    → Verify checksums
  ├── ScreenGroup_Dispatch(0)  → Display initial boot screen
  └── ... (continues boot)
```

### SubCPU_Send_Payload Detail (0xEF068A)

Source: `maincpu/kn5000_v10_program.asm:134123`

```
Phase 1: Transfer 5 x 64KB from Table Data ROM
  0x830000 → SubCPU 0x050000 (64KB)
  0x840000 → SubCPU 0x060000 (64KB)
  0x850000 → SubCPU 0x070000 (64KB)
  0x860000 → SubCPU 0x080000 (64KB)
  0x870000 → SubCPU 0x090000 (64KB)

Phase 2: LZSS Decompression
  Source: 0x3E0000 (Custom Data Flash)
  Dest:   0x050000 (Main CPU RAM, temporary)
  Calls LABEL_EF41E3 (LZSS decompressor)
  If decompression fails (HL=0xFFFF): falls back to Table Data ROM base

Phase 3: Transfer decompressed data to SubCPU
  XIZ+0x100, 64KB    → SubCPU 0x00F000
  XIZ+0x10100, 64KB  → SubCPU 0x01F000
  XIZ+0x20100, 0xFF00 → SubCPU 0x02F000
  XIZ, 0x100 (256B)  → SubCPU 0x000400 (entry point!)
```

### E1 Bulk Transfer Protocol

Source: `maincpu/kn5000_v10_program.asm:139166`

Each E1 transfer follows this protocol:

1. Wait for `SSTAT1` high (Sub CPU ready)
2. Clear `MSTAT0`, set state to 2 (two-phase)
3. Write `0xE1` to latch at `0x140000` → triggers INT0 on Sub CPU
4. Wait for `SSTAT1` low (Sub CPU acknowledged E1)
5. Set `MSTAT0`, send 6-byte header (dest addr + byte count) via `Audio_DMA_Transfer`
6. Wait for state transition, send actual data payload via `Audio_DMA_Transfer`

The Main CPU sends data byte-by-byte in a tight software loop (`Audio_DMA_Transfer` at `0xEF3415`). Each write to the latch triggers INT0 on the Sub CPU.

### Sub CPU Reception (Boot ROM INT0 Handler)

Source: `subcpu/boot/kn5000_subcpu_boot.asm:1159`

The Sub CPU's INT0 handler (`InterCPU_RX_Handler` at `0xFF881F`) processes incoming bytes:

1. **First byte** (command): DMAV0 not armed, so CPU INT0 handler fires
   - Reads command byte from latch (`0x120000`)
   - For E1: Sets up DMA channel 0 destination and count (6 bytes for header)
   - Arms DMAV0 = `0x0A` (DMA triggers on INT0 for subsequent bytes)
2. **Subsequent bytes**: DMAV0 armed, so HDMA processes INT0
   - Each latch write triggers INT0 → HDMA transfers one byte to destination
   - DMA count decrements automatically
3. **DMA completion**: Fires DMA completion interrupt
   - `DMA_Complete_Handler` advances state machine (state 2→1→0)
   - `CMD_Dispatch_Handler` sets up phase 2 DMA (actual data transfer)

### The E3 "Payload Ready" Signal

**Critical finding:** The Main CPU does NOT send a dedicated E3 command after `SubCPU_Send_Payload`. Instead, `0xE3` is a **regular data command byte** that happens to match the E3 case in the Sub CPU's INT0 handler.

The data command byte format is: `(channel << 5) | (count - 1)`

- `0xE3` = `0b11100011` = channel 7, count 4 bytes

When the Main CPU first sends a 4-byte audio data packet on channel 7 (via `InterCPU_Send_Data_Block`), the Sub CPU's INT0 handler interprets `0xE3` as the "payload ready" signal:

```asm
; subcpu/boot/kn5000_subcpu_boot.asm:1189
    cp  A, 0E3h           ; Command E3?
    jr  NZ, .default_cmd
    set 6, (SUBCPU_STATUS_FLAGS)  ; Signal payload ready!
```

The Sub CPU's main loop polls this flag:

```asm
; subcpu/boot/kn5000_subcpu_boot.asm:405
MAIN_LOOP:
    res 6, (SUBCPU_STATUS_FLAGS)    ; Clear ready flag
.wait_loop:
    bit 6, (SUBCPU_STATUS_FLAGS)    ; Check if payload ready
    jr  Z, .check_status
    ei  6                           ; Enable interrupt level 6
    CALL_ABS24 PAYLOAD_ENTRY        ; Call payload at 0x0400
```

**This means:** The SubCPU won't start executing its payload until the Main CPU sends its first channel-7 audio command during boot. This typically happens during audio subsystem initialization after `ScreenGroup_Dispatch`.

## Identified Potential Failure Points

### 1. LZSS Decompression from 0x3E0000 (HIGH priority)

**File:** `maincpu/kn5000_v10_program.asm:140484` (`LABEL_EF41E3`)

The decompressor:
1. Verifies "SLIDE" signature at bytes 0-4
2. Checks version byte ('4' for SLIDE4K, '8' for alternate)
3. Calls appropriate decompressor (`LABEL_EF3FAB` for SLIDE4K)
4. Returns HL=0 on success, HL=0xFFFF on error

ROM flags at `0xFFFEEF` and `0xFFFEED` are both `0xFF` in the v10 ROM, so decompression WILL be attempted.

**Risk:** If decompression fails silently, the fallback reads from Table Data ROM at `0x800000`, which contains config data, NOT executable SubCPU code. The SubCPU would receive garbage at 0x0400.

### 2. DMA Channel Configuration (HIGH priority)

**Sub CPU DMA Setup** (`INIT_DMA_SERIAL` at `0xFF85AE`):
- DMA Channel 0: Source = `0x120000` (latch), mode = receive from latch
- DMA Channel 2: Destination = `0x120000` (latch), used for responses

**MAME SFR Map** (`tmp94c241.cpp:898`):
- `0x000100-0x000103`: DMAV registers mapped via `dmav_w()`

**The Sub CPU writes `0x0A` to address `0x0100`** (DMAV0) to arm DMA channel 0 for INT0 triggering. In MAME, this maps to `dmav_w(0, 0x0A)` which sets `m_dma_vector[0] = 0x0A`.

### 3. DMAR Register Not Mapped (HIGH priority)

**File:** `mame_driver/src/devices/cpu/tlcs900/tmp94c241.cpp`

The DMAR register at SFR address `0x109` is **NOT mapped** in MAME's address map. The Main CPU's INT0 handler writes to it:

```asm
; maincpu/kn5000_v10_program.asm:139267
INT0_HANDLER:           ; EF3525
    BIT 1, (PZ)         ; Check MSTAT1
    JR NZ, LABEL_EF3532
    LD (DMAR), 001h     ; Trigger DMA — WRITES TO UNMAPPED REGISTER!
    RETI
```

This affects the Main CPU's ability to receive data FROM the Sub CPU via DMA. While this doesn't block the initial payload transfer (Main CPU is the sender), it blocks the reverse E2/E3 communication path.

### 4. HDMA Interrupt-to-DMA Chain (HIGH priority)

For HDMA to work correctly, the following chain must be intact:

1. Main CPU writes byte to `subcpu_latch` via `generic_latch_8::write()`
2. `data_pending_callback` asserts `TLCS900_INT0` on Sub CPU
3. INT0 flag set in `INTE0AD` register (bit 3)
4. `tlcs900_check_hdma()` runs at next instruction boundary:
   - Checks DMAV0 (must be `0x0A`)
   - Checks INT0 flag in INTE0AD (must be set)
   - Reads from DMAS0 (`0x120000` = latch)
   - Writes to DMAD0 (destination buffer)
   - Decrements DMAC0
   - Clears INT0 flag

**Potential issues:**
- `tlcs900_check_hdma()` processes only ONE transfer per call and gates on interrupt level
- If `(m_sr.b.h & 0x70) == 0x70`, all HDMA is blocked
- DMA reads from `0x120000` must go through `generic_latch_8::read()`, which clears data_pending and deasserts INT0

### 5. E1 Handshake Timing (MEDIUM priority)

The MSTAT/SSTAT handshake uses 2-bit signals:
- **Main CPU Port Z** bits 0-1: MSTAT (output), bits 2-3: SSTAT (input)
- **Sub CPU Port D** bits 0-1: SSTAT (output), bit 2: MSTAT0 (input), bit 4: MSTAT1 (input)

**Note:** MSTAT1 is at bit 4 of Sub CPU Port D, not bit 3. This is an unusual mapping:
```cpp
// kn5000.cpp:653
m_subcpu->portd_read().set([this] {
    return (BIT(m_mstat, 0) << 2) | (BIT(m_mstat, 1) << 4);
});
```

The timeout for each wait loop is 60,000 iterations (`0xEA60`). If the Sub CPU doesn't respond quickly enough, the transfer aborts.

### 6. Sub CPU Reset Release Timing (LOW priority)

Port A bit 0 controls Sub CPU reset (active low):
```cpp
// kn5000.cpp:540
m_maincpu->porta_write().set([this] (u8 data) {
    m_subcpu->set_input_line(INPUT_LINE_RESET, BIT(data, 0) ? CLEAR_LINE : ASSERT_LINE);
});
```

`SET 0, (PA)` at `0xEF05F3` releases the Sub CPU before payload transfer. A delay loop of 0x2000 iterations follows before the first E1 transfer, allowing the Sub CPU boot ROM to initialize.

## Fixes Applied

### DMAR Register Implementation (0x109)

The DMAR register at SFR address `0x109` was missing from the MAME `tmp94c241` device. This register provides software-triggered DMA: writing bit N triggers an immediate DMA transfer on channel N.

**Fix:** Added `dmar_w()` handler at address `0x109` in the SFR address map. When a bit is set, it calls `tlcs900_process_hdma()` for the corresponding channel, performing an immediate DMA transfer.

This register is used by the Main CPU's INT0 handler (`LD (DMAR), 001h` at `0xEF352D`) to trigger DMA channel 0 when receiving data from the Sub CPU. Without this fix, reverse communication (Sub CPU → Main CPU) via DMA was broken.

### Diagnostic Logging

Added comprehensive logging to trace the inter-CPU communication:

- **Latch writes**: Command bytes (E1/E2/E3) logged with PC address; data bytes logged at verbose level
- **Handshake signals**: MSTAT/SSTAT changes logged with old/new values
- **Sub CPU reset**: Port A bit 0 changes logged
- **DMA vectors**: DMAV register writes logged with channel and value
- **DMA completion**: Logged when HDMA transfer count reaches zero

Logging is controlled by `VERBOSE` flags in `kn5000.cpp` and uses MAME's `logmacro.h` system.

## Research Plan

### Step 1: Add Diagnostic Logging

Add MAME `LOG()` calls to trace the boot flow:

| Location | What to Log |
|----------|-------------|
| `kn5000.cpp` latch write | Every byte written to `subcpu_latch` (Main→Sub) |
| `kn5000.cpp` latch read | Every byte read from `subcpu_latch` (Sub reads) |
| `kn5000.cpp` Port Z write | MSTAT changes |
| `kn5000.cpp` Port D write | SSTAT changes |
| `kn5000.cpp` Port A write | Sub CPU reset (bit 0) |
| `tmp94c241.cpp` HDMA | DMA transfers (channel, src, dst, count) |
| `tmp94c241.cpp` DMAV | DMA vector register writes |

### Step 2: Analyze Log Output

Run MAME with verbose logging and check:
- Does the Main CPU reach `SubCPU_Send_Payload`? (Look for E1 = `0xE1` in latch writes)
- Does the Sub CPU receive INT0? (Look for latch read logs)
- Do MSTAT/SSTAT signals toggle correctly?
- Does HDMA process DMA transfers after DMAV0 is armed?
- Are there timeout patterns (transfer aborting)?

### Step 3: Investigate DMAR Register

The DMAR register at `0x109` needs investigation:
- Check the TMP94C241 datasheet for DMAR behavior
- Determine if DMAR is needed for DMA triggering
- If needed: add SFR mapping in `tmp94c241.cpp`

### Step 4: Verify HDMA Interrupt Triggering

Verify that `tlcs900_check_hdma()` correctly processes INT0-triggered DMA:
- How `generic_latch_8::read()` interacts with INT0 deassertion
- Whether the interrupt flag is still set when `tlcs900_process_hdma()` checks it
- Whether HDMA runs between CPU instruction boundaries correctly

### Step 5: Fix Identified Issues

Based on findings, fix in priority order:
1. **DMAR register**: Add SFR mapping for `0x109`
2. **HDMA triggering**: Fix interrupt→DMA trigger chain if broken
3. **Decompression**: Verify LZSS decompression works with compressed ROM
4. **Timing**: Adjust if handshake timeouts occur

## Key Files

| File | Purpose |
|------|---------|
| `mame_driver/src/mame/matsushita/kn5000.cpp` | Main MAME driver (latches, ports, memory map) |
| `mame_driver/src/devices/cpu/tlcs900/tmp94c241.cpp` | CPU emulation (DMA, SFR, interrupts) |
| `mame_driver/src/devices/cpu/tlcs900/tmp94c241.h` | CPU header (DMA state) |
| `maincpu/kn5000_v10_program.asm:134123` | `SubCPU_Send_Payload` |
| `maincpu/kn5000_v10_program.asm:139166` | `InterCPU_E1_Bulk_Transfer` |
| `maincpu/kn5000_v10_program.asm:139115` | `Audio_DMA_Transfer` |
| `maincpu/kn5000_v10_program.asm:140484` | LZSS decompressor (`LABEL_EF41E3`) |
| `subcpu/boot/kn5000_subcpu_boot.asm:1159` | `InterCPU_RX_Handler` (INT0 handler) |
| `subcpu/boot/kn5000_subcpu_boot.asm:718` | `INIT_DMA_SERIAL` (DMA setup) |
| `subcpu/boot/kn5000_subcpu_boot.asm:405` | Main loop (payload ready polling) |

## Verification

After each fix:
1. Build MAME with the driver changes
2. Run with verbose logging enabled
3. Check if SubCPU payload transfer completes (look for E1 data in logs)
4. Check if "Sound Name Error" messages disappear
5. Check if the SubCPU begins executing payload code (look for `0xE3` command → bit 6 set)
