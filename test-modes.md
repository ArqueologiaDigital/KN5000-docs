---
layout: page
title: Test & Service Modes
permalink: /test-modes/
---

# KN5000 Test & Service Modes

The KN5000 has a comprehensive built-in diagnostic system designed for factory and field service use. There are four categories of test/service modes:

1. **Power-on self-test** — automatic hardware checks at every boot (with checking device)
2. **Control panel button combos** — special modes activated by holding specific panel buttons during power-on
3. **Keybed service modes** — diagnostic tests activated by holding specific piano keys during power-on
4. **HAMA factory diagnostics** — floppy disk and hard disk extension tests (internal Matsushita codename "HAMA")

> **Reference:** Service Manual EMID971655, pages I-17 through I-21.

## MAME Emulation Support

All test modes can potentially be activated in MAME:

| Mode | MAME Status | How to Activate |
|------|------------|-----------------|
| Power-on self-test | Working | Toggle "Main CPU Checking Device" or "Sub CPU Checking Device" DIP switches in Machine Configuration |
| Button combos | Working | Assign keyboard keys to panel buttons via Tab → Input (This Machine), hold during boot |
| Keybed service modes | Untested | Requires keybed input during boot — depends on tone generator device's key scan timing |
| HAMA factory diagnostics | Via keybed | Hold B3+B4 during power-on (same as Test 8). Requires tone gen keybed scan during boot |

---

## Power-On Self-Test

The self-test runs automatically at boot **only when a CHECKING DEVICE is connected** to CN11 or CN12 on the main board. The checking device is a simple circuit: a switch, a 1kΩ resistor, and an LED. Without it, the self-test is skipped entirely (`MainCPU_self_test_routines` at `0xFB729E`).

### Detection

The firmware reads Port D bit 0 (`PD.0` at I/O address `0x30`). If the checking device is not connected, `PD.0` reads high (pull-up) and the self-test returns immediately. With the checking device connected and its switch activated, `PD.0` reads low, and the self-test proceeds.

```
PD.0 = 1 (pull-up)  → No checking device → skip self-test
PD.0 = 0 (grounded) → Checking device present → run self-test
```

### Test Sequence

The self-test reports results by blinking the checking device's LED:
- **Short blink** (0x4000 delay) = component OK
- **Long blink** (0xC000 delay) = component DEFECTIVE

#### Test 1: Sub CPU Peripheral Devices (CN12)

| Blink # | Component | IC |
|---------|-----------|-----|
| 1 | DRAM | IC29 |
| 2 | DRAM | IC28 |
| 3 | Boot ROM | IC30 |
| 4 | (Unassigned) | — |
| 5 | Keyboard Switch Scanning | IC303 |

After the 4th blink, the keyboard switch scanning test engages: pressing any of the 61 keys lights the LED; releasing turns it off. This tests whether key switches and the Tone Generator LSI (IC303) are working.

#### Test 2: Main CPU Peripheral Devices (CN11)

| Blink # | Component | IC |
|---------|-----------|-----|
| 1 | DRAM | IC10 |
| 2 | DRAM | IC9 |
| 3 | SRAM | IC21 |
| 4 | (Unassigned) | — |
| 5 | Program ROM (ODD) | IC6 |
| 6 | Program ROM (EVEN) | IC4 |
| 7 | Table Data ROM | IC3 |
| 8 | Table Data ROM | IC1 |
| 9 | Rhythm Data ROM | IC14 |
| 10 | Custom Data ROM | IC19 |
| 11 | LCD Controller | IC206 |
| 12 | Video RAM | IC207 |

### Firmware Implementation

The self-test is implemented in `MainCPU_self_test_routines` at `0xFB729E`:

| Routine | Address | Tests |
|---------|---------|-------|
| `Test_DRAM_IC10_and_IC9` | `0xFB7348` | Writes `0x5A5A5A5A` / `0xA5A5A5A5` patterns, reads back |
| `Test_SRAM_IC21` | `0xFB7400` | Similar write/readback pattern test |
| `Test_PROGRAM_and_TABLE_DATA_ROMs` | (nearby) | ROM checksum verification |
| `Test_Rhythm_data_ROM_IC14` | (nearby) | ROM checksum verification |
| `Test_Custom_data_ROM_IC19` | (nearby) | ROM checksum verification |
| `Test_LCD_Controller_IC206` | (nearby) | LCD controller register test |
| `Test_Video_RAM_IC207` | (nearby) | VRAM write/readback test |
| `Report_test_result_by_blinking_LED` | `0xFB72EA` | Outputs result via LED blinks |

