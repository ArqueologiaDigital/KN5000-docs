---
layout: page
title: KN7000 Control Panel Protocol
permalink: /kn7000-control-panel/
---

# KN7000 Control Panel Protocol

The KN7000's front panel — its dozens of buttons, the data dial, and the LEDs
that light under them — is not wired directly to the main CPU. Instead it is
**scanned by a set of dedicated panel sub-CPUs**, which report switch presses to
the MN10300 main CPU and drive the LEDs on its behalf. This distributes the
tedious matrix scanning off the main CPU and matches the KN5000's arrangement
(with a different number of sub-CPUs). This page documents the panel from the
firmware (`kn7000_program_even.rom` / `kn7000_program_odd.rom`) — the sub-CPUs, how input becomes events, and the
LED/dial control — grounded in the service-test screens and the named handlers.
In MAME the sub-CPU side is modelled by a dedicated high-level-emulation device,
**`kn7000_cpanel_device`**, which owns the panel's buttons and LEDs and speaks the
serial link to the main CPU (mirroring the KN5000's `kn5000_cpanel` device).

## The panel sub-CPUs

The service manual's schematics show **three panel PCBs, each with its own 8-bit
microcomputer**, and the service-test "PANEL CPU CHECKING" / "PANEL SW&LED CHECK"
screens enumerate **four logical groups**:

| Sub-CPU | PCB | Micro | Role |
|---------|-----|-------|------|
| **CPL** | CPL (page 128) | IC1101 = `C2BBDB000023` | left: LCD soft-keys, style/rhythm groups, fills, performance pads |
| **CPC** | CPC (page 130) | (8-bit micro) | centre: the part mixer — 16 `MUTE UP/DOWN`, contrast, page/exit |
| **CPR** | CPR (page 132) | IC1001 = `C2BBDB000023` | right (**master**): sound groups & families, part select, transpose, LCD soft-keys, memory/disk. The main-CPU serial link attaches here and chains to CPL. |
| **CPSD** | SD front panel | MN102H60 | the SD-card front-panel board. It is **not** on the panel scan link: it has its own MN102H60 and speaks to the main CPU over SIO **channel 2**, framed as MIDI. |

The **data dial** is a rotary encoder (`SW1101` on the ROT board). It is not a
scan-matrix switch: the panel reports it as a continuous-controller frame on wire
`0x10` (see *Continuous controls* below).

### Button inventory (from the schematics)

All 152 front-panel buttons are now declared **by the control-panel device itself**
(`kn7000_cpanel_device::device_input_ports()`), not by the driver — the panel
sub-CPUs own their inputs, so their scan-matrix ports live with the HLE that
emulates them. They are grouped into **22 scan-matrix ports named
`CP{board}_SEG{col}`** (CPL: 7 columns, CPC: 5, CPR: 10), which the internal MAME
layout references by the device-relative tag `cpanel:CP{board}_SEG{col}`. The
**SD front-panel board (CPSD)** switches are *not* on this serial link — they are a
separate GPIO byte (`0x9CC00008`, `CPSD_SDSW`) read directly by the driver — and the
**shared analog controls** (the DATA dial, the four volume faders, and the
Tempo/Program knob) likewise stay in the driver's `INPUT_PORTS` and are handed to the
device by tag, which digitises them into the same link's continuous-controller
frames. By board:

* **CPL** — `LCD Left 1–5`, `START/STOP`, `SYNCHRO & BREAK`, `INTRO & ENDING 1/2`,
  `FILL IN 1/2`, `FADE IN/OUT`, `TAP TEMPO`, `SPLIT POINT`; the style/rhythm groups
  (`8 & 16 BEAT`, `SOUL & FUNK`, `BALLAD`, `JAZZ COMBO`, `ROCK & POP`, `MARCH`,
  `ENTERTAINER`, `COUNTRY`, `LATIN & WORLD`, `BALLROOM`, `MODERN DANCE`,
  `MOVIE SHOW`, `CUSTOM`); `VARIATION & MSA 1–4`,
  `MUSIC STYLE ARRANGER`, `PAD 1–6/SOLO`, `PERFORMANCE PADS BANK/STOP/AUTO`,
  `ONE TOUCH PLAY`, `SOUND SET`, `MUSIC STYLIST`, `AUTO MODE`, `DEMO`,
  `MEMORY/LOAD`, `PLAY CHORD OFF/ON`, `ARRANGER OFF/ON`.
* **CPC** — `OTHER PARTS/TG`, `HELP`, `CONTRAST UP/DOWN`, `MUTE UP/DOWN 1–16`
  (the part mixer), `PAGE UP/DOWN`, `DISPLAY HOLD`, `EXIT`.
* **CPR** — `SOUND GROUP 1–8`; the sound families (`PIANO`, `GUITAR`, `BRASS`,
  `STRINGS & VOCAL`, `BASS`, `SYNTH`, `ORGAN & ACCORDION`, `DRUM KITS`, `WORLD`,
  `PAD`, `MALLET & ORCH PERC`, `TAB ORGAN`, `DIGITAL DRAWBAR`, `SAX & WOODWIND`,
  `ACCORDION REGISTER`); `PART SELECT LEFT/RIGHT 1–2`, `CONDUCTOR LEFT/RIGHT 1–2`,
  `TRANSPOSE R1/R2 ±`, `LCD Right 1–5`, `MEMORY`, `FAVORITES`, `VARIATION`,
  `REVERB`, `CHORUS`, `SUSTAIN`, `DIGITAL EFFECT`, `SOUND DSP`, `EFFECT MIC`,
  `MULTI`, `TECHNI-CHORD`, `SOLO`, `SOUND SET/EXPLORER`, `EW EXPANSION`, disk/SD
  (`DISK EASY REC`, `DISK MENU LOAD`, `DISK PLAY`, `SD CARD LOAD`, `CUSTOMIZE`,
  `CUSTOM PANEL`, `PROGRAM MENUS`, `NEXT BANK`, `BANK VIEW`).

The exact **SEG-column × SW-row** position of every switch is transcribed from
the service-manual schematics (CPL = DIAGRAM-15 p128, own sub-CPU IC1101; CPC =
DIAGRAM-16 p130, the mixer, wired to a scanner via CN1107/1108; CPR = DIAGRAM-17
p132, sub-CPU IC1001). For example CPR's sound families sit on rows SW2–SW5:
`GUITAR` at SEG3·SW4, `PIANO` at SEG4·SW4, `BRASS` at SEG1·SW4, `SYNTH` at
SEG1·SW5, `ORGAN & ACCORDION` at SEG8·SW3. The full three-board matrix lives in
the driver's `notes/panel-matrix-service-manual.md`.

### Scan-matrix port naming (`CP{board}_SEG{col}`)

Each `CP{board}_SEG{col}` port is one scan **column** (segment) that a panel sub-CPU
strobes, and each of its bits is one **SW sense line** the sub-CPU reads on that column.
Port → `normSeg` is a pure identity with the bit unchanged, because each scan column maps
to exactly **one wire `ADDR`** (there is no per-bit repacking). Which button sits on which
column and bit comes from **each button's firmware event code and argument**
(`notes/panel-button-map.md`), not from the schematic transcription: where the two
disagree — `BRASS`, `WORLD`, `SYNTH` and `ORGAN & ACCORDION` sit on different columns in
the two sources — the driver follows the firmware, because that is what actually makes the
instrument perform the function. Before it speaks, the device reverse-normalizes each
column to its wire address: CPL/CPC's columns (`normSeg 0x00`–`0x0B`) go out as wire
`0xC0`–`0xCB`, CPR's columns (`normSeg 0x0C`–`0x15`) as wire `0x00`–`0x09`. On each scan
the device reads these ports, and for any column whose bits changed it emits the 2-byte
`[ADDR][DATA]` switch frame the real sub-CPU would send; the main CPU XORs `DATA`
against its per-segment shadow to recover the pressed/released edges.

#### The bindings that matter most

**LCD soft-keys.** All ten are bound and working. The left column is one port; the
right column is spread over three.

| Key | Port | Mask | Key | Port | Mask |
|---|---|---|---|---|---|
| LCDL 1 | `CPL_SEG0` | `0x02` | LCDR 1 | `CPR_SEG5` | `0x10` |
| LCDL 2 | `CPL_SEG0` | `0x08` | LCDR 2 | `CPR_SEG5` | `0x20` |
| LCDL 3 | `CPL_SEG0` | `0x20` | LCDR 3 | `CPR_SEG7` | `0x01` |
| LCDL 4 | `CPL_SEG0` | `0x01` | LCDR 4 | `CPR_SEG6` | `0x01` |
| LCDL 5 | `CPL_SEG0` | `0x04` | LCDR 5 | `CPR_SEG5` | `0x01` |

**The 16 sound families**, all on CPR:

| Family | Port · mask | Family | Port · mask |
|---|---|---|---|
| `STRINGS & VOCAL` | `CPR_SEG0` `0x10` | `PIANO` | `CPR_SEG4` `0x10` |
| `SYNTH` | `CPR_SEG0` `0x20` | `DIGITAL DRAWBAR` | `CPR_SEG4` `0x20` |
| `WORLD` | `CPR_SEG1` `0x10` | `SOUND EXPLORER` | `CPR_SEG6` `0x08` |
| `PAD` | `CPR_SEG1` `0x20` | `ORGAN & ACCORDION` | `CPR_SEG7` `0x08` |
| `MALLET & ORCH PERC` | `CPR_SEG2` `0x10` | `DRUM KITS` | `CPR_SEG8` `0x04` |
| `ACCORDION REGISTER` | `CPR_SEG2` `0x20` | `SAX & WOODWIND` | `CPR_SEG8` `0x08` |
| `GUITAR` | `CPR_SEG3` `0x10` | `BASS` | `CPR_SEG9` `0x04` |
| `TAB ORGAN` | `CPR_SEG3` `0x20` | `BRASS` | `CPR_SEG9` `0x08` |

**Rhythm genres.** Thirteen are bound, on two CPL columns: `CPL_SEG1` bits 2–7
(`CUSTOM`, `ENTERTAINER`, `LATIN & WORLD`, `MOVIE SHOW`, `MARCH`, `BALLROOM`) and
`CPL_SEG2` bits 0–5 and 7 (`COUNTRY`, `JAZZ COMBO`, `SOUL & FUNK`, `BALLAD`,
`MODERN DANCE`, `ROCK & POP`, `8 & 16 BEAT`). Two positions in that block —
`CPL_SEG1` `0x02` and `CPL_SEG2` `0x40` — are still `IPT_UNUSED`.

**The 16-part mute matrix**, all on CPC, two bits (ON/OFF) per part:

| Port | Parts | Port | Parts |
|---|---|---|---|
| `CPC_SEG5` (bits 4–7) | 1–2 | `CPC_SEG10` | 11–14 |
| `CPC_SEG8` | 3–6 | `CPC_SEG11` (bits 0–3) | 15–16 |
| `CPC_SEG9` | 7–10 | | |

Each scans its own switch matrix and drives its own LEDs; the test mode lights
them group by group (`CPL LEDS to light`, `CPC LEDs to light`, `CPR LEDs to
light`, `CPSD`) and asks the operator to *"Push each button and check the LED"*.
The go/no-go results are surfaced by `PanelCPL_OKNG` / `PanelCPR_OKNG` (and
siblings) and the panel firmware itself can be reflashed (`PanelFlashFunc`),
which is why the test reports "CPU of CPL =" / "CPU of CPR =" as live devices
rather than fixed logic.

## Switch input → events

When a sub-CPU reports a switch change, the main CPU turns it into a MILK
[event]({{ site.baseurl }}/kn7000-event-system/) delivered to the focused object. The panel input
events form a recognisable family:

* **general switches** — `EV_SWON`, `EV_SWOFF`, `EV_SWBOTH`, `EV_ASSSWB`
* **index switches** (the up/down/page navigation keys) — `EV_INDEXSW_UP`,
  `EV_INDEXSW_DOWN`, `EV_INDEXSW_ON`, `EV_INDEXSW_OFF`, `EV_INDEXSW_BOTH`,
  `EV_INDEXSELECT`, plus the AIC and dial-combined variants
  (`EV_INDEXSW_UP_AIC`, `EV_INDEXSW_DOWN_DIAL`, …)
* **the data dial** — `EV_DIAL`, `EV_DIALUP`, `EV_DIALDOWN`,
  `EV_CHANGEDIALFOCUS`

So a button press is a hardware scan on a sub-CPU → a report to the main CPU →
an `EV_SW*` event → the current widget's `…Proc` handler (which typically
switches on `EV_ACTION` / `EV_SWON`).

