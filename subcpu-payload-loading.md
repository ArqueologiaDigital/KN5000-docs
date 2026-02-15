---
layout: page
title: SubCPU Payload Loading
permalink: /subcpu-payload-loading/
---

# SubCPU Payload Loading Investigation

This page documents the investigation into SubCPU firmware payload loading in MAME emulation. The investigation uncovered multiple bugs in MAME's TMP94C241 emulation (LDC CR mapping, DMAM encoding, HDMA/IRQ priority) that prevented DMA transfers. All have been fixed, and the SubCPU payload now loads and executes successfully.

> **Status:** Payload transfer is **WORKING**. The SubCPU receives all 9 E1 blocks (524,358 HDMA transfers) and begins executing payload code. The remaining "Sound Name Error" is caused by unimulated SubCPU sound peripherals (tone generator IC303, DSP IC311), not by the payload transfer itself. See [Boot Sequence]({{ site.baseurl }}/boot-sequence/) for the overall boot flow and [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) for latch communication details.

## Background

After replacing the decompressed SubCPU payload ROMs with the compressed originals (LZSS SLIDE4K format at Custom Data Flash offset 0xE0000 = address 0x3E0000), the MAME driver shows "Sound Name Error" messages. This indicates the SubCPU's sound hardware initialization fails because the tone generator and DSP are not emulated.

The firmware's `SubCPU_Send_Payload` function (address `0xEF068A`) is responsible for:

1. Sending 5 x 64KB of config data from Table Data ROM (`0x830000`-`0x870000`) to SubCPU RAM
2. Decompressing the compressed payload from `0x3E0000` to Main CPU RAM at `0x050000`
3. Sending the decompressed data (preset data + entry point code) to SubCPU via E1 bulk transfers
4. The last 256-byte E1 transfer writes to SubCPU address `0x000400`-`0x04FF`, which includes `SUBCPU_STATUS_FLAGS` at `0x04FE` -- when bit 6 of that byte is set by DMA, the boot ROM's polling loop triggers payload execution

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

### Confirmed Transfer Pattern (from MAME log analysis)

The following 9 E1 blocks were confirmed in the MAME log with 524,358 total HDMA transfers:

| Block | Source Address | SubCPU Dest | Size | Purpose |
|-------|--------------|-------------|------|---------|
| 1 | 0x830000 | 0x050000 | 64KB | Config data |
| 2 | 0x840000 | 0x060000 | 64KB | Config data |
| 3 | 0x850000 | 0x070000 | 64KB | Config data |
| 4 | 0x860000 | 0x080000 | 64KB | Config data |
| 5 | 0x870000 | 0x090000 | 64KB | Config data |
| 6 | 0x050100 | 0x00F000 | 64KB | Decompressed payload part 1 |
| 7 | 0x060100 | 0x01F000 | 64KB | Decompressed payload part 2 |
| 8 | 0x070100 | 0x02F000 | 65280B | Decompressed payload part 3 |
| 9 | 0x050000 | 0x000400 | 256B | Entry point code + status flags |

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

### Payload Execution Trigger

**Critical finding:** The Main CPU does NOT send a dedicated E3 command byte to trigger payload execution. Instead, the last 256-byte E1 transfer (block 9) writes to SubCPU addresses `0x000400`-`0x04FF`. This range includes `SUBCPU_STATUS_FLAGS` at address `0x04FE`.

When the HDMA transfer writes a byte with bit 6 set to address `0x04FE`, the Sub CPU's main loop polling detects this and jumps to the payload entry point:

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

**Confirmed in MAME log:** After HDMA writes to dst=0x0004FE, the SubCPU begins executing payload code at PC=0x01F929 (within the expected payload address range 0x00F000-0x03EE75).

### The E3 Data Command (Separate from Payload Loading)

The `0xE3` byte in the boot ROM's INT0 handler is a **regular data command byte** for the inter-CPU protocol, not related to payload loading:

- `0xE3` = `0b11100011` = channel 7, count 4 bytes
- This is used later during normal operation when the Main CPU sends audio data packets on channel 7
- The boot ROM's E3 handler sets bit 6 of `SUBCPU_STATUS_FLAGS`, which also triggers payload execution
- However, this E3 path is NOT used during normal boot -- the payload loading trigger comes from the DMA write to 0x04FE

## Fixes Applied

### Fix 1: LDC Control Register Mapping (Critical)

**Root cause of HDMA failure:** The TMP94C241 uses different control register (CR) numbers in the `LDC` instruction than the TMP96C141/TMP95C063. MAME's shared TLCS900 instruction decoder only had the old numbering, causing `LDC DMAD0, XWA` and `LDC DMAC0, WA` to silently write to a dummy register. The DMA destination address and transfer count were never set!

