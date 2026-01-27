---
layout: page
title: Control Panel Protocol
permalink: /control-panel-protocol/
---

# Control Panel Serial Protocol - MAME HLE Implementation Guide

This document provides comprehensive information for implementing High Level Emulation (HLE) of the KN5000 control panel MCUs in MAME.

## 1. Overview

### Purpose of Control Panel MCUs

The KN5000 control panel uses two dedicated Mitsubishi M37471M2196S microcontrollers to handle:

- **Button scanning** - Matrix scanning of all front panel buttons
- **LED control** - Multiplexed driving of status LEDs
- **Rotary encoders** - Data wheel, pitch bend, and modulation wheels
- **Analog inputs** - Volume sliders and continuous controllers

### Why HLE is Needed

The control panel MCUs use **mask ROM** (M2196S suffix indicates a specific mask pattern). Without physical decapping and ROM extraction, the firmware is unavailable. However, the main CPU firmware extensively documents the communication protocol, making HLE feasible.

**HLE Strategy:**
1. Intercept serial commands from the main CPU
2. Maintain virtual button/LED/encoder state
3. Generate appropriate response packets
4. Interface with MAME input system for user interaction

## 2. Hardware Architecture

### MCU Identification

| Parameter | Value |
|-----------|-------|
| **Part Number** | Mitsubishi M37471M2196S |
| **Architecture** | 8-bit CMOS (Mitsubishi 740 series) |
| **Features** | Built-in A/D, Serial UART, 16 segment outputs |
| **Quantity** | 2 (CPL = Left panel, CPR = Right panel) |

### Physical Connections

```
Main CPU (TMP94C241F)                Control Panel MCUs
    Port F, SC1                    +---------+  +---------+
        |                          |   CPL   |  |   CPR   |
        |<----- SOUT --------------|   SOUT--|  |--SOUT   |
        |                          |         |  |         |
        |------ SIN -------------->|   SIN---|  |---SIN   |
        |                          |         |  |         |
        |------ SCLK1 ------------>|   CLK---|  |---CLK   |
        |                          |         |  |         |
        |------ CNTR1 ------------>|  CNTR1--|  |--CNTR1  |
        |                          +---------+  +---------+
        |
   PF.5 (INTA) <---- Interrupt from panels
   PF.6 (SCLK1) ---> Serial clock output / clock detect input
```

### Serial Interface Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Serial Channel** | SC1 (Serial Channel 1) | TMP94C241F UART |
| **Clock Source** | Internal, derived from fc=16MHz | |
| **TX Baud Rate** | 250 kHz | fc/16/4 (BR1CR=0x14) during data TX |
| **Initial Baud Rate** | 31.25 kHz | fc/64/8 (BR1CR=0x28) during init |
| **Data Format** | 8-bit, odd parity (disabled), async | SC1MOD, SC1CR config |
| **Flow Control** | Software (CNTR1 pin for chip select) | |

### Clock Configuration (from BR1CR register)

| BR1CR Value | Prescaler | Divider | Baud Rate | Usage |
|-------------|-----------|---------|-----------|-------|
| `0x14` | T2 (fc/16) | /4 | 250 kHz | Normal data transfer |
| `0x24` | T8 (fc/64) | /4 | 62.5 kHz | Idle/reset state |
| `0x28` | T8 (fc/64) | /8 | 31.25 kHz | Initialization |

## 3. Protocol Specification

### Command Format

All commands are **2-byte sequences** sent from main CPU to control panel MCUs:

```
Byte 0: Command/Address byte
Byte 1: Data/Parameter byte
```

The high 3 bits of the command byte (bits 7-5) select the target panel:

| Bits 7-5 | Binary | Target |
|----------|--------|--------|
| 0-3 | `000`-`011` | Left panel (CPL) |
| 4-7 | `100`-`111` | Right panel (CPR) |

### Complete Command Reference

#### Initialization Commands

| Command | Bytes | Purpose | Timing |
|---------|-------|---------|--------|
| `1F DA` | Init sequence 1 | Reset/sync left panel | 3000 loops wait |
| `1F 1A` | Init sequence 2 | Configure left panel | 3000 loops wait |
| `1D 00` | Init sequence 3 | Initialize left panel | 6000 loops wait |
| `DD 03` | Setup mode | Configure both panels | 6000 loops wait |
| `1E 80` | Init sequence 4 | Final init (left) | 9000 loops wait |

#### Query Commands

| Command | Bytes | Purpose | Expected Response |
|---------|-------|---------|-------------------|
| `20 00` | Ping left panel | Communication test | Any response = OK |
| `20 0B` | Poll left buttons | Read button segment 0x0B | Button state packet |
| `20 10` | Query left panel | Read status/sync | Sync packet |
| `E0 00` | Ping right panel | Communication test | Any response = OK |
| `E2 04` | Query right panel | Read specific register | Data packet |
| `E2 11` | Query right panel | Read specific register | Data packet |
| `E3 10` | Query right extended | Extended read | Multi-byte packet |

#### Data Commands

| Command | Bytes | Purpose |
|---------|-------|---------|
| `25 01` | Left panel data | Set/request data mode |
| `2B 00` | Init state array (left) | Initialize button state |
| `EB 00` | Init state array (right) | Initialize button state |

### Response Packet Format

Responses from control panel MCUs are processed by `CPanel_RX_ParseNext` at address `0xFC491A`.

#### Packet Type Encoding

The packet type is encoded in bits 5-3 of the first response byte:

```
Byte 0: [ X | X | Type2 | Type1 | Type0 | X | X | X ]
                 \___________|__________/
                    Packet type (0-7)
```

#### Packet Type Handlers

