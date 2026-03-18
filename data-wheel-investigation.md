---
layout: default
title: Data Wheel Investigation
nav_order: 25
---

# Data Wheel (TEMPO/PROGRAM Encoder) Investigation

## Overview

The KN5000 has a large rotary encoder (data wheel) near the LCD, labeled TEMPO/PROGRAM. This page documents the forensic analysis of how the firmware processes data wheel input, separating confirmed findings from hypotheses still under investigation.

## Confirmed: Transport Mechanism

### Segment 0x0B Encoding

The data wheel state is communicated from the control panel MCU to the main CPU via **segment 0x0B button packets** — the same packet type used for regular buttons, NOT the Type 2 encoder packets used for analog controllers (modwheel, volume, etc.).

**Source:** `cpanel_routines.s:524-536` (`CPanel_ButtonPollLoop`)

```asm
ldda8 a, 36437     ; Read byte at DRAM[0x8E55] (segment 0x0B)
ldb w, 0xD         ; Default: 0x0D (clockwise)
bit 7, a           ; Test bit 7
jr nz, CPanel_EncoderCheck   ; If set → CW (0x0D)
ldb w, 0xE         ; 0x0E (counterclockwise)
bit 6, a           ; Test bit 6
jr nz, CPanel_EncoderCheck   ; If set → CCW (0x0E)
ldb w, 0xC         ; 0x0C (idle)
```

The raw byte at DRAM[0x8E55] encodes:
- **Bit 7 set** → clockwise rotation → derived state `0x0D`
- **Bit 6 set** → counterclockwise rotation → derived state `0x0E`
- **Neither set** → idle → derived state `0x0C`

### Boot-Time Initialization

During boot, the firmware explicitly polls the data wheel:

1. Sends command `20 0B` (query left panel, segment 0x0B)
2. MCU responds with a button-type packet (header `0x0B`, no panel flag)
3. Firmware stores the raw byte at **DRAM[0x8E55]** (button state array offset 0x0B)
4. Derives state (0x0C/0x0D/0x0E) from bits 7-6, stores at **DRAM[0x8E6A]**
5. Loops until state stabilizes (same value on two consecutive reads)

### Packet Reception

`CPanel_RX_ButtonPacket` (cpanel_routines.s:1230-1265) processes incoming button packets. The instruction `ex (xhl), a` (opcode `0x83 0x31`) **atomically swaps** the new data into the button state array and returns the old value, enabling XOR-based change detection.

For a segment 0x0B packet with header byte `0x0B`:
- Packet type bits 5:3 = `001` → routes to `CPanel_RX_ButtonPacket` ✓
- Header masked to offset: stored at `0x8E4A + 0x0B = 0x8E55` ✓

## Confirmed: SwbtWr Event Structure

### Event Layout

SwbtWr events are 4-byte structures in a queue at **DRAM[0xBD3C]**:

```
Byte 0 (E): Event type
Byte 1 (D): Payload byte 1  → dispatched to DRAM[0xC07D]
Byte 2 (A): Payload byte 2  → dispatched to DRAM[0xC07E]
Byte 3 (W): Payload byte 3  → dispatched to DRAM[0xC07F]
Sentinel:   0xFF (marks end of queue)
```

Events are queued via `SwbtWr_QueueMainEvent(DE, WA)` (dsp_config_sysex.s:966-977).

### Dispatch

`SwbtWr_DispatchLoop` (dsp_config_sysex.s:891-948):
1. Reads event type (byte 0) → stored to **DRAM[0xC080]**
2. Uses type as index into a callback handler table (×4 for 32-bit pointers)
3. Stores payload bytes 1-2 to **DRAM[0xC07D]** (`stda16 49277, xwa`)
4. Stores payload byte 3 to **DRAM[0xC07F]**
5. Calls registered callback handler

**Important:** DRAM[0xC07D] contains the **event payload**, not the event type. The type goes to DRAM[0xC080].

### Data Wheel Detection

