---
layout: page
title: "KN7000 Techni-chord: software, not silicon"
permalink: /kn7000-technichord/
---

# Techni-chord: software, not silicon

**Techni-chord** is the KN7000's auto-harmony feature: play a melody with the
right hand while a chord is specified (by the auto-play-chord section or a held
left-hand chord) and the instrument adds harmony notes underneath the melody,
voiced in one of fourteen selectable styles. The user's manual documents it on
page 48; the on-screen `TECHNI-CHORD` editor offers a style grid and an
`ORCHESTRATOR` selector that picks which part sounds the added notes.

A natural assumption about a device with two custom PCM tone-generator LSIs is
that a "harmony" feature might be a capability of that silicon — a note-multiplier
or chord mode inside the tone generator. **It is not.** Reverse engineering the
MN10300 firmware shows Techni-chord is implemented **entirely in software** on the
main CPU. The harmony engine detects the chord, computes MIDI note numbers with
plain semitone arithmetic, and emits them as **ordinary note-ons** through the
same voice path any other note travels. The tone generators never learn that the
notes are "harmony" — they receive ordinary voices.

## How it is turned on

Techni-chord is not a mode bit in the tone generator; it is three entries in the
firmware's **sound-parameter database** (the same key/value store that carries
every other panel setting):

| Parameter | Meaning |
|---|---|
| `0x8080` | Techni-chord **on / off** |
| `0x8081` | harmony **style**, `0..13` (index into the 14 styles below) |
| `0x8082` | **orchestrator** — which part produces the harmony notes |

Pressing the panel `TECHNI-CHORD` button toggles `0x8080`; the `TECHNI-CHORD`
editor's style grid writes `0x8081`; its `ORCHESTRATOR` rocker writes `0x8082`.
These are ordinary CPU-side settings — nothing is written to the sound hardware
to "arm" harmony.

## The harmony-compute path

When a melody note is played with Techni-chord on, the harmony routine at
`0x48472EBA` runs on the MN10300:

1. **Detect the chord.** It calls the chord-detect routine at `0x4844DDF2`,
   which resolves the currently specified chord (root and type) from the
   auto-play-chord / left-hand chord state.
2. **Dispatch by style.** It indexes a **14-entry jump table at `0x485BC3B4`**
   with the style number (`0x8081`), branching to that style's voicing routine —
   for example `CLOSE` at `0x48473051`, `OCTAVE` at `0x48473703`,
   `HARD ROCK` at `0x48473732`, and so on for the remaining styles.
3. **Compute the notes.** The per-style routine reads its interval set from the
   **per-style interval tables at `0x485BC390`** and computes each harmony note's
   **MIDI note number by plain semitone arithmetic** — add or subtract a number
   of semitones from the melody note (and/or from chord tones), fold into range.
   There is no pitch DSP and no reference to sample-zone pitch here; it is
   integer note-number math.
4. **Emit as ordinary note-ons.** The computed notes are sent as **normal
   note-on events on the orchestrator part** (`0x8082`), so they play through
   that part's own patch, volume, effects and the standard voice-allocation path
   — indistinguishable, to the tone generator, from a note the player pressed.

Because the harmony notes are just note-ons on a normal part, everything that
applies to a part applies to them for free: the orchestrator's sound selection,
its transpose and tuning, its reverb / chorus / DSP sends, and the
[sample-zone-relative pitch pipeline]({{ site.baseurl }}/kn7000-sound-subsystem/)
that turns a MIDI note into the tone generator's internal pitch value.

## The fourteen styles

The 14 style names live as a string table at `0x485EC960`, in the order used by
the style parameter (`0x8081`) and the jump table:

| # | Style | # | Style |
|---|---|---|---|
| 0 | CLOSE | 7 | HYMN |
| 1 | OPEN 1 | 8 | BLOCK |
| 2 | OPEN 2 | 9 | BIG BAND BRASS |
| 3 | DUET 1 | 10 | BIG BAND REEDS |
| 4 | DUET 2 | 11 | OCTAVE |
| 5 | COUNTRY | 12 | HARDROCK |
| 6 | THEATRE | 13 | FANFARE |

These are exactly the fourteen entries drawn on the `TECHNI-CHORD` editor screen
(user's manual page 48), confirming the table order matches the panel.

## Why this is dispositive — it is not hardware

Two facts settle it beyond the mere presence of a software routine:

- **The harmony engine writes zero tone-generator registers.** The whole path
  above touches no sound-hardware I/O — there is **no access to `0x98040000` /
  `0x98050000`** (the master / sub tone-generator register ports) anywhere in the
  harmony computation. It produces note events and hands them to the ordinary
  voice engine; the register writes that actually reach the tone generators are
  the same ones used for every other note. A hardware harmony feature would have
  to configure the tone generator; this one never does.
- **The harmony is routed to an arbitrary, user-selectable part with that part's
  own patch.** `0x8082` lets the player send the added notes to *any* part —
  played through whatever sound that part is set to. A note-multiplier built into
  the tone-generator silicon could not redirect its extra notes to an arbitrary
  part and re-voice them with a different patch. That flexibility only exists
  because the notes are computed in software and injected as ordinary note-ons.

## Panel control

Techni-chord has one dedicated panel button and one indicator LED, both bound in
the control-panel device:

| | Physical binding | Part |
|---|---|---|
| **TECHNI-CHORD** button | `CPR_SEG1` bit `0x01` | SW0 |
| **TECHNI-CHORD** indicator LED | `cpr_led33` | D1013 (red) |

(See the [Control Panel Protocol]({{ site.baseurl }}/kn7000-control-panel/) for
the scan-matrix tagging convention.)

## Consequence for emulation

Nothing extra is required to emulate Techni-chord. Because it is a pure-software
feature that ends in ordinary note-ons, **a correct MN10300 running the firmware
plus the existing tone-generator note path reproduces it for free** — the
[MAME driver]({{ site.baseurl }}/kn7000-sound-subsystem/) already executes the
harmony routine as part of normal firmware execution, and the added notes sound
through the same pipeline as any key press. No harmony model, note-multiplier or
special tone-generator mode has to be written.

---

**Footnote — not to be confused with the microphone harmonizer.** The symbol
`HarmOnOffFunc` at `0x484D6EA6` and the writes to `0x90204000` belong to the
**Vocalist Workstation** microphone-harmony feature (a real-time pitch harmonizer
for the mic input, driven through a MILK class descriptor at `0x4874CFF0`) — a
separate subsystem from Techni-chord. Techni-chord harmonizes *keyboard* notes in
software as described above and does not use that path.