| Type | Bits 5-3 | Handler | Address | Purpose |
|------|----------|---------|---------|---------|
| 0 | `000` | `CPanel_RX_ButtonPacket` | 0xFC4985 | Button state (left panel) |
| 1 | `001` | `CPanel_RX_ButtonPacket` | 0xFC4985 | Button state (right panel) |
| 2 | `010` | `CPanel_RX_EncoderPacket` | 0xFC49E0 | Rotary encoder delta |
| 3 | `011` | `CPanel_RX_SyncPacket` | 0xFC4B10 | Sync/ACK |
| 4 | `100` | `CPanel_RX_SyncPacket` | 0xFC4B10 | Sync/ACK |
| 5 | `101` | `CPanel_RX_SyncPacket` | 0xFC4B10 | Sync/ACK |
| 6 | `110` | `CPanel_RX_MultiBytePacket` | 0xFC4A40 | Multi-byte data |
| 7 | `111` | `CPanel_RX_MultiBytePacket` | 0xFC4A40 | Multi-byte data |

### Button State Packet Format (Types 0, 1)

```
Byte 0: [ Panel | Type | Segment Index (bits 3-0 + bit 6) ]
Byte 1: [ Button bitmap - 8 buttons per segment ]
```

**Segment index calculation:**
- If bit 6 is set: `segment = (byte0 & 0x0F) + 0x10` (left panel offset)
- Otherwise: `segment = byte0 & 0x0F`

The handler at `CPanel_RX_ButtonPacket`:
1. Extracts segment index: `W = byte0 & 0x4F`
2. Calculates button array offset
3. XORs new state with previous to detect changes
4. Stores result in `CPANEL_LAST_EVENT_VALUE` for edge detection

### Encoder Packet Format (Type 2)

```
Byte 0: [ ID_hi[1:0] | 0 | 1 | 0 | ID_lo[2:0] ]
         bits 7-6     5   4   3   bits 2-0

Byte 1: [ Delta value (signed 8-bit) ]
```

**Encoder ID Encoding:**
- Bits 0-2 of byte 0 → bits 0-2 of encoder ID
- Bits 6-7 of byte 0 → bits 3-4 of encoder ID
- This gives a 5-bit encoder ID (0-31)

The encoder dispatch routine `CPanel_EncoderDispatch` (0xFC6C5F):
1. Extracts encoder ID: `ID = (byte0 & 0x07) | ((byte0 >> 3) & 0x18)`
2. Multiplies by 4 for jump table offset
3. Indexes into jump table at `ENCODER_HANDLER_TABLE` (0xEDA0BC)
4. Dispatches to encoder-specific handler
5. Returns 0xFFFF if invalid/no change

**Known Encoder IDs:**

| ID | Handler | Output Variable | Physical Control |
|----|---------|-----------------|------------------|
| 2 | `Encoder_ProcessModwheel` | `MIDI_CC_MODWHEEL_VALUE` | Modulation wheel |
| 5 | `Encoder_ProcessVolume` | `MIDI_CC_VOLUME_VALUE` | Volume slider |
| 25 | `Encoder_ProcessBreath` | `MIDI_CC_BREATH_VALUE` | Breath controller |
| 26 | `Encoder_ProcessFoot` | `MIDI_CC_FOOT_VALUE` | Foot controller |
| 27 | `Encoder_ProcessExpression` | `MIDI_CC_EXPRESSION_VALUE` | Expression pedal |
| 31 | `Encoder_ReturnValue` | Direct passthrough | Raw value output |
| 0-1,3-4,6-24,28-30 | `Encoder_ReturnOne` | Returns 1 | Unused |

**Encoder Processing:**
- Raw input values are inverted (`CPL A`) and stored in `ENCODER_RAW_*` variables
- Values are divided by 2 (`SRL 1, A`) and used as lookup table indices
- Lookup tables at `ENCODER_LUT_*` convert raw values to MIDI CC range (0-127)
- Change detection compares with previous value before storing

### Timing Requirements

| Operation | Delay | Method |
|-----------|-------|--------|
| Post-command wait | 6 system ticks | `DELAY_6_TICKS` (0xFC4213) |
| Init command wait | 3000 loop iterations | `DELAY_3000_LOOPS` (0xFC4118) |
| Ready check timeout | 200 attempts * 1500 loops | `CPanel_WaitTXReady` |

## 4. State Machine

### Serial Routine State Machine

The main CPU uses a state machine indexed by `CPANEL_STATE_MACHINE_INDEX` (address 0x8D8A) with values 0-10 (stored as byte offsets 0x00-0x28).

```
State Transition Diagram:

    ┌─────────────────────────────────────────────────────────────────┐
    │                                                                 │
    │  IDLE (0)                                                       │
    │    │                                                            │
    │    │ CPanel_SendCommand called                                  │
    │    ▼                                                            │
    │  ROUTINE_1 (1) ──► Start TX, check SCLK1                        │
    │    │                │                                           │
    │    │ SCLK1=1        │ SCLK1=0 (panel talking)                   │
    │    ▼                ▼                                           │
    │  ROUTINE_2 (2)    Back to IDLE (0)                              │
    │    │                                                            │
    │    │ TX byte, update LED index                                  │
    │    ▼                                                            │
    │  ROUTINE_3 (3) ──► Disable serial pins                          │
    │    │                                                            │
    │    ▼                                                            │
    │  ROUTINE_4 (4) ──► Continue TX, count down STATE_0_TO_17        │
    │    │                │                                           │
    │    │ count > 1      │ count <= 1                                │
    │    ▼                ▼                                           │
    │  ROUTINE_3 (loop)  ROUTINE_5 (5)                                │
    │                      │                                          │
    │                      ▼                                          │
    │                    ROUTINE_6 (6) ──► Check if more LED data     │
    │                      │       │                                  │
    │                      │ more  │ done                             │
    │                      ▼       ▼                                  │
    │                    ROUTINE_1  IDLE (0)                          │
    │                                                                 │
    │  ═══════════════════════════════════════════════════════════    │
    │                                                                 │
    │  ROUTINE_7 (8) ──► RX phase 1, first byte from panel            │
    │    │                                                            │
    │    │ Byte received, calculate STATE_0_TO_17                     │
    │    ▼                                                            │
    │  ROUTINE_8 (9) ──► RX phase 2, additional bytes                 │
    │    │                │                                           │
    │    │ count > 1      │ count <= 1                                │
    │    ▼                ▼                                           │
    │  ROUTINE_8 (loop)  IDLE (0)                                     │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘
```