**TMP94C241 vs TMP96C141 CR numbers:**

| Register | TMP96C141 CR | TMP94C241 CR | Size |
|----------|-------------|-------------|------|
| DMAS0-3 | 0x00-0x0C | 0x00-0x0C | 32-bit (same) |
| DMAD0-3 | 0x10-0x1C | 0x20-0x2C | 32-bit (different!) |
| DMAC0-3 | 0x20-0x2C | 0x40-0x4C | 16-bit (different!) |
| DMAM0-3 | 0x22-0x2E | 0x42-0x4E | 8-bit (different!) |

**Fix:** Added TMP94C241 CR numbers as additional cases in the shared LDC instruction decoder (`900tbl.hxx`). Since the numbers don't overlap within each register size class, this doesn't affect other TLCS900 variants. Also updated the disassembler (`dasm900.cpp`) to recognize the new CR numbers.

**Files modified:**
- `mame_driver/src/devices/cpu/tlcs900/900tbl.hxx` -- Added CR cases for p_CR8, p_CR16, p_CR32 (both p1 and p2 operands)
- `mame_driver/src/devices/cpu/tlcs900/dasm900.cpp` -- Added CR labels for O_CR8, O_CR16, O_CR32

### Fix 2: DMAM Register Encoding

**Second root cause:** The DMAM (DMA Mode) register encoding in `tlcs900_process_hdma()` was wrong. The implementation used independent source/destination direction bits, but the actual TMP94C241 (like TMP95C061) uses a combined mode encoding:

| DMAM bits 4-0 | Source | Destination | Size |
|---------------|--------|-------------|------|
| 0x00 | Fixed | Increment | Byte |
| 0x01 | Fixed | Increment | Word |
| 0x02 | Fixed | Increment | Long |
| 0x04 | Fixed | Decrement | Byte |
| 0x08 | Increment | Fixed | Byte |
| 0x10 | Fixed | Fixed | Byte |

**Impact:** The Sub CPU boot ROM sets DMAM0 = 0 during `INIT_DMA_SERIAL`, which means "byte transfer, source fixed (latch), destination incrementing (buffer)". With the old decoding, DMAM=0 was interpreted as "both fixed", causing all received bytes to overwrite the same address.

**Fix:** Replaced the generic bit-field decoding with a switch-based implementation matching the proven TMP95C061 code in MAME.

### Fix 3: DMAR Register Implementation (0x109)

The DMAR register at SFR address `0x109` was missing from the MAME `tmp94c241` device. This register provides software-triggered DMA: writing bit N triggers an immediate DMA transfer on channel N.

**Fix:** Added `dmar_w()` handler at address `0x109` in the SFR address map. When a bit is set, it calls `tlcs900_process_hdma()` for the corresponding channel, performing an immediate DMA transfer.

This register is used by the Main CPU's INT0 handler (`LD (DMAR), 001h` at `0xEF352D`) to trigger DMA channel 0 when receiving data from the Sub CPU.

### Fix 4: HDMA Priority Over IRQs (Critical)

**Third root cause of HDMA failure:** In MAME's `execute_run()` loop, `check_irqs()` ran BEFORE `check_hdma()`. When INT0 fired, `check_irqs()` would dispatch to the INT0 interrupt handler and clear the interrupt flag. By the time `check_hdma()` ran, the flag was gone -- HDMA never fired even though DMAV0 was correctly set to 0x0A.

On real TMP94C241 hardware, when a DMA channel's DMAV matches an active interrupt source, the DMA transfer takes priority -- the interrupt is consumed by HDMA instead of being dispatched to the CPU's interrupt handler.

**Fix:** Added HDMA priority check in `check_irqs()`. Before processing each interrupt, it checks if any active HDMA channel targets that interrupt source (via DMAV matching). If so, the interrupt is skipped in `check_irqs()`, allowing `check_hdma()` to process it as a DMA trigger instead.

```cpp
// In check_irqs(), before processing an interrupt:
bool hdma_targeted = false;
for (int ch = 0; ch < 4; ch++)
{
    if (m_dma_vector[ch] == tmp94c241_irq_vector_map[i].dma_start_vector)
    {
        hdma_targeted = true;
        break;
    }
}
if (hdma_targeted)
    continue;  // Let check_hdma() handle this instead
```

### Fix 5: CPU Scheduling (perfect_quantum)

**CPU scheduling issue:** MAME runs CPUs in time slices. The Main CPU would write many bytes to the latch in a single time slice before the Sub CPU had a chance to process any of them, causing "latch written before being read" overflows.

