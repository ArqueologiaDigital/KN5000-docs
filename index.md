---
layout: home
title: Home
---

![Technics KN5000]({{ "/assets/images/hero-banner.png" | relative_url }}){: .hero-banner }

# Technics KN5000 Reverse Engineering Project

> **A Digital Archaeology Project**
>
> This project is a labor of love for the Technics KN5000 instrument and a commitment to historical preservation of computer hardware through emulation. As physical hardware ages and becomes scarce, emulation ensures these remarkable instruments remain accessible to future generations of musicians, researchers, and enthusiasts.
>
> **About This Documentation**
>
> This documentation is being developed with the assistance of [Claude Code](https://claude.ai/code) AI agents, guided by Felipe Sanches. While every effort is made to ensure accuracy, some information may be incomplete or contain errors as the reverse engineering work progresses. All content is under continuous review and verification against actual hardware behavior. Contributions and corrections are welcome.

This project aims to fully document and emulate the Technics KN5000 music keyboard. Join the discussion at the [Homebrew Development Forum](https://forum.fiozera.com.br/t/technics-kn5000-homebrew-development/321).

**Project Goals:**

- **ROM Reconstruction** - Achieving 100% byte-matching rebuilds from disassembled source, gaining deeper insight into the device's inner workings to aid development of an accurate emulator
- **MAME Emulation** - Enabling the keyboard to run in the MAME emulator
- **Homebrew Development** - Creating custom software for the real hardware
- **Compiler Development** *(long-term)* - Porting a higher-level compiler (potentially LLVM-based) to target the TMP94C241F CPU, enabling C/C++ development for the KN5000

## Project Status

### ROM Reconstruction

| Component | Size | Match | Notes |
|-----------|------|-------|-------|
| Main CPU Program | 2MB | 99.99% | 177 bytes divergent |
| Sub CPU Payload | 192KB | 100% | Complete match |
| Sub CPU Boot ROM | 128KB | - | Not yet disassembled |
| Table Data | 2MB | 32.42% | Mostly binary assets |
| Custom Data | 1MB | - | User storage, not reconstructed |
| HDAE5000 ROM | 512KB | - | Not yet disassembled |

### Emulation & Tools

| Component | Status | Notes |
|-----------|--------|-------|
| MAME Driver | In progress | [PR #14558](https://github.com/mamedev/mame/pull/14558) |
| Control Panel HLE | In progress | Protocol reverse engineering ongoing |
| Hardware Documentation | Active | Service manual analyzed |
| Image Extraction | Partial | 43+ images catalogued |

## Hardware Overview

- **Main CPU**: TMP94C241F (TLCS-900/H2 variant, 32-bit)
- **Control Panel MCUs**: Mitsubishi M37471M2196S (8-bit, 740 series) - 2 units
- **Program Flash**: 2MB at 0xE00000
- **Control Panel**: Serial bus with SIN/SOUT/CLK signals

See [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) for detailed documentation from service manual schematics.

## Getting Started

- [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) - Detailed hardware documentation from service manual
- [ROM Reconstruction Status]({{ site.baseurl }}/rom-reconstruction/)
- [Reverse Engineering Strategies]({{ site.baseurl }}/reverse-engineering/) - HDAE5000, SubCPU/MicroDMA, embedded images
- [Image Gallery]({{ site.baseurl }}/image-gallery/) - Extracted graphics from the firmware
- [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/)
- [Memory Map]({{ site.baseurl }}/memory-map/)
- [How You Can Help]({{ site.baseurl }}/help-wanted/)
- [Open Questions]({{ site.baseurl }}/questions/)
- [Project Issues]({{ site.baseurl }}/issues/) - Full issue tracker (auto-generated)

## Resources

- [Service Manual PDF]({{ site.baseurl }}/service_manual/technics_sx-kn5000.pdf) (EMID971655 A5, 26MB) - Schematics, board layouts, IC pinouts
- [System Update Disks Archive](https://archive.org/details/technics-kn5000-system-update-disks) - All official firmware versions (v5-v10) and HD-AE5000 updates
- [HDAE5000 Hard Disk Expansion](https://www.keysoftservice.ch/hdae5000-e.htm) - Technical info about the HD-AE5000 accessory
- [GitHub: ROM Disassembly](https://github.com/user/kn5000-roms-disasm) - Disassembled firmware sources
- [GitHub: Homebrew Development](https://github.com/felipesanches/kn5000_homebrew/) - Custom software for the KN5000
- [MAME Pull Request](https://github.com/mamedev/mame/pull/14558) - Emulation work in progress
- [Discussion Forum](https://forum.fiozera.com.br/t/technics-kn5000-homebrew-development/321)

## Contact

**Felipe Sanches** - Project Lead | [Arqueologia Digital](https://github.com/ArqueologiaDigital)

This digital archaeology project uses AI-assisted reverse engineering with Claude Code agents to accelerate documentation and analysis. Human oversight ensures accuracy and guides the research direction.

We believe that preserving the technical knowledge of instruments like the KN5000 is essential for cultural heritage. If you share this passion and find errors or have corrections, please open an issue on GitHub.
