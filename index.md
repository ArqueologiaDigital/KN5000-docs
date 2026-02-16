---
layout: home
title: Home
---

![Technics KN5000]({{ "/assets/images/hero-banner.jpg" | relative_url }}){: .hero-banner }
<small style="display: block; text-align: center; margin-top: -1rem; margin-bottom: 1rem; color: #666;">Photo: [Sound On Sound](https://www.soundonsound.com/reviews/technics-kn5000) (March 1998)</small>

# Technics KN5000 Documentation

Welcome to the comprehensive technical documentation for the Technics KN5000 music keyboard. This site documents the internal architecture, firmware, and protocols of this 1997-era professional arranger keyboard.

> **A Digital Archaeology Project**
>
> This project preserves technical knowledge of the KN5000 through detailed reverse engineering. As physical hardware becomes scarce, accurate documentation ensures these instruments remain accessible for emulation, repair, and homebrew development.

## Project Goals

| Goal | Description |
|------|-------------|
| **ROM Reconstruction** | Create buildable source code that produces byte-identical ROMs |
| **MAME Emulation** | Full system emulation in the MAME framework |
| **Homebrew Development** | Enable custom software development for the hardware |
| **Compiler Development** | LLVM backend for TLCS-900/H2, enabling C/C++ development |

## Start Here

**New to the project?** Begin with the [System Overview]({{ site.baseurl }}/system-overview/) to understand how all the components work together.

<div style="text-align: center; margin: 2rem 0;">
<a href="{{ site.baseurl }}/system-overview/" style="background: #0366d6; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 4px; font-weight: bold;">View System Overview</a>
</div>

## Documentation by Topic

### Hardware & Memory

| Page | Description |
|------|-------------|
| [System Overview]({{ site.baseurl }}/system-overview/) | Architecture diagram and subsystem guide |
| [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) | Physical components from service manual |
| [CPU Subsystem]({{ site.baseurl }}/cpu-subsystem/) | TMP94C241F dual-CPU design |
| [Memory Map]({{ site.baseurl }}/memory-map/) | Complete address space layout |

### Subsystems

| Page | Status | Description |
|------|--------|-------------|
| [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) | Documented | Serial protocol for buttons, LEDs, encoders |
| [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) | Partial | DSP, DAC, tone generation |
| [Keybed Scanning]({{ site.baseurl }}/keybed-scanning/) | Documented | Hardware key scanning, note encoding, voice slots |
| [Display Subsystem]({{ site.baseurl }}/display-subsystem/) | Placeholder | LCD controller, VGA interface |
| [Storage Subsystem]({{ site.baseurl }}/storage-subsystem/) | Partial | Floppy, flash, Table Data ROM |
| [MIDI Subsystem]({{ site.baseurl }}/midi-subsystem/) | Placeholder | MIDI I/O handling |
| [UI Framework]({{ site.baseurl }}/ui-framework/) | Placeholder | Menu system, widgets |
| [Sequencer]({{ site.baseurl }}/sequencer/) | Placeholder | 16-track MIDI sequencer |

### Protocols

| Page | Description |
|------|-------------|
| [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) | MCU serial communication |
| [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) | Main/Sub CPU latch protocol |
| [HDAE5000 Disk Interface]({{ site.baseurl }}/hdae5000-disk-interface/) | IDE/ATA and PC parallel port |

### Firmware Analysis

| Page | Description |
|------|-------------|
| [Boot Sequence]({{ site.baseurl }}/boot-sequence/) | Power-on to ready state |
| [SubCPU Payload Loading]({{ site.baseurl }}/subcpu-payload-loading/) | LZSS decompression, E1 bulk transfer, DMA investigation |
| [Sub CPU Payload Transfer]({{ site.baseurl }}/boot-sequence/#subcpu_send_payload-details) | 192KB firmware loading mechanism |
| [ROM Reconstruction]({{ site.baseurl }}/rom-reconstruction/) | Disassembly progress |
| [FDC Subsystem]({{ site.baseurl }}/fdc-subsystem/) | Floppy disk handlers |
| [Feature Demo & Presentation System]({{ site.baseurl }}/feature-demo/) | SSF XML scripting, demo assets, planned-but-unshipped floppy loading |
| [Floppy Security Analysis]({{ site.baseurl }}/floppy-security-analysis/) | Code injection vectors via crafted update discs |
| [HDAE5000]({{ site.baseurl }}/hdae5000/) | Hard disk expansion firmware |

### Homebrew

| Page | Description |
|------|-------------|
| [Another World VM]({{ site.baseurl }}/another-world-vm/) | Full game port: bytecode VM, polygon rendering, input, frame timing |

### Resources

| Page | Description |
|------|-------------|
| [Image Gallery]({{ site.baseurl }}/image-gallery/) | 46+ extracted graphics (42 main CPU, 4 HDAE5000) |
| [ROM Strings]({{ site.baseurl }}/rom-strings/) | Extracted text resources |
| [Reverse Engineering]({{ site.baseurl }}/reverse-engineering/) | Methodology and strategies |
| [Help Wanted]({{ site.baseurl }}/help-wanted/) | Contribution guide |
| [Open Questions]({{ site.baseurl }}/questions/) | Unsolved mysteries |
| [Issues]({{ site.baseurl }}/issues/) | Project task tracker |

## Learning Paths

Choose based on your goal:

### MAME Emulation Development
1. [System Overview]({{ site.baseurl }}/system-overview/) - Understand the architecture
2. [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) - Physical components
3. [Memory Map]({{ site.baseurl }}/memory-map/) - Address space
4. [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) - HLE for buttons/LEDs

### Homebrew Development
1. [CPU Subsystem]({{ site.baseurl }}/cpu-subsystem/) - TMP94C241F programming
2. [Memory Map]({{ site.baseurl }}/memory-map/) - Available resources
3. [Display Subsystem]({{ site.baseurl }}/display-subsystem/) - Graphics output
4. [Another World VM]({{ site.baseurl }}/another-world-vm/) - Full game port example
5. [Help Wanted]({{ site.baseurl }}/help-wanted/) - Tool development needs

### Reverse Engineering Research
1. [ROM Reconstruction]({{ site.baseurl }}/rom-reconstruction/) - Current progress
2. [Reverse Engineering]({{ site.baseurl }}/reverse-engineering/) - Techniques
3. [Open Questions]({{ site.baseurl }}/questions/) - Areas needing investigation
4. [Issues]({{ site.baseurl }}/issues/) - Specific tasks

## Project Status

### ROM Reconstruction Progress

**Overall ROM-set Progress: 59.54%** (2,466,047 bytes remaining)

| Component | Size | Match | Status |
|-----------|------|-------|--------|
| Main CPU Program | 2MB | **100%** | Complete |
| Sub CPU Payload | 192KB | **100%** | Complete |
| Sub CPU Boot ROM | 128KB | **100%** | Complete |
| Table Data | 2MB | 33.30% | Mostly binary assets |
| Custom Data | 1MB | 0% | User storage, not reconstructed |
| HDAE5000 ROM | 512KB | **100%** | Complete, images extracted |

**Code Organization:** The disassembly uses modular source files with 1,074 lines of shared code across 7 files in the `shared/` directory, plus extracted subsystem files (`fdc_constants.asm`, `fdc_routines.asm`, `gui_constants.asm`).

### MAME Emulation

| Component | Status |
|-----------|--------|
| MAME Driver | [PR #14558](https://github.com/mamedev/mame/pull/14558) in progress |
| Control Panel HLE | Protocol documented, implementation ongoing |
| HDAE5000 Emulation | ATA and PPI interfaces implemented |

## Quick Links

- [Service Manual PDF]({{ site.baseurl }}/service_manual/technics_sx-kn5000.pdf) (26MB, EMID971655 A5) - Schematics, board layouts, IC pinouts
- [GitHub: ROM Disassembly](https://github.com/ArqueologiaDigital/kn5000-roms-disasm) - Source code
- [GitHub: Homebrew](https://github.com/felipesanches/kn5000_homebrew/) - Custom software
- [MAME Pull Request](https://github.com/mamedev/mame/pull/14558) - Emulation work
- [Discussion Forum](https://forum.fiozera.com.br/t/technics-kn5000-homebrew-development/321)
- [Firmware Archive](https://archive.org/details/technics-kn5000-system-update-disks) - All versions (v5-v10, HD-AE5000 updates)
- [Keysoftservice HDAE5000 Page](https://www.keysoftservice.ch/hdae5000-e.htm) - Original HDAE5000 information

## About This Project

**Project Lead**: Felipe Sanches | [Arqueologia Digital](https://github.com/ArqueologiaDigital)

This documentation is developed with AI assistance from [Claude Code](https://claude.ai/code). All content is verified against actual hardware behavior and service documentation. Contributions and corrections are welcome via GitHub issues.

We believe preserving technical knowledge of instruments like the KN5000 is essential for cultural heritage. If you find errors or have additions, please contribute.
