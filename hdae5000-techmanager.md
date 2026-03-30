---
layout: page
title: TechManager5000 Emulation Plan
permalink: /hdae5000-techmanager/
---

# HD-TechManager5000 Emulation Plan

*Last updated: March 30, 2026*

The HD-TechManager5000 is a Windows application that communicates with the HD-AE5000 expansion board via a PC parallel port cable (DB25 to DB15). It enables file management, backup, and formatting of the HDAE5000 hard disk from a PC. This page documents plans for running the original, unmodified TechManager5000 software alongside the KN5000 MAME emulation.

> **Preservation principle**: The TechManager5000 software must run **completely unmodified**. No patching, DLL replacement, or binary modification. The original `ppkn50.dll` performs direct I/O port access (`in`/`out` to LPT base+0/1/2) and must see real (emulated) LPT hardware.

> **See Also**: [HDAE5000 Disk Interface]({{ site.baseurl }}/hdae5000-disk-interface/) for the parallel port protocol details, [HDAE5000 MAME Setup]({{ site.baseurl }}/hdae5000-mame-setup/) for basic setup.

## Background: How ppkn50.dll Works

The `ppkn50.dll` library (disassembled and fully documented) communicates with the HDAE5000 using:

- **PC parallel port registers**: Data (base+0 = 0x378), Status (base+1 = 0x379), Control (base+2 = 0x37A)
- **HDAE5000 PPI registers**: Port A (0x160000), Port B (0x160002), Port C (0x160004)
- **Custom handshake protocol**: Strobe/ACK/BUSY signaling, not standard Centronics
- **Timeouts**: 10,000ms per byte transfer, 512 polling iterations before time check

The DLL exports these functions:

| Function | Description |
|----------|-------------|
| `InitializeTheDllPP50` | Initialize DLL |
| `OpenThePortNumberPP50` | Select LPT port (1-3) |
| `CloseThePortPP50` | Close parallel port |
| `TestTheKNPPPP50` | Test connection to KN5000 |
| `ReadFsbFromKnHdToKnMemPP50` | Read filesystem block from HD |
| `SendFsbFromKnMemToPCPP50` | Transfer FSB to PC |
| `SendFsbFromPCToKnMemPP50` | Transfer FSB to KN |
| `LoadFileFromKnHdToKnMemPP50` | Download file from HD |
| `DeleteFileOnKnHdPP50` | Delete file on HD |
| `FormatTheKn50HardDiskPP50` | Format hard disk |
| `TurnOffTheKn50HdMotorPP50` | Spin down drive motor |

## Plan A: Two MAME Instances (TCP Bridge)

Two separate MAME processes communicate over a TCP socket on localhost:

```
┌──────────────────────────────────────────────────────────────┐
│  MAME instance 1 (PC emulation)                              │
│  ┌────────────────────┐    emulated LPT    ┌───────────────┐ │
│  │ Windows 98 + HD-   │ ◄────────────────► │ Emulated      │ │
│  │ TechManager5000    │   I/O port 0x378   │ parallel port │ │
│  │ (unmodified)       │                    │ hardware      │ │
│  └────────────────────┘                    └───────┬───────┘ │
└────────────────────────────────────────────────────┼─────────┘
                                                     │ TCP socket
┌────────────────────────────────────────────────────┼─────────┐
│  MAME instance 2 (KN5000 emulation)                │         │
│  ┌──────────┐    PPI callbacks    ┌────────────────┴──────┐  │
│  │ KN5000 + │ ◄─────────────────► │ PPI socket device     │  │
│  │ HDAE5000 │    Port A/B/C       │ (listens for PC MAME) │  │
│  └──────────┘                     └───────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### How it works

1. **MAME (KN5000)** runs the keyboard emulation with HDAE5000. The PPI device is bridged to a TCP socket listener.
2. **MAME (PC)** runs a Windows 98 PC driver (e.g., `pcipc`) with TechManager5000 installed on its emulated hard disk. The PC's emulated LPT parallel port connects to the KN5000 MAME instance via TCP.
3. `ppkn50.dll` executes `in`/`out` instructions to the PC's LPT port --- which is real (emulated) hardware from its perspective. The emulated LPT hardware relays the signals to the KN5000's PPI over TCP.

### Implementation needed

- **KN5000 side**: Socket-based PPI bridge device (exposes Port A/B/C over TCP)
- **PC side**: Socket-based external connection for MAME's centronics/LPT device
- **PC disk image**: Windows 98 installation + TechManager5000

### Open questions

- Which MAME PC driver has the best LPT parallel port emulation?
- Does MAME's existing parallel port infrastructure support external socket connections?
- Can MAME's `bitbanger` device serve as the socket transport on both sides?

## Plan B: Single MAME Instance (Multi-Driver)

Run both the KN5000 and a PC driver within a single MAME instance, with the parallel ports wired directly:

```
┌─────────────────────────────────────────────────────────────────┐
│  Single MAME instance                                           │
│                                                                 │
│  ┌────────────────────┐    direct wire    ┌───────────────────┐ │
│  │ Windows PC driver  │ ◄──────────────► │ KN5000 + HDAE5000 │ │
│  │ (pcipc / at)       │   centronics ←→   │ PPI @ 0x160000    │ │
│  │ + TechManager5000  │   PPI callbacks   │                   │ │
│  └────────────────────┘                   └───────────────────┘ │
│                                                                 │
│  Both machines share the same scheduler, so handshake timing    │
│  is cycle-accurate with no socket latency.                      │
└─────────────────────────────────────────────────────────────────┘
```

### Advantages over Plan A

- No TCP socket overhead or timing concerns
- Single process, single scheduler --- handshake signals propagate within the same emulation cycle
- Simpler to launch (one command line)
- More faithful to the original hardware setup (two physical devices connected by a cable)

### Implementation needed

- A MAME "null cable" device that cross-wires the PC's LPT data/status/control lines to the HDAE5000's PPI Port A/B/C, with appropriate signal inversion (PC parallel port inverts BUSY on bit 7)
- A composite driver or multi-machine configuration that instantiates both the KN5000 and a PC system
- Shared display (two screens, or a split layout)

### Open questions

- Does MAME support running two independent machine drivers in one instance? (Multi-system configurations exist for linked arcade cabinets --- can this pattern be reused?)
- How to handle two independent CPUs with different clock domains in the same scheduler?
- How to present two screens (KN5000 LCD + PC VGA) to the user?

## Comparison

| Aspect | Plan A (Two instances) | Plan B (Single instance) |
|--------|----------------------|-------------------------|
| Timing accuracy | Good (10s timeout is generous) | Perfect (same scheduler) |
| Complexity | Lower (independent processes) | Higher (multi-machine config) |
| User experience | Two windows, two commands | One window, one command |
| Latency | TCP localhost (~microseconds) | Zero (direct callback) |
| MAME precedent | Common (networked games) | Exists (linked cabinets) |
| Preservation fidelity | Good | Best (models the physical cable) |

## Status

Both plans are in the design phase. The prerequisite for either plan is:
1. The HDAE5000 PPI callbacks are wired (done --- March 30, 2026)
2. A working ATA interface with disk image support (done --- March 30, 2026)
3. Research into MAME's PC driver LPT implementation and multi-machine support

## Related Pages

- [HDAE5000 MAME Setup]({{ site.baseurl }}/hdae5000-mame-setup/) --- Basic emulator setup
- [HDAE5000 Disk Interface]({{ site.baseurl }}/hdae5000-disk-interface/) --- Parallel port protocol details
- [HDAE5000 Filesystem]({{ site.baseurl }}/hdae5000-filesystem/) --- On-disk data structures
