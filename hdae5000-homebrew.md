---
layout: page
title: "HDAE5000 Homebrew Development"
permalink: /hdae5000-homebrew/
---

# Writing Custom HDAE5000 Extension ROMs

The HD-AE5000 extension slot can run custom code on the KN5000's main CPU. By replacing the HDAE5000 ROM with a custom binary, you can create games, demos, or utilities that run on the keyboard hardware. This page documents the extension ROM protocol, known toolchain bugs, and a working build pipeline.

> **Status**: Boot initialization, frame handler callbacks, and DISK MENU registration are working. The extension ROM appears in the DISK MENU with a custom icon and name. The firmware's object dispatch system (`FA9660`, `FA44E2`, `FA3D85`, `FA4409`) and the HDAE5000's 13-component data record table have been fully analyzed. Display ownership (taking over the LCD from the firmware) and game activation from the DISK MENU require implementing the data record table and handler function.

## Prerequisites

- **LLVM with TLCS-900 backend** -- a custom LLVM build with the TLCS-900 target
- **MAME** with KN5000 driver for testing
- Knowledge of the [HDAE5000 firmware protocol]({{ site.baseurl }}/hdae5000/)

## Extension ROM Protocol

### XAPR Header Format

The KN5000 firmware validates extension ROMs by checking for an "XAPR" magic string at address `0x280000`. The header occupies the first 32 bytes:

```
Offset  Size  Contents              Description
------  ----  --------------------  -----------
0x00    4     "XAPR"                Magic signature
0x04    4     34 A1 2F 00           Version/ID metadata
0x08    4     JP Boot_Init          Entry point 1: boot initialization
0x0C    4     RET + 3x NOP          Padding
0x10    4     JP Frame_Handler      Entry point 2: frame callback
0x14    4     RET + 3x NOP          Padding
0x18    4     RET + 3x NOP          Entry point 3: unused
0x1C    4     RET + 3x NOP          Entry point 4: unused
```

The `JP` instruction (opcode `0x1B`) is followed by a 24-bit little-endian target address.

### Firmware XAPR Validation

The main firmware validates the extension ROM and calls Boot_Init from routine `LABEL_F1E9E0`:

```asm
; At LABEL_F1E9E0 in kn5000_v10_program.rom:
PUSHW 0004h                          ; Compare 4 bytes
PUSHW 00e1h                          ; String compare flags
PUSHW 0ffc6h                         ; Pointer to "XAPR" in firmware ROM
LD    XWA, 00280000h                 ; Extension ROM base address
PUSH  XWA
CALL  String_Compare                 ; Compare first 4 bytes
ADD   XSP, 0000000ah                 ; Clean stack
CP    HL, 0                          ; Match?
JR    NZ, .no_extension              ; Skip if no match

LD    (03DD04h), 001h                ; Set XAPR detection flag

; ... fall through to call Boot_Init ...

LD    XHL, 00280008h                 ; Address of boot init entry point
LDA   XWA, 027ED2h                  ; Workspace pointer = 0x027ED2
CALL  T, XHL                        ; Call Boot_Init(XWA = workspace_ptr)
RET
```

The frame handler dispatcher (`LABEL_F1E9D0`) runs every iteration of the main event loop:

```asm
; Frame handler dispatcher:
CP    (03DD04h), 000h                ; Check XAPR detection flag
RET   Z                              ; Skip if no extension ROM
LD    XHL, 00280010h                 ; Address of frame handler entry point
CALL  T, XHL                        ; Call Frame_Handler()
RET
```

**Key observations:**
- The frame handler is called **unconditionally** every frame -- no registration needed
- The XAPR detection flag at `0x03DD04` is the only gate
- Hardware presence is checked separately via Port E bit 0 (active low)

### Workspace Pointer

The firmware passes `0x027ED2` in XWA to Boot_Init. This is the base address of the firmware's **object table** in main DRAM -- a data structure with 14-byte entries spanning from `0x027ED2` to `0x02BC12` (~1,118 entries).

The workspace provides access to the firmware's callback dispatch system via pointer chains:

```
Workspace (0x027ED2)
    |
    +-- offset +0x0E0A --> Handler Table A pointer
    |                        |
    |                        +-- offset +0x00DC --> Default handler function (lifecycle)
    |                        +-- offset +0x00E4 --> RegisterObjectTable function
    |                        +-- offset +0x0100 --> Secondary dispatch function
    |                        +-- offset +0x0124 --> Display callback function
    |                        +-- offset +0x0168 --> DISK MENU handler (FA44E2)
    |                        +-- offset +0x0244, +0x0248, +0x024C --> UI callbacks
    |                        +-- offset +0x0270 --> Graphics init dispatch
    |                        +-- offset +0x02C4 --> DISK MENU slot registration
    |
    +-- offset +0x0E88 --> Handler Table B pointer
                             |
                             +-- offset +0x0100 --> Init function 2
                             +-- offset +0x0104 --> Init function 3
                             +-- offset +0x0108 --> Init function 1
```

