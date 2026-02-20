---
layout: page
title: "HDAE5000 Homebrew Development"
permalink: /hdae5000-homebrew/
---

# Writing Custom HDAE5000 Extension ROMs

The HD-AE5000 extension slot can run custom code on the KN5000's main CPU. By replacing the HDAE5000 ROM with a custom binary, you can create games, demos, or utilities that run on the keyboard hardware. This page documents the extension ROM protocol, known toolchain bugs, and a working build pipeline.

> **Status**: Boot initialization, frame handler callbacks, and DISK MENU registration are working. The extension ROM appears in the DISK MENU with a custom icon and name. The firmware's object dispatch system (`SendEvent`, `ClassProc`, `ObjectProc`, `InheritedProc`, `RegisterObjectTable`) and the HDAE5000's 13-component data record table have been fully analyzed. Display ownership (taking over the LCD from the firmware) and game activation from the DISK MENU require implementing the data record table and handler function.

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

Both handler tables are in main DRAM (0x000000-0x0FFFFF range). The values at these offsets are function pointers into the firmware ROM. The offset `+0x0168` resolves to `ClassProc` (0xFA44E2), the shared DISK MENU handler used by all built-in modules. The offset `+0x00E4` resolves to `RegisterObjectTable` (0xFA42FB).

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

The Handler_Registration routine at `0x280020` (now fully disassembled) registers handlers by building a 14-byte parameter block on the stack and calling the `RegisterObjectTable` function.

#### Parameter Block Format

```
Parameter block layout (14 bytes):
  +0x00  4 bytes  Port address (identifies handler type)
  +0x04  4 bytes  Handler function pointer (from workspace dispatch table)
  +0x08  2 bytes  Record count (number of sub-objects) ← 16-bit field!
  +0x0A  4 bytes  Data pointer → record table (RAM or ROM address)

Call convention:
  WA  = handler ID (object table index, max 0x045F = 1119)
  XBC = pointer to parameter block (stack or RAM)
  Call workspace[0x0E0A][0x00E4]
```

**Important:** The `+0x08` field is a **record count** (number of 24-byte sub-object records), NOT a byte size. This was confirmed by:
- HDAE5000 handler 0x016A has `+0x08 = 0x000D` (13 records, matching its 13 sub-objects)
- `RegisterObject` (0xFA431A) increments `+0x08` when adding sub-objects
- `UnRegisterObject` (0xFA43B3) decrements `+0x08` when removing them
- Built-in handlers use counts like 55, 32, 256 (matching their sub-object counts)

#### RegisterObjectTable Implementation (0xFA42FB)

The actual implementation is a simple 14-byte block copy:

```asm
RegisterObjectTable:          ; 0xFA42FB
    CP    WA, 045Fh           ; Validate handler ID <= 1119
    RET   UGT                 ; Return if out of range
    EXTZ  XWA                 ; Zero-extend WA to 32-bit
    LD    XDE, XWA
    SLL   3, XDE              ; XDE = id * 8
    SUB   XDE, XWA            ; XDE = id * 7
    ADD   XDE, XDE            ; XDE = id * 14
    LD    XIX, 00027ED2h      ; Object table base address
    ADD   XIX, XDE            ; XIX = base + id * 14
    LD    XIY, XBC            ; XIY = parameter block source
    LD    BC, 7               ; 7 words = 14 bytes
    LDIRW                     ; Block copy from source to object table
    RET
```

This means `RegisterObjectTable` simply copies 14 bytes from the caller's parameter block to `object_table[handler_id * 14]`. The object table base at `0x027ED2` can hold up to 1,120 entries (handler IDs 0x0000-0x045F).

#### RegObjTable Macro (Firmware Convention)

The main CPU firmware uses two macro variants for handler registration:

```asm
; Variant 1: Data size read from ROM address
RegObjTable MACRO ParamA, ParamB, ParamC, ParamD, ParamE
    LDA   XBC, XSP            ; XBC = param block ptr (ON STACK)
    LD    XWA, ParamA          ; Port address (32-bit)
    LD    (XBC), XWA
    LDA   XWA, ParamB          ; Handler function (LEA, not LD)
    LD    (XBC + 004h), XWA
    LD    WA, (ParamC)          ; Data size: 16-bit read from ROM address
    LD    (XBC + 008h), WA      ; 16-BIT store to +0x08
    LDA   XWA, ParamD          ; Data pointer (LEA)
    LD    (XBC + 00Ah), XWA
    LD    WA, ParamE            ; Handler ID (16-bit)
    CALL  RegisterObjectTable
ENDM

; Variant 2: Data size as immediate value
RegObjTabl MACRO ParamA, ParamB, ParamC, ParamD, ParamE
    LDA   XBC, XSP
    LD    XWA, ParamA
    LD    (XBC), XWA
    LDA   XWA, ParamB
    LD    (XBC + 004h), XWA
    LDW   (XBC + 008h:8), ParamC   ; Immediate 16-bit store
    LDA   XWA, ParamD
    LD    (XBC + 00Ah), XWA
    LD    WA, ParamE
    CALL  RegisterObjectTable
ENDM
```

