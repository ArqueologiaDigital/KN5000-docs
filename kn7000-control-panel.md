---
layout: page
title: KN7000 Control Panel Protocol
permalink: /kn7000-control-panel/
---

# KN7000 Control Panel Protocol

The KN7000's front panel — its dozens of buttons, the data dial, and the LEDs
that light under them — is not wired directly to the main CPU. Instead it is
**scanned by a set of dedicated panel sub-CPUs**, which report switch presses to
the MN10300 main CPU and drive the LEDs on its behalf. This distributes the
tedious matrix scanning off the main CPU and matches the KN5000's arrangement
(with a different number of sub-CPUs). This page documents the panel from the
firmware (`kn7000_program.rom`) — the sub-CPUs, how input becomes events, and the
LED/dial control — grounded in the service-test screens and the named handlers.

## The panel sub-CPUs

The service-test "PANEL CPU CHECKING" / "PANEL SW&LED CHECK" screens enumerate
**four panel sub-CPUs**, each responsible for one region of the control surface:

| Sub-CPU | Region (inferred from the naming) |
|---------|-----------------------------------|
| **CPL** | panel **L**eft |
| **CPC** | panel **C**entre |
| **CPR** | panel **R**ight |
| **CPSD** | a fourth panel/slider–display group |

Each scans its own switch matrix and drives its own LEDs; the test mode lights
them group by group (`CPL LEDS to light`, `CPC LEDs to light`, `CPR LEDs to
light`, `CPSD`) and asks the operator to *"Push each button and check the LED"*.
The go/no-go results are surfaced by `PanelCPL_OKNG` / `PanelCPR_OKNG` (and
siblings) and the panel firmware itself can be reflashed (`PanelFlashFunc`),
which is why the test reports "CPU of CPL =" / "CPU of CPR =" as live devices
rather than fixed logic.

## Switch input → events

When a sub-CPU reports a switch change, the main CPU turns it into a MILK
[event](/kn7000-event-system/) delivered to the focused object. The panel input
events form a recognisable family:

* **general switches** — `EV_SWON`, `EV_SWOFF`, `EV_SWBOTH`, `EV_ASSSWB`
* **index switches** (the up/down/page navigation keys) — `EV_INDEXSW_UP`,
  `EV_INDEXSW_DOWN`, `EV_INDEXSW_ON`, `EV_INDEXSW_OFF`, `EV_INDEXSW_BOTH`,
  `EV_INDEXSELECT`, plus the AIC and dial-combined variants
  (`EV_INDEXSW_UP_AIC`, `EV_INDEXSW_DOWN_DIAL`, …)
* **the data dial** — `EV_DIAL`, `EV_DIALUP`, `EV_DIALDOWN`,
  `EV_CHANGEDIALFOCUS`

So a button press is a hardware scan on a sub-CPU → a report to the main CPU →
an `EV_SW*` event → the current widget's `…Proc` handler (which typically
switches on `EV_ACTION` / `EV_SWON`).

## The data dial

The rotary data dial is a first-class input: it emits `EV_DIALUP` / `EV_DIALDOWN`
ticks and `EV_DIAL` value changes, and the currently-focused control claims it
via `EV_CHANGEDIALFOCUS`. The firmware programs the dial's behaviour for the
active field through `SetProgDial` (`0x48417609`) and `SetDialFocus` /
`SetDialEnable` / `SetDialUp`, with the low-level step logic in `DialUpDownOp`
(`0x4847AC2F`). This is how one physical encoder edits whatever parameter the
cursor is on.

## LEDs

The panel LEDs are set through small helpers that the main CPU calls and the
sub-CPUs execute: `SetHoldLed` (`0x48416512`), `SetOtherPartLed` (`0x484164F4`),
and the part/track indicator sets. Because the LEDs sit under the buttons and are
driven by the same sub-CPU that scans them, the "SW&LED CHECK" test can verify a
whole section's matrix in one pass.

## Hardware path & serial protocol