`CtrlPanel_HandleSerialPort` (main_title_ctrl_panel.s:300) checks:
```asm
cpdi8 49277, 33    ; DRAM[0xC07D] == 0x21 (payload byte 1)
```

This means a SwbtWr event must be queued with **D register = 0x21** (which becomes payload byte 1 at 0xC07D) for the data wheel to be detected. When matched, it posts event **0x1C0001F** for UI navigation.

## Confirmed: Two Separate Encoder Systems

The firmware has two independent encoder dispatch systems:

### System A: Type 2 Analog Encoders

Used for potentiometers and analog wheels. Dispatched by `CPanel_EncoderDispatch` (midi_encoder_routines.s:33) via handler jump table at **ROM 0xEDA0BC**:

| Index | ID | Handler | Controller |
|-------|----|---------|------------|
| 2 | 0x02 | Encoder_ProcessModwheel | Modulation wheel |
| 5 | 0x05 | Encoder_ProcessVolume | Volume slider |
| 25 | 0xC1 | Encoder_ProcessBreath | Breath controller |
| 26 | 0xC2 | Encoder_ProcessFoot | Foot controller |
| 27 | 0xC3 | Encoder_ProcessExpression | Expression pedal |

### System B: Encoder_ValueScanAndSync

A periodic scan-table-based system (tonegen_fileio_handlers.s:1242). Reads 3-byte entries from **DRAM[0x8E78]**, dispatches via callback tables at **ROM 0xED9C1E** (primary) or **ROM 0xED9C9E** (alternate). Entry 25 in the primary table contains params `[A9 21 00 FF]`.

### The Data Wheel

The data wheel uses **neither** of these systems for its transport — it uses segment 0x0B button packets (a third mechanism). The relationship between segment 0x0B data and these encoder systems is **unverified** (see Hypotheses below).

## Hypotheses (Unverified)

### H1: How does DRAM[0x8E55] lead to SwbtWr payload 0x21?

After `CPanel_RX_ButtonPacket` updates DRAM[0x8E55] with the new segment 0x0B data, something must queue a SwbtWr event with D=0x21. The exact code path is unknown. Candidates:

- **Path A (NAKA widgets):** The button event's changed bits go into the CPanel event queue. A NAKA widget handler registered for the data wheel area receives the event and calls `SwbtWr_QueueMainEvent` with D=0x21.
- **Path B (Encoder scan table):** `Encoder_ValueScanAndSync` reads the scan table at 0x8E78, which may reference DRAM[0x8E55]. If entry index 25 is active, it dispatches to callback table entry 25 (params `[A9 21 00 FF]`), generating the SwbtWr event.
- **Path C (Direct event processing):** Some main loop code between `CPanel_RX_ProcessOrInit` and `SwbtWr_ProcessAll` directly processes the button event queue and generates SwbtWr events.

**To verify:** Set watchpoint `wpset 0xC07D,1,w` in MAME debugger. When it triggers with value 0x21, the PC will reveal which code path writes it.

### H2: Does the scan table at 0x8E78 reference DRAM[0x8E55]?

The scan table format is 3-byte entries. If one entry contains a pointer to 0x8E55 (the data wheel byte), then System B (Encoder_ValueScanAndSync) would be the link. If not, the path must go through NAKA widgets or another mechanism.

**To verify:** Dump scan table after boot: `d 0x8E78,0x30`

### H3: Callback table entry 25 and the data wheel

Entry 25 in the primary callback table (ROM 0xED9C1E) contains `[A9 21 00 FF]`. The `0x21` here MAY be the SwbtWr payload value that ends up at DRAM[0xC07D]. But entry 25 in the handler jump table (ROM 0xEDA0BC) is labeled `Encoder_ProcessBreath` — a different controller. These tables serve different systems, and index 25 may be coincidental.

**To verify:** Breakpoint on callback table entry 25's handler address. Does it fire when the data wheel rotates?

## Main Loop Call Chain

