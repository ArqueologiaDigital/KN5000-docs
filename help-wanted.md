---
layout: page
title: Help Wanted
permalink: /help-wanted/
---

# How You Can Help

This is a community reverse engineering project. Here's how you can contribute:

**Current Progress:** Main CPU ROM at 99.99% (177 bytes), Sub CPU Boot at **100%**, Sub CPU Payload at **100%**. See the [Project Issues]({{ site.baseurl }}/issues/) page for many open tasks organized by category.

## High Priority

### ROM Dumps Needed

We're missing ROM dumps for several chips:
- **Control Panel MCUs** (Mitsubishi M37471M2196S) - Custom-masked ROMs handling buttons, LEDs, and rotary encoders. These would require decapping to dump.
- **Any other undumped chips** on the KN5000 board

If you have a KN5000 and can dump ROMs, please reach out!

### Main CPU ROM (99.99% match)

The Main CPU ROM has only 177 bytes remaining. Analysis needed to identify and fix the remaining divergences, which may be due to instruction encoding differences between TMP94C241F and TMP96C141 (what ASL supports).

### HDAE5000 ROM Disassembly

The HD-AE5000 hard disk expansion ROM has been partially analyzed but needs complete disassembly:

**Known Entry Points:**
- Boot initialization at 0x28F576 (called via JP at 0x280008)
- Frame handler at 0x28F662 (called via JP at 0x280010)

**Analysis Tasks:**
- Disassemble PPORT command handlers (15 commands documented)
- Document FSB (File System Block) structure
- Trace HD controller communication routines
- Analyze Windows DLL callback interfaces
- Document file transfer protocol details

**Skills Needed:** TLCS-900 assembly, parallel port protocols, filesystem analysis

See [HDAE5000 page]({{ site.baseurl }}/hdae5000/) for current findings.

### Assembly Analysis

Help analyze the disassembled code:
- Trace execution paths through undocumented routines
- Document serial protocol command/response patterns
- Map button/LED indices to physical panel locations
- Identify data structures and their purposes

### Testing

If you have a working KN5000:
- Test homebrew code on real hardware
- Capture serial protocol traces with logic analyzer
- Document hardware behavior for edge cases
- Take photos of PCB for chip identification

## Medium Priority

### Documentation

- Improve code comments in the disassembly
- Write tutorials for new contributors
- Translate documentation to other languages
- Create diagrams of system architecture

### MAME Development

- Help implement HLE for control panel MCUs
- Test emulation accuracy
- Debug emulation issues
- Improve audio emulation

### Tooling

- Extend ASL Macro Assembler support for TMP94C241F-specific instructions
- Create visualization tools for protocol analysis
- Build comparison/diff tools for ROM analysis

## Contribution Guidelines (STRICT POLICIES)

These policies ensure the disassembly remains useful for understanding the firmware, not just rebuilding it.

### Symbolic Cross-Referencing

**All cross-references must be symbolic (using labels), never numeric addresses.**

```asm
; WRONG - numeric address
CALL 0F97544h
LDA XIX, 0E46312h

; CORRECT - symbolic label
CALL FDC_DRIVE_DETECT
LDA XIX, FONT_METRICS_TABLE
```

**Meaningful names are STRONGLY preferred:**
- Use descriptive names: `FDC_SEND_COMMAND`, `LED_CONTROL_DISPATCH`, `MIDI_EVENT_HANDLER`
- `LABEL_XXXXXX` style names are a **last resort** for completely unknown code/data
- When you discover what a `LABEL_*` does, rename it immediately

**Naming conventions:**
- Routines: VerbNoun (`SendCommand`, `InitHardware`)
- Data tables: NOUN_TABLE (`FONT_METRICS_TABLE`)
- Constants: NOUN (`SYSTEM_TIMESTAMP`)
- Flags: NOUN_FLAG (`PAYLOAD_LOADED_FLAG`)

### Binary Include Splitting

**When code references an address inside a binary include (not the first address), the binary must be split.**

This ensures cross-references are symbolic and binary files become smaller for analysis.

**Example:** If `data.bin` covers 0xE02510-0xE06BAF and code references 0xE04000:
1. Split the binary at 0xE04000
2. Replace one `binclude` with two, each with a proper label
3. Remove old binary, add new binaries to git
4. Verify build still produces identical ROM

### Disassembly Quality

- **Prefer disassembled code over raw bytes** - Raw `db` sequences are last resort
- **Never sacrifice readability** for byte-matching
- **Document everything** - Comments, labels, and clear structure

See `CLAUDE.md` in the repository for complete policy details.

## Getting Started

1. Clone the [ROM disassembly repo](https://github.com/ArqueologiaDigital/kn5000-roms-disasm)
2. Read the `CLAUDE.md` for build instructions and **contribution policies**
3. Browse the [Project Issues]({{ site.baseurl }}/issues/) to find tasks you can help with
4. Check the [Open Questions]({{ site.baseurl }}/questions/) for areas needing investigation
5. Join the [discussion forum](https://forum.fiozera.com.br/t/technics-kn5000-homebrew-development/321)

## Long-Term Goals

### Higher-Level Compiler

We envision eventually porting a higher-level compiler to target the TMP94C241F (TLCS-900/H2) CPU, enabling C or C++ development for the KN5000 instead of assembly-only programming.

**Potential approaches:**
- **LLVM backend** - Create a new LLVM target for TLCS-900
- **GCC port** - Port GCC to generate TLCS-900 code
- **SDCC extension** - Extend Small Device C Compiler

This is a significant undertaking requiring compiler development expertise. If you have experience with LLVM backends or retargeting compilers, we'd love to hear from you.

## Skills We Need

- **Assembly programming** (TLCS-900 or similar)
- **Reverse engineering** experience
- **MAME/emulator development**
- **Hardware hacking** (ROM dumping, logic analysis)
- **C++ programming** (for MAME HLE devices)
- **Technical writing** (documentation)
- **Compiler development** (LLVM, GCC) - for long-term goals

## Contact

Reach out to Felipe Sanches to coordinate contributions.