**Fix:** Added `machine().scheduler().perfect_quantum(attotime::from_usec(100))` to `subcpu_latch_w()`. This temporarily forces minimum quantum for tight CPU interleaving, ensuring the Sub CPU's HDMA can process each byte before the next one arrives.

After this fix, "latch written before being read" warnings dropped from 52,815 to just 36.

### Diagnostic Logging

Added comprehensive logging to trace the inter-CPU communication:

- **Latch writes**: Command bytes (E1/E2/E3) logged with PC address; data bytes logged at verbose level
- **Handshake signals**: MSTAT/SSTAT changes logged with old/new values
- **Sub CPU reset**: Port A bit 0 changes logged
- **DMA vectors**: DMAV register writes logged with channel and value
- **DMA transfers**: Each HDMA transfer logged with source, destination, count, and mode
- **DMA completion**: Logged when HDMA transfer count reaches zero

Logging is controlled by `VERBOSE` flags in `kn5000.cpp` and uses MAME's `logmacro.h` system.

## Investigation Log

### Test Run 1: After DMAR fix + diagnostic logging

- E1 handshake works: SubCPU receives E1, arms DMA0V=0x0A, acknowledges
- **Zero HDMA transfers**: No "HDMA ch0 complete" messages in 81,969-line log
- "latch written before being read" warnings: Main CPU bytes overwrite each other
- Root cause identified: LDC instructions for DMA registers silently fail due to wrong CR mapping

### Test Run 2: After LDC CR mapping fix + DMAM encoding fix

- HDMA still showed zero transfers
- Root cause identified: `check_irqs()` consuming INT0 flag before `check_hdma()` could use it

### Test Run 3: After HDMA priority fix + perfect_quantum

- **524,358 HDMA transfers** (up from zero!)
- Only 36 "latch written before being read" warnings (down from 52,815)
- 17 HDMA completions showing correct transfer pattern (9 blocks x ~2 completions each for header + data)
- All 9 E1 blocks transferred successfully
- **SubCPU payload executes!** PC values 0x01F929, 0x034C6F observed after payload load
- SubCPU initializes serial ports, configures interrupts from within payload code
- "Checking device" LED stops blinking (SubCPU left boot ROM polling loop)

## Remaining Issue: Sound Name Error

The "Sound Name Error" persists because the SubCPU's payload code attempts to communicate with unimulated sound hardware:

| Device | Address | Chip | Status in MAME |
|--------|---------|------|----------------|
| Tone generator | 0x110000 | IC303 | **Commented out** in memory map |
| DSP | 0x130000 | IC311 | **Unmapped** |
| SA chip | Serial port 1 | Via SIO | **No emulated receiver** |

The SubCPU payload initializes successfully and begins executing, but gets stuck during sound hardware initialization because:
1. Writes to the tone generator at 0x110000 go nowhere
2. Reads from the DSP at 0x130000 return open bus
3. Serial communication with the SA chip has no receiver

As a result, zero SubCPU→MainCPU latch writes occur after the payload starts, meaning the SubCPU never responds to main CPU sound requests.

**This is a different problem scope** from the original payload transfer investigation. Fixing this requires emulation of the KN5000's sound synthesis hardware.

## Key Files

| File | Purpose |
|------|---------|
| `mame_driver/src/mame/matsushita/kn5000.cpp` | Main MAME driver (latches, ports, memory map) |
| `mame_driver/src/devices/cpu/tlcs900/tmp94c241.cpp` | CPU emulation (DMA, SFR, interrupts) |
| `mame_driver/src/devices/cpu/tlcs900/tmp94c241.h` | CPU header (DMA state) |
| `mame_driver/src/devices/cpu/tlcs900/900tbl.hxx` | Shared TLCS900 instruction decoder (LDC CR fix) |
| `mame_driver/src/devices/cpu/tlcs900/dasm900.cpp` | Disassembler (CR label fix) |
| `maincpu/kn5000_v10_program.asm:134123` | `SubCPU_Send_Payload` |
| `maincpu/kn5000_v10_program.asm:139166` | `InterCPU_E1_Bulk_Transfer` |
| `maincpu/kn5000_v10_program.asm:139115` | `Audio_DMA_Transfer` |
| `maincpu/kn5000_v10_program.asm:140484` | LZSS decompressor (`LABEL_EF41E3`) |
| `subcpu/boot/kn5000_subcpu_boot.asm:1159` | `InterCPU_RX_Handler` (INT0 handler) |
| `subcpu/boot/kn5000_subcpu_boot.asm:718` | `INIT_DMA_SERIAL` (DMA setup) |
| `subcpu/boot/kn5000_subcpu_boot.asm:405` | Main loop (payload ready polling) |
