---
layout: page
title: UI Widget Types (NAKA System)
permalink: /ui-widget-types/
---

# UI Widget Types (NAKA System)

The KN5000 firmware uses a widget object system (internally referred to as "NAKA") for structured UI elements. The **NAKA_UIObjectTable** at ROM address `0xE1344E` contains 478 `.long` pointers to widget structures, registered by `InitializeNaka` with handler `ViewableProc` at `0xFA5995`. Beyond this table, there are approximately **1,410 total widget structures** across the entire Program ROM using 9 distinct type bytes.

## Widget Structure Header

All widget structures share a 4-byte header encoded as a 32-bit little-endian value:

```
Byte 0: type_byte   (widget type identifier)
Byte 1: 0x00        (always zero)
Byte 2: 0x60        (fixed)
Byte 3: 0x01        (fixed)
```

The 32-bit LE value is `0x01600000 | type_byte`. This header is immediately followed by type-specific fields.

## Type Byte Inventory

| Type Byte | Count | Tentative Name | Key Characteristics |
|-----------|-------|----------------|---------------------|
| `0x16` | 3 | Diagnostic List | FD SAVE/LOAD TEST only, counter display with label string |
| `0x1e` | 31 | Panel/Dialog | 4 sub-widget indices, full-screen bounding box |
| `0x2b` | 765 | Label/Button | String pointer (e.g. "200 Preset"), bounding box |
| `0x2e` | 148 | Value Display | Fixed 26 bytes, bounding box, no string pointer |
| `0x2f` | 18 | Option/Choice | Similar to 0x2e but with different flags |
| `0x30` | 16 | Slider/Range | Range parameters (min/max), data pointer |
| `0x31` | 120 | Composite/Group | Links to child indices, bounding box, 22-26 bytes |
| `0x34` | 196 | Container/Frame | Defines screen bounds, string pointer, 42-44 bytes |
| `0x66` | 110 | List/Selector | Dual coordinate sets, count fields, 38-42 bytes |
| `0x6c` | 6 | Bitmap/Image | FTDEMO_SCREEN only, references FTBMPXX strings |

**Note:** Type names are tentative, based on field analysis rather than complete dispatch tracing.

## Common Structure Layout

Widget structures share a common prefix after the 4-byte header:

```
Offset  Size   Field
------  ----   -----
 0      1      type_byte         ; Widget type (see table above)
 1      1      0x00              ; Always zero
 2      1      0x60              ; Fixed
 3      1      0x01              ; Fixed
 4      2      index1 (16-bit LE); Primary parent/group index (0xFFFF = none)
 6      2      index2 (16-bit LE); Related index (meaning varies by type)
 8      2      index3 (16-bit LE); Related index
10      2      index4 (16-bit LE); Related index (0xFFFF = none)
12      1      flags_byte        ; 0x08 (most types) or 0x0A (type 0x34)
13      1      0x00              ; Padding
14+     ...    type-specific fields (coordinates, dimensions, pointers)
```

The index fields at offsets 4-11 are 16-bit little-endian indices into the NAKA_UIObjectTable. The sentinel value `0xFFFF` means "no reference."

## Dispatch Mechanism

Widget dispatch uses a two-level architecture:

### Level 1: ViewableProc (Event Dispatch)

`ViewableProc` at `0xFA5995` is the primary event handler registered via the `RegObjTabl` macro in `InitializeNaka`. It dispatches on 32-bit event IDs (not on the 8-bit widget type byte):

| Event ID | Handler |
|----------|---------|
| `0x1E00052` | LABEL_FA5D5D |
| `0x1E0004F` | LABEL_FA5CFF |
| `0x1E000B5` | LABEL_FA5CAA |
| `0x1E00024` | LABEL_FA5C58 |
| `0x1E0009C` | LABEL_FA5C4D |
| `0x1E00039` | LABEL_FA5C45 |
| `0x1E00038` | LABEL_FA5C3D |
| `0x1E00037` | LABEL_FA5C35 |
| `0x1E00036` | LABEL_FA5C2D |
| `0x1E0000F` | LABEL_FA5C25 |

