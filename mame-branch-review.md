---
layout: page
title: MAME Branch Review & Roadmap
permalink: /mame-branch-review/
---

# MAME Branch Review & Roadmap

*Last updated: March 30, 2026*

This page documents the current state of all KN5000-related MAME branches, the results of a comprehensive branch review and cleanup, and the roadmap for future upstream pull requests.

> **Context**: Following the merge of [PR #15143](https://github.com/mamedev/mame/pull/15143) (interactive control panel), all five initial PRs are now upstream. A full branch review was conducted to identify remaining unmerged work, archive superseded branches, and rebase active branches onto `upstream/master` for future PR preparation.
>
> **See Also**: [MAME Pull Requests]({{ site.baseurl }}/mame-pull-requests/) for the original PR 1--5 documentation.

## Merged PRs (Complete)

All five foundation PRs have been merged into upstream MAME:

| PR | Topic | Upstream | Merged |
|----|-------|----------|--------|
| PR 1 | LDC CR mapping for TMP94C241 DMA registers | [#14970](https://github.com/mamedev/mame/pull/14970) | Yes |
| PR 2 | EI/RETI interrupt acceptance shadow | [#14995](https://github.com/mamedev/mame/pull/14995) | Yes |
| PR 3 | TMP94C241 DMA subsystem (HDMA + DMAR) + port reads | [#15003](https://github.com/mamedev/mame/pull/15003) | Yes |
| PR 4 | TMP94C241 serial port sub-device | [#15015](https://github.com/mamedev/mame/pull/15015) | Yes |
| PR 5 | KN5000 driver: control panel HLE, subcpu payload, keybed | [#15143](https://github.com/mamedev/mame/pull/15143) | Yes |

## Active Branches (Rebased on upstream/master)

These branches contain unmerged work that is being developed toward future PRs. All were rebased onto `upstream/master` on March 30, 2026.

### `kn5000_pr6` --- 18 commits

The most complete active branch, containing the next major batch of driver improvements. Key features not yet upstream:

| Feature | Commits | Description |
|---------|---------|-------------|
| **Major driver rework** | 1 | SubCPU payload loading, control panel HLE, keybed integration |
| **TMP94C241 timer fix** | 1 | 16-bit timer interrupt generation and flip-flop gating |
| **FDC wiring** | 3 | FDC address mapping, PORT D bit 6, register layout (PC AT), floppy DD->HD fix |
| **UART mode** | 1 | 8-bit UART TX/RX for TMP94C241 serial channels (enables MIDI) |
| **MIDI output** | 1 | Wire TX0 to `midi_port` device |
| **Tone generator** | 7 | Full `kn5000_tonegen_device` (IC303): PCM playback, pitch/pan/volume, release envelope, linear interpolation |
| **DSP1 stub** | 1 | IC311 DS3613GF-3BA device stub |
| **Timer 0 output** | 1 | Wire TO0 to FDC Terminal Count |
| **SNS NMI emulation** | 1 | Boot-time write tap for payload checksum (NVRAM persistence) |
| **Code style** | 1 | Minor upstream compliance cleanup |

**Future PR candidates from this branch:**

- **PR 6: Tone generator device** --- The tone generator, FDC wiring, UART, MIDI output, and DSP1 stub could be submitted as one cohesive "bring the rest of the peripherals online" PR.
- **PR 7: SNS NMI / NVRAM** --- The payload checksum emulation for persistent NVRAM across sessions. May be combined with PR 6 or submitted separately.

### `kn5000_research_tonegen` --- 26 commits (superset of PR6)

Research branch extending PR6 with experimental tone generator and Feature Demo investigation work:

| Feature | Commits | Status |
|---------|---------|--------|
| All of PR6 | 18 | Base (rebased) |
| ATA INTRQ wiring | 1 | HDAE5000 extension IRQ routing |
| VGA controller docs | 1 | MN89304 VGA findings |
| Tone gen voice hold timer | 1 | Fix timing for missing waveform ROMs |
| SSF slide transitions | 1 + 1 revert | Experimental, reverted (approach didn't work) |
| DSP1 ready signal | 1 | Port H bit 0 connection |
| Demo workaround removal | 1 | Removed stuck-parts workaround (not needed with voice timing fix) |
| Voice timing fix | 1 | Final fix for missing waveform ROM behavior |

**Status**: Research branch. Contains confirmed fixes (ATA INTRQ, voice timing, DSP1 ready) that should be cherry-picked onto PR6 when preparing the upstream submission.

### `kn5000_research_datawheel` --- 2 commits

Data wheel rotary encoder research:

| Feature | Commits | Status |
|---------|---------|--------|
| Data wheel encoder input | 1 | Program data wheel as MAME input |
| Segment 0x0B fix | 1 | Correct button packet segment for data wheel |

**Status**: Research branch. Small, focused. Could become part of a future control panel improvements PR.

### `kn5000_power_off_nmi` --- 2 commits

Power-off sequence emulation (alternative approach to PR6's boot-time write tap):

| Feature | Commits | Status |
|---------|---------|--------|
| MACHINE_NOTIFY_POWER_OFF | 1 | New machine notification phase before NVRAM save |
| NVRAM + NMI checksum | 1 | KN5000-specific power-off NMI handler |

**Status**: This adds a core MAME machine phase (`MACHINE_NOTIFY_POWER_OFF`), which is a more invasive change than PR6's write-tap approach. The write-tap in PR6 achieves the same NVRAM persistence result without modifying core MAME infrastructure. This branch is kept as a reference for the "proper" approach if the core change is ever deemed acceptable upstream.

## Archived Branches

These branches have been superseded and are kept only for historical reference:

| Branch | Original Purpose | Reason Archived |
|--------|-----------------|-----------------|
| `MERGED_kn5000_pr1_ldc_cr_mapping` | PR 1 | Merged upstream |
| `MERGED_kn5000_pr2_irq_inhibit` | PR 2 | Merged upstream |
| `MERGED_kn5000_pr3_dma_and_port` | PR 3 | Merged upstream |
| `MERGED_kn5000_pr4_serial` | PR 4 | Merged upstream |
| `MERGED_kn5000_pr5_driver` | PR 5 (original) | Merged upstream |
| `MERGED_kn5000_pr5_driver_v2` | PR 5 (final version) | Merged upstream as #15143 |
| `MERGED_kn5000_interactive_control_panel` | PR 5 (identical to v2) | Merged upstream |
| `ARCHIVED_kn5000_aided_by_claude` | Early research branch | Superseded by PR branches |
| `ARCHIVED_kn5000_pr4_serial_downcast` | PR 4 downcast experiment | Superseded by merged PR 4 |
| `ARCHIVED_kn5000_pr5_driver_aided_by_claude` | PR 5 with research additions | Superseded by research branches |
| `ARCHIVED_kn5000_research_encoder` | Data wheel encoder (v1) | Superseded by datawheel branch |
| `ARCHIVED_kn5000_research_encoder_v2` | Data wheel encoder (v2, WIP) | Superseded by datawheel branch |
| `ARCHIVED_kn5000_research_ssf` | SSF presentation research | Identical to tonegen branch |
| `ARCHIVED_kn5000_pr4_serial_to2_trigger` | TO2 trigger for serial | Superseded by merged serial work |
| `ARCHIVED_kn5000_minor_fix` | Old misc fixes | Superseded by PR 5 |
| `ARCHIVED_kn5000_squash_attempt_2025_08_14` | Early squash attempt | Superseded by PR branches |
| `ARCHIVED_kn5000_research_tonegen_pre_rebase` | Pre-rebase snapshot | Replaced by rebased branch |
| `ARCHIVED_kn5000_research_datawheel_pre_rebase` | Pre-rebase snapshot | Replaced by rebased branch |

## Roadmap: Future PR Candidates

Based on the branch review, the following PRs are planned:

### PR 6: KN5000 Peripherals (Tone Gen, FDC, UART, MIDI, DSP1)

**Source**: `kn5000_pr6` + cherry-picks from `kn5000_research_tonegen`

**Scope**: Bring the remaining KN5000 peripherals online:
- Tone generator device (IC303 TC183C230002) with PCM waveform playback, pitch/pan/volume control
- Floppy disk controller wiring (PC AT register layout, PORT D dskchg)
- 8-bit UART mode for TMP94C241 serial channels
- MIDI output via TX0
- DSP1 device stub (IC311 DS3613GF-3BA)
- Timer 0 output to FDC Terminal Count
- SNS NMI payload checksum for NVRAM persistence

**Preparation needed**:
1. Cherry-pick confirmed fixes from `kn5000_research_tonegen` (ATA INTRQ, DSP1 ready, voice timing)
2. Squash/rewrite commits for clean history (one topic per commit)
3. Remove AI attribution from commit messages
4. Build-test on current `upstream/master`

### PR 7: Data Wheel Encoder

**Source**: `kn5000_research_datawheel`

**Scope**: Add rotary encoder input for the KN5000's Program data wheel, enabling parameter editing in the emulator.

**Preparation needed**:
1. Verify the 2 commits apply cleanly on top of PR 6
2. Test with current firmware

### SHARC core contributions (from the KN7000 work)

The KN7000's effects DSP (an ADSP-21065L) drove a series of fixes to MAME's **shared
2106x SHARC core** — they live on the base `adsp21062_device`, so they benefit every
SHARC system in MAME (arcade boards included), not just the Technics drivers. The
series already exists as clean per-fix commits, staged as patch files in
`kn7000_mame/notes/upstream-patches/` and catalogued in
`kn7000_mame/notes/sharc-upstream-patch-series.md`:

| Candidate | Content | State |
|-----------|---------|-------|
| Perf: native fixed MAC | the DRC never implemented the fixed-point multiply/accumulate family and fell back to the interpreter (~82M fallbacks per 22 s of reverb) | applies cleanly to upstream; **ready** |
| Perf: native single-function fixed multiplier | the actual hot path (the multi-op MAC turned out unused by the kernel) | applies cleanly; **ready** |
| Perf: native fixed ALU average (op 0x09) | last big fallback; overflow-free signed average with exact flags | applies cleanly; **ready** |
| Correctness: `MODE1.ALUSAT` in the recompiler | the DRC compiled fixed-point add/sub as plain wrapping ops where the interpreter honored saturation — a silent recompiler-vs-interpreter divergence for any SHARC program with ALUSAT set (this is what railed the KN7000's reverb) | needs the documented small rebase (depends on one op-0x09 hunk; drop one KN7000-only clock hunk) + a per-patch reverb-WAV A/B |
| New device: `adsp21065l_device` | a 21065L personality of the 2106x core (reset PC `0x20004`, internal SRAM map, SDRAM window) — MAME has no 21065L today | gated on cross-checking the RE-derived memory map against the ADSP-21065L datasheet/TRM (PDFs now in the repo) |

All verified bit-identical against the running KN7000 reverb (interpreter == DRC after
the fixes; >99% of interpreter fallbacks eliminated). Submission is under the project
owner's authorship; the apply-tests should be re-run against the current upstream base
before sending.

Also riding with a future KN5000 PR: the control-panel **button ioports moved into
`kn5000_cpanel_device`** (`device_input_ports()`, layout inputtags qualified
`cpanel:...`) — the same boundary cleanup applied to the KN7000 driver, so the panel
device owns its own inputs.

### Future Research Areas

These are not yet ready for PRs but are active research topics:

- **Waveform ROM decoding**: IC307 format has been decoded (see [Waveform ROM Format]({{ site.baseurl }}/waveform-rom-format/)). Remaining waveform ROMs (IC304--IC306) are undumped.
- **DSP emulation**: Both DSP ICs (MN19413 serial, DS3613GF-3BA parallel) have device stubs. Full emulation requires decoding the DSP bytecode interpreter and register semantics.
- **SSF slide transitions**: Feature Demo visual presentation uses SSF bitmaps that never render in emulation. Root cause is likely missing waveform-driven sequencer completion signals.

## Branch Management Policy

All active branches are kept rebased on `upstream/master` to minimize divergence. When preparing a PR:

1. Create a fresh `kn5000_prN_<topic>` branch from `upstream/master`
2. Cherry-pick or rewrite commits from research branches
3. One topic per PR, clean commit history, no AI attribution
4. Test before and after each commit
5. Archive the source research branch with `ARCHIVED_` prefix after the PR is merged

See the [MAME Branch Management policy](https://github.com/felipesanches/kn5000_project/blob/main/CLAUDE.md) for full details.