---

## Control Panel Button Combos

During boot, the firmware scans the control panel buttons via `CPanel_ScanButtons` (`0xFC3EE5`). The routine `CPanel_CheckSpecialCombos` (`0xFC4173`) tests for four specific button combinations and returns a combo code (0–4) in register HL.

### Button Combination Table

| Code | Buttons Held at Power-On | Panel | Bit Pattern | Effect |
|------|--------------------------|-------|-------------|--------|
| 0 | (none) | — | — | Normal boot |
| 1 | MARCH & WALTZ + PARTY TIME + SHOW TIME & TRAD DANCE | Left, SEG6 | `0x38` | Factory Reset (Initial Setting) |
| 2 | GM SPECIAL + ACCORDION REGISTER + DIGITAL DRAWBAR | Right, SEG1 | `0x70` | "ALL INITIAL SETTING!" screen + firmware version on LEDs |
| 3 | AUTO PLAY CHORD + SPLIT POINT + VARIATION 4 + VARIATION 3 | Left, SEG4 | `0x6C` | Software version / internal build numbers |
| 4 | PM 1 + PM 2 + PM 3 + PM 4 (all 4 Panel Memory buttons) | Right, SEG6 | `0x0F` | Flash Memory Update |

### Detailed Descriptions

#### Combo 1: Factory Reset (Initial Setting)

**Buttons:** The three leftmost buttons in the RHYTHM GROUP section.

This is the procedure described in the service manual under "INITIAL SETTING" (p I-3). It resets all programmable settings, functions, and memories to their factory-preset status. **Sequencer**, **Composer**, and **User MIDI** settings are initialized (Rhythm and Custom data are not affected).

**Firmware flow:** The combo code is stored at address `0x402`. At `Boot_HandleFactoryReset` (`0xEF07F3`), the firmware checks if `DRAM[0xFFCA] != 0x5AA5` (payload checksums invalid) **and** combo code == 1. If both conditions are true, it zero-fills all work DRAM (`0x400`–`0x100000`) and SRAM (`0x1E0000`–`0x200000`), then restarts the boot sequence. This is typically used after replacing Flash ROMs.

For normal users, the factory reset is handled through the welcome screen UI widget when combo 2 is detected.

#### Combo 2: ALL INITIAL SETTING / Firmware Version

**Buttons:** Three buttons from the SOUND GROUP section on the right panel.

Displays "ALL INITIAL SETTING!" on the LCD screen and shows the firmware version number on the control panel LEDs. At `Boot_HandleComboDisplay` (`0xEF07A2`), the firmware reads the version byte from `0xFFFFE8` (currently `0x0A` = version 10), looks up the LED pattern from the table at `0xE00000`, and calls `Set_LEDs`.

#### Combo 3: Software Version Screen

**Buttons:** Four buttons spanning the AUTO PLAY CHORD area on the left panel.

Displays the software version screen showing internal build numbers for all firmware components (main program, sub program, etc.). Implemented via `SoundCtrl_SendCommand`.

#### Combo 4: Flash Memory Update

**Buttons:** All four PANEL MEMORY buttons (PM 1–4) on the right panel.

Initiates firmware update from floppy disk. **Requires** both a floppy disk in the drive **and** a first-boot condition (`Get_Firmware_Version` returns `0xFF`). This is the procedure described in the service manual under "How to write program/data into FLASH ROMs" (p I-24). After the update starts, the instrument enters an infinite loop and must be power-cycled.

### Control Panel Memory Layout

The control panel consists of two MCUs (CPL = left, CPR = right) that communicate with the main CPU via serial protocol at 250 kHz. Button states are organized into segments:

| Variable | Address | Panel | Segment |
|----------|---------|-------|---------|
| `CPR_SEG1` | 36427 | Right | Segment 1 (Sound Group buttons) |
| `CPR_SEG6` | 36432 | Right | Segment 6 (Panel Memory buttons) |
| `CPL_SEG4` | 36446 | Left | Segment 4 (Auto Play / Variation buttons) |
| `CPL_SEG6` | 36448 | Left | Segment 6 (Rhythm Group leftmost buttons) |

---

## Keybed Service Modes

These diagnostic tests are activated by holding specific pairs of piano keys while powering on the instrument. They do **not** require the checking device (except Test 4). The keys are always two adjacent notes in the same octave range.

### Service Mode Table