These event IDs correspond to widget lifecycle events (creation, property changes, visibility, rendering) rather than widget type identifiers.

### Level 2: Type Byte Classifier (LABEL_F06898)

`LABEL_F06898` classifies the 8-bit type byte into rendering priority groups using a cascading comparison:

| Type Byte Range | Group | Priority |
|-----------------|-------|----------|
| `0x41`-`0x44` | 4 | Highest |
| `0x31`-`0x34` | 3 | High |
| `0x21`-`0x24` | 2 | Medium |
| `0x11`-`0x14` | 1 | Low |
| Lower values | Bit-based | Varies |

Types `0x31` and `0x34` fall directly into group 3. Types `0x2b`, `0x2e`, `0x66`, and `0x6c` fall into the bit-based classification path (lower nibble checks).

## InitializeNaka Registration

`InitializeNaka` (ROM `0xF221AC`) registers 11 object tables:

```asm
InitializeNaka:
    RegObjTable 0x1600004, 0xFA44E2, 0xE0E962, 0xE0E944, 0x16b
    RegObjTable 0x160000c, 0xFA58FB, 0xE0E962, 0xE0E95E, 0x1cb
    RegObjTable 0x160000d, 0xFA5948, 0xE0E968, 0xE0E964, 0x1eb
    RegObjTabl  0x1600002, 0xFA496C, 0x12, 0xE0E7AE, 0x12b
    RegObjTabl  0x1600002, 0xFA496C, 0x12, 0xE0E7FA, 0x42b
    RegObjTabl  0x1600001, 0xFA48A9, 0x0, 0xE0E96A, 0x10b
    RegObjTabl  0x1600001, 0xFA48A9, 0x0, 0xE0E96E, 0x40b
    RegObjTabl  0x1600003, 0xFA4A18, 0x0, 0xE14824, 0x14b
    RegObjTabl  0x1600003, 0xFA4A18, 0x0, 0xE14828, 0x44b
    RegObjTabl  0x1600010, 0xFA5995, 0x1de, NAKA_UIObjectTable, 0xfd  ; 478 entries
    RegObjTabl  0x160000f, 0xFA62CB, 0x1de, 0xE13BCA, 0x3fd
    ...
```

The `ViewableProc` handler (`0xFA5995`) is associated with type ID `0x1600010` and a count of `0x1DE` (478 decimal) entries in NAKA_UIObjectTable.

## Source Location

| Item | Location |
|------|----------|
| NAKA_UIObjectTable | `maincpu/kn5000_v10_program.s`, label at `0xE1344E` |
| InitializeNaka | `maincpu/kn5000_v10_program.s`, label at `0xF221AC` |
| ViewableProc | `maincpu/kn5000_v10_program.s`, label at `0xFA5995` |
| Type classifier | `maincpu/kn5000_v10_program.s`, `LABEL_F06898` |
| Type constants | `maincpu/shared/macros.s` |

## Assembly Macros

The disassembly uses EQU constants for type bytes and a `naka_header` macro for the common 4-byte header:

```asm
; Usage in the disassembly source:
    naka_header NAKA_TYPE_LABEL        ; emits: .byte 0x2b, 0x00, 0x60, 0x01
    .byte 0x1a, 0x00, 0xff, 0xff, ...  ; type-specific body fields
```

The body bytes remain as raw `.byte` directives because structure sizes vary even within the same type (e.g., type `0x34` ranges 42-44 bytes). Full body parameterization requires deeper reverse-engineering of field consumption.

---

## Related Pages

- [UI Framework]({{ site.baseurl }}/ui-framework/) -- Widget system and event handling
- [Feature Demo & Presentation System]({{ site.baseurl }}/feature-demo/) -- SSF presentation that uses NAKA widgets

---

*Last updated: March 2026*
