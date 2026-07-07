---
layout: page
title: KN6000 / KN6500 Hardware Architecture
permalink: /kn6000-hardware/
---

# KN6000 / KN6500 — hardware architecture

Reconstructed from the **Technics SX-KN6000** (89-page) and **SX-KN6500**
(142-page) service manuals, cross-checked against the decoded firmware. The
KN6000 and KN6500 are **architecturally the KN7000's siblings** — the same
Panasonic **MN10300** main CPU and the same [MILK application
framework](/technics-shared-codebase/) — not the TLCS-900 KN5000. See the
[KN6000/KN6500 roadmap](/kn6000-roadmap/) for the preservation plan and the
[cross-version diff guidebook](/cross-version-diff-guidebook/) for the four-way
code-reuse strategy.

## Main board (board **A**, MAIN)

| Ref | Device | Role |
|-----|--------|------|
| **IC4** | **32-bit micro controller — Panasonic MN10300** (KN6500: **MN103002A**) | Main CPU. Address bus **A0–A25** (64 MB space), data bus **D0–D31**. Same family as KN7000. |
| **IC11 / IC12** | **PROGRAM ROM (ODD) / (EVEN)** — 16 Mbit flash each | The MAIN CPU program, byte-interleaved on the 32-bit bus. **= the decoded `IK1.SLD` image.** Field-rewritable from a floppy system-update disc. |
| **IC13 / IC14** | **PROGRAMMED MASK ROM** | Built-in style / sound tables. **= the `IK2.SLD` table image.** |
| **IC15** | **RHYTHM DATA ROM** | Built-in rhythm/accompaniment pattern data. |
| **IC18** | **CUSTOM DATA ROM** — 16 Mbit flash | RHYTHM & ACCOMP data for the RHYTHM-GROUP / CUSTOM function; user COMPOSER data. **Factory-set, and defaulted from the [Initial Data Disk](/kn7000-initial-data/) (`idd6000`); user data is lost if the chip is replaced.** |
| **IC9 / IC10** | **DRAM** | Main work RAM. |
| **IC20** | **SRAM** | Battery-backed panel / user state. |
| **IC304** | **Digital Signal Processor** (+ **IC305/IC308 SDRAM**) | Reverb / chorus / effects DSP with its own SDRAM. |
| **IC213** | **Tone Generator LSI** | PCM synthesis engine (KB/KF/KS key buses, WAX/WAY wave buses). |
| **IC205–IC208** | **four 64 Mbit WAVE mask ROMs** | PCM sample data (256 Mbit ≈ 32 MB total). |
| **IC108** | **Color LCD Controller** (+ **IC110 4 Mbit DRAM**) | LCD framebuffer / video RAM; backlight via the **INV** board (board K). |
| **IC101** | **Floppy Disk Controller** | 3.5″ 2HD/2DD drive. |
| **IC107** | Computer-port driver / receiver | PC / MAC serial (SW-selected). |
| — | HDD connector (**CN105**) | Optional hard-disk drive. |

**`IC18` is the physical confirmation of the "custom-data flash defaulted from the
Initial Data Disk" mechanism** that the KN7000 rhythm-name investigation traced in
software — the built-in/user rhythm data really does live in a flash IC that the
`idd*` disk initialises.

## Front-panel & keyboard sub-processors

Each panel board carries an **8-bit microcomputer** that scans its switches and
drives its LEDs, reporting to the main CPU over a serial link — the same topology
as the KN7000's CPL/CPC/CPR/CPSD sub-CPUs:

| Board | Sub-CPU / role |
|-------|----------------|
| **E — CPL** | `IC1` 8-bit µC + LED driver/buffer; MAIN VOLUME / APC volume pots |
| **G — CPR** | `IC10` 8-bit µC + `IC11` decoder + LED driver; MIC volume |
| **F — CPC** | switches & LEDs |
| **I — ROT** | rotary **data-wheel** encoder (`SW500`) |
| **L/M/N — LCDL/LCDR/LCDC** | LCD-flanking switches & LEDs, contrast |
| **Q/R/S — MKB1/2/3** | keyboard matrix (decoders + diodes) with an **after-touch** sensor |

## Audio path (board **B** FAJ / **C** ASUB)

Tone-generator + DSP output → D/A → equalizer/integrator → power amps → **66 W**
(18 W × 2 mid/high + 30 W bass); speakers 12 cm × 2, 6.5 cm × 2, 14 cm bass.
Jacks: PHONES, FOOT SW 1/2, FOOT CONTROLLER, EXP PEDAL, LINE OUT (R/R+L,L), AUX
IN, COMPUTER, **MIDI IN/OUT/THRU** (photo-coupled), MIC.

## Service diagnostics (test modes)

The service manual documents a built-in **service diagnostic function**: **ROM
device test, RAM device test, WAVE ROM test, SOUND SYSTEM test, Panel SW & LED
test, LCD module test, Floppy save/load test, MIDI in/out test, In & Out
interface test.** These are directly useful for validating an emulator against the
real hardware's self-tests.

## Specifications (from the owner's-manual excerpt)

200 rhythms × 4 variations · 8-part Composer (~13 000-note capacity) · 16-track
sequencer (~40 000 notes, 1/96 resolution) · 20 preset + 3 user + 2 compile
performance-pad banks · 13 × 8 Panel Memory · 3.5″ floppy + optional HDD ·
MN10300 CPU · ~15.4 kg.