**Key detail:** Both macros use `LDA XBC, XSP` to point XBC at the parameter block which is allocated on the stack. The HDAE5000 also allocates its parameter block on the stack (14 bytes via `LDA XSP, XSP - 0Eh`). The parameter block can be anywhere in RAM -- the `RegisterObjectTable` function just does a block copy from whatever address XBC points to.

#### Firmware Registration Examples

All built-in DISK MENU modules (port `0x01600004`) use `ClassProc` (0xFA44E2) as their handler function:

```
RegObjTable 01600004h, 0FA44E2h, 0E0CDACh, 0E0CD94h, 0166h  ; InitializeScoop
RegObjTable 01600004h, 0FA44E2h, 0E0E95Ch, 0E0E944h, 016Bh  ; InitializeKSS
RegObjTable 01600004h, 0FA44E2h, 0E17322h, 0E16C86h, 0164h  ; InitializeSuna
RegObjTable 01600004h, 0FA44E2h, 0E1F0BCh, 0E1F080h, 0169h  ; InitializeHama
RegObjTable 01600004h, 0FA44E2h, 0E20CAEh, 0E208ECh, 0167h  ; InitializeKubo
RegObjTable 01600004h, 0FA44E2h, 0E27596h, 0E27180h, 0168h  ; InitializeNaka
```

Handler IDs `0x0160`-`0x016B` are all DISK MENU modules. The HDAE5000 claims `0x016A`.

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

The data pointer registered for handler `0x016A` (`0x29C0AA`) points to a table of **24-byte records**, one per UI component (sub-object). The HDAE5000 has 13 sub-objects (record count `+0x08` = 0x000D):

```
Record layout (24 bytes):
  +0x00  4 bytes  Implementation function pointer (in ROM)
  +0x04  4 bytes  Next handler ID (linked list chain, 0xFFFFFFFF = end)
  +0x08  2 bytes  Config size (UI-specific parameter)
  +0x0A  2 bytes  Config flags
  +0x0C  4 bytes  ROM data pointer 1 (name/config strings)
  +0x10  4 bytes  ROM data pointer 2 (secondary config)
  +0x14  4 bytes  RAM workspace pointer
```

| Rec | Name | Func | Next | Size | Flags | Data1 | Data2 | RAM |
|-----|------|------|------|------|-------|-------|-------|-----|
| 0 | SelectList | 0x2807D9 | 0x01600011 | 0x3C | 0x20 | 0x29D972 | 0x29D966 | 0x23975A |
| 1 | DbMemoCl | 0x28122A | 0x01600046 | 0x1A | 0x04 | 0x29D95C | 0x29D958 | 0x23978A |
| 2 | TtlScreenR | 0x280489 | 0x01600034 | 0x2A | 0x00 | 0x29D94C | 0x29D94A | 0x239796 |
| 3 | AcHddNamingWindow | 0x281411 | 0x01600035 | 0x24 | 0x00 | 0x29D938 | 0x29D936 | 0x23979A |
| 4 | IvHddNaming | 0x282681 | 0x01600027 | 0x1A | 0x04 | 0x29D92A | 0x29D928 | 0x23979E |
| **5** | **HDTitleMenu** | **0x2827A8** | **0x0160001D** | **0x36** | **0x00** | **0x29D91C** | **0x29D91A** | **0x2397A6** |
| 6 | TtlScreenR2 | 0x280567 | 0x01600034 | 0x2A | 0x00 | 0x29D90E | 0x29D90C | 0x2397AA |
| 7 | TtlScreenR3 | 0x280645 | 0x01600034 | 0x2A | 0x00 | 0x29D900 | 0x29D8FE | 0x2397AE |
| 8 | AcWindowPage1 | 0x28043C | 0x01600025 | 0x24 | 0x00 | 0x29D8F0 | 0x29D8EE | 0x2397B2 |
| 9 | IvScreenR2 | 0x280723 | 0x0160006A | 0x22 | 0x00 | 0x29D8E2 | 0x29D8E0 | 0x2397B6 |
| 10 | AcLanguageText1 | 0x28B554 | 0x01600066 | 0x2A | 0x00 | 0x29D8D0 | 0x29D8CE | 0x2397BA |
| 11 | LyricBox | 0x28CD08 | 0x01600011 | 0x2E | 0x12 | 0x29D8C4 | 0x29D8BC | 0x2397BE |
| 12 | FDFileSelect | 0x28E61B | 0x01600027 | 0x20 | 0x0A | 0x29D8AE | 0x29D8AA | 0x2397DA |