### STATE_0_TO_17 Meaning

The variable `CPANEL_PACKET_BYTE_COUNT` (address 0x8D8B) tracks the expected byte count in multi-byte transfers:

| Value | Meaning |
|-------|---------|
| 0 | Idle/complete |
| 1 | Last byte expected |
| 2 | Standard 2-byte packet |
| 3-17 | Extended packet, N bytes remaining |

**Calculation (from received byte A):**
```c
if ((A & 0x3F) < 0x30) {
    STATE_0_TO_17 = 2;
} else {
    STATE_0_TO_17 = (A & 0x0F) + 3;  // 3 to 18 bytes
}
```

### Serial Routine Jump Table

Located at `CPANEL_STATE_MACHINE_TABLE` (0xFC4489):

| Offset | Routine | Address | Purpose |
|--------|---------|---------|---------|
| 0x00 | ROUTINE_0 | 0xFC47E9 | Idle state |
| 0x04 | ROUTINE_1 | 0xFC44F9 | Start TX sequence |
| 0x08 | ROUTINE_2 | 0xFC45A8 | Send LED data byte |
| 0x0C | ROUTINE_3 | 0xFC4544 | Disable pins, next byte |
| 0x10 | ROUTINE_4 | 0xFC460D | Continue LED data |
| 0x14 | ROUTINE_5 | 0xFC4573 | Finalize LED group |
| 0x18 | ROUTINE_6 | 0xFC4672 | Check for more data |
| 0x1C | ROUTINE_0 | 0xFC47E9 | (duplicate) Idle |
| 0x20 | ROUTINE_7 | 0xFC46EA | RX first byte |
| 0x24 | ROUTINE_8 | 0xFC4767 | RX subsequent bytes |
| 0x28 | ROUTINE_0 | 0xFC47E9 | (duplicate) Unreachable |

## 5. HLE Implementation Guide

### MAME Device Class Structure

```cpp
// kn5000_cpanel.h

#ifndef MAME_TECHNICS_KN5000_CPANEL_H
#define MAME_TECHNICS_KN5000_CPANEL_H

#pragma once

class kn5000_cpanel_device : public device_t
{
public:
    kn5000_cpanel_device(const machine_config &mconfig, const char *tag, device_t *owner, uint32_t clock);

    // Serial interface
    void sin_w(int state);           // Serial data in (from main CPU)
    int sout_r();                    // Serial data out (to main CPU)
    void sclk_w(int state);          // Serial clock
    void cntr_w(int state);          // Chip select / control

    // Configuration
    auto sout_callback() { return m_sout_cb.bind(); }
    auto irq_callback() { return m_irq_cb.bind(); }

protected:
    virtual void device_start() override;
    virtual void device_reset() override;
    virtual ioport_constructor device_input_ports() const override;

private:
    // Serial state
    uint8_t m_rx_shift;              // Receive shift register
    uint8_t m_tx_shift;              // Transmit shift register
    int m_bit_count;                 // Bit counter
    bool m_sclk_state;               // Previous clock state

    // Command processing
    uint8_t m_cmd_buffer[2];         // 2-byte command buffer
    int m_cmd_index;                 // Current command byte index

    // Panel state
    uint8_t m_button_state[16];      // 16 segments * 8 buttons
    uint8_t m_led_state[60];         // LED array (60 bytes)
    int8_t m_encoder_delta[8];       // Rotary encoder deltas

    // Callbacks
    devcb_write_line m_sout_cb;
    devcb_write_line m_irq_cb;

    // Internal methods
    void process_command();
    void send_response(const uint8_t *data, int length);
    uint8_t get_button_segment(int segment);
    void update_leds(int index, uint8_t pattern);
};

DECLARE_DEVICE_TYPE(KN5000_CPANEL, kn5000_cpanel_device)

#endif // MAME_TECHNICS_KN5000_CPANEL_H
```

### Key Callbacks to Implement

