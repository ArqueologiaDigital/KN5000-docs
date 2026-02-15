---
layout: page
title: SubCPU Payload Loading
permalink: /subcpu-payload-loading/
---

# SubCPU Payload Loading Investigation

This page documents the investigation into SubCPU firmware payload loading in MAME emulation. The investigation uncovered multiple bugs in MAME's TMP94C241 emulation (LDC CR mapping, DMAM encoding, HDMA/IRQ priority) that prevented DMA transfers. All have been fixed, and the SubCPU payload now loads and executes successfully.

> **Status:** Payload transfer is **WORKING**. The SubCPU receives all 9 E1 blocks (524,358 HDMA transfers) and begins executing payload code. Active investigation continues on INT0-driven inter-CPU communication after boot -- fixes for level-detect re-assertion and EI/RETI interrupt shadow are being tested. See [Boot Sequence]({{ site.baseurl }}/boot-sequence/) for the overall boot flow and [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) for latch communication details.

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

### Test Run 4: After DMAR burst DMA fix + INT0 level-detect re-assertion (545K line log)

- **0 INT0 dispatches** -- the level-detect re-assertion was not yet active in this test
- 524,374 HDMA transfers (payload loading phase works)
- SubCPU goes silent after tone generator init -- no INT0 interrupts fire post-boot
- 36 latch overflow warnings
- "Sound Name Error" persists
- **Theory confirmed:** Without level-detect re-assertion, INT0 fires once (consumed by HDMA during boot) but never again after the payload sets DMA0V=0 and expects ISR-based INT0 handling

### Test Run 5: After INT0 level-detect re-assertion fix (3M line log)

