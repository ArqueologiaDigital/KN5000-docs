---
layout: page
title: "Debugging the Serial Protocol: A Deep Dive"
permalink: /serial-debugging/
---

# Debugging the KN5000 Serial Communication: A Journey Through Synchronous Serial Timing

*January 2026*

This post documents our debugging journey attempting to get the MAME driver's control panel HLE (High Level Emulation) communicating correctly with the emulated TMP94C241 CPU. What started as a simple "serial communication isn't working" bug turned into a deep exploration of synchronous serial timing edge cases.

## The Problem

The KN5000 keyboard uses a synchronous serial protocol between the main CPU (TMP94C241) and the control panel MCUs (two Mitsubishi M37471M2196S chips that handle buttons, LEDs, and rotary encoders). Since we don't have ROM dumps for the control panel MCUs, we're using High Level Emulation - our code pretends to be the MCUs by implementing the protocol based on reverse engineering.

During boot, the keyboard was showing "ERROR in CPU data transmission" - the main CPU couldn't establish communication with the control panel.

## Understanding the Protocol

The TMP94C241 CPU uses I/O Interface Mode for serial communication - a synchronous protocol where:
- The CPU is the **master**, generating the clock signal (SCLK)
- The control panel is the **slave**, responding to clock edges
- Data is transmitted LSB-first, 8 bits per byte
- **Rising edge**: Both sides sample incoming data
- **Falling edge**: Both sides output the next bit

The clock is derived from Timer 2's output compare trigger (TO2), giving us a 31250 Hz baud rate.

## Issue 1: Clock Not Being Generated

Our first discovery was that clock pulses weren't reaching the control panel at all. The `TO2_trigger` function was checking the wrong condition:

```cpp
// WRONG: Checking if IOC bit is SET
if ((m_serial_mode & 3) == 0 && BIT(m_serial_control, 1))

// CORRECT: IOC=0 means master mode (SCLK output)
if ((m_serial_mode & 3) == 0 && !BIT(m_serial_control, 1))
```

The IOC bit in the serial control register means:
- **IOC=0**: SCLK is an output (master mode)
- **IOC=1**: SCLK is an input (slave mode)

The firmware sets `serial_control=0x01` (IOC=0, master mode), but we were checking for IOC=1.

## Issue 2: Wrong Idle State

Serial lines idle HIGH, but we had initialized TXD to 0:

```cpp
// WRONG
m_txd(0)

// CORRECT
m_txd(1)  // Idle state is HIGH for serial lines
```

This caused the control panel to receive `0x00` during idle instead of `0xFF`.

## Issue 3: Byte Boundary Synchronization

This is where things got interesting. Even with correct clock generation and idle state, the control panel was receiving garbage. The issue: **byte boundaries weren't synchronized**.

In synchronous serial, both sides need to agree on where each byte starts and ends. The clock runs continuously, so if one side is at bit 3 while the other is at bit 7, they'll never receive correct data.

### The `tx_start` Callback

Our first solution was to add a callback from the CPU to the control panel signaling "I'm starting a new byte":

```cpp
void tmp94c241_serial_device::scNbuf_w(uint8_t data)
{
    m_tx_shift_register = data;
    m_tx_clock_count = 8;
    m_tx_start_cb(1);  // Signal new byte start
    m_txd_cb(m_tx_shift_register & 1);  // Pre-output bit 0
}
```

The control panel would reset its receive counter when receiving this signal.

## Issue 4: Bit 0 Output Twice

After adding byte sync, we noticed the control panel was receiving shifted data. Tracing through the logs revealed that **bit 0 was being output twice**:

1. `scNbuf_w`: Output bit 0 immediately
2. First falling edge: Output bit 0 again, then shift

