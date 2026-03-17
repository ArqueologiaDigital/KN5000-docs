---
layout: page
title: Firmware Architecture Flowchart
permalink: /firmware-flowchart/
---

# Firmware Architecture Flowchart

This page documents the complete execution flow of the KN5000 firmware, from power-on through steady-state operation. The firmware runs on a TMP94C241F (TLCS-900/H2) CPU at 16 MHz with a cooperative multitasking scheduler.

## Power-On Boot Sequence

<pre class="mermaid">
flowchart TD
    RESET["RESET Vector<br/>(0xE00000)"] --> HW_INIT["Hardware Init<br/>IO ports, stack, RAM clear"]
    HW_INIT --> SELF_TEST["Self Test<br/>ROM checksum, RAM test"]
    SELF_TEST --> FW_VER{"Firmware<br/>version?"}
    FW_VER -->|"v0xFF (boot ROM)"| SHOW_WAIT["Display<br/>'Please Wait !!'"]
    FW_VER -->|"Normal"| POST_TEST["Post Self Test"]
    SHOW_WAIT --> POST_TEST
    POST_TEST --> TASK_INIT["TaskSched_Init<br/>Initialize cooperative scheduler"]
    TASK_INIT --> PERIPH["Init Peripherals<br/>GPIO, region code"]
    PERIPH --> FLASH["Flash_InitAllBanks<br/>Initialize flash memory"]
    FLASH --> HDAE{"HD-AE5000<br/>present?"}
    HDAE -->|Yes| PPI_INIT["HDAE5000 PPI Init<br/>Parallel port interface"]
    HDAE -->|No| SEQ_INIT
    PPI_INIT --> SEQ_INIT["Seq_FullInit<br/>Sequencer initialization"]
    SEQ_INIT --> CPANEL["CPanel_ScanButtons<br/>Read power-on key combo"]
    CPANEL --> FLASH_UPD{"Key combo =<br/>flash update?"}
    FLASH_UPD -->|Yes| FW_UPDATE["FLASH_MEM_UPDATE<br/>Firmware update from floppy"]
    FLASH_UPD -->|No| MAIN_BOOT
    FW_UPDATE --> HALT["Boot_MainSequence_Trampoline<br/>(infinite loop — reboot required)"]

    subgraph MAIN_BOOT ["Main Boot Path"]
        FACTORY{"Factory reset<br/>requested?"}
        FACTORY -->|Yes| RESET_DRAM["Clear all DRAM + SRAM"]
        FACTORY -->|No| SUBCPU_INIT
        RESET_DRAM --> SUBCPU_INIT["SubCPU_Init_DMA_Channels"]
        SUBCPU_INIT --> PAYLOAD["SubCPU_Send_Payload<br/>Transfer 192KB firmware"]
        PAYLOAD --> VERIFY["SubCPU_Payload_Verify<br/>Checksum validation"]
        VERIFY --> SCREEN0["ScreenGroup_Dispatch(0)<br/>Initial boot screen"]
        SCREEN0 --> CHECK_ERR{"Payload<br/>transfer OK?"}
        CHECK_ERR -->|Error| ERR_SCREEN["ScreenGroup_Dispatch(2)<br/>'ERROR in CPU data'"]
        CHECK_ERR -->|OK| BOOT_SCREEN["Boot_DisplayScreen<br/>ScreenGroup_Dispatch(1)"]
    end

    BOOT_SCREEN --> MAIN_LOOP
</pre>

## Main Event Loop

After boot, the firmware enters a cooperative multitasking loop driven by a task scheduler and event dispatch system.

<pre class="mermaid">
flowchart TD
    BOOT["Boot_DisplayScreen"] --> INIT_SUBSYS["Initialize All Subsystems"]

    subgraph INIT_SUBSYS ["Subsystem Initialization"]
        INIT_NAKA["InitializeNaka<br/>Register 478 UI widget objects"]
        INIT_HAMA["InitializeHama<br/>Register file I/O titles"]
        INIT_AUDIO["AudioInit<br/>Tone gen, DSP, voice allocation"]
        INIT_MIDI["MIDI Init<br/>Serial port, routing tables"]
        INIT_SEQ["Sequencer Init<br/>Ring buffers, part state"]
    end

    INIT_SUBSYS --> MAIN_LOOP

    subgraph MAIN_LOOP ["Main Event Loop (cooperative multitasking)"]
        SCHED["TaskSched_Dispatch<br/>Run next ready task"]
        SCHED --> EVT_CHECK{"Events<br/>pending?"}
        EVT_CHECK -->|Yes| EVT_DISPATCH["Event Dispatch<br/>Route to registered handler"]
        EVT_CHECK -->|No| TIMER_CHECK{"Timer<br/>expired?"}
        EVT_DISPATCH --> SCHED
        TIMER_CHECK -->|Yes| TIMER_HANDLER["Timer Handler<br/>Sequencer tick, UI refresh"]
        TIMER_CHECK -->|No| SCHED
        TIMER_HANDLER --> SCHED
    end