```cpp
// Command processing
void kn5000_cpanel_device::process_command()
{
    uint8_t cmd = m_cmd_buffer[0];
    uint8_t data = m_cmd_buffer[1];
    uint8_t response[16];
    int resp_len = 0;

    // Determine packet type from high bits
    bool is_right_panel = (cmd & 0xE0) >= 0x80;  // Bits 7-5 >= 4

    switch (cmd)
    {
    // Initialization commands
    case 0x1F:  // Init (left panel)
    case 0x1D:
    case 0x1E:
    case 0xDD:  // Setup
        // Acknowledge with sync packet
        response[0] = 0x18 | (is_right_panel ? 0x80 : 0);  // Type 3 = sync
        response[1] = 0x00;
        resp_len = 2;
        break;

    // Query commands
    case 0x20:  // Query left panel
    case 0xE0:  // Query right panel
        if (data == 0x00) {
            // Ping - respond with sync
            response[0] = 0x18;
            response[1] = 0x00;
            resp_len = 2;
        } else if (data == 0x0B || data == 0x10) {
            // Button state query
            // NOTE: Panel selection is via bit 6, NOT the type field!
            // Bit 6 = 0: right panel, Bit 6 = 1: left panel
            int segment = data & 0x0F;
            response[0] = (is_right_panel ? 0x00 : 0x40) | segment;  // Bit 6 for left panel
            response[1] = get_button_segment(segment + (is_right_panel ? 0 : 16));
            resp_len = 2;
        }
        break;

    case 0x25:  // Left data command
    case 0xE2:
    case 0xE3:
        // Extended data - respond appropriately
        response[0] = 0x18;  // Sync
        response[1] = data;
        resp_len = 2;
        break;

    case 0x2B:  // Init state array (left)
    case 0xEB:  // Init state array (right)
        // Send all button segments
        // NOTE: Bit 6 selects panel (0=right, 1=left)
        for (int seg = 0; seg < 16; seg++) {
            response[0] = seg | (is_right_panel ? 0x00 : 0x40);  // Bit 6 for left panel
            response[1] = get_button_segment(seg + (is_right_panel ? 0 : 16));
            send_response(response, 2);
        }
        return;
    }

    if (resp_len > 0) {
        send_response(response, resp_len);
    }
}
```

### Button State Reporting Format

Buttons are organized in 11 segments per panel, with 8 buttons per segment.

#### Control Panel Right (CPR) Button Mapping

| Segment | Bit 0 | Bit 1 | Bit 2 | Bit 3 | Bit 4 | Bit 5 | Bit 6 | Bit 7 |
|---------|-------|-------|-------|-------|-------|-------|-------|-------|
| **CPR_SEG0** | - | - | - | - | - | TRANSPOSE - | TRANSPOSE + | - |
| **CPR_SEG1** | ORGAN & ACCORDION | ORCHESTRAL PAD | SYNTH | BASS | DIGITAL DRAWBAR | ACCORDION REGISTER | GM SPECIAL | DRUM KITS |
| **CPR_SEG2** | PIANO | GUITAR | STRINGS & VOCAL | BRASS | FLUTE | SAX & REED | MALLET & ORCH PERC | WORLD PERC |
| **CPR_SEG3** | SUSTAIN | DIGITAL EFFECT | DSP EFFECT | DIGITAL REVERB | ACOUSTIC ILLUSION | - | - | - |
| **CPR_SEG4** | LEFT | RIGHT 2 | RIGHT 1 | ENTERTAINER | CONDUCTOR: LEFT | CONDUCTOR: RIGHT 2 | CONDUCTOR: RIGHT 1 | TECHNI CHORD |
| **CPR_SEG5** | - | - | - | SEQUENCER: PLAY | SEQUENCER: EASY REC | SEQUENCER: MENU | - | - |
| **CPR_SEG6** | PM 1 | PM 2 | PM 3 | PM 4 | PM 5 | PM 6 | PM 7 | PM 8 |
| **CPR_SEG7** | PM: SET | PM: NEXT BANK | PM: BANK VIEW | - | - | - | - | - |
| **CPR_SEG8** | - | - | - | R1/R2 OCTAVE - | R1/R2 OCTAVE + | START/STOP | SYNCHRO & BREAK | TAP TEMPO |
| **CPR_SEG9** | - | - | - | - | - | - | MEMORY A | MEMORY B |
| **CPR_SEG10** | - | - | MENU: SOUND | MENU: CONTROL | MENU: MIDI | MENU: DISK | - | - |

#### Control Panel Left (CPL) Button Mapping

| Segment | Bit 0 | Bit 1 | Bit 2 | Bit 3 | Bit 4 | Bit 5 | Bit 6 | Bit 7 |
|---------|-------|-------|-------|-------|-------|-------|-------|-------|
| **CPL_SEG0** | STANDARD ROCK | R & ROLL & BLUES | POP & BALLAD | FUNK & FUSION | SOUL & MODERN DANCE | BIG BAND & SWING | JAZZ COMBO | - |
| **CPL_SEG1** | COMPOSER: MEMORY | COMPOSER: MENU | SOUND ARRANGER: SET | SOUND ARRANGER: ON/OFF | MUSIC STYLIST | FADE IN | FADE OUT | - |
| **CPL_SEG2** | FILL IN 1 | FILL IN 2 | INTRO & ENDING 1 | INTRO & ENDING 2 | - | - | PAGE DOWN | PAGE UP |
| **CPL_SEG3** | DEMO | MSP BANK | MSP MENU | MSP STOP/RECORD | - | - | - | - |
| **CPL_SEG4** | VARIATION 1 | VARIATION 2 | VARIATION 3 | VARIATION 4 | MUSIC STYLE ARRANGER | SPLIT POINT | AUTO PLAY CHORD | - |
| **CPL_SEG5** | MSP 1 | MSP 2 | MSP 3 | MSP 4 | MSP 5 | MSP 6 | - | - |
| **CPL_SEG6** | U.S. TRAD | COUNTRY | LATIN | MARCH & WALTZ | PARTY TIME | SHOWTIME & TRAD DANCE | WORLD | CUSTOM |
| **CPL_SEG7** | RIGHT 5 | RIGHT 4 | DISPLAY HOLD | EXIT | DOWN 7 | UP 7 | DOWN 8 | UP 8 |
| **CPL_SEG8** | RIGHT 3 | RIGHT 2 | RIGHT 1 | - | DOWN 5 | UP 5 | DOWN 6 | UP 6 |
| **CPL_SEG9** | LEFT 5 | LEFT 4 | LEFT 3 | - | DOWN 3 | UP 3 | DOWN 4 | UP 4 |
| **CPL_SEG10** | LEFT 2 | LEFT 1 | HELP | OTHER PARTS/TR | DOWN 1 | UP 1 | DOWN 2 | UP 2 |