| # | Test | Keys Held | Purpose |
|---|------|-----------|---------|
| 3 | LCD Panel Test | G3 + G4 | Tests LCD display hardware |
| 4 | CPR/CPL MCU Check | D3 + D4 (+ checking device on CN11, switch OFF) | Tests control panel MCU communication |
| 5 | Control Panel Switch & LED Check | F3 + F4 | Tests all panel buttons and LEDs |
| 6 | Wave ROM Check | E3 + E4 | Tests tone generator Wave ROMs (IC304-307) |
| 7 | FDC IC Test | A3 + A4 | Tests Floppy Disk Controller IC (IC208) |
| 8 | Floppy Disk SAVE/LOAD Test | B3 + B4 | Tests actual floppy disk read/write |

### Key Detection (Fully Traced)

After the SubCPU payload is transferred and verified, the firmware calls `SelfTest_FirmwareVersionCheck` (`0xFB76D8` in `ui/ui_mode_handlers.s`). This routine:

1. Sends an inter-CPU command (`0xF002`) to the SubCPU to read the tone generator's keybed scan registers
2. Waits for the SubCPU response (polls bit 7 at address 1568)
3. Reads 8 bytes of key scan data from address 36196 (the keybed state buffer)
4. Counts the total number of pressed keys using a population count (`SelfTest_PopCount`)
5. If exactly **2 keys** are pressed, checks which specific key bits are set
6. Posts `UI_PostModeChangeEvent` with the appropriate mode code

**Mode code dispatch:**

| Key Bits | Mode Code | Event Data | Test Mode |
|----------|-----------|------------|-----------|
| byte[3] bit 2 + byte[4] bit 6 | `0xF5` | `0x1A000F5` | Test 3: LCD Panel |
| byte[3] bit 4 + byte[5] bit 0 | `0xF6` | `0x1A000F6` | Test 4: CPR/CPL MCU |
| byte[3] bit 5 + byte[5] bit 1 | `0xF7` | `0x1A000F7` | Test 5: Panel Switch & LED |
| byte[3] bit 7 + byte[5] bit 3 | `0xF8` | `0x1A000F8` | Test 6: Wave ROM |
| byte[4] bit 1 + byte[5] bit 5 | `0xF9` | `0x1A000F9` | Test 7: FDC IC |
| byte[4] bit 3 + byte[5] bit 7 | `0xFC` | `0x1A000FC` | Test 8: FDD SAVE/LOAD (HAMA) |

`UI_PostModeChangeEvent` sends event `0x1C00015` with the mode code in the low byte, which triggers a screen group transition to the corresponding test mode UI.

> **MAME note:** For keybed tests to work in MAME, the tone generator device must respond to the inter-CPU key scan command during boot. The keybed queue in `kn5000_tonegen_device` would need to report held keys at this early stage.

### Test 3: LCD Panel Test (G3 + G4)

Displays "LCD PANEL TEST" on screen and cycles through display patterns:

**white → black → "H" pattern → red → blue → green** (repeats)

The "H" pattern is a large letter H used to check for LCD crosstalk between adjacent pixels. The color cycling tests the LCD's RGB color planes independently.

**Implementation:** LCD test screen group data containing 5 instances of "LCD PANEL TEST" text widgets at different screen regions (addresses `0xED6E10`–`0xED6F60`). Color cycling is handled by palette manipulation routines.

### Test 4: CPR/CPL MCU Check (D3 + D4 + Checking Device)

**Requires:** Checking device connected to CN11 with switch OFF.

Tests communication between the Main CPU (IC5) and the two Control Panel MCUs:
- CPR (IC1) — right panel
- CPL (IC1) — left panel

Results are reported via LED blinks AND displayed on the LCD:

| Blink # | Component |
|---------|-----------|
| 1 | CPR (IC1) |
| 2–3 | CPL (IC1) |
| 4 | (Unassigned) |

Short blink = OK, long blink = defective.

**Implementation:** `TEST4FUNC` at `0xFB7DDA`, dispatched via control panel event `0x1C00013`.

### Test 5: Control Panel Switch & LED Check (F3 + F4)

All LEDs on the control panel light up simultaneously. Press each button to verify:
- Button press → corresponding LED lights
- Button release → LED turns off
- For buttons without dedicated LEDs, the 4 BEAT display LEDs light up together when the START/STOP button is pressed

**Implementation:** `TEST2FUNC` at `0xFB7D99`, dispatched via control panel event `0x1C00013`.