</pre>

## Interrupt Service Routines

The firmware uses hardware interrupts for real-time operations. ISRs feed data into ring buffers consumed by the main loop.

<pre class="mermaid">
flowchart LR
    subgraph ISR ["Hardware Interrupts"]
        DMA_ISR["E1 DMA ISR<br/>Inter-CPU data transfer"]
        TIMER_ISR["Timer ISR<br/>System tick (1ms)"]
        SERIAL_ISR["Serial ISR<br/>MIDI RX/TX, Control Panel"]
    end

    subgraph BUFFERS ["Ring Buffers"]
        NOTE_BUF["NoteEvent Buffer<br/>(0x0203D5)"]
        SOUND_BUF["SoundEdit Buffer"]
        VOICE_BUF["VoiceMap Buffer<br/>(0x0201C1)"]
        DSP_BUF["DspSysEx Buffer<br/>(0x01FCA3)"]
        MIDI_BUF["MIDI Out Buffer<br/>(0x01F785)"]
    end

    DMA_ISR --> NOTE_BUF
    DMA_ISR --> SOUND_BUF
    DMA_ISR --> VOICE_BUF
    DMA_ISR --> DSP_BUF
    SERIAL_ISR --> MIDI_BUF
</pre>

## Subsystem Architecture

<pre class="mermaid">
flowchart TD
    subgraph UI_LAYER ["UI Layer"]
        NAKA["NAKA Widget Framework<br/>478 widget objects, 9 type codes"]
        SCREEN["Screen Manager<br/>Screen groups, mode dispatch"]
        DRAW["Drawing Primitives<br/>Lines, boxes, text, bitmaps"]
        VGA["VGA Controller<br/>320x240 8bpp LCD"]
    end

    subgraph AUDIO_LAYER ["Audio Layer"]
        TONEGEN["Tone Generator (IC303)<br/>64 voices, PCM wavetable"]
        DSP["DSP Effects<br/>IC310 (serial) + IC311 (parallel)"]
        VOICE["Voice Allocator<br/>Note-on/off, velocity, pan"]
        SNDPARAM["Sound Parameters<br/>Preset lookup, category maps"]
    end

    subgraph SEQ_LAYER ["Sequencer Layer"]
        SEQ["Sequencer Engine<br/>16-track, ring buffer playback"]
        ACCOMP["Accompaniment Engine<br/>Rhythm, bass, chord patterns"]
        SMF["SMF Player<br/>Standard MIDI File playback"]
        STYLE["Style System<br/>SSF data, variation select"]
    end

    subgraph IO_LAYER ["I/O Layer"]
        CPANEL["Control Panel<br/>Serial protocol, 150 buttons, 119 LEDs"]
        MIDI["MIDI<br/>31250 baud UART, SysEx, CC routing"]
        FDC["Floppy Disk<br/>UPD72067 controller"]
        IDE["IDE/ATA<br/>HD-AE5000 hard disk"]
        FLASH["Flash Memory<br/>User settings, custom data"]
    end

    subgraph CPU_LAYER ["Inter-CPU Communication"]
        MAIN["Main CPU<br/>TMP94C241F @ 16MHz"]
        SUB["Sub CPU<br/>TMP94C241F (audio engine)"]
        LATCH["Latch @ 0x140000<br/>Command/response protocol"]
    end

    UI_LAYER --> AUDIO_LAYER
    UI_LAYER --> SEQ_LAYER
    SEQ_LAYER --> AUDIO_LAYER
    AUDIO_LAYER --> CPU_LAYER
    IO_LAYER --> UI_LAYER
    IO_LAYER --> SEQ_LAYER
    MAIN <-->|"E1/E2/E3 commands"| LATCH
    LATCH <-->|"DMA bulk transfer"| SUB
    SUB --> TONEGEN
    SUB --> DSP
</pre>

## NAKA Widget Event Flow

The UI framework uses a hierarchical event dispatch system. Events flow from hardware through the control panel to NAKA widget handlers.

