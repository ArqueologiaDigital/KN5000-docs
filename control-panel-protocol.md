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

| Address | Name | Size | Purpose |
|---------|------|------|---------|
| `0x8D8B` | `CPANEL_STATE_0_TO_17` | byte | Protocol state machine (values 0-17) |
| `0x8D9D` | `CPANEL_BACKUP_RX_INDEX` | word | Backup of RX buffer position |
| `0x8D9F` | `CPANEL_RX_INDEX` | word | Current receive buffer index |
| `0x8DFD` | `CPANEL_INDEX_FOR_LEDS` | word | Current LED addressing index |
| `0x8E4A` | `STATE_OF_CPANEL_BUTTONS` | array | Button state array (Right panel) |
| `0x8E5A` | `STATE_OF_CPANEL_BUTTONS_LEFT` | array | Button state array (Left panel) |

### Status Flags

| Address | Name | Bits Used |
|---------|------|-----------|
| `0x8D8C` | `CPANEL_SERIAL_FLAGS_A` (CP_Flags_A) | bits 0,1,2,4,6,7 |
| `0x8D92` | `CPANEL_SERIAL_FLAGS_B` (CP_Flags_B) | bits 0,1,2,3,6,7 |
| `0x8D93` | `CPANEL_SERIAL_FLAGS_C` (CP_Flags_C) | bits 0,4 |

### Flag Usage

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
