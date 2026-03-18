---
layout: default
title: Data Wheel Investigation
nav_order: 25
---

# Data Wheel (TEMPO/PROGRAM Encoder) Investigation

## Overview

The KN5000 has a large rotary encoder (data wheel) near the LCD, labeled TEMPO/PROGRAM. This page documents the forensic analysis of how the firmware processes data wheel input and how it was implemented in the MAME emulator.

## Firmware Mechanism

### Boot-Time Initialization

During boot, the firmware polls the data wheel state via control panel serial protocol:

1. Firmware sends command `20 0B` (query left panel segment 0x0B)
2. MCU responds with a button-type packet (header `0x0B`, no panel flag)
3. Firmware stores the raw byte at **DRAM[0x8E55]** (button state array + 0x0B)
4. Firmware checks bits 7 and 6 to derive encoder state:
   - **Bit 7 set** → state `0x0D` (clockwise / increment)
   - **Bit 6 set** → state `0x0E` (counterclockwise / decrement)
   - **Neither set** → state `0x0C` (idle / neutral)
5. Derived state stored at **DRAM[0x8E6A]** (address 36458)
6. Loop continues until state stabilizes (same value on consecutive reads)

**Source:** `cpanel_routines.s:516-549` (`CPanel_ButtonPollLoop`)

### Steady-State Processing

After boot, the data wheel state is updated via INTA-triggered button packets:

1. Panel MCU detects encoder rotation
2. MCU sends INTA interrupt + segment 0x0B packet via serial
3. `CPanel_RX_ButtonPacket` processes the packet:
   - Uses `ex (xhl), a` to atomically swap new data into DRAM[0x8E55]
   - Computes changed bits via XOR for the event queue
4. Main loop calls `Encoder_ValueScanAndSync` (tonegen_fileio_handlers.s:1242)
5. Scan table at **DRAM[0x8E78]** is read (3-byte entries)
6. `Encoder_PrepareCallback` dispatches to ROM callback tables:
   - Primary table: **ROM 0xED9C1E** (when DRAM[36148] ≠ 20)
   - Alternate table: **ROM 0xED9C9E** (when DRAM[36148] = 20)
7. Callback generates **SwbtWr type 0x21** event
8. `SwbtWr_ProcessAll` dispatches → writes type to **DRAM[0xC07D]**
9. `CtrlPanel_HandleSerialPort` checks DRAM[0xC07D] == 0x21 → posts event **0x1C0001F**
10. UI navigation handler processes the event (tempo change, program scroll, etc.)

### Main Loop Call Chain

```
MainLoop (system_handlers.s:1121)
  ├─ MidiParam_ProcessDeltas       (encoder debounce)
  ├─ CPanel_RX_ProcessOrInit       (process serial RX → updates DRAM[0x8E55])
  ├─ Encoder_TimingAndOutput       (timing/throttle)
  ├─ ...
  ├─ Encoder_ValueScanAndSync      (scan table → callback → SwbtWr 0x21)
  ├─ SwbtWr_ProcessAll             (dispatches → DRAM[0xC07D] = 0x21)
  └─ MainTitle_PrepareAndDispatch  (reads 0xC07D → event 0x1C0001F)
```

## ROM Callback Tables

### Encoder Handler Jump Table (ROM 0xEDA0BC)

Used by `CPanel_EncoderDispatch` for Type 2 encoder packets (analog controllers):

| Index | Encoder ID | Handler | Controller |
|-------|-----------|---------|------------|
| 2 | 0x02 | Encoder_ProcessModwheel | Modulation wheel |
| 5 | 0x05 | Encoder_ProcessVolume | Volume slider |
| 25 | 0xC1 | Encoder_ProcessBreath | Breath controller |
| 26 | 0xC2 | Encoder_ProcessFoot | Foot controller |
| 27 | 0xC3 | Encoder_ProcessExpression | Expression pedal |
| 31 | 0xC7 | Encoder_PassthroughIdentity | Passthrough |
| Others | — | Encoder_ReturnDefaultConstant | Unused (returns 1) |

### Primary Callback Table (ROM 0xED9C1E)

Used by `Encoder_PrepareCallback` for scan table processing. 32 entries × 4 bytes. Entry 25 (encoder_ID 0xC1) contains params `[A9 21 00 FF]` where **0x21 is the SwbtWr event type** for the data wheel.

