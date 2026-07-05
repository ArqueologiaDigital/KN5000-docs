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

## Hardware path

The main CPU reaches the panel through the low `0x34000000` I/O bank — the
largest MMIO block, shared with the [display](/kn7000-display-subsystem/) and key
scan — and the `0x36008000` bit-mapped control/GPIO port (chip selects and
strobes; register `0x36008004` is toggled heavily during I/O). The exact serial
or parallel framing between the main CPU and each sub-CPU is not yet traced from
the disassembly; what is established is the *logical* protocol above (four
scanning sub-CPUs, switch-to-event mapping, dial and LED control). See the
[I/O register map](/kn7000/#io-register-map-from-firmware-analysis).

## Relationship to the KN5000

Distributed panel scanning by dedicated sub-CPUs, the switch-to-event flow, and
the data-dial focus model are **shared with the KN5000**
([Shared Codebase Map](/technics-shared-codebase/), [Control panel
protocol](/control-panel-protocol/)). The KN7000-specific detail observed here is
the set of **four** sub-CPUs (CPL/CPC/CPR/CPSD) and their concrete test-mode and
handler names.