**Known button combinations (from firmware):**

| Segment | Bitmask | Buttons | Effect |
|---------|---------|---------|--------|
| CPL_SEG4 | 0x6C | AUTO PLAY CHORD + SPLIT POINT + VAR4 + VAR3 | Display software build numbers |
| CPR_SEG1 | 0x70 | GM SPECIAL + ACCORDION REGISTER + DIGITAL DRAWBAR | Display firmware version |
| CPL_SEG6 | 0x38 | SHOWTIME & TRAD DANCE + PARTY TIME + MARCH & WALTZ | Unknown function |
| CPR_SEG6 | 0x0F | PM 1 + PM 2 + PM 3 + PM 4 | Firmware update mode |

### LED Control Interface

LEDs are controlled via the `CPANEL_LED_TX_BUFFER` array (60 bytes at 0x8E01):

```cpp
void kn5000_cpanel_device::update_leds(int index, uint8_t pattern)
{
    // Index wraps at 0x3C (60)
    index %= 60;
    m_led_state[index] = pattern;

    // Map LED index to physical LEDs
    // The LED array is transmitted in 2-byte sequences
    // Byte 0: Row select (bits 5-0 = row, bits 7-6 = panel select)
    // Byte 1: Column pattern (which LEDs in row are lit)

    // Update MAME output for visual feedback
    for (int bit = 0; bit < 8; bit++) {
        machine().output().set_indexed_value("led", index * 8 + bit, BIT(pattern, bit));
    }
}
```

#### Control Panel Right (CPR) LED Mapping

| Row | Bit 0 | Bit 1 | Bit 2 | Bit 3 | Bit 4 | Bit 5 | Bit 6 | Bit 7 |
|-----|-------|-------|-------|-------|-------|-------|-------|-------|
| **0x00** | SUSTAIN | DIGITAL EFFECT | DSP EFFECT | DIGITAL REVERB | ACOUSTIC ILLUSION | SEQUENCER: PLAY | SEQUENCER: EASY REC | SEQUENCER: MENU |
| **0x01** | PIANO | GUITAR | STRINGS & VOCAL | BRASS | FLUTE | SAX & REED | MALLET & ORCH PERC | WORLD PERC |
| **0x02** | ORGAN & ACCORDION | ORCHESTRAL PAD | SYNTH | BASS | DIGITAL DRAWBAR | ACCORDION REGISTER | GM SPECIAL | DRUM KITS |
| **0x03** | PM 1 | PM 2 | PM 3 | PM 4 | PM 5 | PM 6 | PM 7 | PM 8 |
| **0x04** | PART: LEFT | PART: RIGHT 2 | PART: RIGHT 1 | ENTERTAINER | COND: LEFT | COND: RIGHT 2 | COND: RIGHT 1 | TECHNI CHORD |
| **0x08** | MENU: SOUND | MENU: CONTROL | MENU: MIDI | MENU: DISK | - | - | - | - |
| **0x0A** | MEMORY A | MEMORY B | - | - | - | - | - | - |
| **0x0B** | SYNCHRO & BREAK | R1/R2 OCTAVE - | R1/R2 OCTAVE + | BANK VIEW | - | - | - | - |
| **0x0C** | START/STOP BEAT 1 | START/STOP BEAT 2 | START/STOP BEAT 3 | START/STOP BEAT 4 | - | - | - | - |

#### Control Panel Left (CPL) LED Mapping

| Row | Bit 0 | Bit 1 | Bit 2 | Bit 3 | Bit 4 | Bit 5 | Bit 6 | Bit 7 |
|-----|-------|-------|-------|-------|-------|-------|-------|-------|
| **0xC0** | COMPOSER: MEMORY | COMPOSER: MENU | SOUND ARR: SET | SOUND ARR: ON/OFF | MUSIC STYLIST | FADE IN | FADE OUT | DISPLAY HOLD |
| **0xC1** | U.S. TRAD | COUNTRY | LATIN | MARCH & WALTZ | PARTY TIME | SHOWTIME & TRAD DANCE | WORLD | CUSTOM |
| **0xC2** | STANDARD ROCK | R & ROLL & BLUES | POP & BALLAD | FUNK & FUSION | SOUL & MODERN DANCE | BIG BAND & SWING | JAZZ COMBO | MSP: MENU |
| **0xC3** | VARIATION 1 | VARIATION 2 | VARIATION 3 | VARIATION 4 | MUSIC STYLE ARRANGER | AUTO PLAY CHORD | - | - |
| **0xC4** | FILL IN 1 | FILL IN 2 | INTRO & ENDING 1 | INTRO & ENDING 2 | SPLIT POINT (LEFT) | SPLIT POINT (CENTER) | SPLIT POINT (RIGHT) | TEMPO/PROGRAM |
| **0xC8** | OTHER PARTS/TR | - | - | - | - | - | - | - |

### Rotary Encoder Format

Encoders send signed delta values via Type 2 packets:

```cpp
void kn5000_cpanel_device::process_encoder(int encoder_id, int8_t delta)
{
    // Known Encoder IDs (from firmware analysis):
    // 2: Data wheel / jog wheel -> ENCODER_0_OUTPUT
    // 5: Volume slider / expression -> ENCODER_1_OUTPUT, MIDI_CC_VOLUME_VALUE
    // Other IDs (0-1, 3-4, 6-31) return 0xFFFF (no handler)

    m_encoder_delta[encoder_id] += delta;

    // Report encoder change
    // Byte 0 format: [ ID_hi[1:0] | 0 | 1 | 0 | ID_lo[2:0] ]
    //                  bits 7-6     5   4   3   bits 2-0
    // Type 2 = bits 5-3 = 010 = 0x10
    uint8_t response[2];
    response[0] = 0x10 | (encoder_id & 0x07) | ((encoder_id & 0x18) << 3);  // Type 2 + encoder ID
    response[1] = delta;
    send_response(response, 2);
}
```

### MIDI Controller Output

Encoder and analog input values are converted to MIDI Control Change messages and stored in RAM variables before being sent to the sound engine:

**Controller Mapping:**

| Variable | MIDI CC# | Controller Name |
|----------|----------|-----------------|
| `MIDI_CC_EXPRESSION_VALUE` | 0 | Bank Select MSB / Expression |
| `MIDI_CC_MODWHEEL_VALUE` | 1 | Modulation Wheel |
| `MIDI_CC_BREATH_VALUE` | 2 | Breath Controller |
| `MIDI_CC_FOOT_VALUE` | 4 | Foot Controller |
| `MIDI_CC_VOLUME_VALUE` | 7 | Volume (estimated) |

**Change Detection:**

The `*_PENDING` variants (e.g., `MIDI_CC_MODWHEEL_PENDING`) use bit 7 as a "value changed" flag:
- When an encoder/ADC value changes, bit 7 is set
- The MIDI output routine checks bit 7, sends the value if set, then clears bit 7
- This prevents redundant MIDI messages for unchanged values

**MIDI Message Format (at 0x9127-0x912A):**

| Address | Field | Example |
|---------|-------|---------|
| 0x9127 | Status byte | 0xB0 (Control Change, channel 0) |
| 0x9128 | Controller # | 0x01 (Modulation) |
| 0x9129 | Value | 0x00-0x7F |
| 0x912A | Velocity/Range | 0x7F |

## 6. Memory Map

### Control Panel RAM Variables

