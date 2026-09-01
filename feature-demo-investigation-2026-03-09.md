---
layout: page
title: "Research Log: Feature Demo Timer Investigation"
permalink: /feature-demo-investigation-2026-03-09/
---

# Research Log: Feature Demo Timer Investigation

**Date:** March 9, 2026
**Duration:** ~18 hours continuous session
**Focus:** Investigating why the Feature Demo timer gets stuck at 10 in MAME
**Issue:** kn5000-y7t5 (P1 — Feature Demo SSF visual presentation broken)

---

## Executive Summary

An 18-hour continuous investigation session traced the Feature Demo timer stall to a specific firmware function (`SwbtWr_ReinitBothBanks`) that runs an inline event dispatch loop, blocking the main loop for many seconds. The root cause was identified but not fully resolved. This report documents the findings, methodology, mistakes, and principles for future investigations.

---

## What Was Being Investigated

The Feature Demo has two independent subsystems:

1. **Demo Timer System** — counts down at DRAM `0x0D2F`, cycling through demo songs. At threshold 10, it loads the next song; at 3, it starts playback; at 1, it updates the display.
2. **SSF Visual Presentation** — renders FTBMP bitmaps to the LCD via XML-scripted actions.

Both systems were partially broken in MAME. The SSF presentation issue was previously solved (documented on the [Feature Demo page]({{ site.baseurl }}/feature-demo/)). This session focused on the timer system — specifically, why the timer gets stuck at value 10 and never decrements further.

---

## Root Cause Found: SwbtWr_DispatchLoop Blocks the Main Loop

### The Discovery

`Demo_SelectEntry_PlaySong` (`file_demo_proc.s:718`) is called when the demo timer reaches 10. Its job is to load and start the next demo song. The call chain:

```
Demo_SelectEntry_PlaySong (0xF86E06)
  → cpdi8 36148, 19              ; check DRAM[0x8D34] == 0x13
  → calr Demo_GetPresetBaseForPartAlt            ; read song pointer from table
  → call ToneGen_FileIO_SaveAndSync            ; configure song data
  → call SwbtWr_ReinitBothBanks  ; ← BLOCKS HERE
  → call Seq_DispatcherEntry     ; ← NEVER REACHED
  → stdi8 36686, 6               ; ← NEVER REACHED (0x8F4E stays 0x04)
  → ret
```

### How the Blocking Works

`SwbtWr_ReinitBothBanks` (`system_handlers.s`, the file `style_data_init.s` was renamed to) calls `SwbtWr_InitBank1` and `SwbtWr_InitBank2` (both in `dsp_config_sysex.s`). Each of these calls `SwbtWr_DispatchLoop_Init`, which has a critical fall-through:

```asm
SwbtWr_DispatchLoop_Init:           ; dsp_config_sysex.s
    stdi16 49275, 0                 ; reset buffer index to 0
                                    ; *** FALLS THROUGH ***
SwbtWr_DispatchLoop:                ; dsp_config_sysex.s
    ldda32 xiy, 49289              ; load buffer base pointer
    addda16 xiy, 49275             ; add current index
    cp (xiy), 0xFF                 ; check for terminator
    jr z, SwbtWr_DispatchLoop_PostCallbacks
    ; ... process one event, call tone generator callback ...
    adddi16 49275, 4               ; advance index by 4 bytes
    jrl SwbtWr_DispatchLoop         ; tight loop — no yield
```

This is a **tight processing loop** that iterates over all buffered MIDI/sequencer events until it hits a `0xFF` terminator byte. Each iteration calls a tone generator callback, which takes approximately 5 frames (~80ms) to complete. With the buffer index climbing from 0 to 140+ entries over 130+ frames, the entire loop takes **many seconds** to complete.

During this time, the main firmware loop is completely blocked. `Demo_SelectEntry_TimerTick` is never called, so the timer stays frozen at 10.

### Evidence

MAME Lua traces confirmed:

| Metric | Value | Implication |
|--------|-------|-------------|
| `DRAM[0x8F4E]` | Stays at `0x04` | `stdi8 36686, 6` at line 741 never executes |
| `swbt_idx` (DRAM `0xC07B`) | Climbs 0→140+ over 130 frames | Loop processing ~1 event per 5 frames |
| Timer (`0x0D2F`) | Stuck at 10 | Main loop blocked, TimerTick never called |
| `chain` (`0xC080`) | Constant during block | No new events being generated |

---

## Follow-Up: Timer Blocking is Temporary (CORRECTION)

**Update (March 9, same day):** After rebuilding MAME (to eliminate stale debug messages) and running the trace for 120 seconds instead of 60, the blocking was found to be **temporary, not permanent**.

| Frame | Event |
|-------|-------|
| 1225 | Timer reaches 10, PlaySong called |
| 1237 | SwbtWr buffer processing begins (`buf_idx` starts climbing) |
| 1600 | `buf_idx` reaches 452, then resets (second bank init) |
| 1686–2100 | Second bank processing cycle (buf_idx 0→488) |
| ~2200 | **`8F4E` changes to `0x06` — PlaySong RETURNED** |
| 2600 | Timer resumes counting: 10→9→8→... |
| 3000 | Timer at 4, system functioning normally |

**Total blocking time:** ~960 frames (~16 seconds). The dispatch loop processes 452+ events across multiple bank reinitializations. Each callback takes ~35ms, which is consistent with the volume of work.

**Previous diagnosis was wrong** because the trace only ran for 1500 frames (25 seconds total, only 5 seconds after LEFT 2). The 16-second blocking period hadn't completed when the trace ended.

**Open question:** Does the ~16 second blocking match real hardware behavior? On real hardware with waveform ROMs present, the tone generator callbacks may complete faster (or slower), affecting the blocking duration.

---

## What Was NOT Resolved

### 1. Whether 16-Second Blocking Matches Real Hardware

The ~16 second SwbtWr processing delay may or may not be correct. On real hardware:
- Tone generator writes go to actual DSP hardware (fast)
- In MAME, they go to HLE (potentially different timing)
- The real question is whether users would notice a 16-second pause when entering the Feature Demo

### 2. SSF Visual Presentation Event Routing

While the timer blocking was traced, the SSF event routing remains separately broken:
- Event `0x1C00038` requires `UIState_KeyScan_Dispatch` to be called with the correct UI state
- LEFT 2 button generates param upper16 = `0xAA0A`, which doesn't match any of the 5 registered filters (`0x1000`–`0x1400`)
- `demo_state` at `0x0251D8` stays `0x0000` throughout

### 3. Demo Song Pointer Table

The table at `0x9C4000` in Table Data ROM holds 19 valid entries (indices 0–18). Entry 18 = `0x008E0000`. Entry 19 = NULL (end-of-list). The demo cycles through these using index stored at DRAM `0x28A4` (10404). The index was confirmed set to 18 (`stda8 10404, a` at `drawbar_panel_ui.s:15232`).

---

## Methodology

### Tools Used

1. **MAME Lua autoboot scripts** — 5 custom scripts created:
   - `trace_demo_events.lua` — Button sequence + DRAM state monitoring
   - `read_demo_table.lua` — Pointer table dump + state monitoring
   - `trace_playsong.lua` — Timer history + playback state tracking
   - `trace_playsong_detailed.lua` — PC + SwbtWr index monitoring
   - `trace_swbt_buffer.lua` — Buffer content dump

2. **ROM disassembly analysis** — Cross-referencing assembly source files:
   - `file_demo_proc.s` — Demo timer and song loading
   - `dsp_config_sysex.s` — SwbtWr dispatch loop
   - `system_handlers.s` (`style_data_init.s` at the time of this session) — Bank initialization
   - `ui_control_panel.s` (`tonegen_voice_ctrl.s` at the time of this session) — UI state dispatch
   - `ui_widget_defs.s` — Event dispatch routing
   - `cpanel_constants.s` — Button mapping
   - `cpanel_routines.s` — Control panel ISR