<pre class="mermaid">
flowchart TD
    BUTTON["Physical Button Press"] --> CPANEL_ISR["Control Panel ISR<br/>Serial packet decode"]
    CPANEL_ISR --> EVT_GEN["Generate Event ID<br/>(e.g., 0x01C00008 = DISK MENU)"]
    EVT_GEN --> VIEWABLE["ViewableProc<br/>(0xFA5995)"]
    VIEWABLE --> TYPE_CLASS["SeMenu_SetObjectFlags<br/>Classify by widget type"]
    TYPE_CLASS --> HANDLER_TABLE["handler_table lookup<br/>(DRAM dispatch table)"]
    HANDLER_TABLE --> INHERITED["InheritedProc<br/>Walk parent chain"]

    subgraph WIDGETS ["Widget Handlers"]
        CONTAINER["Container Handler<br/>Screen root, layout"]
        MENU_ITEM["Menu Item Handler<br/>Selection, navigation"]
        SLIDER["Slider Handler<br/>Value adjustment"]
        DISPATCH["Dispatch Handler<br/>Proc function call"]
    end

    INHERITED --> CONTAINER
    INHERITED --> MENU_ITEM
    INHERITED --> SLIDER
    INHERITED --> DISPATCH
    DISPATCH --> PROC["Proc Function<br/>(e.g., IvDrawbarProc)"]
    PROC --> ACTION["UI Action<br/>Sound change, screen transition"]
</pre>

## Memory Map Overview

<pre class="mermaid">
flowchart LR
    subgraph ADDR_SPACE ["24-bit Address Space"]
        INT_RAM["0x000000-0x000FFF<br/>Internal RAM (4KB)<br/>CPU registers, stack"]
        IO["0x001000-0x0FFFFF<br/>I/O & Peripherals<br/>Timers, serial, DMA"]
        TONE["0x100000-0x15FFFF<br/>Tone Gen Hardware<br/>64 voices × 32 regs"]
        VRAM["0x1A0000-0x1DFFFF<br/>VRAM (256KB)<br/>320×240 8bpp LCD"]
        DRAM["0x200000-0x27FFFF<br/>Extension DRAM (512KB)<br/>Sequencer, NAKA state"]
        HDAE["0x280000-0x2FFFFF<br/>HDAE5000 ROM (512KB)<br/>Hard disk expansion"]
        CUSTOM["0x300000-0x3FFFFF<br/>Custom Data Flash<br/>User settings"]
        TABLE["0x800000-0x9FFFFF<br/>Table Data ROM (2MB)<br/>Styles, rhythms, demos"]
        PROG["0xE00000-0xFFFFFF<br/>Program ROM (2MB)<br/>Main firmware"]
    end
</pre>

## Source File Organization

<pre class="mermaid">
flowchart TD
    MAIN["kn5000_v10_program.s<br/>(3,400 lines — entry point)"]

    subgraph BOOT_FILES ["Boot & System"]
        BOOT_HW["shared/boot_hw_init.s"]
        SYS_HAND["boot/system_handlers.s"]
        FACTORY["factory_test/test_*.s"]
    end

    subgraph UI_FILES ["UI Framework (19 .s + 27 .c)"]
        WIDGET_DEFS["ui/ui_widget_defs.s (19K)"]
        DRAW_PRIM["ui/drawing_primitives.s"]
        CPANEL_RT["ui/cpanel_routines.s"]
        NAKA_C["ui_widgets/*.c (26 files)<br/>Typed C struct widget data"]
    end

    subgraph AUDIO_FILES ["Audio (31 files)"]
        ACE["audio/audio_control_engine.s (8K)"]
        NVM["audio/note_voice_mapping.s (26K)"]
        SEMENU["audio/semenu_routines.s"]
        DSP_CFG["audio/dsp_config_sysex.s"]
        SND_DATA["audio/sound_data_*.s (7 files)"]
    end

    subgraph SEQ_FILES ["Sequencer (15 files)"]
        ACC_ENG["sequencer/accompaniment_engine.s (33K)"]
        SEQ_ENG["sequencer/sequencer_engine.s (32K)"]
        SMF_PLAY["sequencer/smf_playback.s"]
    end

    subgraph MIDI_FILES ["MIDI (9 files)"]
        MIDI_SER["midi/midi_serial_routines.s"]
        MIDI_DISP["midi/midi_dispatch_handlers.s"]
        SYSEX["midi/sysex_routines.s"]
    end

    subgraph STORAGE_FILES ["Storage (2 files)"]
        FDC_RT["storage/fdc_routines.s"]
        FLASH_RT["storage/flash_floppy_handlers.s"]
    end

    MAIN --> BOOT_FILES
    MAIN --> UI_FILES
    MAIN --> AUDIO_FILES
    MAIN --> SEQ_FILES
    MAIN --> MIDI_FILES
    MAIN --> STORAGE_FILES
</pre>

---

## Disassembly Statistics

| Metric | Value |
|--------|-------|
| Total native instructions | 279,441 + ~90,000 newly converted |
| Assembly source files | 154 (.s) + 70 (.c) |
| ROM byte match | 100% on all 6 ROMs |
| Labeled symbols | 37,276 (0 opaque LABEL_XXXXXX) |
| NAKA widget C structs | 26 files with typed fields |

---

*Auto-generated from KN5000 ROM disassembly analysis. Last updated: March 2026.*