### Test 6: Wave ROM Check (E3 + E4)

Enters a sine wave diagnostic mode. The Wave ROMs (IC304/305 and IC306/307) output sine waves when keys are pressed. Available check modes (selected via SOUND GROUP buttons):

| Mode | Description |
|------|-------------|
| (1) SINE WAVE & ROM check (w/o TOUCH) | Basic sine wave output, no velocity |
| (2) GENERATOR LSI OUTSEL check | Output select routing test |
| (3) HIGH SOUND check (+2 octave) | Transposed +2 octaves |
| (4) LOW SOUND check (-2 octave) | Transposed -2 octaves |
| (5) NORMAL SOUND check with TOUCH | Sine wave with velocity sensitivity |
| (6) SINE WAVE & ROM check 16dB DOWN | Attenuated output |

Wave ROM mapping to keys:
- **C keys:** IC304 & IC305
- **C# through B keys:** IC306 & IC307

If no sound is produced or the sound is distorted for a particular key, the corresponding Wave ROM chip may be defective.

**Implementation:** `TEST6FUNC` at `0xFB7E0E` and `TEST3FUNC` at `0xFB7DA6`, dispatched via control panel event `0x1C00013`. String data at `0xED19D0`–`0xED1A70`.

### Test 7: FDC IC Test (A3 + A4)

Tests communication between the Floppy Disk Controller IC (IC208) and the Main CPU. Results are displayed on the LCD.

**Note:** This test only checks the FDC IC ↔ CPU communication path. It does **not** test the actual floppy disk drive mechanism. For a full drive test, use Test 8 instead.

**Implementation:** `TestTitleFunc` at `0xF1E396` (shared test title display routine), with FDC-specific test code dispatched via the screen group event system.

### Test 8: Floppy Disk SAVE/LOAD Test (B3 + B4)

**Requires:** A formatted floppy disk inserted in the drive.

Performs repeated save/load cycles on the floppy disk:
1. Press "▶" on the LCD to start the test
2. Data is saved to and loaded from the disk repeatedly
3. The two data sets are compared
4. OK/NG counts are displayed on the LCD
5. Press "■" to stop the test

Even with a properly functioning drive, occasional "NG" results may occur. If frequent, clean the drive heads with a cleaning disk and re-test. Persistent failures indicate a defective drive.

**Implementation:** `FDLoadSaveTest` at `0xF1E5B0`. Display strings include "FD SAVE/LOAD TEST", "START FDD TEST LOOP", "STOP FDD TEST". Test results shown as "TEST2OKNG", "TEST2OKOK", etc.

---

## HAMA Factory Diagnostics (Codename "HAMA")

The HAMA subsystem is an internal Matsushita factory diagnostic system for testing floppy disk I/O and hard disk extension (HDAE5000) hardware. "HAMA" is the developer codename preserved in the ROM's factory test string table alongside other original symbol names (`assswb_op`, `sendCOMM`, etc.).

### Registration

`InitializeHama` (at `0xF1E2FE`) is called unconditionally during boot from the UI initialization sequence (`ui/ui_widget_defs.s`). It registers:

- **12 NAKA widget object tables** for the test UI system (file browsers, dialog buttons, diagnostic counters)
- **2 diagnostic titles** in the firmware's title system:

| Title | String Address | Widget Table | Description |
|-------|---------------|--------------|-------------|
| `TT_HDDEXT` | `0xE1FD18` | `0x7F` | FDD / Hard Disk Extension test |
| `TT_EXTAPR` | `0xE1FD22` | `0xFC` | Extension APR test |

Both titles use `TestTitleFunc` (`0xF1E396`) as their lifecycle callback.

### TestTitleFunc Event Handler

When a HAMA title becomes active, `TestTitleFunc` processes two event types:

**Event `0x1C00007` — Title lifecycle** (xde parameter):

| xde | Action |
|-----|--------|
| 0 | Title created — initialize test UI |
| 1 | Title destroyed — send cleanup event + kill timer |
| 2 | Title activated — display test counters + set 0.5s auto-refresh timer |
| 3 | Title inactivated — run directory listing |
| 4–5 | Interrupt / interrupt return — re-register HAMA title entries |
| 6 | TBIOS test — list directory (alternate entry) |

**Event `0x1C00013` — User button actions** (xde parameter):

| xde | Action |
|-----|--------|
| 2 | STOP FDD TEST |
| 3 | START FDD TEST LOOP — calls `FDLoadSaveTest` |
| 4 | DIR — display floppy directory listing |
| 5–6 | Debug test functions |