Both handler tables are in main DRAM (0x000000-0x0FFFFF range). The values at these offsets are function pointers into the firmware ROM. The offset `+0x0168` resolves to `FA44E2` (the shared DISK MENU handler used by all built-in modules).

### Boot_Init Calling Convention

```
Entry:
  XWA = workspace pointer (0x027ED2)

Expected behavior:
  Store workspace pointer for later use
  Perform initialization
  Return (RET) to firmware

Notes:
  Must preserve stack state (firmware continues initialization after return)
  Extension RAM at 0x200000-0x27FFFF is available for variables
  Extension ROM at 0x280000-0x2FFFFF is available for code and data
```

### Frame_Handler Calling Convention

```
Entry:
  No parameters (called from firmware main loop)

Expected behavior:
  Perform per-frame updates (display, input, etc.)
  Return (RET) to firmware

Notes:
  Called every main loop iteration while XAPR flag (0x03DD04) is set
  Should be fast -- firmware main loop handles other subsystems too
  All registers should be preserved or restored
```

## Handler Registration

### Overview

The original HDAE5000 firmware performs extensive setup during Boot_Init before any DISK MENU registration:

1. **Clear work buffer** -- 62,762 bytes zeroed at `0x22A000`
2. **Copy init data** -- 3,202 bytes from ROM `0x2F94B2` to RAM `0x23952A`
3. **Register 11 handlers** -- via `workspace[0x0E0A][0x00E4]` (RegisterObjectTable)
4. **Load VGA palette** -- 256 entries from ROM
5. **Allocate DRAM and copy VRAM** -- 76,800 bytes to display areas
6. *Then* **call `workspace[0x0E0A][0x02C4]`** -- DISK MENU slot registration
7. **Set slot fields** -- `slot+0x00` = handler flags, `slot+0x2A` = display name string

For basic frame handler operation, handler registration is **not required**. The firmware calls the Frame_Handler entry point every frame regardless.

### RegisterObjectTable Protocol (workspace[0x0E0A][0x00E4])

The Handler_Registration routine at `0x280020` (now fully disassembled) registers handlers by building a 14-byte parameter block on the stack and calling the RegisterObjectTable function:

```
Parameter block layout (14 bytes on stack):
  (XSP+0x00)  4 bytes  Port address (identifies handler type)
  (XSP+0x04)  4 bytes  Handler function pointer (from workspace dispatch table)
  (XSP+0x08)  2 bytes  Data size (in bytes)
  (XSP+0x0A)  4 bytes  Data pointer (RAM or ROM address)

Call convention:
  WA  = handler ID (object table index)
  XBC = pointer to parameter block on stack
  Call workspace[0x0E0A][0x00E4]
```

RegisterObjectTable stores each 14-byte parameter block at `workspace_base + (handler_ID * 14)` in the firmware's object registry. The workspace base (`0x027ED2`) can hold up to ~1,118 object entries.

### Complete Handler Table

The HDAE5000 registers 11 handlers plus a final graphics initialization call:

| # | ID | Port | Table Offset | Size | Data Address | Description |
|---|-----|------|------|------|------|-------------|
| 1 | 0x016A | 0x01600004 | 0x0168 | variable | 0x29C0AA | UI config strings |
| 2 | 0x01CA | 0x0160000C | 0x013C | variable | 0x2397EA | RAM data area A |
| 3 | 0x01EA | 0x0160000D | 0x0140 | variable | 0x239824 | RAM data area B |
| 4 | 0x012A | 0x01600002 | 0x0248 | 69 (0x45) | 0x23952A | Init data primary |
| 5 | 0x042A | 0x01600002 | 0x0248 | 69 (0x45) | 0x239642 | Init data secondary |
| 6 | 0x010A | 0x01600001 | 0x0244 | 13 (0x0D) | 0x239872 | Serial data primary |
| 7 | 0x040A | 0x01600001 | 0x0244 | 13 (0x0D) | 0x2398AA | Serial data secondary |
| 8 | 0x014A | 0x01600003 | 0x024C | 14 (0x0E) | 0x239FD2 | Parallel data primary |
| 9 | 0x044A | 0x01600003 | 0x024C | 14 (0x0E) | 0x23A00E | Parallel data secondary |
| 10 | 0x007F | 0x01600010 | 0x0280 | 789 (0x315) | 0x2A5D2C | ROM graphics primary |
| 11 | 0x037F | 0x0160000F | 0x0148 | 789 (0x315) | 0x2A6984 | ROM graphics secondary |