## The music key bed

The 61-note key bed is scanned by the tone-generator hardware and read by the CPU
as a **voice-event FIFO** -- the same interface the KN5000 firmware calls
"keyboard input" (KN5000 0x110000; KN7000 the read at **0x98050004**). Each event
is a 16-bit word: **low byte = note, high byte = velocity** (velocity 0 = note
off); the port yields **0xFFFF when empty**. The firmware polls it and turns each
event into an internal note (in parallel with the MIDI-in path). The MAME driver
models this FIFO. All **61 keys (C2..C7)** are declared, each carrying
`PORT_GM_NOTE` musical-note markup, so a USB-MIDI controller routed through MAME's
midi input provider plays the whole bed; the middle two octaves (C4..C6) additionally
keep PC tracker-style key bindings. Audible output still awaits the (undumped)
waveform ROMs, but the note reaches the firmware.

## The data dial

The rotary data dial is a first-class input: it emits `EV_DIALUP` / `EV_DIALDOWN`
ticks and `EV_DIAL` value changes, and the currently-focused control claims it
via `EV_CHANGEDIALFOCUS`. The firmware programs the dial's behaviour for the
active field through `SetProgDial` (`0x48417609`) and `SetDialFocus` /
`SetDialEnable` / `SetDialUp`, with the low-level step logic in `DialUpDownOp`
(`0x4847AC2F`). This is how one physical encoder edits whatever parameter the
cursor is on.