**Record 5 ("HDTitleMenu") is the DISK MENU entry handler.** Its sub-index (5) matches the low word in `slot+0x00 = 0x016A0005` (object index 0x016A, sub-index 0x0005). The "next" link chains each sub-object to a corresponding component in the Root module (object 0x0160), forming an **inheritance hierarchy** where HDAE5000 components extend base firmware components.

**Key observations from ROM data:**
- All data pointer pairs (Data1/Data2) are adjacent ROM addresses 2 bytes apart (Data1 = Data2 + 2)
- RAM workspace pointers are sequential in the 0x2397xx range (10 bytes apart)
- Record 5 chains to Root module handler `0x0160001D`
- Flags 0x04 appear on input-related records (1, 4); 0x12 on LyricBox; 0x0A on FileSelect

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

### Firmware Symbol Names

The main CPU firmware symbol table reveals the real names for these functions:

| Address | Symbol Name | Previous Name | Purpose |
|---------|-------------|---------------|---------|
| 0xFA9660 | **SendEvent** | "FA9660" | Main event dispatch entry point |
| 0xFA44E2 | **ClassProc** | "Layer 1 handler" | UI event handler (shared by all DISK MENU modules) |
| 0xFA3D85 | **ObjectProc** | "Layer 2 dispatch" | Object lifecycle event handler |
| 0xFA4409 | **InheritedProc** | "Layer 3 chain dispatch" | Handler chain traversal |
| 0xFA42FB | **RegisterObjectTable** | "workspace[0x0E0A][0x00E4]" | Register handler in object table |
| 0xFA431A | **RegisterObject** | (unnamed) | Register individual object entry |
| 0xFA43B3 | **UnRegisterObject** | (unnamed) | Remove object entry |
| 0xFAD61F | **PostEvent** | "ApPostEvent" | Queue event for asynchronous dispatch |

### Architecture Overview

```
Object Table (0x027ED2)                  Data Record Table
 14-byte entries, max 1120               24-byte records per sub-object
┌──────────────────────────────┐       ┌────────────────────────────────┐
│ +0x00: Port address (4)      │       │ +0x00: Impl function ptr (4)   │
│ +0x04: Handler function (4)  │       │ +0x04: Next handler ID (4)     │
│ +0x08: Data size (2)         │       │ +0x08: Size/count (2)          │
│ +0x0A: Data pointer (4) ─────┼──────>│ +0x0A: Flags (2)               │
└──────────────────────────────┘       │ +0x0C: ROM data ptr (4)        │
                                       │ +0x10: ROM data ptr 2 (4)      │
Global State (saved/restored            │ +0x14: RAM workspace ptr (4)   │
 per dispatch call):                    └────────────────────────────────┘
  0x02BC14: Current object identity (SetCurrentTarget/GetCurrentTarget)
  0x02BC18-20: Root object/event/param (SetRootObject/GetRootObject etc.)
  0x02BC24-2C: Focus object/event/param (GetFocusObject/GetFocusEvent etc.)
```

### Object Identifiers

Object IDs combine an object table index with a sub-object index:

```
  0x016A0005
  ├── 0x016A  = Object table index (handler ID registered via RegisterObjectTable)
  └── 0x0005  = Sub-object index (record number in data table)
```

The `slot+0x00` field in the DISK MENU slot stores this combined identifier, linking the menu entry to a specific sub-object (record) in the handler's data table.

### SendEvent (0xFA9660) — Main Event Dispatch

`SendEvent` is the firmware's synchronous event dispatch. Every request to an object goes through this function:

```
SendEvent(XWA=object_id, XBC=request_code, XDE=param):
  1. Save current focus state (0x02BC24-2C) to stack
  2. Extract handler_index = (object_id >> 16) & 0xFFF
  3. Look up handler function from object_table[handler_index * 14 + 4]
  4. Call handler(object_id, 0x01E00000, 0) → "identity" query
  5. Set 0x02BC14 = identity result (via handler function)
  6. Extract sub_index from identity result
  7. Look up data record table from object_table[handler_index * 14 + 0x0A]
  8. Read implementation function from record[sub_index * 24 + 0x00]
  9. Call record_function(object_id, request_code, param)
  10. Restore focus state from stack
  11. Return result in XHL
```

The identity query (step 4) calls through the registered handler function (e.g., `ClassProc` for DISK MENU objects). For request `0x01E00000`, `ClassProc` simply returns XWA unchanged, so the identity equals the object ID.

### PostEvent (0xFAD61F) — Asynchronous Event Queue

`PostEvent` (previously called "ApPostEvent") queues events for later dispatch:

```asm
PostEvent:                    ; 0xFAD61F
    ; Allocate 8 bytes on stack, save registers
    ; Acquire lock (CALL 0xEF1EA7 with WA=4)
    ; Read queue state:
    ;   BC = queue size from (0x02EC34)
    ;   DE = write index from (0x02EC36)
    ; Check for queue full (WA = DE + 1, compare with BC)
    ; If full: release lock, spin forever (deadlock!)
    ;
    ; Write 12-byte event entry to queue:
    ;   Queue base: 0x02BC34
    ;   Entry address: 0x02BC34 + (write_index * 12)
    ;   +0x00: XIZ (target object ID)
    ;   +0x04: XBC (event code)
    ;   +0x08: XDE (parameter)
    ;
    ; Advance write index (wrap at 0x03FF)
    ; Increment event counter at 0x02F840
    ; Release locks
    RET
```

The event queue is a ring buffer with 1,024 entries (indices 0x0000-0x03FF), each 12 bytes. Events are dequeued by the main loop and dispatched via `SendEvent`.

### Request Code Dispatch (Three Layers)

`ClassProc` (shared by all DISK MENU modules) dispatches requests through three layers:

```
ClassProc (0xFA44E2): UI event handler
  ├── 0x01E00000-0x01E00007: Jump table via 0xEAA8F8
  │   ├── Case 0 (0x01E00000): Return XWA (identity)
  │   ├── Case 1 (0x01E00001): Return *(XHL)
  │   ├── Case 2 (0x01E00002): Return *(XIZ)
  │   ├── Case 3 (0x01E00003): Return *(XHL+0x0C)
  │   ├── Case 4-7: (complex linked object operations)
  │   Via helper functions:
  │     ClassProc_Event_LoadFromWA   (0xFA4598)
  │     ClassProc_Event_LoadFromHL   (0xFA459D)
  │     ClassProc_Event_LoadFromIZ   (0xFA45A2)
  │     ClassProc_Event_LoadFromOffset (0xFA45A7)
  ├── 0x01E0000D: Special case (keypress handling)
  ├── 0x01E0000E: Special case (other input)
  ├── 0x01E0000F: Return immediately
  ├── 0x01E00015: Return *(XHL+0x0C)
  └── Default (including 0x01E0009C): → ObjectProc
                                         │
ObjectProc (0xFA3D85): Lifecycle events
  ├── Allocates 0x90 bytes stack frame
  ├── Extracts handler index, looks up data records
  ├── Calls handler identity query first
  ├── 0x01E00010-0x01E00023: 20 cases via jump table at 0xEAA8A4
  │   (setters, init/teardown, string operations)
  └── Out of range (including 0x01E0009C): → InheritedProc
                                               │
InheritedProc (0xFA4409): Handler chain traversal
  ├── Read current target identity from 0x02BC14
  ├── Extract handler_index and sub_index
  ├── Look up data record table for current handler
  ├── Read "next" handler ID from record[sub_index * 24 + 0x04]
  ├── If next ≠ 0xFFFFFFFF:
  │     Set 0x02BC14 = next handler ID
  │     Look up next handler's record table
  │     Call next handler's implementation function
  │     Restore 0x02BC14 to original value
  │     Return result
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

### Dispatch Flow for Activation Event (0x01E0009C)

When the DISK MENU activation event reaches our handler:

```
PostEvent(0x00600002, 0x01E0009C, 0)
  → Event queue stores entry
  → Main loop dequeues event
  → SendEvent(slot[+0x00], 0x01E0009C, 0)
    → ClassProc: 0x01E0009C not in simple getter range → ObjectProc
      → ObjectProc: 0x01E0009C not in 0x10-0x23 range → InheritedProc
        → InheritedProc: follows record[+0x04] "next" chain
          → If next = 0xFFFFFFFF: returns 0 (no further handler)
          → If next = valid ID: calls that handler's function
