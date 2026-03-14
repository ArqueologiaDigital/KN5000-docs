---
layout: page
title: "Research Log: TMP94C241 16-Bit Timer Interrupt Bug"
permalink: /feature-demo-timer-bug-2026-03-09/
---

# Research Log: TMP94C241 16-Bit Timer Interrupt Bug

**Date:** March 9, 2026 (second session)
**Duration:** ~6 hours
**Focus:** Why the sequencer timer interrupt (INTTR5) never fires in MAME
**Issue:** kn5000-y7t5 (P1 — Feature Demo sequencer doesn't cycle songs)

---

## Executive Summary

A 6-hour session traced the Feature Demo song cycling failure to two bugs in MAME's TMP94C241 16-bit timer emulation. Both bugs are in the `timer_16bits` lambda in `tmp94c241.cpp`. A fix has been implemented but not yet tested.

**Bug 1:** Both TREG_HIGH and TREG_LOW compare matches set the same interrupt flag (`0x08` = INTTR4). TREG_HIGH should set `0x80` (INTTR5).

**Bug 2:** The T4FFCR flip-flop control register is used to gate the entire match action (interrupt + counter reset + flip-flop), when according to the TMP94C241 datasheet it should only control the flip-flop inversion. The interrupt and counter reset should fire unconditionally on match.

These two bugs combine to ensure INTTR5 never fires. Since the firmware uses INTTR5 (not INTTR4) as the sequencer clock, the sequencer tick counters never increment and demo songs never cycle.

---

## Background: How the Sequencer Timer Works

The KN5000 firmware uses the TMP94C241's Timer 4/5 pair for sequencer timing. The architecture:

```
Timer 4 (16-bit up counter UC4)
  ├── TREG4 (low compare register)  → INTTR4 interrupt on match
  └── TREG5 (high compare register) → INTTR5 interrupt on match + counter reset

T4FFCR (flip-flop control register)
  ├── Bit 2: Invert flip-flop on TREG4 match
  └── Bit 3: Invert flip-flop on TREG5 match
```

The firmware configures:
- INTTR5 at priority 3 (enabled), handler at `0xEF086A`
- INTTR4 at priority 0 (disabled), handler at `0xEF0E21`
- Timer 4 running with TREG5 as the interval register

When INTTR5 fires, the handler drives the sequencer tick counters (DRAM locations 1047, 1051, 1052) which pace the accompaniment engine, metronome, and demo song cycling.

---

## The Bugs in Detail

### Bug 1: Wrong Interrupt Flag for TREG_HIGH Match

The original MAME code:

```cpp
if (((m_timer_16[timer_index] == m_treg_16[timer_reg_high]) && BIT(tffcr, 3)) ||
    ((m_timer_16[timer_index] == m_treg_16[timer_reg_low]) && BIT(tffcr, 2)))
{
    change_timer_flipflop(timer_id, FF_INVERT);
    m_timer_16[timer_index] = 0;
    m_int_reg[interrupt] |= 0x08;  // BUG: always sets INTTR4 flag
    m_check_irqs = 1;
}
```

Both branches of the OR set `m_int_reg[interrupt] |= 0x08`. For the interrupt register INTET45:
- Bit 3 (`0x08`) = INTTR4 pending flag
- Bit 7 (`0x80`) = INTTR5 pending flag

TREG_HIGH (TREG5) match should set `0x80` (INTTR5). TREG_LOW (TREG4) match should set `0x08` (INTTR4). The code always sets the INTTR4 flag regardless of which register matched.

**Impact:** Even if TREG5 match fires, it sets the INTTR4 flag. Since INTTR4 is configured at priority 0 (disabled), the interrupt is masked and the handler never runs.

### Bug 2: T4FFCR Incorrectly Gates the Entire Match

The original code uses `BIT(tffcr, 3)` and `BIT(tffcr, 2)` as conditions for the match to fire at all. This means if T4FFCR bits 2-3 are clear, no match action occurs — no interrupt, no counter reset, nothing.

According to the TMP94C241 datasheet (Section: 16-Bit Timers, Interval Timer Mode):

> "Match with TREGn generates interrupt and optionally inverts flip-flop."

And:

> "Set interval in TREG5/7/9/B (clears counter on match)"

The datasheet describes two separate behaviors on TREG match:
1. **Counter reset + interrupt** — always happens (this IS the interval timer)
2. **Flip-flop inversion** — controlled by T4FFCR bits

T4FFCR is the "Timer Flip-Flop Control Register". It controls the flip-flop, not the interrupt. The MAME code conflates these two behaviors.

**Impact:** The firmware writes T4FFCR with bits 2-3 both clear (no flip-flop needed for sequencer timing). The code interprets this as "don't fire the interrupt at all."

### Combined Effect

```
Real hardware:
  UC4 counts up → matches TREG5 → counter resets → INTTR5 fires → handler runs
  → sequencer ticks → songs cycle ✓

MAME (before fix):
  UC4 counts up → matches TREG5 → BIT(tffcr, 3) is 0 → NOTHING HAPPENS
  Even if it fired: 0x08 flag set → INTTR4 priority 0 → masked → handler never runs
  → ticks never increment → songs never cycle ✗
```

---

## Evidence from Lua Traces

### Interrupt Register State

Using `demo_int_check.lua` reading SFR addresses:

| Register | Address | Value | Meaning |
|----------|---------|-------|---------|
| INTET45 | 0xE6 | varies | INTTR4 priority in bits 6:4, INTTR5 priority in bits 2:0 |
| T16RUN | 0x9E | non-zero | Timer 4 and prescaler running |
| T4FFCR | 0x99 | 0xC3 | Bits 2-3 clear, bits 0-1/6-7 forced to 1 |
| T4MOD | 0x98 | configured | Timer 4 mode register |

T4FFCR reads as `0xC3` because the write handler forces bits 0,1,6,7 to 1: `m_t4ffcr = data | 0xc3`. This confirms bits 2 and 3 are 0, meaning the original MAME code blocks all match actions.

### Sequencer State Monitor

The `demo_state_monitor.lua` trace (180 seconds, ~10800 frames) confirmed:

| Observation | Value | Implication |
|-------------|-------|-------------|
| `tick=0` throughout | Counter never changes | INTTR5 handler never runs |
| `1054=0x00` | Enable promotion chain incomplete | Internal clock promotion never completes |
| `seq_t=0/0` | Sequencer state 0/0 | AccPlayMode never advances |
| `3375` (demo timer) | Counts down 13→0 | Timer tick works (via INTT1), confirming only INTTR5 is broken |

The demo timer at DRAM 3375 counts down normally because it's driven by `Demo_SelectEntry_TimerTick` in the main loop, not by the sequencer timer. But the sequencer tick counters (1047, 1051, 1052) that are driven by INTTR5 never change.

---

## The Fix

The fix separates the three concerns:

```cpp
for ( ; m_timer_change[timer_index + 4] > 0; m_timer_change[timer_index + 4]--)
{
    m_timer_16[timer_index]++;
    if (m_timer_16[timer_index] == m_treg_16[timer_reg_high])
    {
        if (BIT(tffcr, 3))
            change_timer_flipflop(timer_id, FF_INVERT);  // flip-flop: optional
        m_timer_16[timer_index] = 0;                      // counter reset: always
        m_int_reg[interrupt] |= 0x80;                     // INTTR5 flag: always
        m_check_irqs = 1;
    }
    else if (m_timer_16[timer_index] == m_treg_16[timer_reg_low])
    {
        if (BIT(tffcr, 2))
            change_timer_flipflop(timer_id, FF_INVERT);  // flip-flop: optional
        m_int_reg[interrupt] |= 0x08;                     // INTTR4 flag: always
        m_check_irqs = 1;
    }
}
```

Changes:
1. T4FFCR bits only gate `change_timer_flipflop()`, not the entire match
2. TREG_HIGH match sets `0x80` (INTTR5 flag), TREG_LOW match sets `0x08` (INTTR4 flag)
3. Counter reset on TREG_HIGH match is unconditional (interval timer behavior)

**Status:** Implemented in `tmp94c241.cpp`, not yet built/tested. A potential concern is that TREG_HIGH=0 (uninitialized) would match when the counter wraps to 0, generating spurious interrupts during boot. This needs testing.

---

## Investigation Path

### Attempt 1: INTTR4 Handler Analysis (Dead End)

Initially examined the INTTR4_HANDLER at `0xEF0E21` (`style_data_init.s:626`) in detail, mapping its sub-sections:
- CheckMetroEnable, CheckSeqEnable, CheckAltSeqEnable
- MetroPhaseSync, SeqAutoStart
- MetroBeat_Check, AltSeqBeat_Check

This was the wrong handler. The firmware uses INTTR5 (vector 0x64, handler at `0xEF086A`), not INTTR4 (vector 0x60). The vector table in ROM at 0xFFFF60 and 0xFFFF64 confirms these are separate handlers.

**Lesson:** Always verify which interrupt vector the firmware actually enables before analyzing the handler code.

### Attempt 2: Enable Chain Tracing

Traced the sequencer enable chain:
1. Demo delayed start (`SeqTimer_CheckPlaybackCountdown`) sets DRAM 1057=1, 1056=1
2. INTT1 internal clock handler promotes these to 1056=6 when DRAM 1050 > 1
3. `AccPlayMode_Dispatch` rewrites to 1057=12, 1056=12

But this chain requires INTTR5 to fire first, creating the sequencer tick that INTTR5 was supposed to generate. Circular dependency confirmed the problem is upstream — the timer interrupt itself.

### Attempt 3: Timer Register Investigation

Wrote Lua scripts to read timer SFR registers. First attempt used wrong addresses (T4FFCR at 0x95, INTET45 at 0x60). Corrected to T4FFCR at 0x99, INTET45 at 0xE6 (SFR base 0xE0 + INTET45 enum index 6).

Confirmed: T4FFCR bits 2-3 are both 0, T16RUN shows timer running, INTET45 shows INTTR5 priority set.

### Attempt 4: Source Code Analysis

Read `tmp94c241.cpp` `timer_16bits` lambda and identified both bugs. Cross-referenced with TMP94C241 datasheet section on 16-bit interval timers to confirm T4FFCR should not gate the match.

### Attempt 5: First Fix (Failed)

Removed T4FFCR gating entirely AND fixed interrupt flags. Built MAME. The fix caused boot failures — INTTR5 fired during initialization with TREG5=0, disrupting firmware startup. Reverted.

### Attempt 6: Second Fix (Partial, Reverted)

Kept T4FFCR gating, only fixed interrupt flags (0x80 for TREG_HIGH). This was safe but insufficient — T4FFCR bits still gate the match, so no interrupts fire. Functionally equivalent to old code for the KN5000 case.

### Attempt 7: Final Fix (Current)

Separated T4FFCR gating to only control flip-flop, interrupt and counter reset are unconditional. This is the correct hardware behavior per the datasheet. Not yet built/tested.

---

## Comparison with 8-Bit Timer Implementation

The 8-bit timer code in the same file does NOT gate interrupts on flip-flop control:

```cpp
// 8-bit timer match (simplified)
if (m_timer_8[timer_index] == m_treg_8[timer_reg])
{
    if (invert)
        change_timer_flipflop(timer_index | 1, FF_INVERT);
    m_timer_out_state[timer_index] = !m_timer_out_state[timer_index];
    // ... interrupt generation happens unconditionally
}
```

The 8-bit timers correctly separate the flip-flop control from the match/interrupt behavior. The 16-bit timer code was written inconsistently.

---

## What Was NOT Resolved

### 1. Build and Test of the Fix

The fix is implemented but MAME has not been rebuilt and tested. Concerns:
- TREG5=0 at boot may cause spurious INTTR5 fires (65536 ticks to wrap, ~16ms at fastest clock)
- May affect other systems using TMP94C241 16-bit timers
- Need to verify the demo actually cycles songs after the fix

### 2. INTTR5 Handler Analysis

The INTTR5 handler at `0xEF086A` has not been examined. Understanding what it does differently from INTTR4_HANDLER would confirm the fix is sufficient.

### 3. Impact on Other Timers

The fix affects all four 16-bit timers (T4/T6/T8/TA). Need to verify that Timer 6, 8, and A behavior remains correct for whatever the KN5000 firmware uses them for.

### 4. SSF Visual Presentation

The Feature Demo's visual presentation (FTBMP bitmaps) remains broken — a separate issue from the sequencer timer bug.

---

## Key Source Files

| File | Key Location | Relevance |
|------|-------------|-----------|
| `tmp94c241.cpp:1599-1636` | `timer_16bits` lambda | The buggy code (and fix) |
| `tmp94c241.h` | `INTET45 = 6` enum | Interrupt register index mapping |
| `style_data_init.s:626` | INTTR4_HANDLER | Wrong handler (analyzed by mistake) |
| ROM vector 0xFFFF64 | `0x00EF086A` | INTTR5 handler address (correct handler) |
| `style_data_init.s:387` | INTT1_HANDLER | Internal clock handler (reference) |
| `sequencer_engine.s:18893` | AccPlayMode state 3 | Waits on tick counter 1052 |
| `accompaniment_engine.s:8040` | AccPlayMode_Dispatch | Promotion chain endpoint |
| `peripherals.md` | 16-Bit Interval Timer Mode | Datasheet reference |

## Key DRAM Addresses (Sequencer)

| Address | Name | Purpose |
|---------|------|---------|
| 1047 | Metro sub-tick | Metronome timing (driven by INTTR5) |
| 1050 | Internal clock | Internal clock counter (driven by INTT1) |
| 1051 | Alt seq sub-tick | Alternate sequencer sub-tick |
| 1052 | Alt seq tick | Alternate sequencer tick counter |
| 1054 | Enable flags | Bit 2: sequencer enabled |
| 1056 | Alt clock state | Promotion chain variable |
| 1057 | Alt seq state | Promotion chain variable |
| 8956 | AccPlayMode state | State machine index |

## SFR Addresses (Timer 4)

| Address | Register | Purpose |
|---------|----------|---------|
| 0x90-0x91 | TREG4 | Timer 4 compare register (write-only) |
| 0x92-0x93 | TREG5 | Timer 5 compare register (write-only) |
| 0x98 | T4MOD | Timer 4 mode |
| 0x99 | T4FFCR | Timer 4 flip-flop control |
| 0x9E | T16RUN | 16-bit timer run control |
| 0xE6 | INTET45 | Interrupt priority/flags for INTTR4/INTTR5 |

---

## Reflection

### What Went Well

1. **Systematic elimination** — traced from symptom (ticks=0) through interrupt registers → timer registers → MAME source → identified both bugs
2. **Datasheet-driven** — confirmed fix correctness against TMP94C241 peripheral documentation, not just intuition
3. **Multiple Lua scripts** — purpose-built scripts for interrupt state, timer config, tick monitoring, and clock promotion tracing
4. **Cross-reference with 8-bit timers** — comparing the two implementations revealed the inconsistency

### What Could Be Better

1. **Analyzed the wrong handler first** — spent significant time on INTTR4_HANDLER before realizing the firmware uses INTTR5. Should have checked interrupt priority configuration first.
2. **First fix attempt broke boot** — should have anticipated the TREG=0 match issue before building. Could have added logging instead of changing behavior.
3. **Fix not yet tested** — session ended with the fix implemented but not built/tested. Incremental verification (build after each change) would have been better.
4. **Too many fix iterations** — three attempts (unconditional, gated+flags, separated) could have been one if the datasheet was consulted first.

### Key Insight

The TMP94C241 datasheet is clear: "Match with TREGn generates interrupt and optionally inverts flip-flop." The word "optionally" applies only to the flip-flop, not to the interrupt. When writing emulation code for timer peripherals, the match/interrupt/counter-reset behavior is the core function; the flip-flop is an auxiliary output. Gating the core function on an auxiliary control register inverts the hardware's design intent.

---

*This is an automated research log from a continuous investigation session. The fix is implemented but untested. Follow-up testing is required.*

*Last updated: March 9, 2026*
