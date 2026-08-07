---
layout: page
title: Sub-CPU Firmware Images
permalink: /subcpu-firmware-images/
---

# Sub-CPU Firmware Images (v1.40 / v1.41 / v1.42)

The KN5000's sub-CPU has a 128 KB boot ROM of its own (`kn5000_subcpu_boot.ic30`, mapped at
`0xFE0000`) but no flash holding its 192 KB *runtime* payload: that payload is pushed across
the inter-CPU link at every boot by `SubCPU_Send_Payload` (see
[SubCPU Payload Loading]({{ site.baseurl }}/subcpu-payload-loading/)).

**Where the main CPU reads it from is still unresolved.** The routine's two source bases are
the LZSS image at Custom Data flash `0x3E0000` and, on failure, table-data `0x800000` — and
in the images this project holds neither contains the payload: the custom-data dump is erased
at `0x3E0000`, and the table-data ROM's `0x830000` region is the
[tone database]({{ site.baseurl }}/tone-database/), not a copy of the executable.

Three revisions of that payload survive, and they survive in two different shapes — which
turns out to matter for preservation.

## The two shapes

**Decompressed payload (196,608 bytes).** What the sub-CPU actually executes. This is the
form the disassembly reconstructs and the form `compare_roms.py` checks.

**Firmware-update image (~93 KB).** What ships on a system-update floppy: an 11-byte
header — `"SLIDE4K"` + NUL, then the decompressed size as a 24-bit **big-endian** value
(`03 00 00` = 196,608) — followed by the LZSS stream. The update handler for File Type 007
("Technics KN5000 Program DATA FILE PCK") writes it into Custom Data flash at `0x3E0000`;
on the next boot the main CPU decompresses from there instead of taking the
`SubCPU_Send_Payload` fallback branch that points at table-data `0x830000`. That region is
the [tone database]({{ site.baseurl }}/tone-database/), **not** a copy of the sub-CPU
payload, and what the machine would do with tone-database bytes on that path has not been
analysed. See [LZSS Compression]({{ site.baseurl }}/lzss-compression/).

All three compressed images in the repository were extracted from the
[system update floppy disk images](https://archive.org/details/technics-kn5000-system-update-disks)
on the Internet Archive.

## Status of each revision

| Revision | Update image | Decompressed payload | Source tree | In `make all` |
|----------|-------------:|---------------------:|-------------|---------------|
| v1.40 | 93,124 B | 196,608 B — **recovered, committed** | no | no |
| v1.41 | 93,181 B | 196,608 B | no — tracked as `kn5000-v41` | no |
| v1.42 | 93,203 B | 196,608 B | `v142/subcpu/` | **yes, both shapes** |

### v1.42 — fully covered

The v1.42 payload is source-built and byte-identical. Since August 2026 its *update image*
is a verification target too: the build recompresses the source-built payload with
`compress_lzss.py --strict --with-header --reference` — replaying the factory encoder's
own match/literal decisions — and `cmp`s the result against
`original_ROMs/kn5000_subprogram_v142_compressed.rom`. It appears in `compare_roms.py` as
the *subcpu v142 update image* section, at 100.00%.

sha256 of the payload: `16a1b654cea132ac433c16162db4a72ef7227fcc962ff6fae0ce088aa7c6e76e`.

### v1.40 — a preservation recovery

**Before August 2026, no decompressed copy of the v1.40 sub-CPU payload existed anywhere
in this project.** The only artifact was the compressed update image, and nothing in the
build ever unpacked it. A corrupted or lost 93 KB file would have taken the revision with
it.

The 196,608-byte payload has now been decompressed out of that single copy and committed
as `original_ROMs/kn5000_subprogram_v140.rom` (commit `2fb8a95`):

```
sha256  a39025fe7c3968102196c5e20c18c76ec42e31a6c535f48addd58e13dacd7ef0
size    196,608 bytes
```

The recovery is self-checking in both directions: recompressing the extracted payload with
`compress_lzss.py --strict --with-header --reference` against the factory image reproduces
that image **byte for byte** (93,124/93,124). The extraction is therefore not an
interpretation — it is the exact preimage of the shipped file.

There is still no v1.40 source tree, and the payload is not part of any build target. What
exists is an honest, hash-pinned artifact plus a reversible path back to the original.

### v1.41 — internally consistent, no source tree

Both v1.41 artifacts verify against each other: the compressed image decompresses
byte-exactly to `original_ROMs/kn5000_subprogram_v141.rom` (196,608/196,608, consuming
93,181/93,181 input bytes), and recompressing that payload reproduces the image
byte-for-byte. What is missing is a `v141/subcpu/` source tree, so `compare_roms.py`
cannot cover either artifact.

sha256 of the payload: `04212fa6799e75db64b399242b762ce7377669a0a877984659c78c148453d9fe`.

This is tracked as issue **`kn5000-v41`** in the disassembly repository. The proposed route
is the one the main-CPU v7/v9/v10 trees already use: start from the v142 source and
reconcile against the v141 ROM. The raw byte diff looks daunting but is not — most of it is
address-constant ripple that symbolic assembly absorbs for free:

| Pair | Differing bytes | Contiguous runs |
|------|----------------:|----------------:|
| v1.40 ↔ v1.41 | 56,018 | 2,508 |
| v1.41 ↔ v1.42 | 124,033 | 2,875 |
| v1.40 ↔ v1.42 | 124,032 | 2,590 |

v1.40 is much closer to v1.41 than to v1.42, so a future v1.40 tree should be diffed
against v1.41 rather than against the current target.

## Why the update-image target matters

Verifying only the decompressed payload leaves a gap: the bytes a real KN5000 receives from
a firmware-update disk are the *compressed* ones. Adding the compress-and-compare rule
closes it, and it does so without weakening anything — `--strict` aborts the build the
moment the encoder's output diverges from the factory stream, so the check cannot degrade
into "close enough". The same guarantee already covers the in-ROM SLIDE4K demo presets and
the SLIDE8K help databases; see
[ROM Reconstruction]({{ site.baseurl }}/rom-reconstruction/).