| Address | Name | Size | Description |
|---------|------|------|-------------|
| 0x8D8A | `CPANEL_STATE_MACHINE_INDEX` | byte | Current serial state machine index (0-10) |
| 0x8D8B | `CPANEL_PACKET_BYTE_COUNT` | byte | Byte count for multi-byte packets |
| 0x8D8C | `CPANEL_TX_RX_FLAGS` | byte | Flags: bits 0,1,2,4,6,7 used |
| 0x8D8E | `PFCR_VALUE` | byte | Shadow of Port F Control Register |
| 0x8D8F | `PFFC_VALUE` | byte | Shadow of Port F Function Control |
| 0x8D92 | `CPANEL_PROTOCOL_FLAGS` | byte | Flags: bits 0,1,2,3,6,7 used |
| 0x8D93 | `CPANEL_PANEL_DETECT_FLAGS` | byte | Communication test results |
| 0x8D94 | `CPANEL_RX_PACKET_BYTE_1` | byte | First byte of received packet |
| 0x8D95 | `CPANEL_RX_PACKET_BYTE_2` | byte | Second byte of received packet |
| 0x8D96 | `CPANEL_LAST_EVENT_VALUE` | byte | Changed button bits (XOR result) |
| 0x8D97 | `CPANEL_COUNTER_DOWN_FROM_200` | byte | Ready check timeout counter |
| 0x8D98 | `CPANEL_COUNTER_UP_TO_20` | byte | General counter |
| 0x8D9A | `CPANEL_COUNTER_UP_TO_42` | byte | Main loop iteration counter |
| 0x8D9B | `TIMESTAMP_FOR_DELAY` | word | Timestamp for delay routines |
| 0x8D9D | `CPANEL_RX_READ_PTR` | word | Backup of RX buffer position |
| 0x8D9F | `CPANEL_RX_WRITE_PTR` | word | Current RX buffer write position |
| 0x8DA1 | `CPANEL_RX_DATA` | 92 bytes | Circular RX buffer |
| 0x8DFD | `CPANEL_LED_READ_PTR` | word | LED TX buffer read pointer |
| 0x8DFF | `CPANEL_LED_WRITE_PTR` | word | LED TX buffer write pointer |
| 0x8E01 | `CPANEL_LED_TX_BUFFER` | 60 bytes | LED state TX buffer |
| 0x8E4A | `STATE_OF_CPANEL_BUTTONS` | 16 bytes | Button state (right panel) |
| 0x8E5A | `STATE_OF_CPANEL_BUTTONS_LEFT` | 16 bytes | Button state (left panel) |
| 0x8EE0 | `MIDI_CC_MODWHEEL_PENDING` | byte | Modulation value with change flag (bit 7) |
| 0x8EE2 | `MIDI_CC_EXPRESSION_PENDING` | byte | Expression value with change flag (bit 7) |
| 0x8EE4 | `MIDI_CC_MODWHEEL_VALUE` | byte | Current modulation wheel value (CC#1) |
| 0x8EE6 | `MIDI_CC_EXPRESSION_VALUE` | byte | Current expression value (CC#0) |
| 0x8EE8 | `MIDI_CC_BREATH_VALUE` | byte | Breath controller value (CC#2?) |
| 0x8EEA | `MIDI_CC_FOOT_VALUE` | byte | Foot controller value (CC#4?) |
| 0x8EF4 | `MIDI_CC_VOLUME_VALUE` | byte | Volume controller value |
| 0x8EFC | `ENCODER_0_LAST_VALUE` | byte | Previous encoder 0 reading |
| 0x8EFE | `ENCODER_1_LAST_VALUE` | byte | Previous encoder 1 reading |
| 0x8F04 | `ENCODER_0_STATUS` | byte | Encoder 0 flags (bit 3 = changed) |
| 0x8F06 | `ENCODER_1_STATUS` | byte | Encoder 1 flags (bit 3 = changed) |
| 0x8F10 | `ENCODER_0_OUTPUT` | 2 bytes | Encoder 0 output (value + flags) |
| 0x8F16 | `ENCODER_1_OUTPUT` | 2 bytes | Encoder 1 output (value + flags) |
| 0x8F18 | `ENCODER_STATE_BASE` | struct | Base of encoder state structure |
| 0x8F38 | `CPANEL_LEDS__ROW_AND_PATTERN_BYTES` | word | Current LED row/pattern |

### Circular Buffer Parameters

| Buffer | Base Address | Size | Modulus | Notes |
|--------|--------------|------|---------|-------|
| `CPANEL_RX_RING_BUFFER` | 0x8DA1 | 92 bytes | 0x5C | RX from panels |
| `CPANEL_RX_EVENT_QUEUE` | 0x200AD | 128 bytes | 0x80 | Processed button/encoder events |
| `CPANEL_LED_EVENT_QUEUE` | 0x20137 | 128 bytes | 0x80 | LED command queue |

### Flag Definitions

#### CPANEL_TX_RX_FLAGS (0x8D8C)

| Bit | Usage |
|-----|-------|
| 0 | TX in progress |
| 1 | TX active |
| 2 | RX flag (set/clear by CPanel_RX_* functions) |
| 4 | Extended mode (never set?) |
| 6 | Initialized |
| 7 | Reserved |

#### CPANEL_PROTOCOL_FLAGS (0x8D92)

| Bit | Usage |
|-----|-------|
| 0 | RX buffer has space / ready |
| 1 | TX collision detected |
| 2 | Unknown |
| 3 | Sync packet received |
| 6 | Interrupt pending |
| 7 | Ready to send |

#### CPANEL_PANEL_DETECT_FLAGS (0x8D93)

| Bit | Usage |
|-----|-------|
| 0 | Left panel responded to ping |
| 3 | (bit 4 in some code) Right panel responded to ping |

## 7. Code Reference

### Initialization Routines

| Address | Name | Description |
|---------|------|-------------|
| 0xFC3EF5 | `CPanel_InitHardware` | Main initialization sequence |
| 0xFC3FA9 | `CPanel_SendInitSequence` | Send init commands (1F 1A, 1D 00, DD 03, 1E 80) |
| 0xFC4021 | `CPanel_InitLEDBuffer` | Configure serial port, init LED array |
| 0xFC42FB | `CPanel_InitButtonState` | Initialize button state arrays |

### Command Send/Receive

| Address | Name | Description |
|---------|------|-------------|
| 0xFC4374 | `CPanel_WaitTXReady` | TX ready check with timeout |
| 0xFC43D9 | `CPanel_SendCommand` | Send 2-byte command |
| 0xFC490E | `CPanel_RX_ProcessWithFlag` | Process RX with flag set |
| 0xFC4915 | `CPanel_RX_Process` | Process RX with flag clear |
| 0xFC491A | `CPanel_RX_DispatchLoop` | Initialize RX processing pointers |
| 0xFC492B | `CPanel_RX_ParseNext` | Main RX packet dispatch loop |

### Packet Handlers

| Address | Name | Description |
|---------|------|-------------|
| 0xFC4965 | `CPanel_RX_PacketHandlers` | 8-entry jump table for packet types |
| 0xFC4985 | `CPanel_RX_ButtonPacket` | Process button state packets |
| 0xFC49E0 | `CPanel_RX_EncoderPacket` | Process rotary encoder packets |
| 0xFC4A40 | `CPanel_RX_MultiBytePacket` | Process multi-byte packets |
| 0xFC4B10 | `CPanel_RX_SyncPacket` | Process sync/ACK packets |

### LED Transmission

| Address | Name | Description |
|---------|------|-------------|
| 0xFC4B2D | `CPanel_UpdateLEDs` | Main LED transmission routine |
| 0xFC4B85 | `CPanel_LED_PacketHandlers` | 4-entry jump table for LED types |

### Serial Interrupt Handlers

| Address | Name | Description |
|---------|------|-------------|
| 0xFC44B5 | `INTTX1_HANDLER` | Serial TX complete interrupt |
| 0xFC44D7 | `INTRX1_HANDLER` | Serial RX complete interrupt |
| 0xFC4489 | `CPANEL_STATE_MACHINE_TABLE` | Jump table for state machine |

### Helper Routines

| Address | Name | Description |
|---------|------|-------------|
| 0xFC4C08 | `CPanel_IncRXPtr` | Increment RX buffer pointer (modulo 92) |
| 0xFC4C13 | `CPanel_IncLEDPtr` | Increment LED buffer pointer (modulo 60) |
| 0xFC4C1E | `CPanel_IncEventPtr` | Increment event queue pointer (modulo 128) |
| 0xFC4C29 | `CPanel_DecEventPtr` | Decrement event queue pointer (modulo 128) |
| 0xFC6C5F | `CPanel_EncoderDispatch` | Dispatch to encoder-specific handler via jump table |

### Delay Routines

| Address | Name | Iterations/Ticks |
|---------|------|------------------|
| 0xFC40F4 | `DELAY_10_LOOPS` | 10 |
| 0xFC4100 | `DELAY_300_LOOPS` | 300 |
| 0xFC410C | `DELAY_1500_LOOPS` | 1500 |
| 0xFC4118 | `DELAY_3000_LOOPS` | 3000 |
| 0xFC4213 | `DELAY_6_TICKS` | 6 system ticks |
| 0xFC4225 | `DELAY_51_TICKS` | 51 system ticks |

### Button Detection

| Address | Name | Description |
|---------|------|-------------|
| 0xFC4160 | `Detect_Control_Panel_button_combos` | Check for special button combinations |
| 0xFC4265 | `CPanel_PollButtonState_Loop` | Main button polling loop |
| 0xFC4289 | `CPanel_CheckEncoderState` | Check encoder value changes |

## 8. Protocol Gaps (What We Don't Know)

### LED Packet Format

The LED handler uses bits 4-5 of the first byte to dispatch to one of 4 handlers via `CPanel_LED_PacketHandlers` (0xFC4B85). Further investigation needed to understand exact LED packet structure.

### Multi-byte Packet Purpose (Types 6, 7)

The `CPanel_RX_MultiBytePacket` handler has complex decoding logic:
- Calculates byte count from `(byte0 & 0x0F) + 1`
- Uses bit 4 for mode selection
- Purpose and expected data format unknown

### ~~Button-to-Segment Mapping~~ (RESOLVED)

**Complete button mapping now documented** - see "Button State Reporting Format" section above.
- 11 segments per panel (CPR_SEG0-10 and CPL_SEG0-10)
- Each segment holds 8 button states
- Full mapping extracted from MAME INPUT_PORTS definitions

### ~~LED Row Mapping~~ (RESOLVED)

**Complete LED mapping now documented** - see "LED Control Interface" section above.
- Right panel: rows 0x00-0x0C
- Left panel: rows 0xC0-0xC8
- Full mapping extracted from MAME driver cpanel_leds_w function

### Encoder Physical Mapping (RESOLVED)

Six encoder IDs have dedicated processing handlers:
- **ID 2**: Modulation wheel → `MIDI_CC_MODWHEEL_VALUE`
- **ID 5**: Volume slider → `MIDI_CC_VOLUME_VALUE`
- **ID 25**: Breath controller → `MIDI_CC_BREATH_VALUE`
- **ID 26**: Foot controller → `MIDI_CC_FOOT_VALUE`
- **ID 27**: Expression pedal → `MIDI_CC_EXPRESSION_VALUE`
- **ID 31**: Direct passthrough (raw value)

Physical assignments confirmed from firmware analysis. Remaining IDs (0-1, 3-4, 6-24, 28-30) return 1 (unused).

### Baud Rate Transitions

The serial channel switches between rates during operation:
- 31.25 kHz during initialization
- 250 kHz during normal operation
- Exact timing/trigger for rate switches not fully traced

### Remaining Undisassembled Routines

| Address | Size | Context |
|---------|------|---------|
| 0xFC4B95 | Unknown | Called from LED path |
| 0xFC4BC5 | Unknown | Called from LED path |

Note: Encoder handlers (0xFC6C80-0xFC6E41) have been fully disassembled.

## 9. Configuration Switches

### Main CPU Checking Device (CN11)

| Setting | Value | Effect |
|---------|-------|--------|
| On | 0x00 | Enable diagnostic mode |
| Off | 0x01 | Normal operation (default) |

### Sub CPU Checking Device (CN12)

| Setting | Value | Effect |
|---------|-------|--------|
| On | 0x00 | Enable diagnostic mode |
| Off | 0x01 | Normal operation (default) |

### Computer Interface Selection (COM_SELECT)

Read from main CPU Port Z bits 4-7:

| Value | Selection |
|-------|-----------|
| 0xE0 | MIDI |
| 0xD0 | PC1 |
| 0xB0 | PC2 |
| 0x70 | Mac |

### Area Selection

Read from main CPU Port H:

| Value | Regions |
|-------|---------|
| 0x02 | Thailand, Indonesia, Iran, U.A.E., Panama, Argentina, Peru, Brazil |
| 0x04 | USA, Mexico |
| 0x06 | All other regions (default) |

**Complete region list (from service documentation):**

| Code | Region |
|------|--------|
| (M) | U.S.A. |
| (MC) | Canada |
| (XM) | Mexico |
| (EN) | Norway, Sweden, Denmark, Finland |
| (EH) | Holland, Belgium |
| (EF) | France, Italy |
| (EZ) | Germany |
| (EW) | Switzerland |
| (EA) | Austria |
| (EP) | Spain, Portugal, Greece, South Africa |
| (EK) | United Kingdom |
| (XL) | New Zealand |
| (XR) | Australia |
| (XS) | Malaysia |
| (MD) | Saudi Arabia, Hong Kong, Kuwait |
| (XT) | Taiwan |
| (X) | Thailand, Indonesia, Iran, U.A.E., Panama, Argentina, Peru, Brazil |
| (XP) | Philippines |
| (XW) | Singapore |

## References

- **Source Code**: `/home/fsanches/claude_jail/kn5000-roms-disasm/maincpu/kn5000_v10_program.asm`
- **Protocol Analysis**: `/home/fsanches/claude_jail/kn5000-roms-disasm/docs/cpanel_protocol_analysis.txt`
- **Hardware Architecture**: [Hardware Architecture Page]({{ site.baseurl }}/hardware-architecture/)
- **Service Manual**: EMID971655 A5 (Schematics II-9 through II-38)
- **MAME Driver**: `/home/fsanches/claude_jail/kn5000-roms-disasm/mame_driver/src/mame/matsushita/kn5000.cpp`
- **MAME Control Panel HLE**: `/home/fsanches/claude_jail/kn5000-roms-disasm/mame_driver/src/mame/matsushita/kn5000_cpanel.cpp`
