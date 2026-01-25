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
- [ ] What is the addressing scheme?
- [ ] Can LEDs be dimmed or only on/off?
- [ ] Is there multiplexing?

### Rotary Encoders
- [ ] How many encoders are there?
- [ ] Absolute or relative encoding?
- [ ] What is the resolution (steps per rotation)?
- [ ] How is direction determined?

## Hardware Architecture

### Control Panel MCUs
- [ ] What MCU model is used? (chip marking/datasheet)
- [ ] How many MCUs are on the control panel board?
- [ ] What is the serial baud rate?
- [ ] Is it UART, SPI, or custom protocol?

### Inter-CPU Communication
- [ ] How do main CPU and sub CPU coordinate?
- [ ] What data passes through the latches at 0x120000?
- [ ] Are there handshaking signals?

### Audio Processor (HDAE5000)
- [ ] What is the command interface via PPI?
- [ ] How is audio data transferred?
- [ ] What synthesis capabilities does it have?

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
- [ ] **HDAE5000 documentation** - Audio processor interface
- [ ] **KN5000 Service Manual** - Board layout, chip identification
- [ ] **Control panel schematic** - MCU connections and signals

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