### Alternate Callback Table (ROM 0xED9C9E)

Selected when DRAM[36148] == 20 (alternate system mode). Entry 25 uses params `[A8 13 00 FF]` with a different handler.

## Key DRAM Addresses

| Address | Decimal | Size | Name | Purpose |
|---------|---------|------|------|---------|
| 0x8E4A | 36426 | — | STATE_OF_CPANEL_BUTTONS | Button state array base |
| 0x8E55 | 36437 | 1 | Data wheel raw byte | Segment 0x0B data from MCU |
| 0x8E6A | 36458 | 1 | Derived encoder state | 0x0C=idle, 0x0D=CW, 0x0E=CCW |
| 0x8E6C | 36492 | 1 | Scan table index | Current entry in scan loop |
| 0x8E6E | 36494 | 1 | Callback counter | Pending callbacks |
| 0x8E78 | 36472 | — | Encoder scan table | 3-byte entries, 0xFF terminated |
| 0x8E90 | 36496 | 1 | Current scan value | Callback table index |
| 0xC07D | 49277 | 1 | SwbtWr type byte | Type 0x21 = data wheel event |
| 0xC07E | 49278 | 1 | SwbtWr parameter | Encoder value/direction |

## MAME Implementation

### Approach

The data wheel is implemented as two keyboard inputs mapped to segment 0x0B of the control panel HLE:

- **`]` key** → bit 7 set → clockwise (increment)
- **`[` key** → bit 6 set → counterclockwise (decrement)

### HLE Changes

1. **Input port:** `DATA_WHEEL` ioport with bits 7 (CW) and 6 (CCW)
2. **Segment 0x0B handling:** `read_data_wheel_state()` reads the ioport, returns bits 7-6
3. **Boot query:** `20 0B` command returns data wheel state via `send_data_wheel_packet()`
4. **Button scan timer:** Includes data wheel in periodic scan (~143 Hz), sends INTA-triggered packets on change
5. **Debounce:** 2-scan confirmation (14ms) before reporting change, matching button debounce

### Files Modified

- `kn5000.cpp` — DATA_WHEEL ioport definition, wiring to cpanel device
- `kn5000_cpanel.h` — Data wheel port pointer, state tracking members
- `kn5000_cpanel.cpp` — read_data_wheel_state(), send_data_wheel_packet(), button_scan_callback extension

### Branch

`kn5000_research_datawheel` (research branch, not for upstream PR)

## Verification Steps

### Automated (done)
- [x] MAME builds clean with data wheel changes

### Manual (needs human interaction)
- [ ] Dump encoder scan table (DRAM 0x8E78) via MAME debugger after boot
- [ ] Verify CPanel_InitButtonState runs in steady state
- [ ] Set watchpoint on 0x8E78 and test data wheel interaction
- [ ] Confirm SwbtWr type 0x21 appears at DRAM[0xC07D] when pressing `[` or `]`
- [ ] Confirm tempo/program value changes on LCD

### Debugger Commands

```
# Dump encoder scan table
d 0x8E78,0x30

# Watch for data wheel state changes
wpset 0x8E55,1,w

# Watch for SwbtWr type 0x21
wpset 0xC07D,1,w

# Watch for derived encoder state
wpset 0x8E6A,1,w
```

## Previous Approaches (Failed)

1. **Segment 0x0B INTA delivery** — Tried sending segment 0x0B as button type directly via INTA. The firmware received it but the steady-state processing chain didn't generate SwbtWr events.
2. **Type 2 encoder packets** — Sent Type 2 (analog) encoder packets with various IDs. The firmware processed them for MIDI CC (modwheel, volume, etc.) but not as data wheel events.
3. **Piggybacking on E0 13** — Tried including data wheel data in the steady-state right panel poll response. Did not reach the correct processing path.

## Current Hypothesis

The data wheel works through the button state mechanism (segment 0x0B), NOT through the Type 2 encoder system. The key encoding is:
- Bit 7 of segment 0x0B data = clockwise rotation active
- Bit 6 of segment 0x0B data = counterclockwise rotation active

The firmware derives state 0x0C/0x0D/0x0E from these bits and uses it to generate SwbtWr type 0x21 events via the callback table mechanism.