## LEDs

The panel LEDs are set through small helpers that the main CPU calls and the
sub-CPUs execute: `SetHoldLed` (`0x48416512`), `SetOtherPartLed` (`0x484164F4`),
and the part/track indicator sets. Because the LEDs sit under the buttons and are
driven by the same sub-CPU that scans them, the "SW&LED CHECK" test can verify a
whole section's matrix in one pass.

In MAME these become the device's LED outputs, one bank per panel board. The layout
lights **44 `cpl_led#` and 57 `cpr_led#`** under the buttons; the device also declares a
`cpc_led#` bank, which the layout does not yet reference. A LED command
rides the **same serial channel** as the button reports: the firmware sends a
`[ADDR][DATA]` frame whose `ADDR` selects a board and an 8-bit LED register and whose
`DATA` bits are the individual lamps, and the device decodes it onto those outputs. The
map is **authoritative from a real-machine lamp test** — driving the firmware's
`F3`+`F4` service LED sweep on Felipe's own KN7000 confirmed **79 press-lit LEDs** (the
lamp under each button). Together with the mode/indicator lamps (state LEDs such as the
CUSTOMIZE-menu, DISK-in-use, split-point and conductor indicators), the device binds
**101 named LED outputs**. Of the 171 decoded LED bits, **68 are marked
`(unmapped)`** — driven by the firmware but not yet tied to a named panel function. The
decoder still passes those through, so the layout can name them once identified.

