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

### Initialization and Setup

| Routine | Address | Purpose |
|---------|---------|---------|
| `SOME_CPANEL_ROUTINE__FC3EF5` | 0xFC3EF5 | Initial setup |
| `CPanel_Init_Serial_LEDs` | 0xFC4021 | Initialize serial communication and LED array |
| `CPanel_Init_StateArray` | 0xFC42FB | Initialize state arrays for RX/TX |
| `SEND_CMD_TO_CPANEL` | 0xFC43D9 | Low-level 2-byte command send |
| `CHECK_IF_WE_ARE_READY_TO_SEND_CMD_TO_CPANEL` | 0xFC4374 | TX ready check with timeout |

### RX Packet Processing

| Routine | Address | Purpose |
|---------|---------|---------|
| `Process_CPanel_Rx_SetFlag` | 0xFC490E | Entry point with flag set |
| `Process_CPanel_Rx_ClearFlag` | 0xFC4915 | Entry point with flag clear |
| `Process_CPanel_Rx_Setup` | 0xFC491A | Initialize pointers for packet processing |
| `Process_CPanel_Rx_Loop` | 0xFC492B | Main packet processing loop |
| `Process_CPanel_Rx_Return` | 0xFC4B2C | Return from processing |

### Packet Type Handlers

The `CPanel_Packet_Handler_Table` at 0xFC4965 dispatches to handlers based on packet type (bits 3-5 of first byte):

| Type | Handler | Address | Purpose |
|------|---------|---------|---------|
| 0, 1 | `CPanel_Handle_ButtonState` | 0xFC4985 | Process button state packets |
| 2 | `CPanel_Handle_EncoderLookup` | 0xFC49E0 | Process rotary encoder data |
| 3, 4, 5 | `CPanel_Handle_SyncPacket` | 0xFC4B10 | Synchronization/acknowledgment packets |
| 6, 7 | `CPanel_Handle_MultiBytePacket` | 0xFC4A40 | Multi-byte data packets |

### LED Transmission

| Routine | Address | Purpose |
|---------|---------|---------|
| `CPanel_Send_LED_Data` | 0xFC4B2D | Send LED state to panel MCUs |
| `CPanel_LED_Handler_Table` | 0xFC4B85 | Jump table for LED packet types |

### Button Polling

| Routine | Address | Purpose |
|---------|---------|---------|
| `CPanel_PollButtonState_Loop` | 0xFC4293 | Main button state polling loop |
| `CPanel_CheckEncoderState` | 0xFC42B7 | Check rotary encoder changes |

### Serial Interrupt Handlers

| Routine | Purpose |
|---------|---------|
| `CPANEL_SERIAL_ROUTINE_0` | Idle state |
| `CPANEL_SERIAL_ROUTINE_1` through `_6` | TX state machine |
| `CPANEL_SERIAL_ROUTINE_7` | Read buttons state (phase 1) |
| `CPANEL_SERIAL_ROUTINE_8` | Read buttons state (phase 2) |

## Packet Format

### RX Packet Structure

Incoming packets from control panel MCUs:
- **Byte 0**: Type/flags byte
  - Bits 3-5: Packet type (0-7, indexes into handler table)
  - Other bits: Type-specific flags
- **Byte 1**: Data byte (meaning depends on packet type)

### Button State Packets (Types 0, 1)

Stored in `CPANEL_RX_PACKET_BYTE_1` (0x8D94) and `CPANEL_RX_PACKET_BYTE_2` (0x8D95):
- First byte: Button segment identifier
- Second byte: Button state bitmap

## Response Handling

The main CPU processes responses via `Process_CPanel_Rx_Loop` which:
1. Checks if enough data is in the RX buffer
2. Extracts packet type from first byte
3. Dispatches to appropriate handler via jump table
4. Updates buffer indices and state flags

## Button Mapping

*Analysis in progress - mapping button indices to physical buttons.*

## LED Mapping

*Analysis in progress - mapping LED indices to physical LEDs.*

## Rotary Encoder Format

*Analysis in progress - determining encoder data format.*
