---
layout: home
title: Home
---

# Technics KN5000 Reverse Engineering Project

This project aims to fully document and emulate the Technics KN5000 music keyboard through:

- **ROM Reconstruction** - Achieving 100% byte-matching rebuilds from disassembled source
- **MAME Emulation** - Enabling the keyboard to run in the MAME emulator
- **Homebrew Development** - Creating custom software for the real hardware

## Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| Main CPU ROM | 99.99% | 177 bytes remaining |
| Sub CPU ROM | Needs rebuild | Source exists |
| Table Data ROM | 32.42% | Mostly binary data |
| Control Panel HLE | In progress | Protocol RE ongoing |

## Hardware Overview

- **Main CPU**: TMP94C241F (TLCS-900/H2 variant)
- **Architecture**: 32-bit microcontroller
- **Program Flash**: 2MB at 0xE00000
- **Control Panel**: Dedicated MCUs for buttons, LEDs, rotary encoders

## Getting Started

- [ROM Reconstruction Status]({{ site.baseurl }}/rom-reconstruction/)
- [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/)
- [Memory Map]({{ site.baseurl }}/memory-map/)
- [How You Can Help]({{ site.baseurl }}/help-wanted/)
- [Open Questions]({{ site.baseurl }}/questions/)

## Resources

- [GitHub: ROM Disassembly](https://github.com/user/kn5000-roms-disasm)
- [MAME Pull Request](https://github.com/mamedev/mame/pull/14558)
- [Discussion Forum](https://forum.fiozera.com.br/t/technics-kn5000-homebrew-development/321)

## Contact

Felipe Sanches - Project Lead