## Hardware path & serial protocol

The service-manual schematics (SX-KN7000, *SCHEMATIC DIAGRAM-15* "CPL CIRCUIT")
pin this down. **Each panel PCB carries its own 8-bit microcomputer** — on the
CPL board it is **IC1101 = C0BDB646823** (with crystal X1101) — and that sub-CPU
does the local work:

* it **scans an 8×8 switch matrix** — eight strobe lines `SW0…SW7` against eight
  sense columns `SEG0…SEG7`, each cell a diode + a momentary switch (`EVQ2140SR`),
  so up to 64 buttons per board;
* it **drives an LED matrix** through a **74LS138 (IC1102) 3-to-8 decoder** plus
  transistor rows and buffers (IC1103), the LEDs sitting under the buttons;
* it talks to the main CPU over a **synchronous serial link** — the pins
  **`SIN`, `SOUT`, `CLK`, `RST`, `CNTR1`** (data in, data out, shared clock,
  reset, and a control/attention line). CPL chains to the CPR board and on to the
  main board.

On the **main-CPU side** the link is **one channel of a multi-channel USART/SIO
ASIC** in the `0x34000000` bank at base **`0x34000800`** — traced register by
register from the firmware:

| Register | Role |
|----------|------|
| `0x34000800` | channel config/direction (low 3 bits: `\|0x07` = RX+clear, `\|0x04` = TX) |
| `0x34000804` | channel control (set at init `0x484ABCBA`) |
| `0x34000808` | **TX data** — LED/command bytes *out* to the sub-CPUs |
| `0x34000809` | **RX data** — switch/panel bytes *in* |
| `0x3400080C` | channel status |
| `0x34000168` | interrupt-control register (ICR) for the channel |

The link is **interrupt-driven and half-duplex** (the same channel carries LEDs
out and switches in):

1. an **RX interrupt** enters ISR `0x484ACC13`, which does the GPIO handshake,
   re-arms the config, acks the ICR, and reads **one byte** from `0x34000809`;
2. the byte is pushed into a **92-byte ring buffer** at `0x5006BDB4` (head
   `0x5006BDB2`, tail `0x5006BDB0`, data-ready = bit 0 of `0x5006BDA4`);
