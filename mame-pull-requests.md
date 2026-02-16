---
layout: page
title: MAME Pull Requests
permalink: /mame-pull-requests/
---

# MAME Pull Requests for KN5000 Emulation

This page describes the planned series of pull requests to upstream MAME that implement functional emulation of the Technics KN5000 music keyboard. The changes span the TLCS-900/H CPU core, the TMP94C241 microcontroller, and the KN5000 machine driver.

> **Context**: The Technics KN5000 is a 1996 professional arranger keyboard built around dual Toshiba TMP94C241F processors (TLCS-900/H family). All firmware ROMs have been dumped and fully disassembled. A MAME skeleton driver has existed since 2024 but could not proceed beyond early boot due to missing CPU core features. These PRs fix that, bringing the driver from non-functional to fully operational with working sound program selection, control panel interaction, and MIDI I/O.
>
> **See Also**: [SubCPU Payload Loading]({{ site.baseurl }}/subcpu-payload-loading/) for the investigation that identified these issues, [Boot Sequence]({{ site.baseurl }}/boot-sequence/) for overall firmware flow, and [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) for the serial protocol implemented by the HLE.

## Dependency Graph

The PRs form a dependency chain. PR 1 and PR 2 are independent and can be reviewed simultaneously. Each subsequent PR builds on the previous.

```
PR 1 (LDC CR mapping) ──┐
                         ├── PR 3 (DMA + port fix) ── PR 4 (serial) ── PR 5 (KN5000 driver)
PR 2 (EI/RETI shadow) ──┘
```

## Overview of Changes

