---
layout: home
title: Home
---

![Technics KN5000]({{ "/assets/images/hero-banner.jpg" | relative_url }}){: .hero-banner }
<small style="display: block; text-align: center; margin-top: -1rem; margin-bottom: 1rem; color: #666;">Technics KN5000. Photo: [Sound On Sound](https://www.soundonsound.com/reviews/technics-kn5000) (March 1998)</small>

# Technics Keyboards — Reverse Engineering & Preservation

Welcome to the technical documentation for the reverse engineering and digital
preservation of **Technics musical keyboards**. Our long-term goal is to preserve
the history of these instruments — their internal architecture, firmware, and
protocols — as the physical hardware becomes scarce.

> **A Digital Archaeology Project**
>
> This project preserves technical knowledge of Technics keyboards through
> detailed reverse engineering. As physical hardware becomes scarce, accurate
> documentation ensures these instruments remain accessible for emulation,
> repair, and homebrew development.

## The Instruments

| Keyboard | Year | Main CPU | Documentation |
|----------|------|----------|---------------|
| **[Technics SX-KN5000](#technics-kn5000)** | 1997 | Toshiba TLCS-900/H2 (TMP94C241F) | Extensive — 6 ROMs reconstructed 100% byte-perfect, MAME driver, homebrew SDK |
| **[Technics SX-KN6000]({{ site.baseurl }}/kn6000-hardware/)** | 2000 | Panasonic MN10300 | New — firmware extracted, hardware mapped from the service manual; ~85% code shared with KN7000 |
| **[Technics SX-KN6500]({{ site.baseurl }}/kn6000-hardware/)** | 2001 | Panasonic MN10300 (MN103002A) | New — firmware extracted, hardware mapped from the service manual |
| **[Technics SX-KN7000]({{ site.baseurl }}/kn7000/)** | 2002 | Panasonic MN10300/AM33 | Early research — update-disk extraction and firmware analysis underway |

These arrangers span **two CPU architectures** — the TLCS-900 KN5000 and the
**MN10300 trio (KN6000, KN6500, KN7000)** — yet all four clearly descend from a
**single evolving source codebase**: the same update-disk container format
(`.SLD`/LZSS), the same MILK UI-framework symbol conventions, resource tables and
message text recur across every model (the KN6000 shares ~85 % of its strings with
the KN7000). See the
[Shared Codebase Map]({{ site.baseurl }}/technics-shared-codebase/) and the
[cross-version diff guidebook]({{ site.baseurl }}/cross-version-diff-guidebook/)
for the four-way comparison.

## Project Goals

| Goal | Description |
|------|-------------|
| **ROM Reconstruction** | Create buildable source code that produces byte-identical ROMs |
| **MAME Emulation** | Full system emulation in the MAME framework |
| **Homebrew Development** | Enable custom software development for the hardware |
| **Compiler Development** | LLVM backend for TLCS-900/H2, enabling C/C++ development |

---

## Technics KN7000

The **[Technics SX-KN7000]({{ site.baseurl }}/kn7000/)** (2002) is the successor
to the KN5000. Research here is at an early stage, focused so far on extracting
and understanding its system-update disks and firmware images.

| Page | Description |
|------|-------------|
| [KN7000 Overview]({{ site.baseurl }}/kn7000/) | Hardware summary, MN10300 CPU, memory map, project status |
| [KN7000 System Update Discs]({{ site.baseurl }}/kn7000-system-update-discs/) | `.SLD` container format, LZSS decompression, `.INF` checksums, extraction tool |
| [KN7000 Firmware Images]({{ site.baseurl }}/kn7000-firmware/) | Program & table flash layout, version numbers, string/hardware inventory, byte-exact disassembly project |
| [KN7000 Image Gallery]({{ site.baseurl }}/kn7000-image-gallery/) | 169 images extracted from the firmware (demo slideshows, product photos, digital-drawbar UI graphics) |
| [Shared Codebase Map]({{ site.baseurl }}/technics-shared-codebase/) | Cross-model code/data reuse between KN5000 and KN7000 |
| [Roadmap (vs KN5000)]({{ site.baseurl }}/kn7000-roadmap/) | What was done for the KN5000 and how each piece maps onto the KN7000 |

---

## Technics KN5000

The **Technics SX-KN5000** (1997) is the most thoroughly documented instrument on
this site: a 1997-era professional arranger keyboard whose firmware, protocols
and hardware have been reverse engineered in depth.

**New to the KN5000?** Begin with the [System Overview]({{ site.baseurl }}/system-overview/) to understand how all the components work together.

<div style="text-align: center; margin: 2rem 0;">
<a href="{{ site.baseurl }}/system-overview/" style="background: #0366d6; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 4px; font-weight: bold;">View System Overview</a>
</div>

## KN5000 Documentation by Topic

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
| [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) | Documented | DSP effects, tone generation, voice management |
| [Keybed Scanning]({{ site.baseurl }}/keybed-scanning/) | Documented | Hardware key scanning, note encoding, voice slots |
| [Display Subsystem]({{ site.baseurl }}/display-subsystem/) | Documented | Framebuffer layout, palette, VGA registers |
| [Storage Subsystem]({{ site.baseurl }}/storage-subsystem/) | Documented | Floppy, flash, Table Data ROM, HDAE5000 |
| [MIDI Subsystem]({{ site.baseurl }}/midi-subsystem/) | Documented | 26-channel voice routing, CC handlers, SysEx |
| [UI Framework]({{ site.baseurl }}/ui-framework/) | Documented | 550+ widget handlers, event system, drawing API |
| [Sequencer]({{ site.baseurl }}/sequencer/) | Documented | 16-track engine, ring buffer, style system |

### Protocols

| Page | Description |
|------|-------------|
| [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) | MCU serial communication |
| [Inter-CPU Protocol]({{ site.baseurl }}/inter-cpu-protocol/) | Main/Sub CPU latch protocol |
| [HDAE5000 Disk Interface]({{ site.baseurl }}/hdae5000-disk-interface/) | IDE/ATA and PC parallel port |
| [HDAE5000 Filesystem]({{ site.baseurl }}/hdae5000-filesystem/) | Custom FSB/FGB/FEB filesystem |

### Firmware Analysis

| Page | Description |
|------|-------------|
| [Boot Sequence]({{ site.baseurl }}/boot-sequence/) | Power-on to ready state |
| [SubCPU Payload Loading]({{ site.baseurl }}/subcpu-payload-loading/) | LZSS decompression, E1 bulk transfer, DMA investigation |
| [Sub CPU Payload Transfer]({{ site.baseurl }}/boot-sequence/#subcpu_send_payload-details) | 192KB firmware loading mechanism |
| [ROM Reconstruction]({{ site.baseurl }}/rom-reconstruction/) | Disassembly progress |
| [Source Code Map]({{ site.baseurl }}/source-map/) | Guide to every source file in the disassembly |
| [FDC Subsystem]({{ site.baseurl }}/fdc-subsystem/) | Floppy disk handlers |
| [Feature Demo & Presentation System]({{ site.baseurl }}/feature-demo/) | SSF XML scripting, demo assets, planned-but-unshipped floppy loading |
| [Floppy Security Analysis]({{ site.baseurl }}/floppy-security-analysis/) | Code injection vectors via crafted update discs |
| [HDAE5000]({{ site.baseurl }}/hdae5000/) | Hard disk expansion firmware |
| [Firmware v9 vs v10]({{ site.baseurl }}/firmware-v9-vs-v10/) | Detailed comparison of the last two firmware releases |

### Homebrew

| Page | Description |
|------|-------------|
| [Playing Games on MAME]({{ site.baseurl }}/playing-games/) | Step-by-step guide to running homebrew games in the emulator |
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
1. [Playing Games on MAME]({{ site.baseurl }}/playing-games/) - Get the emulator running first
2. [CPU Subsystem]({{ site.baseurl }}/cpu-subsystem/) - TMP94C241F programming
3. [Memory Map]({{ site.baseurl }}/memory-map/) - Available resources
4. [Display Subsystem]({{ site.baseurl }}/display-subsystem/) - Graphics output
5. [Another World VM]({{ site.baseurl }}/another-world-vm/) - Full game port example
6. [Help Wanted]({{ site.baseurl }}/help-wanted/) - Tool development needs

### Reverse Engineering Research
1. [ROM Reconstruction]({{ site.baseurl }}/rom-reconstruction/) - Current progress
2. [Reverse Engineering]({{ site.baseurl }}/reverse-engineering/) - Techniques
3. [Open Questions]({{ site.baseurl }}/questions/) - Areas needing investigation
4. [Issues]({{ site.baseurl }}/issues/) - Specific tasks

## Project Status

### ROM Reconstruction Progress

**All 6 ROMs: 100% byte-perfect match.** Built with a custom [LLVM TLCS-900 backend](https://github.com/felipesanches/llvm-project/tree/tlcs900_backend) -- 279,441 native instructions, zero workaround macros.

| Component | Size | Match | Status |
|-----------|------|-------|--------|
| Main CPU Program | 2MB | **100%** | 239,683 native instructions |
| Sub CPU Payload | 192KB | **100%** | 35,721 native instructions |
| Sub CPU Boot ROM | 128KB | **100%** | 1,357 native instructions |
| Table Data | 2MB | **100%** | 1,678 native instructions + binary data |
| Custom Data | 1MB | **100%** | Binary data (no code) |
| HDAE5000 ROM | 512KB | **100%** | 502 native instructions |

### Homebrew Development

A [homebrew SDK]({{ site.baseurl }}/hdae5000-homebrew/) is available for writing custom HDAE5000 extension ROMs. Features a Quick Start guide, C + assembly build pipeline, and a fully playable [Minesweeper game](https://github.com/ArqueologiaDigital/Mines/tree/kn5000_port/platforms/kn5000) as a working example.

### MAME Emulation

| Component | Status |
|-----------|--------|
| MAME Driver | [PR #14558](https://github.com/mamedev/mame/pull/14558) in progress |
| Display | 320x240 LCD working (VGA controller emulated) |
| Audio | DSP protocol decoded, tone generator HLE |
| Control Panel | Protocol documented, button state arrays emulated |
| HDAE5000 | Extension board detected, IDE/ATA wired, homebrew ROMs loadable |
| Floppy | UPD72067 FDC emulated, disk images available |

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

We believe preserving technical knowledge of instruments like the Technics KN5000 and KN7000 is essential for cultural heritage. Our long-term goal is to preserve the history of Technics musical keyboards as a whole. If you find errors or have additions, please contribute.
