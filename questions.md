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
- [ ] What do the 4 LED packet types (bits 4-5) represent? (Handlers at 0xFC6C80+ undisassembled)
- [x] LED packet format? **Bits 4-5 select handler, bits 5-0 = row, bits 7-6 = panel select**

### Rotary Encoders
- [ ] How many encoders are there? (Firmware supports 32 IDs, only 2 have handlers)
- [x] Absolute or relative encoding? **Relative** (quadrature: ROTA/ROTB signals)
- [ ] What is the resolution (steps per rotation)?
- [x] How is direction determined? **Quadrature decoding** of ROTA/ROTB phase relationship
- [x] Encoder ID encoding? **5-bit ID from bits 0-2 and 6-7 of packet byte 0**
- [ ] Which physical encoders map to IDs 2 and 5? (Only IDs with handlers)

## Hardware Architecture

### Control Panel MCUs
- [x] What MCU model is used? **Mitsubishi M37471M2196S** (8-bit CMOS, 740 series)
- [x] How many MCUs are on the control panel board? **2** (CPL board and CPR board)
- [x] What is the serial baud rate? **250 kHz normal operation, 31.25 kHz during init** (fc/16/4 and fc/64/8)
- [x] Is it UART, SPI, or custom protocol? **UART** (M37471 has built-in serial interface)

### Inter-CPU Communication
- [x] How do main CPU and sub CPU coordinate? **Command/response via latch at 0x120000, DMA for bulk transfers**
- [x] What data passes through the latches at 0x120000? **Commands (E1/E2/E3/00-1F), response bytes, status flags**
- [x] Are there handshaking signals? **Yes: status flags at 0x04FE (bit 6=payload ready, bit 7=xfer complete)**

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
- `CPANEL_TX_RX_FLAGS.2` - Set by `CPanel_RX_ProcessWithFlag`/`CPanel_RX_Process` but never read?
- `CPANEL_TX_RX_FLAGS.4` - Never set, only tested?
- `CPANEL_PROTOCOL_FLAGS.1`, `.2`, `.3`, `.6` - Purpose unclear

### State Machine
- `CPANEL_PACKET_BYTE_COUNT` can hold values 0-17, tracking expected bytes in multi-byte transfers
- See [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) for complete state machine diagram

### Multi-byte Packets (Types 6, 7)
- Complex decoding in `CPanel_RX_MultiBytePacket` (0xFC4A40)
- Byte count = `(byte0 & 0x0F) + 1`
- Bit 4 used for mode selection
- Purpose and expected data format unknown

### Timing
- Various routines use "wait 6 ticks" or "wait 3000 loops" - what are the actual timing requirements?

### Undisassembled Code
- LED packet handlers at 0xFC6C80 (~112 bytes of raw data)
- Several routines called from LED/encoder paths need disassembly

---

*Last updated: January 2026*

*Have answers or new questions? Contribute to the project!*
