---
layout: page
title: Control Panel Protocol
permalink: /control-panel-protocol/
---

# Control Panel Serial Protocol

The KN5000 control panel uses dedicated MCUs to handle:
- **LED indicators** - Status lights across the front panel
- **Button scanning** - All front panel buttons
- **Rotary encoders** - Data wheel, pitch/mod wheels

These MCUs communicate with the main CPU via serial protocol. Since we lack ROM dumps for these MCUs, MAME emulation requires **High Level Emulation (HLE)** based on reverse-engineered protocol understanding.

## Protocol Overview

Communication uses 2-byte command sequences sent from main CPU to control panel MCUs.

### Command Categories

| Prefix | Purpose | Example |
|--------|---------|---------|
| `1d`, `1e`, `1f` | Initialization | `1f da`, `1f 1a`, `1d 00`, `1e 80` |
| `dd` | Setup | `dd 03` |
| `20` | Query/Read | `20 00`, `20 10`, `20 0b` |
| `25`, `2b` | Data commands | `25 01`, `2b 00` |
| `e0`, `e2`, `e3`, `eb` | Extended commands | `e0 00`, `e2 04`, `e2 11`, `e3 10`, `eb 00` |

### Initialization Sequence

From `SOME_CPANEL_ROUTINE__FC3EF5`:
```
send 1f da / wait / INDEX_FOR_LEDS = 0 / wait
send 1f 1a / wait / INDEX_FOR_LEDS = 0 / wait
send 1d 00 / wait / INDEX_FOR_LEDS = 0 / wait
send dd 03 / wait / INDEX_FOR_LEDS = 0 / wait
send 1e 80 / wait
```

## Key Data Structures

### Memory Locations

| Address/Name | Purpose |
|--------------|---------|
| `STATE_OF_CPANEL_BUTTONS` | Button state array |
| `CPANEL_INDEX_FOR_LEDS` | Current LED index |
| `CPANEL_STATE_0_TO_17` | Protocol state machine |
| `CPANEL_BACKUP_RX_INDEX` | RX buffer position |
| `RX_INDEX` | Current receive index |

### Status Flags

| Flag | Used By |
|------|---------|
| `CP_Flags_A.10` | Serial routines, interrupt handler |
| `CP_Flags_A.76` | Setup routines |
| `CP_Flags_B.0` | Most command routines |
| `CP_Flags_B.7` | Ready check, serial handler |
| `CP_Flags_C.0`, `CP_Flags_C.4` | Initial comm test results |

## Key Routines

| Routine | Purpose |
|---------|---------|
| `SOME_CPANEL_ROUTINE__FC3EF5` | Initial setup |
| `SEND_SOME_CPANEL_COMMANDS__FC41FC` | Command sequence |
| `ANOTHER_CPANEL_ROUTINE__FC426A` | Button state check |
| `LABEL_FC42FB` | Multi-command sequence |
| `SEND_CMD_TO_CPANEL` | Low-level send |
| `CHECK_IF_WE_ARE_READY_TO_SEND_CMD_TO_CPANEL` | TX ready check |
| `CPANEL_SERIAL_ROUTINE_0` through `_8` | Serial handlers |
| `LABEL_FC4915`, `LABEL_FC490E` | Response interpretation |

## Response Handling

*Analysis in progress - documenting expected responses for each command.*

## Button Mapping

*Analysis in progress - mapping button indices to physical buttons.*

## LED Mapping

*Analysis in progress - mapping LED indices to physical LEDs.*

## Rotary Encoder Format

*Analysis in progress - determining encoder data format.*
