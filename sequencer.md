---
layout: page
title: Sequencer
permalink: /sequencer/
---

# Sequencer

The KN5000 includes a full-featured 16-track MIDI sequencer with real-time and step recording, playback, and editing capabilities. It also runs the auto-accompaniment style system and Feature Demo playback.

## Architecture

The sequencer engine runs on the **Main CPU** and generates MIDI events that are sent to the Sub CPU via the inter-CPU latch for sound generation. The architecture has three main stages: a tick-driven dispatcher, a ring buffer pipeline, and MIDI event processing.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     MAIN CPU SEQUENCER ENGINE                           │
│                                                                         │
│  MainLoop (0xEF1245) ─── continuous loop ──────────────────────┐        │
│       │                                                        │        │
│       ├─ Seq_TickWrapper (0xEF1388) ─────────────────┐         │        │
│       │       │                                      │         │        │
│       │       └─ Seq_DispatcherEntry (0xF532E1)      │         │        │
│       │               │                              │         │        │
│       │               └─ Seq_DispatcherTick           │         │        │
│       │                       │                      │         │        │
│       │              ┌────────┴─────────┐            │         │        │
│       │              │ State Check      │            │         │        │
│       │              │ (8D36h)          │            │         │        │
│       │              │ skip if 0x10-0x16│            │         │        │
│       │              └────────┬─────────┘            │         │        │
│       │                       │                      │         │        │
│       │              Seq_DispatcherTick_Process       │         │        │
│       │                       │                      │         │        │
│       │              ┌────────┴─────────┐            │         │        │
│       │              │ RhythmROM_       │            │         │        │
│       │              │ CheckValid       │            │         │        │
│       │              │ (3277h check)    │            │         │        │
│       │              └────────┬─────────┘            │         │        │
│       │                       │                      │         │        │
│       │              Seq_RhythmProcessor (0xF5EC75)   │         │        │
│       │              RhythmROM_PatternDispatcher       │         │        │
│       │                       │                      │         │        │
│       │               ┌───────┴────────┐             │         │        │
│       │               │  Song Engine   │             │         │        │
│       │               │  writes MIDI   │─────────┐   │         │        │
│       │               │  to ring buf   │         │   │         │        │
│       │               └────────────────┘         │   │         │        │
│       │                                          v   │         │        │
│       │                              ┌──────────────────┐      │        │
│       │                              │  RING BUFFER     │      │        │
│       │                              │  Base: 0x01F37B  │      │        │
│       │                              │  WrPos: 0x01F377 │      │        │
│       │                              │  RdPos: 0x01F373 │      │        │
│       │                              └────────┬─────────┘      │        │
│       │                                       │                │        │
│       ├─ Seq_EventProcessingTick (0xEF14A3) ──┘                │        │
│       │       │                                                │        │
│       │       └─ Seq_ProcessEventLoop (0xEF14CA)               │        │
│       │               │                                        │        │
│       │       ┌───────┴──────────┐                             │        │
│       │       │ Seq_CheckSongEnd │                             │        │
│       │       │ WrPos == RdPos?  │                             │        │
│       │       └───────┬──────────┘                             │        │
│       │               │ (if data available)                    │        │
│       │               v                                        │        │
│       │       Seq_ProcessMidiEvent (0xEF13CD)                  │        │
│       │               │                                        │        │
│       │       ┌───────┴──────────────────────────┐             │        │
│       │       │ Parse MIDI status byte:           │             │        │
│       │       │  0x90 = Note On                   │             │        │
│       │       │  0x80 = Note Off                  │             │        │
│       │       │  0xB0 = Control Change            │             │        │
│       │       │  0xC0 = Program Change            │             │        │
│       │       │  0xE0 = Pitch Bend                │             │        │
│       │       └──────────────────────────────────┘             │        │
│       │                       │                                │        │
│       │                       v                                │        │
│       │               sendCOMM (0xEF32F4)                      │        │
│       │               Inter-CPU Latch → Sub CPU                │        │
│       │                                                        │        │
│       └────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
```

## Main Loop

The Main CPU firmware's main application loop at `MainLoop` (0xEF1245) runs continuously after boot. Each iteration calls two sequencer functions:

| Routine | Address | Purpose |
|---------|---------|---------|
| `Seq_TickWrapper` | 0xEF1388 | Drives the sequencer tick dispatcher (song position advance, pattern loading) |
| `Seq_EventProcessingTick` | 0xEF14A3 | Reads MIDI events from the ring buffer and dispatches them to the Sub CPU |

The main loop also handles other firmware tasks (UI updates, floppy I/O, MIDI processing) between sequencer calls, with control flow returning to `MainLoop` via `JRL T`.

## Sequencer Dispatcher

The tick dispatcher processes sequencer timing and loads song/pattern data. It runs through a guarded pipeline:

### Entry and Guards

| Routine | Address | Purpose |
|---------|---------|---------|
| `Seq_DispatcherEntry` | 0xF532E1 | Entry point from `Seq_TickWrapper` |
| `Seq_DispatcherTick` | 0xF53318 | State guard: skips processing if `(8D36h)` is 0x10-0x16 |
| `Seq_DispatcherTick_Process` | 0xF53328 | Rhythm ROM guard: calls `RhythmROM_CheckValid`, skips if validation fails |
| `Seq_RhythmProcessor` | 0xF5EC75 | Main rhythm/sequencer processing after guards pass |

### State Machine Variable (8D36h)

The master sequencer state is stored in RAM at `0x8D36`. The state controls which processing paths are active:

| State Range | Behavior |
|-------------|----------|
| 0x10-0x16 | **Skip all** — `Seq_DispatcherTick` returns immediately |
| 0x00-0x0F, 0x17+ | **Process** — dispatcher continues to tick processing |

State transitions are written at a single location in the firmware: `SeqState_TransitionMode` (0xF9936D), which executes `LD (8D36h), L`.

**Observed states during Feature Demo (from MAME log):**

| State | Meaning | When |
|-------|---------|------|
| 0x00 | Idle/startup | Boot through initialization |
| 0x01 | Pre-demo | Brief transition state |
| 0xE0 | `DemoMode_Main_Operation` | Demo playback active (t=21s) |
| 0xE4 | `DemoMode_Initialize` | Demo init complete (t=22.6s) |

None of these values fall in the 0x10-0x16 skip range, confirming the sequencer dispatcher IS active during demo mode.

## Ring Buffer Pipeline

The sequencer uses a ring buffer at RAM `0x01F37B` to queue MIDI events for processing:

| Variable | Address | Purpose |
|----------|---------|---------|
| Read Position | 0x01F373 | Current read index |
| Write Position | 0x01F377 | Current write index |
| Buffer Data | 0x01F37B | Circular buffer start |

### Ring Buffer Routines

Multiple ring buffer instances exist for different sequencer channels. The core ring buffer implementation provides:

| Routine | Address | Purpose |
|---------|---------|---------|
| `Seq_RingBuf_Init_256` | 0xEF2F69 | Initialize 256-byte ring buffer |
| `Seq_RingBuf_Init_512` | 0xEF2FF8 | Initialize 512-byte ring buffer |
| `Seq_RingBuf_Init_1024` | 0xEF3087 | Initialize 1024-byte ring buffer |
| `Seq_RingBuf_Init_2048` | 0xEF3116 | Initialize 2048-byte ring buffer |
| `Seq_RingBuf_ReadByte` | 0xEF2F83 | Read one byte from ring buffer |
| `Seq_RingBuf_ReadData` | 0xEF30BF | Read data block from ring buffer |
| `Seq_RingBuf_WriteByte` | 0xEF30F5 | Write one byte to ring buffer |
| `Seq_RingBuf_WriteByte_Small` | 0xEF2FD7 | Write byte (small buffer variant) |

### SeqMain Buffer Wrappers (buffer at 0x01F37B)

| Routine | Address | Purpose |
|---------|---------|---------|
| `SeqMain_WriteByte` | 0xEF276D | Write one byte to main sequencer buffer |
| `SeqMain_WriteBytes` | 0xEF2783 | Write multiple bytes |
| `SeqMain_GetTimingValue` | 0xEF27B7 | Get timing/delta value |
| `SeqMain_InitBuffer` | 0xEF27BD | Initialize main buffer |
| `SeqMain_SaveWritePos` | 0xEF27CB | Save current write position |
| `SeqMain_ReadData` | 0xEF27D8 | Read data from main buffer |

### Additional Buffer Instances

| Buffer | Base Address | Read Routine | Write Routine |
|--------|-------------|--------------|---------------|
| SeqAlt1 | 0x01F785 | `SeqAlt1_ReadByte` (0xEF280E) | — |
| SeqAlt2 | 0x01FCA3 | — | `SeqAlt2_WriteByte` (0xEF2A25) |
| SeqAlt3 | 0x0201C1 | `SeqAlt3_ReadByte` (0xEF2C22) | — |
| SeqAlt4 | 0x0204DF | `SeqAlt4_ReadByte` (0xEF2E2C) | — |

### Event Processing

`Seq_EventProcessingTick` (0xEF14A3) calls `Seq_ProcessEventLoop` (0xEF14CA), which:

1. Calls `Seq_CheckSongEnd` (0xEF27A5) — compares write position `(0x01F377)` with read position `(0x01F373)`
2. If positions are equal (buffer empty), returns 0 — no events to process
3. If data available, reads MIDI bytes and calls `Seq_ProcessMidiEvent` (0xEF13CD)
4. `Seq_ProcessMidiEvent` parses the MIDI status byte and dispatches via `sendCOMM` to the Sub CPU

## Rhythm ROM

The 4MB Rhythm ROM (0x400000-0x7FFFFF) contains factory preset rhythm patterns, drum kits, and style data.

### Validation

At boot, the firmware validates the rhythm ROM:

| Routine | Address | Purpose |
|---------|---------|---------|
| `RhythmROM_ValidateHeader` | 0xF54651 | Reads magic bytes at 0x400000, expects LE word 0x05040100 |
| `RhythmROM_CheckValid` | 0xF5452F | Checks if `(3277h)` == 0xFFFFFFFF; if so, returns C=1 (invalid) |

The validation result is stored at RAM `0x3277`:
- **0x00000000** = Valid (rhythm ROM present and header matches)
- **0xFFFFFFFF** = Invalid (no rhythm ROM or header mismatch)

When `RhythmROM_CheckValid` returns C=1, `Seq_DispatcherTick_Process` skips ALL rhythm/sequencer processing.

### Pattern Loading

| Routine | Address | Purpose |
|---------|---------|---------|
| `RhythmROM_PatternDispatcher` | 0xF634F3 | Dispatches pattern loading by type |
| `RhythmROM_LoadPattern` | 0xF6358D | Loads a pattern from rhythm ROM into RAM |
| `RhythmROM_CalcPatternAddr` | 0xF636E4 | Calculates pattern address from index |
| `RhythmROM_LoadDrumKit` | 0xF64550 | Loads a drum kit configuration |

## Audio Mixer (0x150000)

The Main CPU configures an audio mixer/attenuator at address 0x150000 during initialization:

| Routine | Address | Purpose |
|---------|---------|---------|
| `AudioMix_Init` | 0xEF17F4 | Initialize audio mixer hardware |
| `AudioMix_EnableChannels_Loop` | 0xEF1830 | Enable mixer channels |
| `AudioMix_WriteChannelGroup` | 0xEF183D | Write channel group configuration |
| `AudioMix_WriteChannelGroup_Loop` | 0xEF184B | Per-channel write loop |

## Demo Mode Integration

The Feature Demo uses the sequencer engine to play pre-recorded demonstration songs. See [Feature Demo]({{ site.baseurl }}/feature-demo/) for the SSF presentation system and [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/#feature-demo) for the detailed playback analysis.

### Demo Mode Entry

| Routine | Address | Purpose |
|---------|---------|---------|
| `DemoMode_Main_Operation` | 0xF8696F | Normal demo playback (disables Timer7, posts events, calls `Seq_StartMainControl`) |
| `DemoMode_Initialize` | 0xF869E3 | First-time demo init (calls `Seq_StartMainControlAlt`, initializes buffers) |

### Demo Mode State

The demo mode handler `SeqState_DemoModeHandler` (0xF993AD) responds to event `0x01c00013`. During demo playback:

1. State transitions to 0xE0 (`DemoMode_Main_Operation` entry)
2. State transitions to 0xE4 (`DemoMode_Initialize` completion)
3. Startup flag at `0x0251D8` controls whether `Seq_StartMainControlAlt` configures audio hardware

### Demo Song Data

Style/rhythm preset data at `Demo_StyleRhythmData` (0xF5CFCC) contains:
- Rhythm/style parameter bytes (96 bytes)
- ASCII variation names: "a-variation1" through "c-variation4" (12 variations)
- Section names: "a-intro 1", "a-fill in 1", "a-ending 1", etc. (24 sections)

## Medley Playback System

The KN5000 supports several medley playback modes for playing multiple songs in sequence.

### Medley Types

| Type | Function | Description |
|------|----------|-------------|
| Internal Medley | `FmmIntMedleyFunc` | Plays user-recorded sequences stored in SRAM |
| Disk Medley | `FmmDiskMedleySelectFunc` | Plays sequences from floppy disk |
| SMF Medley | `FmmSmfMedleyFunc` | Plays Standard MIDI Files |
| Performance Data | `FmmPdMedleyFunc` | Plays performance data files |
| Document Medley | `FmmDocMedleyFunc` | Plays document files |

### Internal Medley Memory Layout

Internal medley songs are stored in battery-backed SRAM:

| Address | Size | Description |
|---------|------|-------------|
| `0xAB000` | 20KB | 10 song slots (0x800 bytes each) |
| `0xF180` | 2KB | Current playback buffer |

Each slot is 2048 bytes (0x800) and stores one user-recorded sequence.

### Key Routines

| Routine | Address | Purpose |
|---------|---------|---------|
| `LABEL_F2065A` | 0xF2065A | Check if slot has valid data |
| `LABEL_F20BCE` | 0xF20BCE | Load and play a song from slot |
| `LABEL_F20BFA` | 0xF20BFA | Copy slot to playback buffer (LDIR) |
| `LABEL_F2076D` | 0xF2076D | Get current playback state |

### Medley State Variables

| Address | Name | Description |
|---------|------|-------------|
| `0x84FE` | Play flag | 0=stopped, 1=playing |
| `0x889A` | Song count | Number of songs in playlist |
| `0x889C` | Current index | Currently playing song |
| `0x889E` | Repeat flag | 0=no repeat, 1=repeat |
| `0x8890` | Order array | 10-byte play order (0xFF=unused, 0xFE=marked) |

### Source Code

The medley system is implemented in `maincpu/file_io/medley.asm` with ~4700 lines of disassembled code including:
- Song selection UI handlers
- Playback state machine
- Repeat/shuffle logic
- Multi-format file loading

---

## Known Information

### Features

Based on KN5000 specifications:

| Feature | Description |
|---------|-------------|
| Tracks | 16 MIDI tracks |
| Resolution | 96 PPQ (presumed) |
| Recording | Real-time and step modes |
| Playback | Variable tempo, loop |
| Editing | Quantize, transpose, copy |
| Storage | Save to floppy or HD |

### Style System

The auto-accompaniment styles include:

| Component | Description |
|-----------|-------------|
| Intro | Opening pattern |
| Main A-D | Main variations |
| Fill A-D | Transition fills |
| Ending | Closing pattern |
| Break | Pause pattern |

### File Formats

Sequences and styles can be stored:

| Format | Extension | Description |
|--------|-----------|-------------|
| KN Sequence | .SQT | Native sequencer format |
| Standard MIDI | .MID | Import/export |
| Style | .STY | Auto-accompaniment |

## MAME Emulation Status

### What Works

- Sequencer dispatcher runs and rhythm ROM is validated successfully
- State machine transitions correctly (0x00 → 0x01 → 0xE0 → 0xE4 during demo)
- Rhythm ROM data is read from 0x400000 during demo (1800-3800 reads/second)
- Sequencer processing code executes (PCs in F5CFxx-F641xx range during demo)

### Known Issues

- **Ring buffer never written**: The main sequencer ring buffer at 0x01F37B always has write position == read position (both 0x0000). The song engine never generates MIDI events into the buffer.
- **Startup flag stuck at 0**: The flag at `0x0251D8` is always 0, which may cause `Seq_StartMainControlAlt` to skip audio hardware configuration.
- **Event loop rate drops 60x**: After demo initialization, the event processing loop drops from ~11,500 iterations/sec to ~168-180/sec. The sequencer is busy processing but producing no output.
- **No Note On/Off events**: The demo sends CC, Pitch Bend, Channel Pressure, and SysEx commands, but never Note On (0x90) or Note Off (0x80).

See [Audio Subsystem - Feature Demo]({{ site.baseurl }}/audio-subsystem/#feature-demo) for detailed diagnostic log analysis.

## Related Pages

- [Audio Subsystem]({{ site.baseurl }}/audio-subsystem/) - Sound playback and Sub CPU
- [Feature Demo]({{ site.baseurl }}/feature-demo/) - SSF presentation system
- [MIDI Subsystem]({{ site.baseurl }}/midi-subsystem/) - MIDI I/O handling
- [Storage Subsystem]({{ site.baseurl }}/storage-subsystem/) - File save/load
- [System Overview]({{ site.baseurl }}/system-overview/) - Overall architecture

## Research Needed

- [ ] Identify why the song engine never writes MIDI events to the ring buffer
- [ ] Investigate the startup flag at `0x0251D8` — what sets it on real hardware?
- [ ] Trace the path from rhythm ROM data reading to ring buffer writing
- [ ] Document sequence data structure format
- [ ] Analyze playback timing engine (Timer7 involvement)
- [ ] Map recording routines
- [ ] Understand style format in Rhythm ROM
- [ ] Document chord recognition
- [ ] Identify quantization algorithms
- [x] Document medley playback system
- [x] Document main loop and dispatcher architecture
- [x] Document ring buffer pipeline and instances
- [x] Document rhythm ROM validation and loading
- [x] Document sequencer state machine
