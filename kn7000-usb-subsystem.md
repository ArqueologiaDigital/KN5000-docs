---
layout: page
title: KN7000 USB Subsystem
permalink: /kn7000-usb-subsystem/
---

# KN7000 USB Subsystem

What the rear **USB** terminal is, what it does, and how far it can be emulated. This is the opening
survey of a fresh investigation — the hardware topology and feature set are established; reverse-
engineering the host-side protocol is the work that follows.

*Sources: KN7000 service manual (block diagram, parts list, main-CPU schematics), the KN7000 owner's
manual, and firmware strings. Started 2026-08-03.*

## In one line

The USB terminal is a **USB *device* port to a personal computer** (type-B, "type AB cable"), driven by
a **dedicated USB co-processor subsystem** separate from the main MN10300 CPU. It provides **USB-MIDI**,
**USB audio recording**, and **PC-side data management**, used with Panasonic's bundled software.

## It is a co-processor, not a main-CPU peripheral

The USB port and the SD card slot share a board and each has its own processor. The main CPU never
drives the USB wires — it talks to a USB CPU over a serial link.

```
   USB port (USB+ / USB-)                          rear jack -> CN702 / CN701
        │
   ┌─ IC408  "USB AUDIO" ──────────────┐   the USB device controller: handles USB+/USB-, a MIDI RX
   │   USB device + USB-MIDI front end  │   line (USB-MIDI), and the serial control link to the MAIN CPU
   │        │  DU0-DU7 (8-bit bus)      │
   │   ┌─ IC407 "USB MICRO CONTROLLER" ─┘   the audio streamer:
   │   │      SDIU ← IC410 (PCM1800E ADC)   instrument audio → PC   ("record")
   │   │      SDOU → IC406 (PCM1716  DAC)   PC audio → instrument   ("play")
   │
   └── serial link to the MAIN CPU (MN10300):
         USB.SI, USB.SO, USBM.TX, USB.WAITM, USB.WAITH, USB.SD, USB.ST
```

The **SD card** is a *sibling* co-processor on the same board — an SD µ-COM (`IC401`, `MN102H60`) with
its own SD decoder (`IC402`), program flash (`IC414`, 4 Mbit) and config EEPROM (`IC403`) — not the
same block as the USB controllers.

