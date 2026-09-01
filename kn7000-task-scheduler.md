---
layout: page
title: KN7000 Tasks & Scheduler
permalink: /kn7000-task-scheduler/
---

# KN7000 Tasks & Scheduler

The KN7000 firmware runs as **two cooperative tasks** on top of the MILK kernel:
a **main** task (the foreground UI / panel loop) and an **AP** ("application")
task (background work — song/data processing, longer operations). They take turns
by explicitly sleeping and waking each other through a small message API. This
page documents that mechanism as decoded from `kn7000_program.rom`; it is the
companion to the [Event & Dispatch System]({{ site.baseurl }}/kn7000-event-system/), which is what
each task actually runs while awake.

## The two tasks

The currently-running task and the main task are identified by handles kept in
work RAM:

| Global | Meaning |
|--------|---------|
| `0x50380004` | handle of the **currently running** task |
| `0x5038002C` | handle of the **main** task |

Code decides "am I the main or the AP task?" by comparing them — exactly what the
event layer's `GetCurrentObjectId` helper does before it picks the active task's
focused-object id (`0x500D3C60` for main, `0x500D3C5C` for AP; see the
[event page]({{ site.baseurl }}/kn7000-event-system/)). So each task carries its own focused UI
object, and the event dispatcher always acts on the running task's object.

## Sleep / wake API

Four thin entry points let code hand control back and forth:

| Function | CPU addr | Effect |
|----------|----------|--------|
| `SleepMainTask` | `0x48414B8D` | suspend the main task |
| `WakeUpMainTask` | `0x48414BA7` | resume the main task |
| `SleepApTask` | `0x48414BC1` | suspend the AP task |
| `WakeUpApTask` | `0x48414BDB` | resume the AP task |

Each is a one-line wrapper that builds a **task-control message** and dispatches
it — decoded straight from the source (`SleepMainTask`):

```
SleepMainTask:                   # CPU 0x48414B8D
    add     -0x14, sp
    clr     d0
    mov     d0, (0x10, sp)       # message param slot = 0
    mov     0x00020009, d0       # message opcode/class
    mov     0x0006009D, d1       # message id  (see table)
    call    0x48414A77           # task-control message handler
    ret
```

The opcode in `d0` is the constant `0x00020009` for all four; the **message id in
`d1`** is what selects the action, and the ids form a small contiguous block:

| Message id | Action |
|------------|--------|
| `0x0006009D` | sleep main |
| `0x0006009E` | wake main |
| `0x0006009F` | sleep AP |
| `0x000600A0` | wake AP |
| `0x000600A1` | (a fifth task-control message) |

The handler at `0x48414A77` (with a sibling at `0x48414AFD` for the AP side) is a
`switch` on `d1` that runs the matching sleep/wake code — from its first
instructions:

```
cmp 0x6009F, d1 ; beq …        # sleep AP
cmp 0x600A0, d1 ; beq …        # wake AP
cmp 0x6009D, d1 ; beq …        # sleep main
cmp 0x6009E, d1 ; beq …        # wake main
cmp 0x600A1, d1 ; beq …
```

The underlying context switch / run-queue lives in the **MILK kernel** (the
banner `MILK MN10300 Ver1.0R1` at `0x3B8AAC`), part of which is in the
still-[undumped library ROM]({{ site.baseurl }}/kn7000-firmware/) at `0x4C000000`.

## Task refresh

`RefreshApTask` (`0x48414BF5`) and `RefreshSwEvent` (`0x48414C98`) reset a small
block of task-state globals (`0x50021FD8`, `0x50021FDC`, `0x50021FE0`) and then
re-broadcast events (`mov -1, d0` with event-category ids `0x00050006` /
`0x00050005`) so the UI redraws after a task transition. This is the seam where
the scheduler hands back to the event system.

## Relationship to the KN5000

Cooperative main/AP tasking on the MILK kernel is **shared with the KN5000**
(same source tree — [Shared Codebase Map]({{ site.baseurl }}/technics-shared-codebase/)); the
message opcode/id convention and the sleep/wake naming carry across. What is
observed here for the KN7000 specifically are the concrete addresses — the task
handles (`0x50380004` / `0x5038002C`), the per-task focused-object pointers, the
message-id block (`0x6009D…0x600A1`) and the handler entry points.

## The same kernel is in four processors, across two products

*Added 2026-09-02.* The sharing above turns out to reach considerably further than
the KN5000. The **SX-WSA1R**, a physical-modelling synthesiser built on a different
CPU family (two TMP95C061s against the KN7000's MN10300), runs the **same
multitasking kernel** — and so does each of the KN5000's two processors. One
kernel, four processors, two products.

The proof for the WSA1R pair is a build, not a resemblance: `wsa1/kernel/kernel.s`
is a single source that assembles into **2,180 bytes of `prom_a` and 2,180 bytes of
`prom_c`, both byte-identical to the real EPROMs**. Over the union of the two
blocks there are 941 instruction slots; 735 needed no reconciliation, 129 differed
only in house style, and the remaining 81 reduce to **21 named constants** (twelve
RAM addresses, six array sizes, three ROM pointers) — with no conditional assembly
anywhere in the file.

For the KN5000 the instrument had to change, and that is the part worth
remembering. ⚠ **Byte-identity was the wrong test and had already answered "no"**:
a tool in the tree reported zero byte-identical matches for 23 routines across all
41 KN5000 images. That is true about bytes and false about the question — two
processors *in the same product*, from *the same build*, running *the same source*,
still differ in 81 of 941 slots, so a third built years apart cannot possibly be
closer. Matching on control-flow shape instead, against a **foil control** of
non-kernel code cut to the same instruction counts:

| | n | max | median | ≥ 0.70 |
|---|---:|---:|---:|---:|
| kernel routines (≥ 20 instr) | 20 | 1.000 | 0.909 | 20 |
| non-kernel foils | 26 | 0.333 | 0.212 | 0 |

No overlap, and a gap of 0.41.

⚠ **Do not trust the KN5000's kernel labels.** The measured alignment does not
match them: the site that actually corresponds to `MsgQueue_Send` is labelled
`TaskSched_Wait`, the one matching `Kernel_SemaSignal` is labelled
`TaskEvent_Wait`, and on the main CPU the site matching `Kernel_StartTask` at 0.978
is called `Show_ScreenGroup_Entry`. Several KN5000 kernel labels are simply wrong —
a renaming pass waiting to happen, and a reminder that names point an instrument at
a region without being evidence about it.

Not established: who wrote it, and that the sources are identical.
`Kernel_Dispatch` scores only 0.742, because the KN5000 version has no tick-drain
loop and its lock depth has moved out of a control register the TMP94C241 does not
have. The same program; not the same file.