3. **Button-to-event tracing** — Full path from physical button press through ISR → event queue → dispatch → handler

### Approach: Progressive Narrowing

The investigation followed a progressive narrowing pattern:

```
Timer stuck at 10
  → Which function is called at timer=10?
    → Demo_SelectEntry_PlaySong
      → Which call in PlaySong blocks?
        → SwbtWr_ReinitBothBanks
          → How does ReinitBothBanks block?
            → InitBank → DispatchLoop_Init falls through to DispatchLoop
              → Why is DispatchLoop slow?
                → Each callback takes ~5 frames (UNRESOLVED)
```

---

## Reflection: Advances and Mistakes

### Advances

1. **Identified the exact blocking function** — `SwbtWr_DispatchLoop` running inline via fall-through from `SwbtWr_DispatchLoop_Init`, called from `SwbtWr_ReinitBothBanks`
2. **Mapped the full call chain** from timer tick → PlaySong → ReinitBothBanks → DispatchLoop
3. **Confirmed with Lua traces** that `DRAM[0x8F4E]` stays at `0x04` (PlaySong never returns)
4. **Documented the SwbtWr buffer protocol** — 4-byte events, `0xFF` terminator, base at `0xC089`, index at `0xC07B`
5. **Traced the button-to-event path** — CPanel ISR → event queue at `0x200AD` → dispatch → handler

### Mistakes

1. **Spent too long on ROM byte reading** — Tried to manually interleave even/odd Table Data ROM files to read the pointer table. Got wrong byte ordering. Should have immediately used MAME Lua to read through the memory map.

2. **Didn't rebuild MAME early enough** — The C07D debug messages that obscured trace output came from a stale binary. Should have verified the MAME binary was current before starting intensive tracing.

3. **Explored tangential paths** — Spent significant time tracing the SSF event routing (which was already documented as working via a different path) instead of focusing exclusively on the timer blocking.

4. **Insufficient scope control** — The session drifted between investigating the timer system and re-investigating the SSF event routing, diluting focus on either.

5. **Too many Lua scripts** — Created 5 separate trace scripts with overlapping functionality. A single well-structured script with configurable sections would have been more efficient.

6. **Delayed the "measure, don't guess" principle** — Spent time reading assembly and hypothesizing before writing traces. The Lua traces provided definitive answers much faster than code reading.

7. **No intermediate commits** — Findings accumulated for hours without being committed to documentation or the issue tracker, risking loss of context.

---

## Principles for Future Investigation Sessions

Based on this session's experience, the following principles should guide future deep-dive investigations:

### 1. Measure First, Read Second

Write a Lua trace script within the first 30 minutes. Let the emulator tell you what's happening before spending hours reading assembly. Assembly reading should be guided by trace data, not the other way around.

### 2. One Question Per Script

Each Lua trace script should answer exactly one question. Don't combine buffer dumps, state monitoring, and event tracing in a single script. Focused scripts produce focused answers.

### 3. Rebuild Before Tracing

Always verify the MAME binary is current before starting any trace session. Run `git status` in the MAME directory and rebuild if there are uncommitted changes or if the binary is older than the source.

### 4. Commit Findings Incrementally

After each significant finding, commit it to the documentation and issue tracker immediately. Don't accumulate hours of undocumented discoveries. A finding that isn't committed doesn't exist.

### 5. Time-Box Tangents

If an investigation path hasn't yielded results in 2 hours, write down what was tried and switch to a different approach. Don't follow the same lead for 8+ hours.

### 6. Separate Issues Stay Separate

The timer blocking and the SSF event routing are different bugs. Investigating both in the same session is fine, but switching between them without closing one first leads to confusion and duplicated work.

### 7. Use the Right Tool for the Job