```

**Key insight:** For the activation event `0x01E0009C`, neither `ClassProc` nor `ObjectProc` handle it directly. It falls through to `InheritedProc`, which follows the "next handler" chain in the data record. If the chain ends (`0xFFFFFFFF`), nothing happens. The actual activation must be handled by the record's implementation function (called by `SendEvent` at step 9), or by a chained handler via `InheritedProc`.

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
LD    XBC, 01E0009Ch         ; Event code: activate
LD    XDE, 0                 ; Parameter: none
CALL  PostEvent              ; Queue event for dispatch
```

`PostEvent` (0xFAD61F) queues events in a ring buffer at `0x02BC34` (12-byte entries, max 1,024). The main event loop dequeues events and dispatches them synchronously via `SendEvent`.

### Complete Activation Flow

When `PostEvent(0x00600002, 0x01E0009C, 0)` is dispatched:

```
1. Main loop dequeues event from ring buffer at 0x02BC34
2. SendEvent(object_id, 0x01E0009C, 0)
   where object_id = slot[+0x00] (e.g., 0x016A0005)

3. SendEvent extracts handler_index = 0x016A
4. Looks up object_table[0x016A * 14 + 4] → handler function (ClassProc)
5. Calls ClassProc(0x016A0005, 0x01E00000, 0) → identity = 0x016A0005
6. Sets 0x02BC14 = 0x016A0005

7. Looks up data_ptr from object_table[0x016A * 14 + 0x0A]
8. Extracts sub_index = 5 from identity
9. Reads record[5 * 24 + 0x00] → implementation function (0x2827A8)
10. Calls 0x2827A8(0x016A0005, 0x01E0009C, 0)
11. Handler delegates to workspace[0x0E0A][0x00DC] (default handler)
12. Default handler manages the DISK MENU activation lifecycle
```

### What Mines Needs for DISK MENU Activation

Based on the complete dispatch analysis, the Mines project needs:

1. **Register handler `0x016A`** via `RegisterObjectTable` (workspace[0x0E0A][0x00E4]) with:
   - Port: `0x01600004`
   - Handler function: `ClassProc` (via workspace[0x0E0A][0x0168], resolves to 0xFA44E2)
   - Record count: number of 24-byte records in the data table (e.g., 1 for a single sub-object)
   - Data pointer: address of data record table in ROM

2. **Provide a data record table** with at least one 24-byte record:
   - `+0x00`: Implementation function pointer (our handler function)
   - `+0x04`: Next handler ID (`0xFFFFFFFF` for end-of-chain, or chain to Root module e.g. `0x0160001D`)
   - `+0x08-0x14`: Config fields (may need specific values for the default handler to work)

3. **Set `slot+0x00`** to `0x016A0005` (handler 0x016A, sub-index 5 matching the HDAE5000 convention) — or `0x016A0000` if using sub-index 0

4. **Implement a handler function** that:
   - Delegates most requests to `workspace[0x0E0A][0x00DC]` (the default handler)
   - Intercepts `0x01E0009C` to set the `GAME_ACTIVE` flag
   - Optionally intercepts `0x01C0000F` for custom initialization (as the original HDAE5000 does)

### Object System Initialization

The firmware initializes the object table at startup via `InitializeObjectTable` (0xFA40B2). This function:

1. Clears all 1,120 entries in the object table (14 bytes each)
2. Initializes internal dispatch tables (0x0328FC and 0x032ABC)
3. Registers built-in system handlers (IDs 0x0260, 0x0180, 0x01A0, 0x0000-0x00FF, 0x0300-0x03FF)
4. Calls 31 `Initialize*` functions (one per built-in module): `InitializeMurai`, `InitializeToshi`, `InitializeEast`, `InitializeSuna`, `InitializeCheap`, `InitializeScoop`, `InitializeYoko`, `InitializeKubo`, `InitializeHama`, `InitializeKSS`, `InitializeNaka`, and `InitializeUser12`-`InitializeUser31`
5. Each `Initialize*` function calls `RegisterObjectTable` with that module's handlers

The HDAE5000's `Handler_Registration` runs later (during `Boot_Init`), overwriting the table entry for handler `0x016A` that was previously initialized by one of the built-in modules.

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