The final call uses dispatch table offset `0x0270` with additional parameters for graphics initialization.

**Port address pattern:** Handlers are grouped by port number. Pairs with the same port and table offset (e.g., 0x012A/0x042A on port 0x01600002) are primary/secondary instances of the same handler type.

**Module naming pattern:** The main CPU firmware has similar registration routines named after developers: InitializeSuna (idx 4), InitializeScoop (6), InitializeKubo (8), InitializeHama (9), HDAE5000 (A), InitializeNaka (B). DISK MENU entries use object indices `0x0160`-`0x016B`.

### Data Record Table (Handler 0x016A)

The data pointer registered for handler `0x016A` (`0x29C0AA`) points to a table of **24-byte records**, one per UI component (sub-object). The HDAE5000 has 13 sub-objects:

```
Record layout (24 bytes):
  +0x00  4 bytes  Implementation function pointer (in ROM)
  +0x04  4 bytes  Next handler ID (linked list chain, 0xFFFFFFFF = end)
  +0x08  2 bytes  Size/count field
  +0x0A  2 bytes  Flags field
  +0x0C  4 bytes  ROM data pointer (name string, config)
  +0x10  4 bytes  ROM data pointer (secondary config)
  +0x14  4 bytes  RAM workspace pointer
```

| Rec | Sub-Index | Name | Func | Next Link | Notes |
|-----|-----------|------|------|-----------|-------|
| 0 | 0x0000 | SelectList | 0x2807D9 | 0x01600011 | Main selection list UI |
| 1 | 0x0001 | DbMemoCl | 0x28122A | 0x01600046 | Database/memo |
| 2 | 0x0002 | TtlScreenR | 0x280489 | 0x01600034 | Title screen |
| 3 | 0x0003 | AcHddNamingWindow | 0x281411 | 0x01600035 | HDD naming dialog |
| 4 | 0x0004 | IvHddNaming | 0x282681 | 0x01600027 | HDD naming input |
| **5** | **0x0005** | **HDTitleMenu** | **0x2827A8** | **0x0160001D** | **DISK MENU entry** |
| 6 | 0x0006 | TtlScreenR2 | 0x280567 | 0x01600034 | Title screen variant |
| 7 | 0x0007 | TtlScreenR3 | 0x280645 | 0x01600034 | Title screen variant |
| 8 | 0x0008 | AcWindowPage1 | 0x28043C | 0x01600025 | Window page |
| 9 | 0x0009 | IvScreenR2 | 0x280723 | 0x0160006A | Screen input handler |
| 10 | 0x000A | AcLanguageText1 | 0x28B554 | 0x01600066 | Language text display |
| 11 | 0x000B | LyricBox | 0x28CD08 | 0x01600011 | Lyrics display box |
| 12 | 0x000C | FDFileSelect | 0x28E61B | 0x01600027 | File selection dialog |

**Record 5 ("HDTitleMenu") is the DISK MENU entry handler.** Its sub-index (5) matches the high word in `slot+0x00 = 0x016A0005` (object index 0x016A, sub-index 0x0005). The "next" link chains each sub-object to a corresponding component in the Root module (object 0x0160), forming an **inheritance hierarchy** where HDAE5000 components extend base firmware components.

### DISK MENU Slot Registration (workspace[0x0E0A][0x02C4])

After registering all 11 handlers, Boot_Init calls `workspace[0x0E0A][0x02C4]` with ID `0x00600002` to create a DISK MENU entry. The returned XHL points to a handler slot structure:

| Offset | Size | Value (HDAE5000) | Value (Mines) | Description |
|--------|------|-------------------|---------------|-------------|
| +0x00 | 4 | `0x016A0005` | *(not set)* | Handler flags + object index |
| +0x2A | 4 | `0x2F8DCE` → "HD-AE5000" | MENU_NAME → "Mines Game" | Display name string pointer |
| +0x32 | 4 | *(from firmware)* | 176 | Icon ID (table_data ROM) |

The `slot+0x00` field links the DISK MENU entry to a registered handler object. The low word (`0x016A`) is the object table index, and the high word (`0x0005`) contains flags. The Mines project does not currently set `slot+0x00`, which may explain why DISK MENU activation doesn't work.

The `slot+0x2A` field has been **confirmed** as a display name string pointer by verifying that address `0x2F8DCE` in the HDAE5000 ROM contains the null-terminated string "HD-AE5000".

## Display Ownership Model

Understanding how the firmware manages the LCD display is critical for any homebrew project that wants to render graphics.

### Firmware Display Architecture

The KN5000 display is **NOT driven by a vertical blank interrupt (VBI)**. Instead, display updates happen in the firmware's main event loop at `LABEL_EF1245`:

```
Main Event Loop (LABEL_EF1245)
    |
    +-- Control Panel Poll
    +-- Display Update         <-- firmware draws its UI here
    +-- MIDI Processing
    +-- FDC Handler
    +-- Frame_Handler call     <-- extension ROM runs AFTER firmware drawing
    +-- Audio Sync
    |
    (loop)
```

**Key implication:** The Frame_Handler is called **after** the firmware has already drawn its screen content. Any VRAM writes made by the extension ROM will be visible briefly, then overwritten by the firmware on the next loop iteration.

### Display Disable Flag (SFR 0x0D53, bit 3)

The firmware checks a flag before performing display updates:

```asm
BIT 3, (0D53h)           ; Check display disable flag
JR NZ, skip_display      ; If set, skip all firmware screen drawing
```

**To take display ownership**, an extension ROM should:
1. Set bit 3 of the byte at SFR address `0x0D53`
2. This prevents the firmware from overwriting VRAM
3. The extension ROM then has full control of the framebuffer

**WARNING:** This is based on disassembly analysis and has not been fully tested. The address `0x0D53` is in the TMP94C241F's internal RAM / SFR space. Additional firmware state may need to be managed to prevent side effects.

### VGA Controller Details

The KN5000 uses an **MN89304** LCD controller, which is VGA-compatible with some differences:

| Property | Standard VGA | MN89304 (KN5000) |
|----------|-------------|-------------------|
| DAC resolution | 6-bit (0-63) | **4-bit (0-15)** |
| Palette format | 18-bit RGB | **12-bit RGB** |
| Row pitch | configurable | `svga_device::offset() << 3` (8x multiplier) |
| CRTC start | standard | standard |

#### VGA Register Map

| Register | CPU Address | Description |
|----------|-------------|-------------|
| DAC Mask | 0x1703C6 | Palette mask register |
| DAC Write Index | 0x1703C8 | Select palette entry to write |
| DAC Data | 0x1703C9 | Write R, G, B values sequentially |
| CRTC Index | 0x1703D4 | Select CRTC register |
| CRTC Data | 0x1703D5 | Read/write CRTC register value |

#### Palette Format

The MN89304 uses a **4-bit RAMDAC** (`pal4bit()` in MAME). Only the lower 4 bits of each color component are used:

```c
// Writing a palette entry
*VGA_DAC_WRITE_INDEX = palette_index;
*VGA_DAC_DATA = red >> 2;    // Convert 6-bit VGA to 4-bit
*VGA_DAC_DATA = green >> 2;
*VGA_DAC_DATA = blue >> 2;
```

The original HDAE5000 firmware shifts RGB values right by 4 bits (`>> 4`) from 8-bit source data. If your palette data is already in 6-bit VGA format (0-63), shift right by 2 (`>> 2`) to get 4-bit values.

#### CRTC Start Address

The CRTC start address (registers 0x0C high, 0x0D low) determines which VRAM address appears at the top-left of the screen. The firmware initializes this to `0x0000` during VGA setup, meaning VRAM address `0x1A0000` maps to pixel (0,0).

The MN89304 applies an additional 8x multiplier to the row offset calculation (`mn89304::offset()` overrides `svga_device::offset()` and left-shifts by 3). This affects scrolling but not the basic framebuffer start address.

### VRAM Layout

| Property | Value |
|----------|-------|
| Base address | 0x1A0000 |
| Size | 256KB (0x1A0000-0x1DFFFF) |
| Active display | 76,800 bytes (320 x 240) |
| Pixel format | 8-bit indexed color |
| Row stride | 320 bytes |

VRAM is linear and row-major. Pixel at screen position (x, y) is at VRAM address `0x1A0000 + y * 320 + x`.

### Experimental Observations

Testing with MAME confirmed:
- VRAM writes at `0x1A0000` are effective (filling VRAM with 0xFF produced visible red at the bottom of the screen)
- The firmware continuously redraws its UI, overwriting extension ROM VRAM writes within one main loop iteration
- Setting CRTC start to 0 and continuously resetting it was insufficient to maintain display ownership
- The display disable flag at `0x0D53` bit 3 is the intended mechanism for an extension to take over the display

## Object Dispatch System

The firmware implements an **object-oriented dispatch system** that manages all DISK MENU interactions. Understanding this system is essential for proper DISK MENU integration.

### Architecture Overview