3. a **frame-decoder task** (`0x484AD111`) drains the ring, reads a **header**
   byte and extracts a **3-bit message type** (`(hdr & 0x38) >> 3`), then pulls
   the following switch/parameter bytes;
4. the **3-bit message type** (step 3) selects the path. **Momentary switches**
   (types 0 and 1) are edge-detected against a per-segment shadow byte —
   `CHANGED = DATA XOR shadow` — and each changed bit becomes an
   `EV_SW*`/`EV_INDEXSW_*` event via `SendEvent` (`0x48429388`).
   **Latched/continuous controls** (type 2 — the volume faders, data dial and
   pedal) are instead dispatched through `0x484AD680`, which forms an index
   `((b & 0xC0) >> 3) | (b & 0x07)` into a **32-entry jump table at `0x48613108`**
   and latches the new value (see *Continuous controls* below). Momentary keys do
   **not** go through `0x484AD680`; they take the shadow-XOR path above.

LED output rides the **same channel**: `SetHoldLed`/`SetOtherPartLed` →
`SetLedByIndex` (`0x484B1BCB`, a jump table at `0x4861518C`) accumulate bits into
a RAM shadow, and the **TX path `0x484ABF50`** flushes a byte to `0x34000808`
after switching direction. The `0x36008004`/`0x36008024`/`0x36008064` GPIO lines
strobe/select which sub-CPU is on the shared bus.

This is the **same serial-panel design the KN5000 uses**, and MAME now models the
KN7000's sub-CPU side the same way — with its own **`kn7000_cpanel_device`** HLE. The
main CPU reaches it over **channel 0** of this on-chip USART/SIO controller, run in
**synchronous** mode; the driver forwards each channel-0 TX byte to the device
(`tx_byte`) and the device pushes replies back through two callbacks — an **ATN** pulse
(main asserts interrupt group `0x1A`) and an **RXD** byte (pushed onto the channel-0
receive FIFO, asserting group `0x10`). The **two sibling channels** at `0x34000810` and
`0x34000820` are the *same* controller at a `+0x10` stride but configured for
**asynchronous UART** framing: channel 1 is MIDI port 1 and channel 2 is the **SD
sub-CPU (CPSD) link** (which itself frames its traffic as MIDI). That identical `+0x10`
channel layout is what pins `0x34000800` down as the panel link.

### Continuous controls: the volume faders

The four analog volume faders (MAIN, APC/SEQ, MIC, LINE IN), plus the data dial,
the pitch/modulation controls and the expression pedal, are **not** an ADC read on
the main CPU — they are digitised by the panel sub-CPUs and delivered as **type-2
"latched control" frames** `[ADDR, DATA]` on the very same serial link. The
`0x484AD680` dispatch routes each `ADDR` to one of **six** live handlers (the other
26 table slots share a no-op); the four volume pots are wire addresses
**`0xD0`–`0xD3`**, each latching its 8-bit value to a RAM byte (`0x5006BEA1`–`A6`)
through a per-control invert/halve and a 256-entry taper table before emitting a
change event.

The MAME driver reproduces this for the **APC/SEQ** fader — identified as `0xD2` by
correlating its RAM writes against **MUTE UP 9**, which edits the *same* setting
(their write sets overlap by 44 addresses vs. 20 for the others), and consistent
with the service manual's ADC map (VR1102 = AD2). Moving the fader makes the driver
emit `[0xD2, value]`, so it drives the firmware's own accompaniment/sequencer volume
— the faithful path, not a post-mixer gain. One subtlety: a frame emitted **before**
the firmware services the panel handshake wedges the whole link (delivery re-arms its
attention signal only when the outgoing queue is empty), so the driver records the
fader's power-on position silently and only speaks when it moves.

The remaining two type-2 handlers are the panel's **rotary encoders**, both on wire
bank `00`: **`0x17` is the TEMPO/PROGRAM knob** and **`0x10` is the large DATA dial**
(the one with the central `SET` button). Neither is an absolute pot, and the two are
consumed differently:

| Wire | Control | Firmware consumption | Driver port |
|---|---|---|---|
| `0x17` | TEMPO/PROGRAM knob | **Adds** the wire byte as a signed 8-bit step every frame: `tempo += (int8_t)wire`. It does not diff an absolute position, and the response is linear — one detent is about 1 BPM. | `TEMPO_KNOB`, a `PORT_ADJUSTER(50)` that the layout knob drags in a circle |
| `0x10` | DATA dial | The panel keeps an 8-bit position counter and ships it; the main-CPU handler **diffs** successive positions. It moves the *focused* edit field and leaves the tempo alone on the home screen. | `DIAL`, an `IPT_DIAL` (0..255, wraps), forwarded verbatim |