### FDD SAVE/LOAD Test (FDLoadSaveTest)

The core diagnostic test (`0xF1E5B0`):

1. Allocates a 2 KB buffer
2. Fills it with a counting pattern (`0x000`–`0x3FF`, 2 bytes each)
3. Opens file `A:IMMUNITY.TST` via `FileOpen`
4. Writes the buffer via `FileWrite`
5. Closes and reopens the file
6. Reads back via `FileRead`
7. Compares read-back data against original pattern byte-by-byte
8. Reports OK/NG via `FDTest_PrintDiag` debug output

The test dialog displays three DIAGLIST widgets showing TOTAL, OK, and NG counters.

### Memory Dump Tool (DbMemoryDumpProc)

The HAMA diagnostic system includes a built-in **memory hex viewer** (`DbMemoryDumpProc` at `ui/ui_widget_defs.s:6878`). This is a complete debugging tool for inspecting arbitrary memory addresses.

**Display format:** Each row shows an address, 8 bytes of hex data, and their ASCII interpretation (non-printable characters shown as `.`).

**Controls:**
- **Address input** — enter a target address to inspect
- **UP/DOWN** — scroll through memory (0x80 bytes per step)
- **Confirm** — read and display the selected address range
- Address range: full 24-bit space (`0x000000`–`0xFFFFFF`)

**Events handled by `DbMemoryDumpProc`:**

| Event | Action |
|-------|--------|
| `0x1C00007` | Activate — initialize and show the memory viewer window |
| `0x1C0000D` | Paint — render memory contents with box borders |
| `0x1C0000E` | Select — navigation input (UP/DOWN scrolling) |
| `0x1C0000F` | Confirm — read memory at the entered address |
| `0x1C00002` | Close — exit the memory viewer |

**Activation:** The memory dump widget is part of the "DEBUG SCREEN for HD-AE" layout within the HAMA test system. It is accessed by entering HAMA test mode (hold **B3 + B4** during power-on), then selecting one of the Debug Test buttons (xde=5 or xde=6 in the `TestTitleFunc` action dispatch).

**Implementation:** `DbMemoryDumpProc` in `ui/ui_widget_defs.s:6878`. The widget descriptor is at `FDTest_Label_MemoryDump` in `factory_test/fd_test_data.s:157`.

### HAMA Function Reference Table

The factory test string table in `test_data.s` lists the original Matsushita debug symbol names for functions tested by the diagnostic system:

| Original Symbol | Semantic Name | Address | Purpose |
|----------------|---------------|---------|---------|
| `sendCOMM` | `sendCOMM` | `0xEF32F4` | Chunked SubCPU data transfer |
| `assswb_op` | `SwbtWr_ReinitBothBanks` | `0xEF14D8` | Reinitialize both tone gen banks |
| `assswb_out` | `SwbtWr_ReinitOutputBank` | `0xEF14F3` | Reinitialize output tone gen bank |
| `SwbtWr` | `SwbtWr` | — | Sound Write Bank Table Writer root |
| `AddswbWr` | `AddswbWr` | — | Add sound write bank entry |
| `AssswbWr` | `AssswbWr` | — | Assign sound write bank entry |
| `ChangePalette` | `ChangePalette` | — | LCD palette change |
| `free_X` | `free_X` | — | Memory free |
| `malloc_X` | `malloc_X` | — | Memory allocate |
| `SetGlobalError` | `SetGlobalError` | — | Set global error flag |

These strings are displayed on the diagnostic LCD during hardware validation, providing factory technicians with the original source code function names for debugging.

### Activation Path (Traced)

The HAMA titles are activated through the **keybed service mode system**:

**Test 8 (B3 + B4) → TT_EXTAPR (mode 0xFC):**
Holding keys B3 and B4 during power-on causes `SelfTest_FirmwareVersionCheck` to post mode code `0xFC` via `UI_PostModeChangeEvent`. This matches the widget table ID `0xFC` used when registering `TT_EXTAPR`, activating the full HAMA diagnostic screen with FDD SAVE/LOAD test, directory listing, and debug functions.

