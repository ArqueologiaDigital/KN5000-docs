---
layout: page
title: "Event Codes Reference"
permalink: /event-codes/
---

# Firmware Event Codes Reference

The KN5000 firmware uses a **hierarchical event dispatch system** to communicate between UI components, DISK MENU handlers, and extension ROMs. Events are 32-bit codes dispatched via `SendEvent` (synchronous) or `PostEvent` (asynchronous queue). This page documents all known event codes, their dispatch paths, and how they interact with the handler chain.

> **Freshness policy**: This page must be updated whenever new event codes are discovered during reverse engineering or homebrew development. See [Documentation Freshness Policy](#documentation-freshness-policy) below.

## Event Code Format

Event codes are 32-bit values with a structured layout:

```
  0x01E0009C
  ├── 0x01E0  = Event port/category prefix
  └── 0x009C  = Event number within that category
```

The prefix determines which dispatch layer handles the event:

| Prefix | Category | Dispatch Layer | Description |
|--------|----------|----------------|-------------|
| `0x01E0` | Lifecycle / Object | ClassProc → ObjectProc → InheritedProc | Object lifecycle, getters, activation |
| `0x01C0` | Request / Action | Record function directly | Button presses, UI actions, initialization |
| `0x01E4` | Grid/Check Response | UI widget system | Widget state query responses |

## Dispatch Architecture

```
Event arrives (via SendEvent or PostEvent queue)
    │
    ▼
SendEvent (0xFA9660)
    │  Saves global state, looks up handler from object table
    │  Calls handler function (typically ClassProc)
    │
    ▼
ClassProc (0xFA44E2) ─── Layer 1: Simple Getters & Specials
    │  Handles: 0x01E00000-0x01E00007 (getters via jump table)
    │           0x01E0000D (keypress), 0x01E0000E (input)
    │           0x01E0000F (return immediately)
    │           0x01E00015 (return config pointer)
    │
    │  Everything else falls through to:
    ▼
ObjectProc (0xFA3D85) ─── Layer 2: Lifecycle Events
    │  Handles: 0x01E00010-0x01E00023 (20 lifecycle cases)
    │           via jump table at 0xEAA8A4
    │
    │  Everything else falls through to:
    ▼
InheritedProc (0xFA4409) ─── Layer 3: Handler Chain
    │  Follows "next handler" chain in data record (+0x04)
    │  Calls chained handler's implementation function
    │
    ▼
Record Function (implementation) ─── Layer 4: Handler-Specific
    │  Called by SendEvent (step 9) for ALL events
    │  Receives: XWA=object_id, XBC=event_code, XDE=param
    │  This is where extension ROM handlers intercept events
    │
    ▼
Default Handler (workspace[0x0E0A][0x00DC])
    Handles remaining lifecycle management if delegated
```

**Key insight:** The record function (Layer 4) receives ALL events, regardless of which layer processed them first. For extension ROMs, the record function is the primary interception point.

## Known Event Codes

### ClassProc Getter Events (0x01E00000-0x01E00007)

Handled by ClassProc's jump table at `0xEAA8F8`. These are fast property queries.

| Code | Name | Handler | Return Value |
|------|------|---------|-------------|
| `0x01E00000` | `EVT_IDENTITY` | ClassProc_Event_LoadFromWA | Returns XWA unchanged (identity query) |
| `0x01E00001` | `EVT_GET_HL` | ClassProc_Event_LoadFromHL | Returns *(XHL) |
| `0x01E00002` | `EVT_GET_IZ` | ClassProc_Event_LoadFromIZ | Returns *(XIZ) |
| `0x01E00003` | `EVT_GET_CONFIG` | ClassProc_Event_LoadFromOffset | Returns *(XHL+0x0C) |
| `0x01E00004` | `EVT_GETTER_4` | (complex) | Linked object operation |
| `0x01E00005` | `EVT_GETTER_5` | (complex) | Linked object operation |
| `0x01E00006` | `EVT_GETTER_6` | (complex) | Linked object operation |
| `0x01E00007` | `EVT_GETTER_7` | (complex) | Linked object operation |

### ClassProc Special Events

| Code | Name | Dispatch | Description |
|------|------|----------|-------------|
| `0x01E0000D` | `EVT_KEYPRESS` | ClassProc special | Keypress handling |
| `0x01E0000E` | `EVT_INPUT` | ClassProc special | Other input event |
| `0x01E0000F` | `EVT_RETURN_ZERO` | ClassProc special | Returns immediately (no-op) |
| `0x01E00015` | `EVT_GET_CONFIG_2` | ClassProc special | Returns *(XHL+0x0C) |

### ObjectProc Lifecycle Events (0x01E00010-0x01E00023)

Handled by ObjectProc's jump table at `0xEAA8A4`. These manage object lifecycle (creation, destruction, state changes). Each maps to a specific lifecycle phase.

| Code | Name | Description |
|------|------|-------------|
| `0x01E00010` | `EVT_LIFECYCLE_10` | Lifecycle phase 0x10 |
| `0x01E00011` | `EVT_LIFECYCLE_11` | Lifecycle phase 0x11 |
| `0x01E00012` | `EVT_LIFECYCLE_12` | Lifecycle phase 0x12 |
| `0x01E00013` | `EVT_LIFECYCLE_13` | Lifecycle phase 0x13 |
| `0x01E00014` | `EVT_REDRAW` | UI redraw / refresh (observed during DISK MENU open and selection) |
| `0x01E00015` | `EVT_LIFECYCLE_15` | Lifecycle phase 0x15 (also ClassProc special) |
| `0x01E00016` | `EVT_LIFECYCLE_16` | Lifecycle phase 0x16 |
| ... | ... | Phases 0x17-0x22 (not yet individually documented) |
| `0x01E00023` | `EVT_LIFECYCLE_23` | Lifecycle phase 0x23 (last) |

### DISK MENU Selection Events (0x01C0xxxx)

These are **request/action events** that reach the record function directly. They are the primary events extension ROMs should intercept.

| Code | Name | Context | Description |
|------|------|---------|-------------|
| `0x01C00001` | `EVT_MENU_OPEN` | DISK MENU opens | Sent when the DISK MENU screen is displayed |
| `0x01C00002` | `EVT_SELECT_CONFIRM` | Entry selected | Part of the selection sequence after button press |
| `0x01C00008` | **`EVT_ACTIVATE`** | **Entry selected** | **Primary activation event from button press. Intercept this to detect DISK MENU selection.** |
| `0x01C0000F` | `EVT_INIT_HOOK` | Menu initialized | Custom initialization hook (HDAE5000 intercepts this specifically) |
| `0x01C00039` | `EVT_BUTTON_FOCUS` | Entry selected | Button focus/navigation event during selection |

### Activation Events

| Code | Name | Source | Description |
|------|------|--------|-------------|
| **`0x01C00008`** | **`EVT_ACTIVATE`** | Button press | Sent by firmware when user selects a DISK MENU entry via LCD panel button. **This is the event to intercept for button-press activation.** |
| **`0x01E0009C`** | **`EVT_POST_ACTIVATE`** | PostEvent injection | Sent by `LABEL_F8B1DF` via `PostEvent(0x00600002, 0x01E0009C, 0)`. Used for programmatic activation. Falls through ClassProc → ObjectProc → InheritedProc chain. |

### Display/Memory Allocation Events

Used by `Alloc_Memory` functions to query display parameters:

| Code | Name | Return Value | Description |
|------|------|-------------|-------------|
| `0x01E000A1` | `EVT_ALLOC_DATA_PTR` | ROM pointer | Returns palette/graphics data pointer |
| `0x01E000A2` | `EVT_ALLOC_WIDTH` | 0x140 (320) | Returns display width |
| `0x01E000A3` | `EVT_ALLOC_HEIGHT` | 0xF0 (240) | Returns display height |

### Grid/Check Widget Events (0x01E4xxxx)

Used by the UI widget system for checkbox and grid controls:

| Code | Name | Description |
|------|------|-------------|
| `0x01E40008` | `EVT_GRIDCHECK_RESP_A` | Grid/Check widget response variant A |
| `0x01E40009` | `EVT_GRIDCHECK_RESP_A2` | Grid/Check widget response variant A2 |
| `0x01E4000A` | `EVT_GRIDCHECK_RESP_B` | Grid/Check widget response variant B |
| `0x01E4000B` | `EVT_GRIDCHECK_RESP_B2` | Grid/Check widget response variant B2 |

### Initialization/Callback Events

Used in `Boot_Init` and `Frame_Handler` for display initialization:

| Code | Name | Context | Description |
|------|------|---------|-------------|
| `0x01C00016` | `EVT_HD_INIT_PARAMS` | Boot_Init | Hard disk initialization parameters |
| `0x01CA0000` | `EVT_DISPLAY_CALLBACK` | Frame_Handler | Display callback identifier |
| `0x01CA0004` | `EVT_DISPLAY_UPDATE` | Frame_Handler | Display state update callback |

### Object State Query Events

| Code | Name | Description |
|------|------|-------------|
| `0x01E0008F` | `EVT_OBJECT_STATE_QUERY` | Queries object state, used by GridCheck widget system |
| `0x01C0000D` | `EVT_POST_INIT` | Posted by HDAE5000 after `0x01C0000F` custom init |
| `0x01C00013` | `EVT_CPANEL_EVENT` | Control panel event code (referenced in control-panel-protocol.md) |

## Event Queue (PostEvent)

`PostEvent` (0xFAD61F) enqueues events for asynchronous dispatch:

```
Queue base:   0x02BC34
Entry size:   12 bytes
Max entries:  1,024 (indices 0x0000-0x03FF)
Write index:  0x02EC36 (16-bit)
Counter:      0x02F840

Entry layout:
  +0x00  4 bytes  Target object ID (e.g., 0x016A0005)
  +0x04  4 bytes  Event code (e.g., 0x01E0009C)
  +0x08  4 bytes  Parameter
```

Events are dequeued by the main event loop and dispatched via `SendEvent`.

## DISK MENU Activation Flow

The complete sequence when a user selects a DISK MENU entry by pressing a panel button:

```
1. User presses RIGHT 5 button on LCD panel
2. Control panel HLE sends scan code via SC1 serial
3. Firmware interprets button as DISK MENU selection
4. SendEvent dispatches events to registered handler:

   Step 1: EVT_ACTIVATE (0x01C00008)
       → ClassProc → ObjectProc → InheritedProc → Record function
       → Mines_Handler intercepts: sets GAME_ACTIVE=1, skips delegation

   Step 2: EVT_BUTTON_FOCUS (0x01C00039)
       → Delegated to default handler (Mines_Handler doesn't intercept)

   Step 3: EVT_SELECT_CONFIRM (0x01C00002)
       → Delegated to default handler

   Step 4: EVT_REDRAW (0x01E00014)
       → Handled by ObjectProc lifecycle, then delegated

5. Next Frame_Handler call detects GAME_ACTIVE=1
6. C runtime initialized, main() called
7. Game renders minesweeper board to VRAM
```

For comparison, programmatic activation via `PostEvent`:

```
1. LABEL_F8B1DF calls PostEvent(0x00600002, 0x01E0009C, 0)
2. Main loop dequeues event
3. SendEvent(slot[+0x00], 0x01E0009C, 0)
4. ClassProc: not a getter → ObjectProc
5. ObjectProc: not in 0x10-0x23 range → InheritedProc
6. InheritedProc: follows handler chain
7. Record function (Mines_Handler) intercepts: sets GAME_ACTIVE=1
```

## Implementing Event Handlers

For homebrew extension ROMs that register handlers via `RegisterObjectTable`:

```c
// Pseudo-code for a handler record function
void My_Handler(uint32_t object_id, uint32_t event_code, uint32_t param) {
    switch (event_code) {
    case 0x01C00008:  // Button-press activation (DISK MENU selection)
        GAME_ACTIVE = 1;
        return;       // Skip delegation to prevent default handler UI

    case 0x01E0009C:  // Programmatic activation (PostEvent injection)
        GAME_ACTIVE = 1;
        return;       // Skip delegation

    default:
        // Delegate everything else to default handler
        call_default_handler(object_id, event_code, param);
        break;
    }
}
```

Assembly implementation (TLCS-900, from the Mines project):

```asm
Mines_Handler:
    push  xix
    push  xiz

    ; Check for DISK MENU selection event
    ld    xix, 0x01C00008
    cp    xbc, xix
    jr    z, .activate

    ; Check for PostEvent activation
    ld    xix, 0x01E0009C
    cp    xbc, xix
    jr    z, .activate

    ; Delegate to default handler
    ld    xiz, (WORKSPACE_PTR)
    add   xiz, 0x0E0A
    ld    xiz, (xiz)
    add   xiz, 0x00DC
    ld    xix, (xiz)
    call  (xix)
    jr    .done

.activate:
    ; Set game active flag
    ld    xhl, GAME_ACTIVE
    ld    xwa, 0x00000001
    ld    (xhl), xwa
    ; Fall through to .done (skip default handler)

.done:
    pop   xiz
    pop   xix
    ret
```

## Documentation Freshness Policy

This event codes reference and the following related documentation must be updated whenever new event codes are discovered or existing codes are better understood:

1. **This page** (`event-codes.md`) -- Add new codes, update descriptions, correct dispatch paths
2. **[HDAE5000 Homebrew Development]({{ site.baseurl }}/hdae5000-homebrew/)** -- Update handler examples and activation flow
3. **ROM disassembly** (`~/devel/kn5000-roms-disasm/`) -- Update symbolic names (`EVT_*` constants) in assembly source
4. **Symbol reference files** -- Keep `hdae5000_symbols_reference.txt` and `maincpu_symbols_reference.txt` in sync with assembly

See also: [HDAE5000 Homebrew Development]({{ site.baseurl }}/hdae5000-homebrew/) for the full handler registration and dispatch system documentation.