The receiver would sample bit 0 on the first rising edge, then sample bit 0 *again* on the second rising edge (since the falling edge hadn't advanced to bit 1 yet).

### The Skip-First-Falling Fix

The solution was to skip the first falling edge after a buffer write:

```cpp
void tmp94c241_serial_device::scNbuf_w(uint8_t data)
{
    m_tx_shift_register = data;
    m_tx_clock_count = 7;  // 7 more bits after pre-output
    m_txd_cb(m_tx_shift_register & 1);  // Pre-output bit 0
    m_tx_skip_first_falling = true;  // Skip next falling edge
}
```

But this introduced another bug...

## Issue 5: Clock Phase Matters

The skip logic worked when the clock was HIGH at the time of the buffer write, but failed when the clock was LOW:

**Clock HIGH when writing:**
1. Buffer write: output bit 0
2. Falling edge: skip (bit 0 stays on line)
3. Rising edge: receiver samples bit 0 ✓
4. Falling edge: output bit 1
5. Rising edge: receiver samples bit 1 ✓

**Clock LOW when writing:**
1. Buffer write: output bit 0
2. Rising edge: receiver samples bit 0 ✓
3. Falling edge: skip (bit 0 stays on line)
4. Rising edge: receiver samples bit 0 AGAIN ✗

The fix: only skip if the clock is HIGH when writing:

```cpp
m_tx_skip_first_falling = (m_sioclk_state == 1);
```

## Issue 6: Repeated Writes During Init

Even with all timing fixed, the control panel was only receiving `0xFF`. The firmware was in an initialization loop, repeatedly re-writing `0x45` to the serial buffer before a complete byte could be transmitted.

Each write fired `tx_start`, resetting the control panel's receive counter. The panel would receive 2-3 bits, get reset, receive 2-3 bits, get reset, etc. - never completing a byte.

### Only Signal on Idle-to-Active Transition

The solution: only fire `tx_start` when starting a *new* transmission, not when replacing an in-progress byte:

```cpp
void tmp94c241_serial_device::scNbuf_w(uint8_t data)
{
    bool was_idle = (m_tx_clock_count == 0);
    m_tx_shift_register = data;
    m_tx_clock_count = 7;

    if (was_idle)
        m_tx_start_cb(1);  // Only signal if we were idle

    m_txd_cb(m_tx_shift_register & 1);
    m_tx_skip_first_falling = was_idle && (m_sioclk_state == 1);
}
```

## Current State

After all these fixes, individual bits are now being transmitted correctly:
- Bit 0 = 1 (shift_reg=0x80) ✓
- Bit 1 = 0 (shift_reg=0x40) ✓
- Bit 2 = 1 (shift_reg=0xA0) ✓

These match the expected values for `0x45` (binary: 01000101).

However, the firmware's initialization behavior still prevents complete bytes from being received. The root cause appears to be how the firmware polls/retries during serial setup - it keeps reconfiguring the serial port and rewriting the buffer before transmission completes.

## Lessons Learned

1. **Synchronous serial timing is subtle**: The relationship between clock edges, data output, and data sampling must be precisely coordinated.

2. **Clock phase at write time matters**: The same code can behave differently depending on when in the clock cycle you write data.

3. **Initialization loops can mask correct behavior**: Even if your protocol implementation is correct, firmware polling/retry behavior during initialization can prevent successful communication.

4. **Debug logging is essential**: Without detailed logs showing every clock edge, bit output, and bit sample, we never would have traced these timing issues.

5. **Real hardware has more tolerance**: Physical serial interfaces have electrical characteristics that make them more forgiving of slight timing variations. Emulation requires exact logical correctness.

## Next Steps

The remaining challenge is understanding why the firmware keeps re-initializing the serial port during boot. Possibilities include:

1. The firmware expects a specific response from the control panel that we're not providing
2. There's additional handshaking or status checking we haven't implemented
3. The initialization has specific timing requirements we're not meeting

We'll continue analyzing the firmware's serial initialization routines to understand exactly what conditions it's checking before proceeding past the init loop.

## Code References

The relevant MAME driver files:
- `src/devices/cpu/tlcs900/tmp94c241_serial.cpp` - CPU serial implementation
- `src/mame/matsushita/kn5000_cpanel.cpp` - Control panel HLE
- `src/mame/matsushita/kn5000.cpp` - Main driver

The firmware serial routines (in the disassembly):
- `CPanel_*` routines handle control panel communication
- Serial initialization happens early in the boot sequence

---

*This is part of the ongoing effort to create a working MAME emulator for the Technics KN5000 music keyboard. See the [main documentation](/) for more details on the project.*
