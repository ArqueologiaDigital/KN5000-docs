---
layout: page
title: Open Questions
permalink: /questions/
---

# Open Questions

Things we don't know yet and need to investigate.

## Control Panel Protocol

### Command Structure
- [ ] What is the complete list of valid command bytes?
- [ ] Are there command categories we haven't discovered?
- [ ] What determines the response length for each command?
- [ ] Are there error/retry mechanisms in the protocol?

### Button Handling
- [ ] How many buttons are there total?
- [ ] How are button banks organized?
- [ ] Is there debouncing in the MCU or main CPU?
- [ ] How are simultaneous button presses handled?

### LED Control
- [ ] How many LEDs are there total?
- [x] What is the addressing scheme? **Segment outputs SEG00-SEG15** via HD74LS07P drivers
- [ ] Can LEDs be dimmed or only on/off?
- [x] Is there multiplexing? **Yes**, MCU multiplexes via segment outputs

### Rotary Encoders
- [ ] How many encoders are there?
- [x] Absolute or relative encoding? **Relative** (quadrature: ROTA/ROTB signals)
- [ ] What is the resolution (steps per rotation)?
- [x] How is direction determined? **Quadrature decoding** of ROTA/ROTB phase relationship

## Hardware Architecture

### Control Panel MCUs
- [x] What MCU model is used? **Mitsubishi M37471M2196S** (8-bit CMOS, 740 series)
- [x] How many MCUs are on the control panel board? **2** (CPL board and CPR board)
- [ ] What is the serial baud rate?
- [x] Is it UART, SPI, or custom protocol? **UART** (M37471 has built-in serial interface)

### Inter-CPU Communication
- [ ] How do main CPU and sub CPU coordinate?
- [ ] What data passes through the latches at 0x120000?
- [ ] Are there handshaking signals?

### HDAE5000 Hard Disk Expansion
- [ ] What is the command interface via PPI at `0x160000`?
- [ ] How does it communicate file data to the keyboard?
- [ ] What is the protocol for directory listing and file loading?

## ROM Reconstruction

### Main CPU Divergences
- [ ] What instructions produce the 177 divergent bytes?
- [ ] Are they encoding issues or data issues?
- [ ] Can they be fixed in the assembler or source?

### Table Data
- [ ] What is the structure of the table data ROM?
- [ ] What file formats are embedded (images, samples)?
- [ ] How is data indexed/accessed?

## Needs Technical Documentation

These areas would benefit from official datasheets or service manuals:

- [ ] **TMP94C241F datasheet** - Full instruction encoding tables
- [ ] **HDAE5000 documentation** - Hard disk expansion interface
- [x] **KN5000 Service Manual** - ✓ Have it! (EMID971655 A5, 59 pages)
- [x] **Control panel schematic** - ✓ Analyzed pages II-35 to II-38

## Partially Understood

Things we have some info on but need verification:

### CP_Flags Usage
Some flag bits appear unused in the code we've analyzed:
- `CP_Flags_A.2` - Set by `LABEL_FC490E`/`LABEL_FC4915` but never read?
- `CP_Flags_A.4` - Never set, only tested?
- `CP_Flags_B.1`, `B.2`, `B.3`, `B.6` - Purpose unclear

### State Machine
- `CPANEL_STATE_0_TO_17` can hold values 0-17, but we don't have a complete state diagram

### Timing
- Various routines use "wait 6 ticks" or "wait 3000 loops" - what are the actual timing requirements?

---

*Last updated: January 2026*

*Have answers or new questions? Contribute to the project!*