```
Object Table (0x027ED2)                  Data Record Table
 14-byte entries, max 1118               24-byte records per sub-object
┌──────────────────────────────┐       ┌────────────────────────────────┐
│ +0x00: Port address (4)      │       │ +0x00: Impl function ptr (4)   │
│ +0x04: Handler function (4)  │       │ +0x04: Next handler ID (4)     │
│ +0x08: Data size (2)         │       │ +0x08: Size/count (2)          │
│ +0x0A: Data pointer (4) ─────┼──────>│ +0x0A: Flags (2)               │
└──────────────────────────────┘       │ +0x0C: ROM data ptr (4)        │
                                       │ +0x10: ROM data ptr 2 (4)      │
Global State (saved/restored            │ +0x14: RAM workspace ptr (4)   │
 per dispatch call):                    └────────────────────────────────┘
  0x02BC14: Current object identity
  0x02BC24: Current handler ID
  0x02BC28: Current request code
  0x02BC2C: Current parameter
```

### Object Identifiers

Object IDs combine an object table index with a sub-object index:

```
  0x016A0005
  ├── 0x016A  = Object table index (handler ID registered via RegisterObjectTable)
  └── 0x0005  = Sub-object index (record number in data table)
```

The `slot+0x00` field in the DISK MENU slot stores this combined identifier, linking the menu entry to a specific sub-object (record) in the handler's data table.

### Main Dispatch Function (0xFA9660)

`FA9660` is the firmware's general-purpose object method dispatch. Every request to an object goes through this function:

```
FA9660(XWA=object_id, XBC=request_code, XDE=param):
  1. Save current global state (0x02BC14, 0x02BC24-2C)
  2. Look up handler function from object entry[+4]
  3. Call handler(object_id, 0x01E00000, 0) → "identity" query
  4. Set 0x02BC14 = identity result
  5. Look up data table record for the sub-object index
  6. Read implementation function from record[+0x00]
  7. Call record_function(object_id, request_code, param)
  8. Restore global state
  9. Return result
```

The identity query (step 3) calls through the registered handler function (e.g., `FA44E2` for DISK MENU objects). For request `0x01E00000`, `FA44E2` simply returns XWA unchanged, so the identity equals the object ID.

### Request Code Dispatch (Three Layers)

The handler function `FA44E2` (shared by all DISK MENU modules) dispatches requests through three layers:

```
FA44E2 (Layer 1): Simple getters (0x01E00000-0x01E00007)
  ├── Case 0 (0x01E00000): Return XWA (identity)
  ├── Case 1 (0x01E00001): Return *(XHL)
  ├── Case 2 (0x01E00002): Return *(XIZ)
  ├── Case 3 (0x01E00003): Return HL from (XIZ+0x08)
  ├── Case 4 (0x01E00004): Linked object search
  ├── Case 5 (0x01E00005): String data processing
  ├── Case 6 (0x01E00006): (complex)
  ├── Case 7 (0x01E00007): (complex)
  ├── 0x01E0000D, 0x01E0000E: Special cases
  ├── 0x01E0000F: Return immediately
  ├── 0x01E00015: Return (XHL+0x0C)
  └── Default (including 0x01E0009C): → FA3D85
                                         │
FA3D85 (Layer 2): Lifecycle events (0x01E00010-0x01E00023)
  ├── 20 cases via jump table at 0xEAA8A4
  │   (setters, init/teardown, string operations)
  └── Out of range (including 0x01E0009C): → FA4409
                                               │
FA4409 (Layer 3): Chain dispatch for unhandled requests
  ├── Read current dispatch context from 0x02BC14
  ├── Look up "next" handler from record[+0x04]
  ├── If next ≠ 0xFFFFFFFF: follow chain, call next handler
  └── If next = 0xFFFFFFFF: return 0
```

### HDAE5000 Handler Behavior (Record 5: "HDTitleMenu")

The HDAE5000's DISK MENU handler function at `0x2827A8` (Record 5) is minimal:

```
0x2827A8(XWA=handler_id, XBC=request, XDE=param):
  if (request == 0x01C0000F):
    call workspace[0x0E0A][0x00DC]  // Call default handler first
    call workspace[0x0E0A][0x0100]  // Then post 0x01C0000D request
    return 0
  else:
    jp workspace[0x0E0A][0x00DC]    // Delegate to default handler
```

**The default handler at `workspace[0x0E0A][0x00DC]` manages the full DISK MENU lifecycle for most requests, including 0x01E0009C (activation).** The HDAE5000 only intercepts request `0x01C0000F` to perform additional initialization after the default handler runs.

## DISK MENU Activation Mechanism

When the user selects a DISK MENU entry, the firmware does not directly call the extension ROM. Instead, it uses the event dispatch system to activate the registered handler.

### Activation Trigger

The main firmware routine at `LABEL_F8B1DF` handles extension board activation:

```asm
; LABEL_F8B1DF: Check if HDAE5000 extension is present
CALL  LABEL_F1E9A3           ; Read XAPR detection flag from (0x03DD04)
CP    L, 0
JR    Z, .no_extension       ; Skip if no extension ROM

; Extension present -- post activation event
LD    XWA, 00600002h         ; Target handler ID (same as DISK MENU registration)
LD    XBC, 01E0009Ch         ; Event parameter
LD    XDE, 0
CALL  ApPostEvent            ; Dispatch event to registered handler
```

The `ApPostEvent` function queues events in a ring buffer at `0x02BC34` (12-byte entries: target_object + handler_id + event_param, max 1024 entries). The event processor dequeues events and dispatches them via `FA9660`.

### Complete Activation Flow

When `ApPostEvent(0x00600002, 0x01E0009C, 0)` is dispatched:

```
1. Event processor calls FA9660(object_id, 0x01E0009C, 0)
   where object_id comes from the DISK MENU slot+0x00 (e.g., 0x016A0005)
2. FA9660 calls identity query: FA44E2(0x016A0005, 0x01E00000, 0) → 0x016A0005
3. FA9660 sets 0x02BC14 = 0x016A0005
4. FA9660 looks up Record 5 in data table → func = 0x2827A8
5. FA9660 calls 0x2827A8(0x016A0005, 0x01E0009C, 0)
6. Handler delegates to workspace[0x0E0A][0x00DC] (default handler)
7. Default handler manages the DISK MENU activation lifecycle
```

### What Mines Needs for DISK MENU Activation

Based on the complete dispatch analysis, the Mines project needs:

1. **Register handler `0x016A`** via `workspace[0x0E0A][0x00E4]` (RegisterObjectTable) with:
   - Port: `0x01600004`
   - Handler function: `workspace[0x0E0A][0x0168]` (the shared DISK MENU handler `FA44E2`)
   - Data size: number of records
   - Data pointer: address of a record table in ROM or RAM

2. **Provide a data record table** with at least one 24-byte record (for the DISK MENU sub-object):
   - `+0x00`: Implementation function pointer (our handler function)
   - `+0x04`: Next handler ID (chain to Root module, e.g., `0x0160001D`, or `0xFFFFFFFF` for none)
   - `+0x08-0x14`: Config fields (may need specific values for the default handler to work)

3. **Set `slot+0x00`** to `0x016A0005` (or appropriate sub-index matching the record position in the data table)

4. **Implement a handler function** that:
   - Delegates most requests to `workspace[0x0E0A][0x00DC]` (the default handler)
   - Optionally intercepts specific requests (e.g., `0x01C0000F`) for custom initialization

### Open Questions

- What specific record fields (`+0x08` through `+0x14`) does the default handler at `workspace[0x0E0A][0x00DC]` expect?
- Can the "next" chain link (`record[+0x04]`) be `0xFFFFFFFF` for a standalone handler, or must it chain to a Root module component?
- What lifecycle events does the default handler send to the record function during activation, and what responses are expected?
- Can the Mines project use a simpler approach (e.g., intercepting the activation in Frame_Handler via a flag) instead of fully participating in the object dispatch system?

## Control Panel Input

The KN5000 control panel communicates with the main CPU via SC1 synchronous serial at 250 kHz. The firmware manages this communication in its main event loop.

### Input Routing Considerations

For homebrew projects that need button input:

1. **Direct SC1 access** -- Reading SC1BUF directly works but may conflict with the firmware's own panel polling. The firmware polls the control panel every main loop iteration, and concurrent access to SC1 could corrupt the serial protocol state.

2. **Firmware-mediated input** -- The firmware's callback dispatch system likely provides a way for extensions to receive input events. The workspace callbacks at offsets `0x0244`, `0x0248`, and `0x024C` in Handler Table A are labeled as "UI callbacks" and may provide this mechanism.

3. **Interrupt-based input** -- The SC1 RX interrupt (`INTRX1`) could be used, but would need careful coordination with the firmware's interrupt handlers.

**Current approach in Mines:** Direct SC1 serial access works for basic testing in MAME, with edge detection to convert held buttons into single-press events. For production use on real hardware, firmware-mediated input would be more reliable.

### Button Mapping

See the [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) page for the full serial protocol. For game-like input, useful buttons include:

| Button Group | Panel | Segment | Bit | Suggested Use |
|-------------|-------|---------|-----|---------------|
| Part Select: Right 2 | Right | 4 | 1 | UP |
| Conductor: Left | Right | 4 | 4 | LEFT |
| Conductor: Right 2 | Right | 4 | 5 | DOWN |
| Conductor: Right 1 | Right | 4 | 6 | RIGHT |
| Variation 4 | Left | 4 | 3 | ACTION (open cell) |
| Page Up | Left | 2 | 7 | SECONDARY (flag) |
| Exit | Left | 7 | 3 | QUIT |