```
MainLoop (system_handlers.s:1121)
  ├─ MidiParam_ProcessDeltas       (encoder parameter debounce)
  ├─ CPanel_RX_ProcessOrInit       (serial RX → updates DRAM[0x8E55])
  ├─ Encoder_TimingAndOutput       (encoder timing/throttle)
  ├─ ...
  ├─ Encoder_ValueScanAndSync      (scan table at 0x8E78 → callbacks)
  ├─ SwbtWr_ProcessAll             (merges post-events into main queue)
  ├─ [SwbtWr dispatch]             (via InitBank → DispatchLoop)
  │     └─ writes payload to DRAM[0xC07D]
  └─ MainTitle_PrepareAndDispatch
        └─ CtrlPanel_HandleSerialPort
              └─ checks DRAM[0xC07D] == 0x21 → posts event 0x1C0001F
```

## Key DRAM Addresses

| Address | Decimal | Name | Purpose |
|---------|---------|------|---------|
| 0x8E4A | 36426 | STATE_OF_CPANEL_BUTTONS | Button state array base |
| 0x8E55 | 36437 | Data wheel raw byte | Segment 0x0B data from MCU |
| 0x8E6A | 36458 | Derived encoder state | 0x0C=idle, 0x0D=CW, 0x0E=CCW |
| 0x8E78 | 36472 | Encoder scan table | 3-byte entries, 0xFF terminated |
| 0xBD3C | — | SwbtWr main event queue | 4-byte events + 0xFF sentinel |
| 0xC07D | 49277 | SwbtWr payload byte 1 | Written during dispatch (D register) |
| 0xC07E | 49278 | SwbtWr payload byte 2 | Written during dispatch (A register) |
| 0xC07F | 49279 | SwbtWr payload byte 3 | Written during dispatch (W register) |
| 0xC080 | 49280 | SwbtWr event type | Written during dispatch (type byte) |

## MAME Implementation

### Approach

The data wheel is implemented as an `IPT_DIAL` input with an interactive rotating knob in the layout. The HLE converts dial position deltas into segment 0x0B button packets delivered via INTA.

### Input

- **Mouse:** Click and drag the knob in the layout
- **Keyboard:** Default MAME dial keys
- **Input type:** `IPT_DIAL` with sensitivity 25, key delta 5

### HLE Mechanism

1. **Delta detection:** Button scan timer (~143 Hz) reads dial position, computes delta
2. **Direction latch:** Delta > 0 → `0x80` (CW bit 7); delta < 0 → `0x40` (CCW bit 6)
3. **Packet delivery:** Sends segment 0x0B button packet (header `0x0B`, no panel flag) via INTA
4. **Idle transition:** When encoder stops, sends `0x00` (neutral) for firmware to see idle state
5. **Boot query:** `20 0B` command returns current latch value

### Layout

Lua script rotates the encoder finger grip based on the `ENCODER` port value, providing visual feedback.

### Debug write tap

A write tap on DRAM[0xC07D] logs all writes with PC address, helping identify which code path generates the 0x21 payload at runtime.

### Branch

`kn5000_research_datawheel` (research branch)

## Verification Steps (Need MAME Debugger)

```
# 1. Watch for SwbtWr payload 0x21 — reveals which PC writes it
wpset 0xC07D,1,w

# 2. Dump encoder scan table — reveals if it references 0x8E55
d 0x8E78,0x30

# 3. Watch data wheel raw state — confirms packets arrive
wpset 0x8E55,1,w

# 4. Watch derived encoder state — confirms firmware processes bits 7-6
wpset 0x8E6A,1,w

# 5. Watch SwbtWr event type — see what type accompanies payload 0x21
wpset 0xC080,1,w
```

## Previous Approaches (Failed)

1. **Type 2 encoder packets** — Sent analog encoder packets with various IDs. Firmware processed them for MIDI CC but not as data wheel events. Wrong system entirely.
2. **Piggybacking on E0 13** — Appended encoder data to right panel poll responses. Wrong delivery mechanism.
3. **Segment 0x0B via INTA (current)** — Correct transport mechanism based on boot code analysis. Whether the firmware's steady-state processing generates SwbtWr 0x21 from this input is the open question.