**TT_HDDEXT (widget table 0x7F):**
The `TT_HDDEXT` title (Hard Disk Extension test) is registered with widget table `0x7F`, which does not correspond to any direct keybed mode code. It is likely accessible from **within** the TT_EXTAPR test screen — the `TestTitleFunc` lifecycle handler processes interrupt/resume events (xde=4-5) that call `RegHamaTitle1/2_Entry`, which may switch between the two HAMA titles. This allows a technician to enter the diagnostic system via Test 8 (B3+B4) and then navigate to the HDD extension test using on-screen buttons.

**Complete activation chain:**
```
Power on while holding B3 + B4
  → Boot sequence runs normally
  → SelfTest_FirmwareVersionCheck reads keybed via SubCPU
  → Detects 2 keys: byte[4] bit 3 + byte[5] bit 7
  → Posts UI_PostModeChangeEvent(0xFC)
  → Event 0x1C00015 with data 0x1A000FC
  → Title system activates TT_EXTAPR (widget table 0xFC)
  → TestTitleFunc receives lifecycle event 0x1C00007 (activate)
  → HAMA diagnostic screen displayed
  → User can START/STOP FDD test, browse files, run debug tests
```

### Source Files

| File | Purpose |
|------|---------|
| `factory_test/test_init.s` | `InitializeHama` — title & widget registration, `TestTitleFunc` lifecycle handler |
| `factory_test/test_data.s` | HAMA function reference table, UI configuration data, `HamaList` widget descriptors |
| `factory_test/fd_test_code.s` | `FDLoadSaveTest` — floppy disk test execution, `HamaListProc` event handler |
| `factory_test/fd_test_data.s` | NAKA widget descriptors for test dialog, title strings `TT_HDDEXT` / `TT_EXTAPR` |

---

## Code Locations Summary

| Routine | Address | File | Purpose |
|---------|---------|------|---------|
| `MainCPU_self_test_routines` | `0xFB729E` | `boot/system_handlers.s` | Power-on self-test dispatcher |
| `Report_test_result_by_blinking_LED` | `0xFB72EA` | `boot/system_handlers.s` | LED blink result reporter |
| `Test_DRAM_IC10_and_IC9` | `0xFB7348` | `boot/system_handlers.s` | DRAM test (write patterns) |
| `Test_SRAM_IC21` | `0xFB7400` | `boot/system_handlers.s` | SRAM test |
| `CPanel_ScanButtons` | `0xFC3EE5` | `ui/cpanel_routines.s` | Boot-time button scan |
| `CPanel_CheckSpecialCombos` | `0xFC4173` | `ui/cpanel_routines.s` | Button combo detection |
| `InitializeHama` | `0xF1E2FE` | `factory_test/test_init.s` | HAMA subsystem registration |
| `TestTitleFunc` | `0xF1E396` | `factory_test/test_init.s` | Test title lifecycle handler |
| `FDLoadSaveTest` | `0xF1E5B0` | `factory_test/fd_test_code.s` | Floppy disk SAVE/LOAD test |
| `HamaListProc` | `0xF1E8C0` | `factory_test/fd_test_code.s` | File browser event handler |
| `TEST2FUNC` | `0xFB7D99` | `boot/system_handlers.s` | Panel switch & LED test handler |
| `TEST3FUNC` | `0xFB7DA6` | `boot/system_handlers.s` | Wave ROM test handler (part) |
| `TEST4FUNC` | `0xFB7DDA` | `boot/system_handlers.s` | CPR/CPL MCU test handler |
| `TEST6FUNC` | `0xFB7E0E` | `boot/system_handlers.s` | Wave ROM test handler (part) |
| `Boot_HandleComboDisplay` | `0xEF07A2` | `kn5000_v10_program.s` | Boot combo handler (LED version) |
| `Boot_HandleFactoryReset` | `0xEF07F3` | `kn5000_v10_program.s` | Boot combo handler (factory reset) |
| `WidgetParam_TestMode_Entry` | `0xEDBA44` | `ui_widgets/widget_dispatch.s` | Test mode widget entry |
| `Get_Firmware_Version` | `0xFFFEE5` | `kn5000_v10_program.s` | Returns firmware version byte |
| `FIRMWARE_VERSION` | `0xFFFFE8` | `boot/rom_end_structure.s` | Version byte (0x0A = v10) |

---

## See Also

- [Boot Sequence]({{ site.baseurl }}/boot-sequence/) — Complete boot flow including button combo handling
- [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) — Serial communication with panel MCUs
- [Keybed Scanning]({{ site.baseurl }}/keybed-scanning/) — How the keyboard interfaces with IC303
- [Hardware Architecture]({{ site.baseurl }}/hardware-architecture/) — IC numbers and board layout