The service-manual schematics (SX-KN7000, *SCHEMATIC DIAGRAM-15* "CPL CIRCUIT")
pin this down. **Each panel PCB carries its own 8-bit microcomputer** — on the
CPL board it is **IC1101 = C0BDB646823** (with crystal X1101) — and that sub-CPU
does the local work:

* it **scans an 8×8 switch matrix** — eight strobe lines `SW0…SW7` against eight
  sense columns `SEG0…SEG7`, each cell a diode + a momentary switch (`EVQ2140SR`),
  so up to 64 buttons per board;
* it **drives an LED matrix** through a **74LS138 (IC1102) 3-to-8 decoder** plus
  transistor rows and buffers (IC1103), the LEDs sitting under the buttons;
* it talks to the main CPU over a **synchronous serial link** — the pins
  **`SIN`, `SOUT`, `CLK`, `RST`, `CNTR1`** (data in, data out, shared clock,
  reset, and a control/attention line). CPL chains to the CPR board and on to the
  main board.

On the **main-CPU side** the link is **one channel of a multi-channel USART/SIO
ASIC** in the `0x34000000` bank at base **`0x34000800`** — traced register by
register from the firmware:

| Register | Role |
|----------|------|
| `0x34000800` | channel config/direction (low 3 bits: `\|0x07` = RX+clear, `\|0x04` = TX) |
| `0x34000804` | channel control (set at init `0x484ABCBA`) |
| `0x34000808` | **TX data** — LED/command bytes *out* to the sub-CPUs |
| `0x34000809` | **RX data** — switch/panel bytes *in* |
| `0x3400080C` | channel status |
| `0x34000168` | interrupt-control register (ICR) for the channel |

The link is **interrupt-driven and half-duplex** (the same channel carries LEDs
out and switches in):

1. an **RX interrupt** enters ISR `0x484ACC13`, which does the GPIO handshake,
   re-arms the config, acks the ICR, and reads **one byte** from `0x34000809`;
2. the byte is pushed into a **92-byte ring buffer** at `0x5006BDB4` (head
   `0x5006BDB2`, tail `0x5006BDB0`, data-ready = bit 0 of `0x5006BDA4`);
3. a **frame-decoder task** (`0x484AD111`) drains the ring, reads a **header**
   byte and extracts a **3-bit message type** (`(hdr & 0x38) >> 3`), then pulls
   the following switch/parameter bytes;
4. each switch byte is dispatched through `0x484AD680`, which forms an index
   `(b & 0xC0) >> 3 | (b & 0x07)` into a **32-entry jump table at `0x48613108`** —
   the four panel groups (CPL/CPC/CPR/CPSD) × sub-codes;
5. decoded changes are edge-detected and emitted as `EV_SW*`/`EV_INDEXSW_*`/
   `EV_DIAL` events via `SendEvent` (`0x48429388`).

LED output rides the **same channel**: `SetHoldLed`/`SetOtherPartLed` →
`SetLedByIndex` (`0x484B1BCB`, a jump table at `0x4861518C`) accumulate bits into
a RAM shadow, and the **TX path `0x484ABF50`** flushes a byte to `0x34000808`
after switching direction. The `0x36008004`/`0x36008024`/`0x36008064` GPIO lines
strobe/select which sub-CPU is on the shared bus.

This is the **same serial-panel design the KN5000 uses** (its MAME driver models
it with a `cpanel` HLE device) — the KN7000 has four sub-CPUs on one channel
instead of two. Note that the **sibling SIO channels at `0x34000810` and
`0x34000820` are the two MIDI ports**, not the panel — an identical channel
layout at `+0x10` stride, which is what confirms `0x34000800` as the panel link.

## Relationship to the KN5000

Distributed panel scanning by dedicated sub-CPUs, the switch-to-event flow, and
the data-dial focus model are **shared with the KN5000**
([Shared Codebase Map](/technics-shared-codebase/), [Control panel
protocol](/control-panel-protocol/)). The KN7000-specific detail observed here is
the set of **four** sub-CPUs (CPL/CPC/CPR/CPSD) and their concrete test-mode and
handler names.
