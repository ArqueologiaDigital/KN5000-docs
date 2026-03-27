---
layout: page
title: "SNS NMI Emulation"
permalink: /sns-nmi-emulation/
---

# SNS NMI Emulation — Power-Off Checksum Mechanism

## The Problem

The KN5000 shows "ALL INITIAL SETTING!" on every boot instead of the splash animation when payload checksums at DRAM[0xFFD4/0xFFD2] are invalid.

## Real Hardware Behavior

On the real KN5000, the power supply has an SNS (sense) monitoring circuit that detects when AC mains power is removed. Before the DC voltage drops below the CPU's operating threshold, the SNS circuit asserts the CPU's `~NMI` pin. The CPU has a few milliseconds of execution time on remaining capacitor charge.

### Boot Sequence

1. `Boot_DisplayScreen` (0xEF0620) clears DRAM[0xFFD4] = 0 (invalidates old checksum)
2. `Boot_DisplayScreen` writes 0x80 to internal CPU RAM[0x0400] (arms the NMI guard)
3. Normal operation proceeds

### Power-Off Sequence

1. User presses power button → power supply begins shutdown
2. SNS circuit asserts `~NMI` on the CPU
3. CPU vectors to NMI handler at 0xEF08A5
4. NMI handler calls `NMI_StorePayloadChecksums` at 0xEF08D4:
   - Checks NMI guard: internal RAM[0x0400] == 0x80? If not, returns immediately
   - Saves voice presets and flush data to SRAM
   - Computes checksums for two DRAM regions:
     - **Region 1**: DRAM[0xF180], 0x800 words (2 KB) → one's complement sum → DRAM[0xFFD4]
     - **Region 2**: DRAM[0xF980], 0x280 words (640 bytes) → one's complement sum → DRAM[0xFFD2]
   - Copies DRAM[0xF980..] to backup SRAM at 0x1E8000
   - Executes `halt` instruction (CPU stops; power dies shortly after)

### Next Boot

`SubCPU_Payload_Verify` (0xEF06A0) compares stored checksums against freshly computed ones:
- If match: boot proceeds normally → splash animation plays
- If mismatch: firmware enters factory reset → "ALL INITIAL SETTING!" displayed

## MAME Emulation Challenge

MAME's exit sequence calls `eat_all_cycles()` simultaneously with `schedule_exit()`, preventing any CPU execution after exit is requested. The exit path is:

```
schedule_exit() → eat_all_cycles() → [main loop exits] → nvram_save() → EXIT notifiers
```

There is **no hook point** between "user requested exit" and "NVRAM saved to disk" where driver code can run the emulated CPU.

## Current Solution: Boot-Time Write Tap

We intercept `Boot_DisplayScreen`'s clearing of DRAM[0xFFD4] using `install_write_tap`. When the firmware writes zero to 0xFFD4, our tap reads the actual DRAM payload regions and computes the same one's-complement checksums the NMI handler would. The tap substitutes the correct checksum value, so `SubCPU_Payload_Verify` passes on the same boot.

This approach:
- Reads real emulated DRAM data (not synthetic values)
- Runs the same algorithm as the ROM handler
- Works reliably with `-seconds_to_run` and manual exit
- Only fires once per boot (during `Boot_DisplayScreen`)

### Checksum Algorithm

```
For each region:
    sum = 0
    for each 16-bit word in region:
        sum = (sum + word) & 0xFFFF
    checksum = ~sum & 0xFFFF  (one's complement)
```

## Proposed Upstream Improvement

A `MACHINE_NOTIFY_POWER_OFF` phase in MAME's `machine.cpp` would allow drivers to execute power-off logic (like NMI handlers) before NVRAM is saved. This would let the KN5000 driver fire the real NMI and give the CPU cycles to execute the ROM handler natively.

## Key Addresses

| Address | Description |
|---------|-------------|
| 0x0400 (internal CPU RAM) | NMI guard flag (0x80 = armed) |
| 0xEF0620 | `Boot_DisplayScreen` — clears 0xFFD4, arms guard |
| 0xEF06A0 | `SubCPU_Payload_Verify` — checks checksums |
| 0xEF08A5 | NMI handler entry |
| 0xEF08D4 | `NMI_StorePayloadChecksums` — computes and stores checksums |
| 0xFFD2 | Payload checksum 2 (Region 2) |
| 0xFFD4 | Payload checksum 1 (Region 1) |
| 0xF180 | Region 1 start (0x800 words) |
| 0xF980 | Region 2 start (0x280 words) |