## LLVM TLCS-900 Assembler Encoding Bugs

The LLVM TLCS-900 assembler backend has several encoding bugs that produce invalid machine code. These affect any project using LLVM to target the TLCS-900 architecture.

### Bug 1: Direct Memory Load Prefix

**Instruction:** `ld reg, (addr)` (load from absolute address)

**Bug:** LLVM uses the `F2` prefix (F0/store group) instead of `E2` (E0/load group). In the F0 sub-opcode table, entry `0x26` is `LDA` (load address), not `LD` (load data) as in the E0 table.

**Workaround:**
```asm
; Instead of: ld xwa, (0x200008)     -- BROKEN
ld   xhl, 0x200008                    ; load address into register
ld   xwa, (xhl)                       ; then dereference
```

### Bug 2: Immediate-to-Memory Store Sub-opcode

**Instruction:** `ld (addr), imm32` (store immediate to absolute address)

**Bug:** LLVM emits sub-opcode `0x08` in the F0 table, which does not exist on the TLCS-900. The hardware only supports `0x00` (byte immediate) and `0x02` (word immediate) -- there is no 32-bit immediate-to-memory store.

**Workaround:**
```asm
; Instead of: ld (0x200000), 0x100   -- BROKEN
ld   xde, 0x200000                    ; load address
ld   xwa, 0x00000100                  ; load value
ld   (xde), xwa                       ; store via register-indirect
```

### Bug 3: Indirect CALL Sub-opcode

**Instruction:** `call (xreg)` (call function at address in register)

**Bug:** LLVM emits sub-opcode `0x1F` in the b0 table, which is undefined on the TLCS-900. The correct encoding for an unconditional call is `0xE8` (CALL T, where T = True = condition code 8). CALL entries occupy `0xE0-0xEF` in the b0 table, one per condition code.

**Workaround:**
```asm
; Instead of: call (xix)             -- BROKEN (emits 0x1F)
.byte 0xB4, 0xE8                      ; B4 = XIX prefix, E8 = CALL T

; Register prefix bytes for indirect CALL:
;   B0 = XWA, B1 = XBC, B2 = XDE, B3 = XHL
;   B4 = XIX, B5 = XIY, B6 = XIZ, B7 = XSP
```

### Bug 4: JP Opcode (Fixed in LLVM Backend)

**Instruction:** `jp target` (unconditional jump)

**Bug:** LLVM originally encoded JP as opcode `0x1C`, which is actually `CALL I16` (call with 16-bit address) on the real hardware. This was fixed in the LLVM backend to use the correct opcode `0x1B` (JP I24, jump with 24-bit address).

### Bug 5: Register+Displacement Loads

**Instruction:** `ld xreg, (xreg + disp)` (load from register + displacement)

**Bug:** LLVM does not support encoding register+displacement loads. This was initially believed to be a hardware limitation, but the original HDAE5000 ROM uses instructions like `ld XWA, (XWA + 0x0E0A)` successfully -- confirming the hardware *does* support this addressing mode. Stores with displacement (`ld (xreg + disp), src`) work correctly in LLVM.

**Workaround:**
```asm
; Instead of: ld xiz, (xiz + 0x0E0A)  -- NOT SUPPORTED
add  xiz, 0x0E0A                       ; modify register (destructive)
ld   xiz, (xiz)                        ; then dereference
```

### TLCS-900 Opcode Reference for Workarounds

Understanding the opcode table structure helps when crafting raw `.byte` workarounds:

| Prefix Range | Table | Purpose |
|-------------|-------|---------|
| A0-A7 | a0/e0 | Source register indirect (loads) |
| B0-B7 | b0 | Destination register indirect (stores, CALL, JP) |
| B8-BF | b0 + 8-bit displacement | Register indirect + displacement |
| E0-E5 | e0 | Direct memory addressing (loads) |
| F0-F5 | f0 | Direct memory addressing (stores) |

Key b0 sub-opcodes:

| Range | Operation |
|-------|-----------|
| 0x40-0x47 | LD (M), C8 -- store 8-bit register |
| 0x50-0x57 | LD (M), C16 -- store 16-bit register |
| 0x60-0x67 | LD (M), C32 -- store 32-bit register |
| 0xD0-0xDF | JP cc, (M) -- conditional jump indirect |
| 0xE0-0xEF | CALL cc, (M) -- conditional call indirect |

Register indices (for prefixes and sub-opcodes):

| Index | 32-bit | 16-bit | 8-bit |
|-------|--------|--------|-------|
| 0 | XWA | WA | A |
| 1 | XBC | BC | C |
| 2 | XDE | DE | E |
| 3 | XHL | HL | L |
| 4 | XIX | IX | - |
| 5 | XIY | IY | - |
| 6 | XIZ | IZ | - |
| 7 | XSP | SP | - |