> **Naming caveat.** The block diagram's *function* and the parts list's *name* look transposed for
> these two chips: the block wired to `USB+/USB-` + `MIDI RX` + the main-CPU link is drawn as **IC408**
> (part name "USB AUDIO"), while the block wired to the audio codecs is **IC407** (part name "USB MICRO
> CONTROLLER"). The datapath above is what matters and is unambiguous; the exact chip split can be
> confirmed when an example board is on the bench.

### Board IC inventory

| IC | part | role |
|---|---|---|
| IC401 | `MN102H60KTA` | SD µ-COM (SD-card microcontroller) — separate from USB |
| IC402 | `MN67737DB1` | SD decoder → the SD card slot (CN921/CN922) |
| IC403 | `S29L331AFSTB` | serial EEPROM/flash for the SD µ-COM |
| IC406 | `PCM1716ET2` | USB-audio DAC (PC → instrument) |
| IC407 | `C2CBGF000150` | audio streamer (codecs ↔ IC408) |
| IC408 | `C2BBGE000618` | front-end USB controller (USB port, USB-MIDI, main-CPU link) |
| IC410 | `PCM1800E-T1` | USB-audio ADC (instrument → PC) |
| IC414 | `C3FBKD000162` | 4 Mbit flash — SD µ-COM program (undumped) |

Every processor here — IC408, IC407, the SD µ-COM and its flash/EEPROM — runs **undumped** firmware.
The dumped main program ROM holds only the *host side* of the link.

## What the port offers

The terminal takes a **type-AB USB cable** to a PC. The bundled CD-ROM carries three PC applications —
**Audio Recorder**, **Song Manager**, and a **USB Driver**.

1. **USB-MIDI.** The owner's manual "Computer Connection" screen (in the MIDI menu) selects the MIDI
   signal-flow mode:

   | mode | meaning |
   |---|---|
   | NORMAL | ordinary operation |
   | PC as master | tuned for data transmission from the PC |
   | KN as master | the KN7000 is the master keyboard (MIDI → PC) |
   | KN as slave | the KN7000 is a slave (PC → MIDI) |
   | INTERFACE | the KN7000 bridges a USB-only PC to a MIDI-only instrument (a USB-MIDI adapter) |

2. **USB audio recording** (the "Audio Recorder" app). Streams the instrument's audio to the PC and
   saves **WAV / WMA / MP3** files — the "make a CD from your playing" feature. Hardware path:
   instrument audio → PCM1800 ADC → USB controller → USB.
3. **Data management** (the "Song Manager" app). Manage and transfer the instrument's data to and from
   the PC. The firmware warns not to unplug during a transfer or *"you may damage your SD Card"* — the
   operation reaches the SD card by way of the main CPU and the SD µ-COM.

## Emulation

- **Have:** the *host* (main MN10300) side of the link, in the dumped program ROM — the firmware's
  "USB driver / manager". Its interface is the `USB.SI/SO` serial pair plus a `WAIT` handshake, and
  probably a mailbox in the `0x98050000` I/O window (compare the existing `0x9805000C` "SD mailbox").
- **Missing:** the USB controllers (IC407/IC408), the SD µ-COM (IC401) and its flash (IC414) — all
  undumped, all masked custom parts.
- **Plan.**
  1. **HLE the host link first.** Find where `USB.SI/SO` map, decode the command framing, and answer as
     a "no PC attached" device so the Computer Connection menu and any USB status polling stay stable.
     Pure disassembly, no hardware — the same shape as the SD-mailbox HLE already in the driver.
  2. **Present a USB device to a host — later, and optional.** Making the emulated KN7000 appear as a
     real USB-MIDI / USB-audio device to the host is beyond MAME's current USB-device support and needs
     the co-processor behaviour regardless; deferred until step 1 lands.

## Register-level reverse engineering — first pass

Pushing on "which main-CPU register is the link" narrows it sharply, mostly by elimination:

- **Not an on-chip serial (SIO).** The MN10300 has exactly three USARTs, and all three are already
  identified — control panel, MIDI-1, MIDI-2. The USB link is not one of them.
- **Not a memory-mapped mailbox.** Every access into the whole `0x9800xxxx` I/O window is accounted for
  by the tone generators, the SD mailbox, the floppy controller, and sound control — none is USB.
- **It is a transistor-buffered GPIO bit-bang.** On the main-CPU schematic the link's signals
  (`USB.SD` = data, `USB.ST` = clock/strobe, `USB.MAITU`, and the `USB.WAIT*` handshake) pass through
  discrete level-shifter transistors and gate glue — i.e. ordinary port pins toggled in software, which
  is exactly why it does not appear as a peripheral register. The USB-board end adds a UART (`UTXD2`)
  on the USB controller.
- **The link is non-blocking at boot.** The instrument boots fully with no PC attached, so the USB code
  runs only on demand. **No boot stub is needed** — HLE is required only to make the USB *features*
  work, which lowers its priority and de-risks it.

**Dynamic trace, and the real gate.** A Lua GPIO/SIO tracer was driven straight to **MIDI MENU →
Computer Connection** using the (fully mapped) LCD soft-keys, and the mode was cycled on-screen. The
result is a clean negative: *opening the screen and changing the mode produce only control-panel serial
traffic* — SIO channel 0 muxed by GPIO `0x36008024`/`0x36008064`, driven from `0x484AC6xx-0x484ACDxx`.
**No USB communication fires.** The USB co-processor only starts talking to the main CPU once a PC is
physically attached (VBUS + enumeration); with no PC and the (undumped) USB controller unmodelled,
nothing raises "connected", so the main CPU never drives the link. Reaching the USB bit-bang is
therefore a firmware/HLE task — modelling the controller's connected/enumeration handshake — not a
UI-navigation one.

## See also

- [Storage & File System](/kn7000-storage-subsystem/) — the SD card sibling co-processor
- [MIDI / Serial I/O](/midi-serial-io/)
- [Hardware Architecture](/hardware-architecture/)
