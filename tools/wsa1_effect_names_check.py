#!/usr/bin/env python3
"""Re-derive the SX-WSA1 effect-name offsets quoted on the /wsa1/ page.

QUESTION THIS ANSWERS
  wsa1.md claims, in "Why this machine matters to the KN work", that the WSA1
  carries a DSP effect-name table in prom_b at specific addresses, and that
  four of the names in it -- SLOW ATTACKER, PITCH SHIFTER, PEDAL WAH and
  PEDAL WAH+DELAY -- are among the twelve effects the KN5000 ships as programs
  byte-identical to NO OPERATION (dsp-effect-data-zone.md).  The KN5000 half of
  that claim is already sourced on this site; THIS script is the evidence for the
  WSA1 half: that those strings exist, at those addresses, in that table.

WHAT COUNTS AS PASS
  Every expected name is found exactly once in prom_b, at the CPU address the
  page quotes.  Exits non-zero otherwise.  It prints the surrounding bytes as
  printable text so a reader can see the 16-character centred fields and the
  "----------" placeholders, and it prints NOTHING from any other ROM.

⚠ ROM IMAGES NEVER LEAVE THIS MACHINE.  This script reads a local path and
  prints only the few name fields it is asserting about.  Do not extend it to
  dump ROM contents.

USAGE
  python3 tools/wsa1_effect_names_check.py [--roms DIR]

  DIR defaults to ../wsa1-roms-disasm/original_ROMs relative to this repository.
"""
import argparse
import os
import sys

PROM_B_BASE = 0xF00000
PROM_B_FILE = "wsa1_prom_b.ic13"

# name -> CPU address quoted on the page
EXPECTED = {
    "SLOW ATTACKER":   0xF149FD,
    "PITCH SHIFTER":   0xF14ABD,
    "PEDAL WAH+DELAY": 0xF14BFC,
}
# PEDAL WAH occurs twice: once alone, once inside PEDAL WAH+DELAY.
EXPECTED_MULTI = {
    "PEDAL WAH": ([0xF14ADF, 0xF14BFC], "the second hit is inside PEDAL WAH+DELAY"),
}


def printable(b):
    return "".join(chr(c) if 32 <= c < 127 else "." for c in b)


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser()
    ap.add_argument("--roms", default=os.path.join(here, os.pardir,
                                                   "wsa1-roms-disasm", "original_ROMs"))
    args = ap.parse_args()

    path = os.path.join(args.roms, PROM_B_FILE)
    if not os.path.isfile(path):
        print(f"FAIL: {path} not found (pass --roms DIR)")
        return 2
    data = open(path, "rb").read()

    failures = 0
    for name, want in EXPECTED.items():
        hits = [PROM_B_BASE + i for i in range(len(data))
                if data.startswith(name.encode(), i)]
        ok = hits == [want]
        failures += not ok
        print(f"{'ok  ' if ok else 'FAIL'}  {name!r:20s} at {[hex(h) for h in hits]} "
              f"(page says {hex(want)})")

    for name, (want, note) in EXPECTED_MULTI.items():
        hits = [PROM_B_BASE + i for i in range(len(data))
                if data.startswith(name.encode(), i)]
        ok = hits == want
        failures += not ok
        print(f"{'ok  ' if ok else 'FAIL'}  {name!r:20s} at {[hex(h) for h in hits]} "
              f"(page says {[hex(w) for w in want]}; {note})")

    # Show the field layout the page describes, so "16-character centred fields"
    # and the "----------" placeholders are visible rather than asserted.
    print("\nthe table as it reads in the image:")
    for addr in (0xF149FD, 0xF14ABD, 0xF14BFC):
        off = addr - PROM_B_BASE
        print(f"  {hex(addr)}  {printable(data[off - 64:off + 64])}")

    if b"----------" not in data:
        print("FAIL: no '----------' placeholder in prom_b")
        failures += 1
    else:
        print("\nok    the '----------' placeholder convention is present in prom_b")

    print(f"\n{'PASS' if not failures else 'FAIL'}: {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