## Build Pipeline

The build uses a pure LLVM toolchain:

```
C sources --> clang (-emit-llvm) --> .ll files
                                        |
                                        v
                            llvm-link (merge) --> merged.ll
                                                     |
                                                     v
                                    llc (-filetype=obj) --> all_c.o
                                                               |
startup.s --> clang -c --> startup.o                           |
                              |                                |
                              v                                v
                     ld.lld (linker script) --> ELF
                                                |
                                                v
                              llvm-objcopy -O binary --> raw ROM
                                                           |
                                                           v
                                               dd pad --> 512KB ROM
```

### Linker Script

The linker script places code and data in the extension ROM address space:

```
MEMORY {
  ROM (rx)  : ORIGIN = 0x280000, LENGTH = 512K
  RAM (rwx) : ORIGIN = 0x200000, LENGTH = 12K
}
SECTIONS {
  .startup 0x280000 : { startup.o(.startup) } > ROM
  .text             : { all_c.o(.text) } > ROM
  .rodata           : { *(.rodata*) } > ROM
  .data             : { *(.data*) } > RAM AT > ROM
  .bss              : { *(.bss*) } > RAM
}
```

### Minimal Startup Assembly

A minimal working extension ROM needs only a header, Boot_Init, and Frame_Handler:

```asm
.section .startup, "ax", @progbits

; XAPR Header
    .ascii  "XAPR"
    .byte   0x34, 0xA1, 0x2F, 0x00

; Entry Point 1: Boot_Init (offset 0x08)
    jp      Boot_Init
    ret
    .byte   0x00, 0x00, 0x00

; Entry Point 2: Frame_Handler (offset 0x10)
    jp      Frame_Handler
    ret
    .byte   0x00, 0x00, 0x00

; Entry Points 3-4: Unused
    ret
    .byte   0x00, 0x00, 0x00
    ret
    .byte   0x00, 0x00, 0x00

; Boot_Init: called once with XWA = workspace pointer (0x027ED2)
Boot_Init:
    push    xde
    ld      xde, 0x200000           ; extension RAM
    ld      (xde), xwa              ; store workspace pointer
    pop     xde
    ret

; Frame_Handler: called every frame by firmware
Frame_Handler:
    ; Your per-frame code here
    ret
```

## Memory Map for Custom ROMs

| Address Range | Size | Region | Use |
|--------------|------|--------|-----|
| 0x200000-0x27FFFF | 256KB | Extension RAM | Variables, stack, heap |
| 0x280000-0x2FFFFF | 512KB | Extension ROM | Code, read-only data |
| 0x1A0000-0x1DFFFF | 256KB | Video RAM | 320x240 8bpp linear framebuffer |
| 0x1703C6 | 1B | VGA DAC Mask | Palette mask register |
| 0x1703C8 | 1B | VGA DAC Index | Palette write index |
| 0x1703C9 | 1B | VGA DAC Data | RGB data (write 3 bytes sequentially) |
| 0x1703D4 | 1B | VGA CRTC Index | CRTC register select |
| 0x1703D5 | 1B | VGA CRTC Data | CRTC register data |
| 0x0D53 | 1B | Display Flags | Bit 3: display disable (firmware SFR) |
| 0x03DD04 | 1B | XAPR Flag | Extension ROM detection (1=present) |

The KN5000's LCD is 320x240 pixels at 8 bits per pixel (256-color indexed palette). VRAM starts at `0x1A0000` with a linear framebuffer layout (row-major, 320 bytes per row). See [Display Ownership Model](#display-ownership-model) for details on taking control of the display.

## Testing with MAME

Install your ROM as the HDAE5000 extension:

```bash
# Copy to MAME ROM set
cp your_rom.bin rompath/kn5000/hd-ae5000_v2_06i.ic4

# Run with extension enabled
mame kn5000 -rompath rompath -extension hdae5000 -window -oslog
```

The `-oslog` flag captures debug output, including any invalid instruction reports from the TLCS-900 CPU emulation.

## Related Pages

- [HDAE5000 Hard Disk Expansion]({{ site.baseurl }}/hdae5000/) -- Original firmware documentation
- [Display Subsystem]({{ site.baseurl }}/display-subsystem/) -- VGA controller and display architecture
- [Control Panel Protocol]({{ site.baseurl }}/control-panel-protocol/) -- Serial input protocol
- [Memory Map]({{ site.baseurl }}/memory-map/) -- Full system address space
- [Boot Sequence]({{ site.baseurl }}/boot-sequence/) -- System startup and XAPR validation
- [Another World VM]({{ site.baseurl }}/another-world-vm/) -- Another homebrew project for the KN5000