| PR | Scope | Files Changed | New Files | Risk Level |
|----|-------|---------------|-----------|------------|
| [1](#pr1) | TLCS-900/H core | 900tbl.hxx, dasm900.cpp, dasm900.h, tmp94c241.cpp, tmp95c061.cpp, tmp95c063.cpp, tmp96c141.cpp | --- | None (additive + structural refactor) |
| [2](#pr2) | TLCS-900/H core | 900tbl.hxx, tlcs900.cpp, tlcs900.h | --- | Low (all variants) |
| [3](#pr3) | TMP94C241 only | tmp94c241.cpp, tmp94c241.h | --- | None (TMP94C241 only) |
| [4](#pr4) | TMP94C241 only | tmp94c241.cpp, tmp94c241.h | tmp94c241_serial.cpp/h | None (TMP94C241 only) |
| [5](#pr5) | KN5000 driver | kn5000.cpp, kn5000.lay | kn5000_cpanel.cpp/h | None (KN5000 only) |

---

## PR 1: TLCS-900/H --- LDC Control Register Mapping for TMP94C241 DMA Registers {#pr1}

<div style="background: #fff3cd; border: 3px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0; font-size: 1.1em;">
<strong>&#9888;&#65039; REVIEW STATUS:</strong> All PRs on this page were drafted with AI assistance (Claude). <strong>Only this PR (PR 1) has been fully reviewed</strong> by the author (Felipe Sanches) and <a href="https://github.com/mamedev/mame/pull/14970">submitted upstream</a>. PRs 2&ndash;5 are still under human review and may be tweaked before submission.
</div>

**Branch:** [`kn5000_pr1_ldc_cr_mapping`](https://github.com/felipesanches/mame/tree/kn5000_pr1_ldc_cr_mapping)

### Summary

Add TMP94C241 DMA control register encodings to the TLCS-900/H CPU core's `LDC` instruction handler, and refactor the disassembler's CR register name resolution from hardcoded switch blocks into model-specific symbol tables.

### Problem

The `LDC` (Load Control Register) instruction uses an immediate byte to select which internal register to access. The TLCS-900/H family shares the same instruction encoding, but different chip variants place their DMA registers at different offsets within the control register space.

MAME's existing implementation only handles the TMP96C141/TMP95C061/TMP95C063 encodings:

| Register | TMP96C141/TMP95C061/TMP95C063 | TMP94C241 |
|----------|-------------------------------|-----------|
| DMAM0-3 (CR8) | 0x22, 0x26, 0x2A, 0x2E | 0x42, 0x46, 0x4A, 0x4E |
| DMAC0-3 (CR16) | 0x20, 0x24, 0x28, 0x2C | 0x40, 0x44, 0x48, 0x4C |
| DMAD0-3 (CR32) | 0x10, 0x14, 0x18, 0x1C | 0x20, 0x24, 0x28, 0x2C |

Without the TMP94C241 cases, `LDC cr,DMAMn` instructions write to a dummy register and DMA never configures correctly. This was the first bug identified in the KN5000 payload loading investigation --- the Main CPU's firmware uses `LDC` extensively to set up HDMA transfers for the 524KB SubCPU firmware payload.

Additionally, the disassembler had all variants' CR register names hardcoded in the shared `dasm900.cpp`, which doesn't scale well as new variants are added. The existing SFR symbolic names already use a model-specific table pattern --- CR register names should follow the same approach.

### Changes

- **`900tbl.hxx`**: Add TMP94C241 cases to the six existing `switch` blocks in `prepare_operands()` (three for operand 1, three for operand 2). Each block gains four new `case` entries mapping the TMP94C241 offsets to the same `m_dmam[]`, `m_dmac[]`, and `m_dmad[]` arrays. Existing TMP96C141/TMP95C061/TMP95C063 cases are unchanged.

- **`dasm900.h`**: Add a `cr_sym` struct (`{size, encoding, name}`) for model-specific control register names, a new constructor overload accepting a CR symbol table alongside the existing SFR symbol table, and a private `cr_name()` lookup helper.

- **`dasm900.cpp`**: Replace six hardcoded `switch` blocks for `O_CR8`/`O_CR16`/`O_CR32` operands (two copies --- one for operand 1, one for operand 2) with table-driven lookups via `cr_name()`. This removes all variant-specific register names from the shared disassembler code.

- **`tmp94c241.cpp`**: Define a `tmp94c241_cr_syms[]` table with TMP94C241 DMA register encodings and pass it to the disassembler constructor.

- **`tmp96c141.cpp`**, **`tmp95c061.cpp`**, **`tmp95c063.cpp`**: Move their existing DMA CR register names (previously hardcoded in `dasm900.cpp`) into model-specific `*_cr_syms[]` tables, following the same pattern.

### Risk Assessment

**None.** The CPU core change only adds new `case` entries to existing `switch` statements --- all existing cases are untouched and the new encodings do not overlap with any existing variant's register map. The disassembler refactoring is purely structural: the same register names are resolved for the same encodings, just driven by per-variant tables instead of a shared switch. No existing driver is affected.

### Design Note: Why `900tbl.hxx` Is Not Model-Specific

The disassembler's CR register names were moved to model-specific files, but the emulation-side CR register mapping in `900tbl.hxx` (`prepare_operands()`) was intentionally left as a shared switch with all variants' cases together. We considered the same model-specific split but decided against it for three reasons:

1. **Performance.** `prepare_operands()` runs on every instruction in `execute_run()` --- it is the hottest path in the CPU emulation. The compiler optimizes the `switch` into a jump table. Replacing it with virtual dispatch or a table lookup would add overhead to every LDC instruction for no functional benefit.

2. **No overlap.** The encoding values are disjoint between variants (TMP94C241 uses 0x42--0x4e for DMAM, TMP96C141 uses 0x22--0x2e). A TMP94C241 binary will never contain TMP96C141 encodings, and vice versa. Both sets of `case` entries coexist harmlessly in the same switch --- extra cases that are never reached have zero runtime cost.

3. **Alternatives are worse.** Separating the behavior would require one of: (a) virtual method dispatch per LDC instruction, (b) a runtime table search, (c) overriding the entire 2000+ line `prepare_operands()` in each variant, duplicating 99% shared logic, or (d) an `if (type() == TMP94C241)` guard before variant-specific switch blocks, which adds a runtime branch on every LDC and duplicates the shared DMAS0--3 cases into both branches. None of these improve correctness, and all add complexity or overhead.

The encoding byte itself acts as an implicit variant discriminator --- a TMP94C241 binary will never emit encoding `0x22` for DMAM0, so the TMP96C141 case for `0x22` is simply never reached when running TMP94C241 firmware. The compiler merges all cases into a single jump table where unreachable entries cost nothing. Each `case` in the source is annotated with a comment identifying which variant(s) use that encoding, making the shared switch self-documenting.

The disassembler refactoring was worthwhile because disassembly is not performance-critical and the model-specific symbol table pattern was already established. For the instruction decoder, extra `case` entries in a shared switch are the idiomatic MAME approach for handling variant differences in the TLCS-900 core.

### Datasheet Reference

The TMP94C241 control register map is documented in the Toshiba TMP94C241F Data Sheet, Section 5 "DMA Controller", Table 5-1 "DMA Register Map". The offsets differ from TMP96C141 because the TMP94C241 has a larger internal register file with additional peripheral blocks occupying the 0x20-0x3F range.

---

## PR 2: TLCS-900/H --- EI/RETI Interrupt Acceptance Shadow {#pr2}

**Branch:** [`kn5000_pr2_irq_inhibit`](https://github.com/felipesanches/mame/tree/kn5000_pr2_irq_inhibit)

### Summary

Implement the documented 1-instruction interrupt deferral after `EI` and `RETI` instructions, matching real TLCS-900/H hardware behavior.

### Problem

Per the Toshiba TLCS-900/H Programming Manual (Section 8.2 "Interrupt Processing"), interrupt acceptance is inhibited for one instruction following `EI` or `RETI`. This is an architectural feature of the TLCS-900/H family, not specific to any single variant.

Without this deferral, the common firmware pattern:

```asm
EI 0        ; Enable all interrupt levels
NOP         ; This MUST execute before any IRQ is accepted
EI 6        ; Restrict to level 6+ only
```

fails because `EI 0` immediately triggers a pending interrupt before `NOP` executes. The interrupt handler runs, returns via `RETI`, and the CPU re-enters the handler infinitely --- `EI 6` never executes, and the CPU is stuck.

This pattern appears extensively in the KN5000 firmware (hundreds of occurrences) and likely in other TLCS-900/H firmware as well. The real hardware's 1-instruction shadow prevents this problem.

### Changes

- **`tlcs900.h`**: Add `bool m_irq_inhibit` member to `tlcs900_device` (the base class for all TLCS-900/H variants).

- **`tlcs900.cpp`**:
  - Register `m_irq_inhibit` in `device_start()` for save states.
  - Initialize to `false` in both `tlcs900_device::device_reset()` and `tlcs900h_device::device_reset()`.
  - In `execute_run()`: when `m_check_irqs` is set and `m_irq_inhibit` is true, clear the inhibit flag but skip the IRQ check for this cycle. On the next iteration (after one instruction has executed), the IRQ check proceeds normally. If `m_check_irqs` is not set, clear `m_irq_inhibit` unconditionally.

- **`900tbl.hxx`**: Set `m_irq_inhibit = true` in `op_EI()` and `op_RETI()`.

### Risk Assessment

**Low.** This change affects all TLCS-900/H variants (TMP96C141, TMP95C061, TMP95C063, TMP94C241). It is documented hardware behavior, and the implementation is minimal (a single boolean flag). If any existing driver were relying on the incorrect immediate-acceptance behavior (e.g., using `EI` without a guard `NOP`), it could see a timing change. However, real hardware has always had this shadow, so any such driver was already accidentally working.

Drivers using TLCS-900/H variants that should be regression-tested:
- `ngp` (Neo Geo Pocket --- TMP95C061)
- `zorba` (Zorba portable --- TMP95C063)

### Datasheet Reference

Toshiba TLCS-900/H Programming Manual, Section 8.2: "After the EI instruction or RETI instruction is executed, the interrupt acceptance is inhibited for one instruction period."

---

## PR 3: TMP94C241 --- DMA Subsystem (HDMA + DMAR) and Port Read Fix {#pr3}

**Branch:** [`kn5000_pr3_dma_and_port`](https://github.com/felipesanches/mame/tree/kn5000_pr3_dma_and_port)

**Depends on:** PR 1 + PR 2

### Summary

Implement the TMP94C241's complete DMA subsystem and fix the port read behavior to match real hardware.

### Problem

The existing TMP94C241 device in MAME has empty stubs for `tlcs900_check_hdma()` and no DMA transfer logic. The KN5000's Main CPU relies heavily on DMA for two critical operations:

1. **HDMA (Hardware DMA)**: Triggered by interrupt events. The Main CPU uses HDMA to transfer the 524KB SubCPU firmware payload. Each time the SubCPU acknowledges a byte via INT5, the HDMA engine automatically transfers the next byte without CPU intervention. Nine bulk transfers (5x 64KB config blocks + 4 payload blocks) use this mechanism.

2. **DMAR (Software DMA)**: Triggered by writing to SFR register 0x109. The SubCPU uses DMAR to receive inter-CPU command bytes --- each INT0 event triggers one DMAR write, transferring a single byte from the latch at `0x120000` to RAM. This is how the SubCPU receives sound program change commands, mixer settings, and other real-time data from the Main CPU after boot.

Additionally, `port_r()` always returned the external pin level, but real TMP94C241 hardware returns the output latch value for bits configured as output. Firmware that reads back its own output port state (a common pattern for read-modify-write operations) got wrong values.

### Changes

- **`tmp94c241.h`**:
  - Move the interrupt register enum (`INTE45`, `INTE67`, ..., `INTNMWDT`) from the `.cpp` file to the header. This makes the enum accessible to the serial sub-device (PR 4) for setting interrupt flags.
  - Add declarations for `tlcs900_process_hdma()`, `tlcs900_process_software_dma()`, and `dmar_w()`.

- **`tmp94c241.cpp`**:
  - **`tlcs900_process_hdma(channel)`**: Implements one HDMA transfer for a channel. Looks up the channel's DMA start vector, checks if the corresponding interrupt flag is pending (the DMA trigger condition), performs one transfer according to the DMAM mode register, decrements the transfer count, and fires INTTC on completion. Clears the triggering interrupt flag after the transfer (consuming the interrupt instead of dispatching to the handler).
  - **`tlcs900_process_software_dma(channel)`**: Same transfer logic as HDMA but triggered by DMAR register writes instead of interrupt events. One write = one transfer unit.
  - **`tlcs900_check_hdma()`**: Checks all four channels in priority order (0 highest). Only processes one transfer per call to maintain correct timing. Skips processing when all interrupts are masked.
  - **`tlcs900_check_irqs()`**: Added HDMA priority --- interrupts targeted by active HDMA channels are skipped (consumed by DMA instead of dispatching to the interrupt handler). Added INT0 level-detect re-assertion for level-triggered interrupt mode. Added `debug()->interrupt_hook()` for MAME debugger integration.
  - **`dmar_w()`**: Handler for SFR 0x109 writes. Each set bit triggers one software DMA transfer on the corresponding channel.
  - **`port_r()`**: Now returns `(latch & direction) | (external & ~direction)`, correctly mixing output latch bits with external pin levels based on the port control register.
  - **DMAM decoding**: Uses switch-based transfer mode decoding (byte/word/long, increment/decrement/fixed) matching the proven TMP95C061 implementation already in MAME.

### Risk Assessment

**None.** All changes are within the TMP94C241 device. No other TLCS-900/H variant or driver is affected.

### Datasheet Reference

TMP94C241F Data Sheet:
- Section 5.1 "HDMA Operation" --- interrupt-triggered DMA with priority over normal interrupt dispatch
- Section 5.2 "DMAR Register" --- software DMA trigger at SFR 0x109
- Section 5.3 "DMAM Register" --- transfer mode encoding (bits 4:0)
- Section 9.2 "Port Read Operation" --- output latch vs. external pin multiplexing based on PxCR

---

## PR 4: TMP94C241 --- Serial Port Sub-Device {#pr4}

**Branch:** [`kn5000_pr4_serial`](https://github.com/felipesanches/mame/tree/kn5000_pr4_serial)

**Depends on:** PR 3

### Summary

Replace the inline serial port stubs with a proper sub-device implementation supporting synchronous I/O interface mode, baud rate generation, TX double buffering, and data callbacks for connecting external devices.

### Problem

The existing TMP94C241 serial implementation consists of inline stubs that immediately set the TX-complete interrupt flag on every write to `SCxBUF`. This was sufficient for early bringup but cannot support any real serial communication. The KN5000 uses both serial channels:

- **Serial Channel 0**: MIDI In/Out at 31.25 kbaud (standard MIDI rate). Uses UART mode with the baud rate generator.
- **Serial Channel 1**: Control panel communication at ~500 kHz using synchronous I/O interface mode. The Main CPU exchanges button/LED/encoder data with the control panel MCU (whose ROM is not dumped) via a clocked serial protocol.

### Changes

- **`tmp94c241_serial.h`** (new file): Device class for `tmp94c241_serial_device`. Exposes:
  - `txd()`, `rxd()`, `sclk_out()`, `sclk_in()` callbacks for connecting to external devices
  - `tx_start()` callback signaling the start of each byte transmission (with PFFC pin function state, allowing connected devices to distinguish real transmissions from phantom ones during pin reconfiguration)
  - SFR register accessors: `scNbuf_r/w`, `scNcr_r/w`, `scNmod_r/w`, `brNcr_r/w`

- **`tmp94c241_serial.cpp`** (new file): Full implementation:
  - **I/O interface mode** (SCxMOD bits 1:0 = 0): Synchronous clocked serial. Supports internal clock (baud rate generator) and external clock (IOC=1) sources. Data is shifted MSB-first on clock edges.
  - **Baud rate generator**: Configurable via BRxCR register with 4-bit divisor and clock source selection. Drives a timer that toggles SCLK at the configured rate.
  - **TX double buffering**: CPU writes to SCxBUF go to the TX buffer. If the shift register is idle, the buffer auto-transfers immediately. If the shift register is busy, the buffer holds data until the current byte finishes, then auto-loads on the trailing rising edge. This matches real TMP94C241 hardware behavior and prevents byte loss during back-to-back transmissions.
  - **TX/RX shift registers**: 8-bit shift with proper edge timing. TX pre-outputs bit 0 before the first clock edge so the receiver can sample it on the rising edge. RX samples on rising edges and fires INTRX when 8 bits are received.
  - **SCLK output**: Forwarded to connected devices via callbacks, enabling clocked protocols.
  - **TO2 trigger**: Timer 1 match events are forwarded to serial channels for mode 0 transfer gating.

- **`tmp94c241.cpp`**: Replace inline serial stubs with sub-device delegation. Serial register mappings in `internal_mem()` now route to `m_serial[0]` and `m_serial[1]`. Add `device_add_mconfig()` to instantiate the two serial sub-devices. Set TX-complete flags (`INTES0`/`INTES1` bit 7) at `device_reset()` to indicate empty TX buffers at power-on.

- **`tmp94c241.h`**: Add `#include "tmp94c241_serial.h"`, friend declaration, `device_add_mconfig()` override, `required_device_array<tmp94c241_serial_device, 2> m_serial`. Remove old inline serial member variables (`m_serial_control`, `m_serial_mode`, `m_baud_rate`).

### Risk Assessment

**None.** All changes are within the TMP94C241 device and its new sub-device. No other driver is affected. The sub-device's callbacks are optional --- if not connected by a driver, they are no-ops, preserving backward compatibility.

### Datasheet Reference

TMP94C241F Data Sheet:
- Section 7 "Serial Interface" --- I/O interface mode, UART mode, baud rate generator
- Section 7.3 "Baud Rate Generator" --- divisor and clock source configuration
- Section 7.4 "Transmit/Receive Operation" --- shift register timing, double buffering
- Table 7-1 "Serial Control Register (SCxCR)" --- IOC, SCLKS, error flags

---

## PR 5: KN5000 Driver --- Control Panel HLE, SubCPU Payload Transfer, Keybed HLE {#pr5}

**Branch:** [`kn5000_pr5_driver`](https://github.com/felipesanches/mame/tree/kn5000_pr5_driver)

**Depends on:** PR 4

### Summary

Rework the KN5000 machine driver from a non-functional skeleton to a working system that boots to normal operation with sound program selection, control panel interaction, and MIDI I/O.

### Problem

The existing KN5000 driver defines the basic hardware layout (two TMP94C241 CPUs, ROM regions, LCD) but cannot proceed past early boot because:

1. The firmware validates backup SRAM contents and enters diagnostic mode if validation fails (NVRAM is empty on first run).
2. The SubCPU memory map lacks mappings for the tone generator, DSP, inter-CPU latch, and waveform RAM, causing unmapped memory accesses.
3. No scheduling synchronization between CPUs, making the latched inter-CPU communication unreliable.
4. The control panel MCU ROM is not dumped, so the serial protocol to the panel has no responder.
5. No keybed input mechanism exists.

### Changes

- **`kn5000.cpp`** (major rework):
  - **NVRAM factory defaults**: Seeds the 32KB backup SRAM from the program ROM's factory default region (`0xEF3AC8`). On real hardware, this data is written during factory programming. In MAME, the NVRAM starts empty, so the firmware's validation checksum fails and it enters a diagnostic loop. Seeding from the ROM image allows normal boot to proceed. On subsequent runs, the NVRAM file persists with any user changes.
  - **SubCPU memory map**: Maps the tone generator registers at `0x100000`/`0x100002` (IC303, TC183C230002), tone generator keyboard scanning at `0x110000`/`0x110002`, the inter-CPU latch at `0x120000`, DSP registers at `0x130000`/`0x130002`, and 4MB waveform RAM at `0x200000`-`0x5FFFFF`. These are stub handlers that log accesses and return appropriate idle values.
  - **Inter-CPU latch**: Read/write handlers with logging and `machine().scheduler().perfect_quantum(attotime::from_usec(100))` on writes. The perfect quantum ensures both CPUs see latch updates atomically, which is critical for the HDMA-based payload transfer where the Main CPU writes a byte to the latch and the SubCPU's HDMA must read it before the next byte arrives.
  - **MIDI ports**: Serial channel 0 of both CPUs is wired to `midi_port` devices for standard MAME MIDI I/O integration.

- **`kn5000_cpanel.cpp`** (new file): Control panel HLE implementing the serial protocol between the Main CPU and the control panel MCU. The control panel MCU's ROM is not dumped, so HLE is the only option. Key features:
  - **INTA-driven sessions**: The panel asserts INTA to request attention, then exchanges button/LED data via synchronous serial on channel 1. Each session consists of 8 segments of 8 bytes each (64 bytes total), carrying button states inbound and LED states outbound.
  - **Button mapping**: 85+ buttons mapped to MAME input ports, organized by panel region (transport, sound selection, accompaniment, registration, numeric pad, etc.).
  - **LED output routing**: LED states received from the firmware are routed to MAME layout output elements, enabling the layout to display button backlighting.
  - **Rotary encoder input**: Tempo, volume, and data entry encoders generate delta values in the protocol format expected by the firmware.

- **`kn5000_cpanel.h`** (new file): Header for the control panel HLE device class.

- **`kn5000.lay`**: LED output element names updated to match the names emitted by the control panel HLE, enabling proper LED visualization.

### Result

With all five PRs applied, the KN5000 driver:
1. Boots from power-on through the complete boot sequence (ROM validation, SubCPU payload transfer, hardware initialization)
2. Displays the main screen with voice names (Piano, Bigband Brass, Modern E.P.1), rhythm patterns, and mixer levels
3. Responds to control panel buttons for sound selection, menu navigation, and parameter editing
4. Accepts MIDI input for external control
5. SubCPU processes inter-CPU commands in real-time (no "Sound Name Error" messages)

### Risk Assessment

**None.** All changes are within the KN5000 driver and its new HLE device. No other driver or shared code is affected.

---

## Testing Notes

The complete change set has been tested with the following ROM set:

- `kn5000_v10_program.ic9` (Main CPU, 2MB)
- `kn5000_subcpu_boot.ic30` (SubCPU boot ROM, 128KB)
- `kn5000_table_data.ic8` (Table data, 2MB)
- `kn5000_waverom1.ic5` through `kn5000_waverom4.ic2` (Wave ROM, 4x 8MB)

**Test scenarios verified:**
- Cold boot with empty NVRAM (factory defaults are seeded)
- Warm boot with existing NVRAM (user settings preserved)
- SubCPU payload transfer (524KB via HDMA, all 9 transfer blocks complete)
- Sound program selection via control panel buttons
- Menu navigation (display updates correctly)
- MIDI note input
- Keybed note input (when assigned via MAME input configuration)
