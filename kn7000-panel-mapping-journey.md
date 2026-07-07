---
layout: page
title: "Mapping the KN7000 Front Panel — with the keyboard's own help system"
permalink: /kn7000-panel-mapping/
---

# Mapping the KN7000 Front Panel

*July 2026*

The Technics SX-KN7000 has a *lot* of front-panel buttons — well over a hundred, spread across
rhythm styles, sound groups, performance pads, effects, transport controls, part mixers, and a
cluster of system keys around the LCD. For the [work-in-progress MAME driver](/kn7000-roadmap/)
to feel like a real KN7000, every one of those buttons has to send the right signal to the
emulated firmware. This post is the story of how we got most of the way there — including a few
wrong turns that are worth telling.

## The problem: 250 bits, no labels

The panel is a scanned switch matrix. From the driver's point of view it's ~30 "segments" of 8
bits each — roughly 250 individual switch positions — and *nothing* says which position is which
button. Early on we guessed the wiring from the firmware's descriptor tables, but guesses have a
way of being confidently wrong. The genre buttons, for instance, were mapped one way in the
layout and turned out to be somewhere else entirely.

What changed everything was a feedback loop with the instrument's owner. They ran the published
emulator build and sent back precise reports: *"pressing the button labelled CUSTOM opens the
ENTERTAINER screen"*, *"MUTE 1 actually triggers MUTE 7"*, and so on. Each of those is a hard
data point. Combined with snapshot probing in the emulator — press a bit, capture the LCD, read
what screen it opened — we rebuilt the RHYTHM GROUP genre map from scratch and got it verified:
the 16 genres live on segments SEG00/SEG01/SEG02, bits b2–b7, in order.

## The breakthrough: the keyboard names its own buttons

Snapshot probing works for buttons that open a distinctive screen, but many buttons don't — they
toggle a mode, nudge a value, or mute a part. Progress was slow until the owner passed along a
tip that turned out to be the key to the whole panel:

> **Press the HELP button, then press any other button, and the screen tells you what that button
> does** — a little info page titled *"HELP : &lt;BUTTON NAME&gt;"*.

That's a built-in, per-button oracle. Pressing a candidate bit in HELP mode makes the KN7000
*itself* tell us the button's name. We automated it: enter HELP mode once, press each bit in a
segment, and grab just the LCD's title strip. Because a no-op leaves the previous title on screen,
we de-duplicate consecutive identical strips and stack the distinct ones into a single tall image
— so one emulator run and one screenshot reveal a whole segment's worth of button names at once.

One sweep of segments SEG0F–SEG13 handed us **twenty buttons** in a single shot: SOUND DSP, SPLIT
POINT, VARIATION & MSA, PART SELECT, SOLO, FADE IN/OUT, FILL IN, CONDUCTOR, TECHNI-CHORD, INTRO &
ENDING, TAP TEMPO, START/STOP, PROGRAM MENU, DISK, TRANSPOSE, R1/R2 OCTAVE, REVERB, MIC REVERB &
EFFECT… The map even **validated itself**: DISK and PROGRAM MENUS were already bound and confirmed
working by the owner, and the sweep landed on exactly those bits.

## The EXIT saga (a cautionary tale)

Not every hunt went smoothly. We spent an embarrassing amount of effort chasing the EXIT button.
A first "confident" identification bound EXIT to a bit that, in a modal HELP screen, *seemed* to
close it. It didn't — that bit is actually a **tempo control**, and our screen-change detector had
been fooled by the tempo digit ticking from ♩=120 to ♩=121 in the title bar. Lesson filed: verify
a screen *close* by its body, not by a hash that includes a live-updating number, and always read
the actual screen before believing an automated verdict.

The HELP sweeps also fought us here: HELP is a toggle (pressing it again turns help *off*), and a
few buttons navigate away instead of showing info, so a single-boot sweep silently contaminates
after the first such press. The reliable method turned out to be a **clean fresh-boot test per
candidate**: boot, enter HELP, press exactly one bit, screenshot, check for the home screen. EXIT
is the bit that turns HELP off and returns home — and it finally fell out as **SEG08 0x20**,
completing the tidy set of LCD-corner keys: OTHER PARTS (0x04), HELP (0x08), DISPLAY HOLD (0x10),
EXIT (0x20).

## Peeking at the firmware's own table

In parallel we found the firmware's master dispatch table (at `0x48614978`): for every switch it
records an event code, so genres show up as one event class, part-mutes as on/off pairs, and a
distinct `0x1xxx` class marks the system keys. It's a gorgeous artifact and a strong lead — the
catch is that the firmware's internal segment numbering doesn't line up cleanly with the layout's
segment numbering yet, so we can't blindly transcribe it. Pinning that remap is on the list; once
it's done it should name every remaining switch at once.

## Cracking the MUTE matrix by counting presses

The one place the HELP oracle goes quiet is the sixteen **MUTE UP / MUTE DOWN** buttons under the
LCD — press them in HELP mode and nothing happens; they have no info pages. They're really per-part
*volume* nudges: one press drops a part's mixer level by one. That subtlety turned out to be the
key to a neat trick. Instead of pressing one button and reading the screen, we **encode each
button's identity in the number of presses**: press the first candidate 5 times, the second 10,
the third 15, and so on. Then a single snapshot of the PT1–16 mixer shows each affected part
sitting at a distinct level — the part at 95 was the 5-press button, 90 the 10-press button, and so
on. One screenshot decodes a whole segment's worth of buttons at once.

The result was beautifully regular: **SEG04 = parts 1–4, SEG05 = parts 5–8, SEG06 = parts 9–12,
SEG07 = parts 13–16**, with each segment's four up/down pairs driving four consecutive parts.
Sixteen parts, thirty-two buttons, all mapped in a handful of runs.

It also caught a subtle bug. The "AUTO PLAY CHORD ON/OFF" button had been guessed from the
firmware's dispatch table — but that table indexes the firmware's *internal* segment numbering,
which doesn't match the layout's, and the bit we'd assigned to APC is physically a part-10 mute.
A good reminder that the static table is a lead, not gospel, until a live test confirms it.

## Where things stand

Between the owner's testing, snapshot probing, and the HELP-name sweeps, the great majority of the
KN7000 front panel is now correctly wired in the emulator — genres, sound groups, effects,
transport, performance pads, the LCD soft-keys, and the system corner keys. It's a good example of
how emulation and reverse engineering feed each other: a working (if incomplete) emulator became
the instrument that helped map the very hardware it emulates.

*The button map lives in `notes/panel-button-map.md` in the driver overlay repo; the running
tally is on the [KN7000 roadmap](/kn7000-roadmap/).*
