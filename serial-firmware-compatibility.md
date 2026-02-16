---
layout: page
title: "Serial Firmware Compatibility: Debugging Report"
permalink: /serial-firmware-compatibility/
---

# Making the MAME Serial Driver Compatible with the Original KN5000 Firmware

*February 2026 — RESOLVED*

> **Status: FULLY WORKING.** As of February 15, 2026, the original KN5000 firmware boots without errors and all control panel buttons (both left and right panels) produce correct LED and menu responses. The Another World VM also works with the same driver.

This report documents the effort to fix the MAME KN5000 driver's serial communication so the **original KN5000 program ROM** boots without the "ERROR in CPU data transmission" dialog. All fixes simultaneously support the Another World VM custom ROM that uses the same serial hardware.

## Background

The [first round of serial debugging](/serial-debugging/) (January 2026) got individual bytes transmitting correctly between the CPU serial device and the control panel HLE. The [compatibility review](https://github.com/felipesanches/custom-kn5000-roms/blob/main/anotherworld/docs/serial-cpanel-compatibility-2026-02-11.md) (February 11) fixed three additional bugs that made the AW VM's polled serial work.

But the original firmware uses a fundamentally different serial approach than the AW VM, and it was still broken:

| Feature | AW VM | Original Firmware |
|---------|-------|-------------------|
| Clock source | Baud rate generator (SC1MOD=0x01) | TO2 trigger (SC1MOD=0x00) |
| TX method | Polled (write + delay + read) | Interrupt-driven state machine (11 states) |
| RX method | Read SC1BUF after TX | INTA interrupt → slave mode → self-clock |
| Baud rates | Fixed 250 kHz | Varies: 31.25 / 62.5 / 250 kHz per state |
| Phantom bytes | None (all bytes are real) | 4 phantom bytes per 2-byte command |
| Response clocking | CPU sends dummy 0xFF bytes | Panel self-clocks after INTA |

## The Firmware's TX State Machine

The firmware uses an interrupt-driven state machine triggered by INTTX1 (serial transmit complete interrupt). Each SC1BUF write triggers the next state after the byte finishes transmitting:

```
CPanel_SendCommand          SM_StartTX            SM_SendByte1
─────────────────          ──────────            ────────────
BR1CR = 0x28 (31 kHz)     BR1CR = 0x24 (63 kHz) BR1CR = 0x14 (250 kHz)
PFFC off (SCLK disabled)  PFFC still off         PFFC ON (SCLK enabled)
IOC = 0 (master mode)     Write SC1BUF           Write REAL byte 1
Write SC1BUF (phantom)    (phantom)              from LED_TX_BUFFER
        │                       │                       │
        └── INTTX1 ────────────┘── INTTX1 ─────────────┘── INTTX1 ──>

    SM_TXDelay1           SM_SendByteN           SM_TXDelay2
    ───────────           ────────────           ───────────
    DELAY_10 (~6 µs)      BR1CR = 0x14 (250 kHz) DELAY_10 (~6 µs)
    PFFC OFF               PFFC ON                PFFC OFF
    BR1CR = 0x24 (63 kHz) Write REAL byte 2       BR1CR = 0x24 (63 kHz)
    Write SC1BUF           from LED_TX_BUFFER      Write SC1BUF
    (phantom)                     │                (phantom)
         │                        │                     │
<────────┘── INTTX1 ─────────────┘── INTTX1 ───────────┘── INTTX1 ──>

    SM_TXComplete
    ─────────────
    More data? → restart SM_StartTX
    No data?   → go IDLE, disable SCLK
```

**Key observation:** Each 2-byte command produces **6 SC1BUF writes**: 4 phantom (PFFC off) + 2 real (PFFC on). The baud rate changes per state.

## The INTA Response Mechanism

After the firmware finishes transmitting, it waits for the panel to assert INTA:

```
  CPU (firmware)                    Control Panel (HLE)
  ──────────────                    ───────────────────
  TX state machine completes
  SM_TXComplete → IDLE
  SCLK stops
                                    Receives 2-byte command
                                    Queues response (2 bytes)
                                    Detects SCLK idle (250 µs)
                                    Asserts INTA on PE.5
  ┌─────────────────────────────────────────────┐
  │ INTA_HANDLER:                               │
  │   IOC = 1 (slave mode)                      │
  │   RXE = 1 (receive enable)                  │
  │   State → SM_RXByte1                        │
  └─────────────────────────────────────────────┘
                                    Self-clocks response at 250 kHz
                                    ── SCLK edges ──>
  SM_RXByte1: reads SC1BUF
  SM_RXByteN: reads SC1BUF
  Response complete → IDLE
                                    Deasserts INTA
```

## CPanel_WaitTXReady: The Timeout Gate

Before each command, the firmware calls `CPanel_WaitTXReady` which polls four conditions:

```
┌─────────────────────────────────────────────────────────┐
│  CPanel_WaitTXReady (200 retries × ~1 ms each)         │
│                                                          │
│  1. PF.6 == HIGH?    (SCLK pin at idle pull-up)         │
│  2. PE.5 == LOW?     (INTA not asserted)                │
│  3. TX flag == 0?    (no transmission in progress)      │
│  4. RX flag == 0?    (no reception in progress)         │
│  5. LED buffer empty? (no queued LED commands)          │
│                                                          │
│  ALL must pass → proceed to send command                │
│  ANY fails → DELAY_1500_LOOPS (~1 ms), retry            │
│  200 failures → set PROTOCOL_FLAGS.7 → ERROR dialog     │
└─────────────────────────────────────────────────────────┘
```

The ERROR dialog appears when this 200-retry (~200 ms) timeout is exhausted.

## Boot Sequence Timing Diagram

```
Time    CPU Firmware                     MAME Serial Device       Control Panel HLE
─────   ───────────────────────────────  ─────────────────────    ────────────────────
0 ms    Hardware init (watchdog,
        memory controller, DRAM)
        │
~5 ms   Timer setup (T0/T1 cascade)
        Prescaler start (T16RUN)
        │
~8 ms   CPanel_InitHardware:
        │ SC1MOD = 0x00 (TO2 trigger)
        │ BR1CR  = 0x14 (250 kHz)        Timer starts at 250 kHz
        │ SC1CR  = 0x01 (IOC=1)
        │ INTA interrupt enabled
        │
~8.5    DELAY_6_TICKS (480 µs)
        │
~9 ms   SendCommand(0x1F, 0xDA):
        │ BR1CR = 0x28 (31 kHz)          Timer adjusts to 31 kHz
        │ PFFC off, IOC = 0 (master)
        │ SC1BUF = phantom                                        tx_start(0), reject
        │   └─INTTX1─>
        │ SM_StartTX: phantom SC1BUF                              tx_start(0), reject
        │   └─INTTX1─>
        │ SM_SendByte1: REAL 0x1F         250 kHz                 tx_start(1), accept
        │   └─INTTX1─>                                           cmd_buf[0] = 0x1F
        │ SM_TXDelay1: phantom SC1BUF     62.5 kHz                tx_start(0), reject
        │   └─INTTX1─>
        │ SM_SendByteN: REAL 0xDA         250 kHz                 tx_start(1), accept
        │   └─INTTX1─>                                           cmd_buf[1] = 0xDA
        │                                                         process_command()
        │                                                         → queue sync response
        │                                                         → start idle_detect
        │                                                            (250 µs timer)
        │ SM_TXDelay2: phantom SC1BUF     62.5 kHz                tx_start(0), reject
        │   └─INTTX1─>                                       *** MUST NOT cancel
        │ SM_TXComplete → IDLE                                    idle_detect! ***
        │
~11 ms  DELAY_3000_LOOPS (~2 ms)                                 idle_detect fires
        │                                                         → assert INTA
        │                                                         → self-clock response
        │
        │ [INTA fires]
        │ INTA_HANDLER: IOC=1, RXE=1                             self-clock: 0x18, 0x00
        │ SM_RXByte1: read 0x18
        │ SM_RXByteN: read 0x00
        │ Response received OK
        │
~13 ms  Reset LED ptr
        DELAY_3000_LOOPS (~2 ms)
        │
~15 ms  CPanel_SendInitSequence:
        │ SendCommand(0x1F, 0x1A)
        │ DELAY_3000 + reset + DELAY_3000
        │ SendCommand(0x1D, 0x00)
        │ DELAY_3000 + reset + 2×DELAY_3000
        │ SendCommand(0xDD, 0x03)
        │ DELAY_3000 + reset + 2×DELAY_3000
        │ SendCommand(0x1E, 0x80)
        │ 3×DELAY_3000
        │ Enable interrupts
        │
~40 ms  CPanel_PollStartup:
        │ CPanel_WaitTXReady              <── Must pass all 4 checks
        │ SendCommand(0x20, 0x0B)
        │ DELAY_6_TICKS
        │ Process response
        │ ... (repeat until encoder stable)
        │
~55 ms  CPanel_InitButtonState:
        │ WaitTXReady + Send(0x2B, 0x00)  <── Query all left segments (22 bytes response)
        │ WaitTXReady + Send(0xEB, 0x00)  <── Query all right segments (22 bytes response)
        │ WaitTXReady + Send(0x20, 0x10)
        │ WaitTXReady + Send(0xE3, 0x10)
        │
~70 ms  Init complete, enter main loop
```

## Attempts Log

### Attempt 1: Phantom byte signaling via tx_start (commit f3e0eb7)

**Approach:** Instead of gating SCLK on PFFC (which causes clock desync), signal PFFC state through `tx_start_cb`. Cpanel skips phantom bytes.

**Changes:**
- `serial.cpp sioclk()`: Always forward sclk_out_cb (no PFFC gating)
- `serial.cpp scNbuf_w()`: Pass PFFC state via `tx_start_cb(pffc ? 1 : 0)`
- `serial.cpp timer_callback()`: Added `(m_serial_mode & 3) != 1` early return (only drive SCLK in baud rate mode)
- `cpanel.cpp`: Added `m_accept_next_byte` flag, skip phantom bytes

**Result:** AW VM works. Firmware shows ERROR, LEDs off.

**Root cause:** The `(m_serial_mode & 3) != 1` check disabled the baud rate timer for the firmware (which uses TO2 mode, SC1MOD=0x00). But the firmware also configures BR1CR, and on this hardware the baud rate timer is the primary 250 kHz SCLK source regardless of SC1MOD.

### Attempt 2: TO2_trigger IOC fix + activity gate (commit ffb8110)

**Approach:** Fix the IOC bit check (was checking bit 1 / SCLKS instead of bit 0 / IOC). Add activity gate to TO2_trigger so it only drives SCLK during active transfers.

**Changes:**
- `serial.cpp TO2_trigger()`: `BIT(m_serial_control, 1)` → `BIT(m_serial_control, 0)` for IOC
- `serial.cpp TO2_trigger()`: Activity gate: only call `sioclk()` when `tx_clock_count > 0 || tx_skip_first_falling || rx_clock_count != 8`

**Result:** Firmware still shows ERROR, LEDs off.

**Root cause:** Baud rate timer still disabled by the SC1MOD check from attempt 1. The IOC and activity gate fixes were correct but insufficient alone.

### Attempt 3: timer_callback IOC-only check (commit 22dc3e4)

**Approach:** Replace the SC1MOD check with an IOC-only check. Idea: don't drive SCLK in slave mode (IOC=1).

**Changes:**
- `serial.cpp timer_callback()`: `BIT(m_serial_control, 0)` — return early when IOC=1

**Result:** AW VM has very bad performance. Firmware shows ERROR but **LEDs eventually turn on** (partial success!).

**Root cause:** AW VM sets SC1CR=0x01 (IOC=1) even in baud rate mode. The IOC check blocked the AW VM's clock. Firmware improvement: serial communication partially works, confirming the IOC/activity gate fixes help.

### Attempt 4: Refined timer_callback — only check IOC in TO2 mode (commit a86b906)

**Approach:** Only check IOC in TO2 trigger mode. In baud rate mode, the timer always drives.

**Changes:**
- `serial.cpp timer_callback()`: `(m_serial_mode & 3) == 0 && BIT(m_serial_control, 0)` — only block in TO2 slave mode

**Result:** Not tested (user provided policy clarification instead).

### Attempt 5: Remove idle_detect retrigger, one-shot accept (commit 35c38a1)

**Approach:** Fix three interconnected issues in the cpanel HLE:

1. **Remove idle_detect retrigger from sioclk()** — Continuous TO2 edges at 12.5 kHz retriggered the 250 µs timer on every edge, preventing it from ever firing. Now only `process_command()` starts the timer.

2. **Cancel idle_detect from tx_start()** — When the CPU sends more bytes, cancel pending idle detection.

3. **One-shot accept_next_byte** — Default false, set true only by `tx_start(1)`, consumed after accepting one byte. Rejects stale bytes from continuous clock edges.

**Result:** Firmware still shows ERROR, LEDs turn on correctly.

**Root cause discovered:** The unconditional cancel in `tx_start()` killed the timer for phantom bytes too. The firmware sends SM_TXDelay2 (phantom) AFTER SM_SendByteN (real), and tx_start(0) from the phantom cancelled the idle_detect that process_command() had just started.

### Attempt 6: Only cancel idle_detect for real bytes (commit 9d786d3)

**Approach:** Phantom bytes (tx_start state=0) should NOT cancel idle_detect. Only real bytes (state=1) cancel it.

**Changes:**
- `cpanel.cpp tx_start()`: `if (state != 0) m_idle_detect_timer->reset(attotime::never);`

**Rationale:** The firmware's TX sequence: phantom → phantom → REAL → phantom → REAL → phantom. The idle_detect timer starts when process_command() fires (after the 2nd real byte). The subsequent phantom (SM_TXDelay2) must NOT cancel it. The AW VM sends real dummy bytes, which correctly cancel the timer.

**Result:** Partial success — phantom byte cancellation still an issue (see later attempts).

### Attempts 7-27: Iterative Serial Fixes (not individually documented)

Multiple rounds of fixes addressed interconnected timing issues:
- **Deferred tx_start flags:** MAME's synchronous execution model causes `tx_start` for byte N+1 to fire before byte N's last rising edge. Solution: pending values applied at byte boundaries.
- **rx_waiting_for_start:** After completing a byte, orphan clock edges (from baud rate timer's internal RX completion) must be ignored until the next `tx_start` signals a new byte.
- **Sliding idle_detect window:** Instead of starting/cancelling idle_detect in `tx_start`, retrigger the 50 µs timer on every `sioclk()` edge. This creates a sliding window that fires only after the LAST edge (including phantom bytes).
- **LED commands must not generate responses:** Firmware sends LED data in rapid batches via the TX state machine. Queuing sync responses causes INTA delivery during the next TX command, setting IOC=1 and deadlocking the baud rate timer.

### Attempt 41: Right Panel Button State Desynchronization

**Problem:** Right panel buttons sometimes triggered the wrong LED.

**Root cause:** A residual byte left in `SC1BUF` from a previous serial operation caused the firmware's `scNcr_w()` to start a phantom reception. The stale byte was treated as a valid response, desynchronizing the button state arrays.

**Fix:** Cleared residual bytes in `scNcr_w()` and added timestamp-based debounce to the cpanel HLE.

### Attempt 42: INTRX1 Missing from Compiled Binary

**Problem:** Left panel buttons delivered bytes correctly via INTA self-clocking, but the firmware never processed them.

**Root cause:** The compiled MAME binary had an older version of `tmp94c241_serial.cpp` that logged "RX byte received" (line 182) but was missing the `INTRX1` interrupt flagging code (line 187) — both in the same `if (m_rx_clock_count == 0)` block. The source was correct; the binary was stale.

**Evidence:** 3,523 "RX byte received" log entries vs 0 "INTRX pending set" entries.

**Fix:** Rebuild MAME with current source.

### Attempt 43: Left Panel Header Encoding + Ghost Toggle Fix (FINAL FIX)

**Problem 1 — Ghost button toggles:** MAME input ports momentarily return single-bit non-zero values that revert within one scan interval (7 ms). The global 100 ms debounce converted each glitch into a full press-release cycle, flooding the event queue with phantom events. Log analysis found 110 left panel events + 50 right panel events, ALL ghost toggles, ZERO real presses.

**Fix 1:** Per-segment confirmation — state change must be stable for 2 consecutive scans (14 ms) before being reported.

**Problem 2 — Left panel header encoding (ROOT CAUSE):** The button packet header for left panel used `0x40 | segment` (bits 7:6=01), which falls in a dead zone of the firmware's ROM lookup table at `0xEDA03C`. All left panel events mapped to index 0x1F (> 0x15), bypassing LED dispatch entirely.

```
ROM lookup table at 0xEDA03C:
[0x00-0x0A]: 0B 0C 0D 0E 0F 10 11 12 13 14 15   → right (bits 7:6=00) ✓
[0x20-0x2A]: all 1F                                → DEAD ZONE (bits 7:6=01) ✗
[0x60-0x6A]: 00 01 02 03 04 05 06 07 08 09 0A     → left (bits 7:6=11) ✓
```

**Fix 2:** Changed left panel header from `0x40 | segment` to `0xC0 | segment`. Right panel kept at `segment` (already working).

**Result:** Both panels fully working. Left panel buttons produce correct LED reactions. Right panel unchanged.

## Remaining Minor Issues

### Baud Rate Half Speed
The baud rate timer fires at `m_hz` but toggles SCLK, so the effective bit rate is `m_hz / 2`. At BR1CR=0x14 (250 kHz nominal), the actual SCLK frequency is 125 kHz. This doesn't break correctness but makes serial communication 2x slower than real hardware.

## Resolution Summary

The complete set of fixes required to make the original firmware's control panel fully functional in MAME:

| Layer | Fix | Impact |
|-------|-----|--------|
| **CPU Serial** | Timer checks both TX and RX clock counts | Bytes complete correctly |
| **CPU Serial** | Defer TX bit 0 output to next falling edge | No last-bit corruption |
| **CPU Serial** | Capture RXD before forwarding clock | No race condition |
| **CPU Serial** | Gate SCLK output on PFFC state | No phantom bytes to cpanel |
| **CPU Serial** | Fix IOC bit check (bit 0, not bit 1) | Correct slave mode detection |
| **CPU Serial** | Refined timer_callback gate | 250 kHz clock works in all modes |
| **CPU Serial** | Gate TO2_trigger on TX/RX activity | Idle detection works |
| **CPU Serial** | INTRX1 interrupt flag set on RX complete | Firmware gets RX notifications |
| **CPanel HLE** | INTA mechanism with idle detect + self-clock | Bidirectional serial protocol |
| **CPanel HLE** | Phantom byte filtering via tx_start | Command parser not corrupted |
| **CPanel HLE** | Deferred tx_start flags at byte boundaries | No mid-byte flag application |
| **CPanel HLE** | rx_waiting_for_start (orphan edge filter) | No byte boundary desync |
| **CPanel HLE** | Sliding idle_detect window (50 µs retrigger) | Fires after last phantom byte |
| **CPanel HLE** | LED commands produce no response | No INTA during TX batches |
| **CPanel HLE** | Left panel header 0xC0 (not 0x40) | ROM lookup table valid zone |
| **CPanel HLE** | Per-segment confirmation (14 ms) | Ghost toggles filtered |

## Key Delay Calculations

All calculations assume 16 MHz CPU clock (2 × 8 MHz XTAL).

| Delay Routine | Iterations | Time per Iteration | Total Time |
|---------------|------------|-------------------|------------|
| DELAY_6_TICKS | 6 timer ticks | 80 µs/tick | **480 µs** |
| DELAY_51_TICKS | 51 timer ticks | 80 µs/tick | **4.08 ms** |
| DELAY_10_LOOPS | 10 | ~625 ns | **~6 µs** |
| DELAY_300_LOOPS | 300 | ~625 ns | **~188 µs** |
| DELAY_1500_LOOPS | 1500 | ~625 ns | **~938 µs** |
| DELAY_3000_LOOPS | 3000 | ~625 ns | **~1.875 ms** |

Timer tick rate: 12,500 Hz (T0/T1 cascade from 16 MHz ÷ prescaler).
Loop timing: DEC 1, WA (2) + CP WA, 0 (2) + JR Z (2) + JR T (4) = ~10 cycles = 625 ns.

## Code References

**MAME driver files (editable):**
- `src/devices/cpu/tlcs900/tmp94c241_serial.cpp` — CPU serial channel
- `src/mame/matsushita/kn5000_cpanel.cpp` — Control panel HLE
- `src/mame/matsushita/kn5000.cpp` — Main driver wiring

**Firmware reference (read only):**
- `maincpu/cpanel_routines.asm` — State machine, CPanel_WaitTXReady, INTA handler
- `shared/sfr_tmp94c241.asm` — SFR register addresses

**Related documentation:**
- [Serial Debugging Journey (Jan 2026)](/serial-debugging/) — First round of bit-level timing fixes
- [Control Panel Protocol](/control-panel-protocol/) — Command format, button segments, LED commands

---

*This is part of the ongoing effort to create a working MAME emulator for the Technics KN5000 music keyboard. See the [main documentation](/) for more details on the project.*
