# CLAUDE.md — KN5000 Documentation Website

## Overview

Jekyll-based documentation website for the KN5000 reverse engineering project. Build: `bundle exec jekyll serve`.

## Issue Tracker

Project issues are tracked centrally using [Beads](https://github.com/beads-ai/beads) in `~/devel/kn5000-roms-disasm/.beads/issues.jsonl`. Use `~/devel/tools/bd` commands (never edit JSONL directly). The `issues.md` page is auto-generated — update via `cd ~/devel/kn5000-roms-disasm && make issues`, then commit the result here.

**After meaningful work, agents MUST:** (1) update relevant issues with progress comments, (2) open new issues for next steps, (3) sync issues to this website (`make issues` in roms-disasm), (4) pick the next task from the tracker.

## Policies

- **Keep in sync** with reverse engineering discoveries across all subprojects (see Documentation Freshness policy in central CLAUDE.md).
- **Symbol names in docs must match assembly source** (see Symbol Name Synchronization policy in roms-disasm CLAUDE.md).