- MAME Lua for runtime state observation
- `llvm-mc --disassemble` for decoding bytes
- ROM disassembly source for understanding control flow
- `llvm-objdump` for labeled ELF disassembly
- Don't try to manually decode ROM bytes when tools exist

### 8. Document the Dead Ends

Failed approaches are valuable — they narrow the search space for the next session. Write them down with the reason they didn't work.

### 9. Check Assumptions Early

The assumption that LEFT 2 sends event `0x1C00038` via `UIState_KeyScan_Dispatch` was wrong — it goes through a different path. Testing assumptions with traces before building on them saves hours.

### 10. Keep a Running Log

Maintain a timestamped log of what was tried, what was found, and what questions remain. This prevents re-exploring paths that were already dead-ended and makes handoff (to another session or another agent) much smoother.

---

## Next Steps

1. **Verify SwbtWr buffer terminator** — Dump the buffer at `0xBD3C` to check for proper `0xFF` termination. If missing, this explains the long blocking.

2. **Profile tone generator callbacks** — Instrument the callback function to measure per-call timing. The ~5-frame-per-event rate may indicate an emulation issue.

3. **Rebuild MAME** — Clean rebuild to eliminate stale debug messages and ensure the binary matches current source.

4. **Test with shorter buffer** — If the buffer has hundreds of events, the blocking is by-design behavior (processing a large backlog). The real fix may need to happen in how the buffer is populated.

5. **Investigate SSF event routing independently** — The `0xAA0A` parameter not matching any filter is a separate issue from the timer blocking.

---

## Key Source Files

| File | Key Functions | Relevance |
|------|---------------|-----------|
| `file_demo_proc.s` | `Demo_SelectEntry_TimerTick`, `Demo_SelectEntry_PlaySong`, `Demo_SelectEntry_ProcessSongList` | Timer state machine and song loading |
| `dsp_config_sysex.s` | `SwbtWr_DispatchLoop`, `SwbtWr_QueueMainEvent` | The blocking dispatch loop |
| `system_handlers.s` (`style_data_init.s` at the time of this session) | `SwbtWr_ReinitBothBanks`, main loop Phase 4 | Initialization that triggers the block |
| `ui_control_panel.s` (`tonegen_voice_ctrl.s` at the time of this session) | `UIState_KeyScan_Dispatch` | Button event routing |
| `ui_widget_defs.s` | `EventDispatch_Direct` (0xFA9945) | Event filter matching |
| `cpanel_constants.s` | Button mapping tables | Physical button → event param |
| `cpanel_routines.s` | `CPanel_RX_ButtonPacket` | Control panel ISR |
| `smf_event_processor.s` (`seq_task_sched.s` at the time of this session) | `Seq_DispatcherEntry`, `Seq_DispatcherTick` | Sequencer task scheduling |

## Key DRAM Addresses

| Address | Name | Purpose |
|---------|------|---------|
| `0x0D2F` | Demo timer | Countdown value (set to 15, triggers at 10/3/1) |
| `0x8F4E` | Playback state | Set to 6 by PlaySong (stays at 4 = blocked) |
| `0x8D34` | UI state | Must be 0x13 for PlaySong to execute |
| `0x8D38` | UI sub-state | 0xE4 = Feature Presentation mode |
| `0xC07B` | SwbtWr buffer index | Current read position in dispatch buffer |
| `0xC089` | SwbtWr buffer base | Pointer to event buffer |
| `0xC080` | Chain byte | Handler chain selector |
| `0xC07D` | Param byte | Handler parameter |
| `0x0251D8` | Demo state | SSF presentation state (stays 0x0000) |
| `0x28A4` | Demo entry index | Current song index (set to 18) |
| `0x28B4` | Guard variable | Song list pointer |

---

*This is an automated research log from a continuous investigation session. Findings are preliminary and some conclusions may be revised as investigation continues.*

*Last updated: March 9, 2026*
