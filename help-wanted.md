---
layout: page
title: Help Wanted
permalink: /help-wanted/
---

# How You Can Help

This is a community reverse engineering project. Here's how you can contribute:

## High Priority

### ROM Dumps Needed

We're missing ROM dumps for several chips:
- **Control Panel MCUs** - The MCUs handling buttons, LEDs, and rotary encoders
- **Sub CPU Boot ROM** (`kn5000_subcpu_boot.ic30`) - Need to verify/update source
- **Any other undumped chips** on the KN5000 board

If you have a KN5000 and can dump ROMs, please reach out!

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

- Improve the custom assembler (tlcs900asm)
- Create visualization tools for protocol analysis
- Build comparison/diff tools for ROM analysis

## Getting Started

1. Clone the [ROM disassembly repo](https://github.com/user/kn5000-roms-disasm)
2. Read the `CLAUDE.md` for build instructions
3. Check the [open questions](questions.html) for areas needing investigation
4. Join the [discussion forum](https://forum.fiozera.com.br/t/technics-kn5000-homebrew-development/321)

## Skills We Need

- **Assembly programming** (TLCS-900 or similar)
- **Reverse engineering** experience
- **MAME/emulator development**
- **Hardware hacking** (ROM dumping, logic analysis)
- **C++ programming** (for MAME HLE devices)
- **Technical writing** (documentation)

## Contact

Reach out to Felipe Sanches to coordinate contributions.