Both are bound. The TEMPO knob's adjuster is an infinite rotary control, so a
full-circle drag wraps its 0..100 range; the device takes the direction the short way
round and emits `±1` per detent. Because the firmware adds rather than diffs, sending a
growing absolute position drives the tempo to the 300 BPM rail regardless of which way
the knob turns. Its raw adjuster setting is read from the field's live value rather than
through the analog port read, whose interpolation wobble would otherwise inject spurious
mixed-sign steps that cancel the encoder motion.

When probing the KN7000 in MAME: the musical-notes-over-a-globe image a few seconds
after launch is the **boot splash**, not the idle demo. The `PMEM` home screen appears
around 13 s in, so timed probes must wait for it.

### Boot handshake

Before the main CPU reaches its home screen it must complete a **handshake** with
the panel sub-CPUs; if it fails, the boot draws a full-screen diagnostic reading
**"ERROR in CPU data transmission."** The chain:

1. **Transmit side (interrupt group 0x11).** The main CPU sends **7-byte frames
   with line-sync bytes woven between the payload**: positions 0,1 sync, 2 =
   payload byte 1, 3 sync, 4 = payload byte 2, 5,6 sync. A state machine (states
   1–6, one byte each) advances on a *transfer-complete* interrupt after every
   byte. The init/ping commands match the KN5000 protocol: `1F DA`, `1F 1A`,
   `1D 02`, then pings `20 00` (CPL) and `E0 00` (CPR).

2. **The panel answers with a two-edge "attention" pulse (interrupt group
   0x1A).** On a completed command the panel pulses a dedicated
   external-interrupt pin twice, and the main CPU flips that pin's **trigger-mode
   register `0x34000280`** (an eight-field, 2-bits-each register; the panel-ATN
   pin is bits 7:6) between the two edges — arming the opposite edge for the
   second transition.

3. **Reply bytes (interrupt group 0x10).** After the ATN handshake the main CPU
   switches the link to RX and clocks the panel's reply bytes in, **one per
   interrupt**, into the 92-byte ring buffer described above.

4. **Success test.** The boot code declares success when the **ring's write
   pointer has moved** (a reply arrived) within a short window; otherwise it
   retries — **ten times** — and then paints the error screen.

Three emulation details are load-bearing here, besides the frame format:
interrupt-priority masking must be correct on the CPU, so a handler that re-enables
interrupts mid-body does not re-enter itself; every interrupt must be delivered
through a deferred timer, because a completion asserted synchronously from inside a
register write is wiped by the ISR-exit acknowledge; and the two-edge ATN pulse must
be driven off the `0x34000280` re-arm write.

## Relationship to the KN5000

Distributed panel scanning by dedicated sub-CPUs, the switch-to-event flow, and
the data-dial focus model are **shared with the KN5000**
([Shared Codebase Map]({{ site.baseurl }}/technics-shared-codebase/), [Control panel
protocol]({{ site.baseurl }}/control-panel-protocol/)). The KN7000-specific detail observed here is
the set of **four** sub-CPUs (CPL/CPC/CPR/CPSD) and their concrete test-mode and
handler names.

## PAGE and CONTRAST

The firmware resolves these two CPC rockers as ordinary **pseudo-part up/down**
events, which the panel scanner delivers like any other switch:

| Rocker | Pseudo-part | Event pair | Driver bits (normSeg.bit) | Notes |
|---|---|---|---|---|
| **PAGE Up / Down** | `0x18` | `0x2001` / `0x2000` | `SEG0B` 0x10 / 0x20 | page-box widget `0x4841DF23` accepts key `0x18`; `AcWindowPageProc` does page +1 / −1 |
| **CONTRAST + / −** | `0x1D` | `0x2001` / `0x2000` | `SEG05` 0x04 / 0x08 | contrast-edit filter `0x4854E693` accepts only arg-hi `0x1D`; shares the value stepper with the Tempo/Program wheel |

normSeg `0x16`–`0x1A` are **not buttons** at all: they are the absolute-analog
inputs (DATA dial, pitch-bend / modulation wheels, Tempo/Program encoder). The PAGE
rocker walks MULTI EFFECT `PAGE 6/8 → 7 → 8 → 7 → 6 → 5` and the within-group
effect-type sub-pages. The LCD contrast value is driven but not rendered.
