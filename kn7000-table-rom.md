---
layout: page
title: KN7000 Table ROM — Resource Archive
permalink: /kn7000-table-rom/
---

# Technics SX-KN7000 — table ROM resource archive

The KN7000's 4 MB **table ROM** (mapped at `0x48000000`, a mask ROM byte-interleaved across two
flash chips) is not code — it is a **directory-based resource archive**. It opens with a table of
little-endian u32 chunk offsets, and each entry points to a tagged resource.

## Chunk kinds

| Address | Tag / content | Meaning |
|--------|---------------|---------|
| `0x48000000` | u32 offset directory | index of all chunks (first chunk at `0x48000200`) |
| `0x48035d08` | **`TCMP`** | a **MN10300 code overlay** copied to RAM `0x50180000` at boot and executed — the KN7000 keeps part of its program in the table ROM |
| `0x48040674` | **`TPAD`** | performance-**pad** index / parameters |
| `0x4804238c` | `Technics Pads` | accompaniment pad pattern data |
| `0x483e828c` | `Technics Rhythms` | style/rhythm resource index |
| (throughout) | **JFIF JPEG** | 117 embedded UI/graphics images |

## The UI graphics are standard JPEGs

Scanning for JPEG streams recovers **117 images, 115 of which decode cleanly with an ordinary JFIF
decoder** — 52 are `160×120` icons/thumbnails and twelve are full-screen `640×240` reference/help
screens. In other words the KN7000 stores its on-screen artwork as ordinary JPEGs and decodes them
in firmware. (A long-standing emulation note that "the boot-splash JPEG decodes to garbage" is
therefore a **software JPEG-decoder bug**, not a bad dump or an exotic format — the source stream is
valid JFIF.)

Example full-screen reference screens, extracted verbatim from the ROM:

![KN7000 RHYTHM home screen reference]({{ site.baseurl }}/assets/images/table-rom/rhythm-home.jpg)

![KN7000 ORGAN STYLIST style-list reference]({{ site.baseurl }}/assets/images/table-rom/organ-stylist.jpg)

The ORGAN STYLIST list above shows real style names (`Swing Tonewheels`, `Classic B3 Jazz`, …) that
match the [built-in rhythm catalog]({{ site.baseurl }}/kn7000-rhythm-catalog/) recovered from the program ROM.

A smaller `240×160` panel graphic:

![KN7000 panel graphic]({{ site.baseurl }}/assets/images/table-rom/icon-sample.jpg)

## Reproduce
De-interleave `kn7000_table_{even,odd}.rom` (`out[0::4]=e[0::2]; out[1::4]=e[1::2]; out[2::4]=o[0::2];
out[3::4]=o[1::2]`) → 4 MB image; walk the u32 directory at offset 0; extract JPEGs by scanning
`ff d8 ff e0` → `ff d9`. See also the [firmware images]({{ site.baseurl }}/kn7000-firmware/) page for the full
per-segment breakdown; technical detail in `kn7000_mame/notes/table-rom-format.md`.