- **394,118 INT0 dispatches** (up from 0!) -- level-detect re-assertion IS working
- 524,374 INT0 ASSERT events
- **INT0 storm detected:** 91,391 INT0 dispatches from PC=`0x01FFF0` (the NOP between `EI 0` and `EI 6`)
- Only 5 latch overflow warnings (down from 36)
- Last HDMA ch0 complete at dst=`0x0010F1` (payload's own HDMA setup)
- After that, INT0 storm begins and SubCPU is trapped in infinite ISR dispatch loop
- Blinking patterns of the SubCPU checking device slightly different vs previous test
- "Sound Name Error" still present
- **Root cause identified:** Missing interrupt shadow after RETI allows INT0 to re-dispatch before the return-address instruction executes, preventing the `EI 0; NOP; EI 6` masking pattern from working. See Fix 8.

### Test Run 6: After EI/RETI interrupt shadow fix (14.8M line log)

- **EI/RETI shadow fix WORKED:** 0 INT0 dispatches from PC=`0x01FFF0` (old storm at boot ROM window eliminated)
- **NEW INT0 storm emerged:** 12,203,435 INT0 dispatches (82% of all log lines), mostly from DSP_SEND_DATA loop (PCs `0x036828`-`0x03685E`)
- 524,353 INT0 ASSERT / 524,354 CLEAR events → ~23 dispatches per ASSERT (level-detect amplification)
- 22,719 INT0 dispatches from PC=`0x01FFF1` (EI 6 address) — these are the correctly-working EI windows
- INTTC0 = 18 (payload DMA completions), **INTTC2 = 0** (SubCPU never sends data back)
- 14 latch overflow warnings (in two clusters: post-boot + E2 command attempt)
- Only 38 INTA + 82 INTRX1 + 157 INTTX1 on MainCPU (very little MainCPU activity)
- Payload loading succeeded (all 9 E1 blocks, 524K HDMA transfers)
- SubCPU payload booted (SSTAT 0→3 at PC=`0x01F986`)
- **SubCPU stuck in `DSP_Send_Data` timeout loop** — DSP not emulated, `DSP_Read_Status` returns 0

**Root cause chain identified:**
1. `DSP_Read_Status` reads Port PH bit 0, which returns 0 (DSP "not ready") because `port_r()` ignores the direction register
2. PH.0 is configured as OUTPUT (PHCR=0x07), so reading should return the output latch (1, set by `SET 0, (PH)`)
3. The SubCPU's DSP init has ~40 `DSP_Send_Data` calls, each with an 8000-iteration timeout loop
4. During timeout loops, IFF=0 (EI 0 in the function), so INT0 fires on every instruction
5. The INT0 ISR checks MSTAT0=1 (MainCPU in data phase), exits without reading the latch
6. Level-detect re-assertion causes INT0 to fire 23x per assertion, creating massive overhead
7. The MainCPU's E2 command handshake check passes spuriously (SSTAT1 already 0 from a previous transfer, not from SubCPU acknowledgment)
8. MainCPU sets MSTAT0=1 and starts sending data before SubCPU reads the command byte
9. All data bytes overflow the latch (written before being read)

### Test Run 7: After port_r direction-aware fix (Pending)

- Fix 9 applied: `port_r()` now returns `(latch & dir) | (external & ~dir)` — output bits from latch, input bits from external callback
- Expected outcome: `DSP_Read_Status` returns 1 (output latch), DSP init skips timeout loops, SubCPU enters main event loop quickly and processes commands before MainCPU's Sound Name Error timeout

## Remaining Issues

### Fix 6: DMAR Software-Triggered Burst DMA (Pending Test)

Analysis of the SubCPU payload's main loop revealed that `InterCPU_DMA_Send_Chunk` (at `0x020CF3`) uses the `DMAR` register to trigger DMA channel 2 for sending data back to the Main CPU. After triggering, it waits in `DMA_Chunk_Wait` for `DMA_XFER_STATE` to be cleared by the `MICRODMA_CH2_HANDLER` interrupt (INTTC2 at vector `0x9C`).

**Bug:** The previous `dmar_w()` implementation called `process_hdma()`, which requires a matching interrupt flag to be pending. Software-triggered DMA via DMAR should bypass the interrupt check and perform a burst transfer (all DMAC units at once), then fire INTTC on completion.

**Fix:** Replaced `dmar_w()` to call a new `tlcs900_process_software_dma()` function that transfers the entire block without checking interrupt flags and fires the INTTC completion interrupt when done.

Without this fix, every attempt by the SubCPU to send data back to the Main CPU would silently fail, and the `DMA_Chunk_Wait` loop would hang forever.

### Fix 7: INT0 Level-Detect Re-assertion

**Root cause:** On real TMP94C241 hardware, when IIMC bit 1 = 0 (level-detect mode for INT0), the interrupt flag in INTE0AD is continuously driven by the external input level. MAME's `check_irqs()` clears the flag when dispatching the interrupt, but on real hardware the flag immediately re-asserts if the input pin is still active.

During boot, this doesn't matter because HDMA consumes INT0 (the flag is cleared but HDMA handles the data transfer). After boot, when the SubCPU payload takes over and configures DMA0V=0 (disabling HDMA for INT0), the ISR handles INT0 directly. Without level-detect re-assertion, INT0 fires once but never again -- the SubCPU stops receiving commands from the Main CPU.

**Fix:** Added re-assertion logic in `check_irqs()`: after dispatching an INT0 interrupt and clearing its flag, if INT0 is in level-detect mode and the input is still ASSERT_LINE, immediately re-set the INTE0AD flag and schedule another `check_irqs`.

```cpp
// In check_irqs(), after clearing INT0's flag:
if (tmp94c241_irq_vector_map[irq].reg == INTE0AD &&
    tmp94c241_irq_vector_map[irq].iff == 0x08 &&
    !(m_iimc & 0x02) &&
    m_level[TLCS900_INT0] == ASSERT_LINE)
{
    m_int_reg[INTE0AD] |= 0x08;
    m_check_irqs = 1;
}
```

### Fix 8: EI/RETI Interrupt Shadow (Pending Test)

**Root cause of INT0 storm:** Fix 7 exposed a second bug. The SubCPU payload uses a deliberate `EI 0; NOP; EI 6` pattern at address `0x01FFEE`-`0x01FFF1` to create a one-instruction interrupt window:

```asm
EI 0    ; 01FFEE - Enable all interrupts (IFF=0)
NOP     ; 01FFF0 - One-instruction window for pending interrupts
EI 6    ; 01FFF1 - Re-mask low-priority interrupts (IFF=6)
```

On real TLCS-900 hardware, both EI and RETI defer interrupt acceptance until after the next instruction executes (a "1-instruction interrupt shadow"). This means:
1. `EI 0` enables interrupts, but the CPU executes NOP before accepting any
2. INT0 dispatches from `0x01FFF1` (the address of `EI 6`)
3. ISR handles INT0, returns via RETI
4. RETI has its own shadow -- `EI 6` executes before another INT0 can fire
5. IFF is now 6, masking INT0 (priority 1) -- storm prevented

In MAME, `check_irqs()` runs at the START of the execution loop, BEFORE the instruction executes. After RETI restores IFF=0, `check_irqs` fires before the return-address instruction (NOP) gets a chance to execute. The ISR checks MSTAT0=1, exits without reading the latch, RETI returns to 01FFF0, and INT0 re-dispatches immediately -- an infinite storm of 91,391+ INT0 dispatches in the log.

**Fix:** Added `m_irq_inhibit` flag to the TLCS900 base class. Both `op_EI()` and `op_RETI()` set this flag. In `execute_run()`, when `m_irq_inhibit` is set, interrupt checking is deferred by one instruction:

```cpp
// In execute_run():
if ( m_check_irqs )
{
    if ( m_irq_inhibit )
    {
        // Interrupt shadow: defer until after next instruction
        m_irq_inhibit = false;
    }
    else
    {
        tlcs900_check_irqs();
        m_check_irqs = 0;
    }
}
```

**Files modified:**
- `mame_driver/src/devices/cpu/tlcs900/tlcs900.h` -- Added `bool m_irq_inhibit` member
- `mame_driver/src/devices/cpu/tlcs900/tlcs900.cpp` -- Shadow logic in `execute_run()`, init in `device_start()`/`device_reset()`
- `mame_driver/src/devices/cpu/tlcs900/900tbl.hxx` -- Set `m_irq_inhibit = true` in `op_EI()` and `op_RETI()`

### Fix 9: Port Read Direction Awareness (Pending Test)

**Root cause of DSP timeout loops:** The `port_r()` function in `tmp94c241.cpp` always returns the external callback value, ignoring the port direction register (PXCR). On real TMP94C241 hardware, reading a port returns:
- Output latch value for bits configured as output (PXCR bit = 1)
- External pin level for bits configured as input (PXCR bit = 0)

The SubCPU firmware configures Port PH bits 0-2 as output (`LD (PHCR), 007h`). The `DSP_Read_Status` function at `0x0383F7` does `SET 0, (PH)` then reads back PH.0 to check DSP ready status. Since PH.0 is output, the read should return 1 (what was just written). But MAME's `port_r()` called the external callback (unconnected for Port PH), returning 0.

This caused all `DSP_Send_Data` and `DSP_Send_Command` calls to enter their timeout loops (0x1F40 = 8000 iterations each), severely delaying SubCPU initialization. During these long timeouts, INT0 level-detect re-assertion created a massive interrupt storm (12M+ dispatches).

**Fix:** Made `port_r()` direction-aware:

```cpp
uint8_t dir = m_port_control[P];
uint8_t external = m_port_read[P](0);
return (m_port_latch[P] & dir) | (external & ~dir);
```

This fix improves ALL port reads:
- **Port PH** (SubCPU): DSP status reads back output latch → DSP init completes instantly
- **Port D** (SubCPU): SSTAT output bits read back from latch; MSTAT input bits from callback
- **Port Z** (MainCPU): MSTAT output bits read back from latch; SSTAT input bits from callback

**Files modified:**
- `mame_driver/src/devices/cpu/tlcs900/tmp94c241.cpp` -- `port_r()` direction-aware implementation

### SubCPU Initialization Analysis

Detailed analysis of the SubCPU payload init sequence revealed that **initialization does NOT hang** -- all init-phase loops are bounded by timeouts or complete harmlessly with unmapped hardware returning 0:

| Loop | Location | Reads From | Bounded? | Behavior with Unmapped HW |
|------|----------|-----------|----------|--------------------------|
| `DSP_Send_Command` wait | 0x036331 | Port PH bit 0 | Yes (8,000 iter) | PH output latch reads back 1 -- exits immediately |
| `DSP_Send_Data` wait | 0x0367EE | Port PH bit 0 | Yes (8,000 iter) | Same as above |
| `ToneGen_Poll_Delay` | 0x03D227 | Nothing (pure delay) | Yes (10,000 iter) | Runs 160,000 iterations total, completes |
| `ToneGen_Poll_Read` | 0x03D239 | 0x110002 / 0x110000 | Single read | Returns 0, processes 16 fake note-off events |

After init, the SubCPU enters the main event loop (`LABEL_01FAE6`), which runs continuously. The main loop does NOT hang because:
- `ToneGen_Process_Notes` reads 0 from unmapped 0x110002 (no notes available)
- Ring buffers are empty (no serial data, no queued commands)
- No DMA transfers are triggered on the first iterations

### "Sound Name Error" Root Cause (Updated)

The "Sound Name Error" is triggered by the Main CPU's `MainGetSoundName()` function (at `0xF98D3E`). It sends a sound name request to the SubCPU via the inter-CPU latch, then waits for a 32-byte response with a timeout of ~60,000 iterations. When the SubCPU never responds, the timeout fires and displays the error.

**Multiple contributing factors identified:**

1. **DMAR burst DMA (Fix 6):** The SubCPU's `InterCPU_DMA_Send_Chunk` uses DMAR to trigger DMA channel 2 for sending responses. Without burst DMA support, responses silently fail and the SubCPU hangs in `DMA_Chunk_Wait`.

2. **INT0 level-detect (Fix 7):** After the payload takes over from the boot ROM and sets DMA0V=0, INT0 must be delivered as CPU interrupts (not HDMA). Without level-detect re-assertion, INT0 fires once and never again -- the SubCPU stops receiving commands entirely.

3. **EI/RETI interrupt shadow (Fix 8):** The level-detect fix exposed the interrupt shadow bug. The SubCPU's `EI 0; NOP; EI 6` interrupt window pattern causes an infinite INT0 storm because MAME dispatches INT0 before the return-address instruction executes. The SubCPU is trapped and can never process commands.

All three fixes must be in place for the SubCPU to successfully receive and respond to Main CPU commands. Even with all fixes, unimulated sound peripherals mean responses will contain no real audio data:

| Device | Address | Chip | Status in MAME |
|--------|---------|------|----------------|
| Tone gen registers | 0x100000/0x100002 | IC303 (TC183C230002) | **Not mapped** -- writes go to void |
| Tone gen keyboard | 0x110000/0x110002 | IC303 | **Commented out** -- reads return 0 |
| DSP registers | 0x130000/0x130002 | IC310/IC311 | **Not mapped** -- writes go to void |
| Serial1 (DAC/DSP control) | UART port 1 | IC313? (PCM69AU) | **No receiver** |

See [Tone Generator]({{ site.baseurl }}/tone-generator/) for the complete register map and chip inventory.

## Debugging Inner Thoughts

This section captures the detailed reasoning process behind each investigation step, preserving the "how we got there" alongside the results.

### Reasoning: INT0 Level-Detect Re-assertion (Fix 7)

**Starting observation:** After applying DMAR burst DMA fix, log showed 0 INT0 dispatches post-boot. The payload loaded fine (524K HDMA transfers) but then the SubCPU went completely silent.

**Key insight chain:**
1. During boot, INT0 is consumed by HDMA (DMA0V=0x0A). After boot, the payload calls `InterCPU_Latch_Setup` which sets DMA0V=0x0A for receive and DMA2V for transmit -- but later the main loop's INT0 handler at `0x01F929` processes INT0 via ISR, NOT HDMA. When does DMA0V become 0?
2. Searched the payload code: `InterCPU_Latch_Setup` (line 10964) sets `LDC DMA0V, 000Ah` -- armed for HDMA. But the INT0 handler at line 11247 checks MSTAT0 and if conditions are right, reads the latch byte directly. This means DMA0V stays armed for HDMA throughout, and the HDMA path handles most bytes, but the ISR handles command bytes.
3. Wait -- if HDMA handles INT0, `check_hdma` processes it and clears the flag. But `check_irqs` re-assertion only fires when check_irqs dispatches INT0 to the ISR. In HDMA mode, `check_hdma` clears the flag and... does the level-detect re-assertion fire?
4. **Root cause found:** `check_hdma` calls `process_hdma` which clears the INT0 flag at line 1106. But there's no re-assertion logic in `check_hdma` -- only in `check_irqs`. Since the latch is still pending (ASSERT_LINE), the flag should re-assert. But `execute_set_input`'s `update_int_reg` lambda only updates on level CHANGE (`if (level != m_level[input])`). Since the latch read triggers synchronous CLEAR followed by deferred ASSERT via `synchronize()`, the level does toggle -- but the ASSERT arrives as a callback AFTER the current instruction.
5. The real issue is simpler: when `check_irqs` dispatches INT0, it clears the flag. On real hardware, level-detect means the flag stays set as long as the input is asserted. We need to re-assert immediately after clearing.

### Reasoning: EI/RETI Interrupt Shadow (Fix 8)

**Starting observation:** After Fix 7, log exploded to 3M lines with 394K INT0 dispatches. 91K of them were from PC=`0x01FFF0` -- an INT0 storm.

**Key insight chain:**
1. What's at `0x01FFF0`? It's a NOP instruction, sandwiched between `EI 0` (01FFEE) and `EI 6` (01FFF1). This is a deliberate pattern: enable all interrupts for exactly one instruction, then re-mask.
2. Why does INT0 keep dispatching from `0x01FFF0` instead of letting NOP execute and reaching EI 6?
3. Checked `execute_run()` flow: `check_irqs` runs at the START of the loop, BEFORE instruction execution. After RETI restores SR (with IFF=0), the next loop iteration runs `check_irqs` BEFORE executing the instruction at the return address.
4. So the flow is: `RETI` → returns to `0x01FFF0` → loop starts → `check_irqs` fires (IFF=0, INT0 pending) → dispatches INT0 from `0x01FFF0` → NOP never executes!
5. The ISR at this point checks MSTAT0 (PD bit 2). If MSTAT0=1, it exits without reading the latch (because the Main CPU is in the middle of a transfer phase). The latch stays pending, INT0 re-asserts (Fix 7), RETI returns to `0x01FFF0`, and the cycle repeats.
6. **On real TLCS-900 hardware:** After RETI (and after EI), the CPU executes at least one instruction before accepting another interrupt. This is the "interrupt shadow" -- identical to the Z80's behavior after EI. The NOP absorbs one ISR call, then EI 6 at `0x01FFF1` raises IFF to 6, masking INT0 (priority 1).
7. Checked `op_RETI` in `900tbl.hxx`: it sets `m_prefetch_clear = true` and `m_check_irqs = 1` but has NO interrupt shadow mechanism.
8. **Fix:** Add `m_irq_inhibit` flag, set by EI and RETI, that causes `execute_run` to skip one `check_irqs` call.

### Reasoning: Port Read Direction & DSP Timeout (Fix 9)

**Starting observation:** Test Run 6 showed the EI/RETI shadow fix worked (0 dispatches from PC=01FFF0), but a NEW INT0 storm emerged from DSP_SEND_DATA loop PCs. 12.2M INT0 dispatches with only 524K ASSERTs = 23x amplification.

**Key insight chain:**
1. The storm PCs (0x036828-0x03685E) are in `DSP_Send_Data_WaitLoop` and `DSP_Send_Data_Poll` — a bounded timeout loop (8000 iterations) that polls DSP readiness via `DSP_Read_Status`.
2. `DSP_Read_Status` at 0x0383F7 does: `SET 0, (PH)` → `LDCF 0, (PH)` → return carry. It sets PH.0 high, then reads it back.
3. The SubCPU firmware sets `PHCR = 0x07` (line 9318) — Port PH bits 0-2 are OUTPUT.
4. On real hardware, reading an output bit returns the output latch. Since `SET 0, (PH)` just wrote 1, the read should return 1 (DSP "ready").
5. But MAME's `port_r()` calls `m_port_read[P](0)` — the external callback. Port PH has no callback → returns 0.
6. So `DSP_Read_Status` always returns 0 (not ready), causing 8000-iteration timeouts.
7. `DSP_Send_Data` has `EI 0` / `EI 6` windowing — IFF=0 during the timeout loop body.
8. With level-detect re-assertion, every pending latch byte causes INT0 to fire ~23 times per assertion (ISR checks MSTAT0=1, exits without reading, INT0 re-fires).
9. The E2 handshake protocol race: MainCPU checks SSTAT1=0 (already low from a previous handshake), proceeds to set MSTAT0=1 before SubCPU reads the command.

**The fix** is fundamental: make `port_r()` respect the direction register, combining output latch for output bits and external callback for input bits. This is correct for ALL ports, not just PH.

### DMA Macro Name Confusion (Side Investigation)

During the INT0 investigation, discovered that several DMA macros in `tmp94c241.inc` had misleading names:
- `LDC_DMAM0_WA` (bytes D8,2E,40) actually writes to CR 0x40 = DMAC0 (count register, NOT mode)
- `LDC_DMAC0_A` (bytes C9,2E,42) actually writes to CR 0x42 = DMAM0 (mode register, NOT count)

The names had DMAC and DMAM swapped. Fixed in commit b4ed825 -- all macros now correctly named, duplicates removed, and all call sites updated across all assembly files. Build still produces 100% byte-matching ROMs.

## Key Files

| File | Purpose |
|------|---------|
| `mame_driver/src/mame/matsushita/kn5000.cpp` | Main MAME driver (latches, ports, memory map) |
| `mame_driver/src/devices/cpu/tlcs900/tmp94c241.cpp` | CPU emulation (DMA, SFR, interrupts, INT0 re-assertion) |
| `mame_driver/src/devices/cpu/tlcs900/tmp94c241.h` | CPU header (DMA state) |
| `mame_driver/src/devices/cpu/tlcs900/tlcs900.cpp` | TLCS900 base class (execute_run, interrupt shadow) |
| `mame_driver/src/devices/cpu/tlcs900/tlcs900.h` | TLCS900 base header (m_irq_inhibit) |
| `mame_driver/src/devices/cpu/tlcs900/900tbl.hxx` | Shared instruction decoder (LDC CR, EI/RETI shadow) |
| `mame_driver/src/devices/cpu/tlcs900/dasm900.cpp` | Disassembler (CR label fix) |
| `maincpu/kn5000_v10_program.asm:134123` | `SubCPU_Send_Payload` |
| `maincpu/kn5000_v10_program.asm:139166` | `InterCPU_E1_Bulk_Transfer` |
| `maincpu/kn5000_v10_program.asm:139115` | `Audio_DMA_Transfer` |
| `maincpu/kn5000_v10_program.asm:140484` | LZSS decompressor (`LABEL_EF41E3`) |
| `subcpu/kn5000_subprogram_v142.asm:10964` | `InterCPU_Latch_Setup` (payload DMA config) |
| `subcpu/kn5000_subprogram_v142.asm:11247` | Payload INT0 handler |
| `subcpu/boot/kn5000_subcpu_boot.asm:1159` | `InterCPU_RX_Handler` (boot ROM INT0 handler) |
| `subcpu/boot/kn5000_subcpu_boot.asm:718` | `INIT_DMA_SERIAL` (DMA setup) |
| `subcpu/boot/kn5000_subcpu_boot.asm:405` | Main loop (payload ready polling) |
