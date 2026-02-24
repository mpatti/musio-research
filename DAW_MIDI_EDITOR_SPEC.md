# Browser DAW — MIDI Editor Specification (Phase 1)

## Goal
Build a professional-grade browser MIDI editor as the foundation of a full DAW.

Primary UX target: **fast, precise, musical editing at scale** (10k+ notes smoothly), with predictable timing and reliable undo/redo.

---

## Product Principles
1. **Musical correctness first**: PPQ tick timeline, tempo map, deterministic note/event math.
2. **Performance is a feature**: canvas/WebGL rendering and worker-based heavy ops.
3. **No toy shortcuts**: pro essentials from day one (quantize, velocity lane, snap modes, multi-select editing, undo/redo).
4. **Composable architecture**: MIDI editor modules become DAW-wide building blocks (transport, timeline, automation, clips).

---

## Phase 1 Scope (MIDI Editor Foundation)

### Must-have
- Timeline with bars/beats and zoom
- Piano roll grid (virtualized rendering)
- Note CRUD + edits:
  - create, select, move, resize, duplicate, delete
  - multi-select (box + additive selection)
- Snap engine:
  - off / 1/4 / 1/8 / 1/16 / 1/32
  - triplet grid
  - adaptive snap based on zoom
- Velocity lane:
  - per-note velocity bars
  - drag single/multi values
  - linear ramp tool
- Quantize:
  - hard quantize
  - iterative strength %
- Humanize:
  - timing jitter range
  - velocity jitter range
- Transport + playback:
  - play/stop/loop
  - playhead sync with editor
  - WebAudio scheduler baseline
- Full undo/redo for all edit ops
- MIDI import/export (SMF)

### Should-have in Phase 1.5
- Ghost notes from nearby clips
- Note overlap tools (legato/fix overlaps)
- Keyboard shortcut system + keymap table

---

## Data Model

### Time
- Internal editing time: **ticks**
- `PPQ = 960` default
- Convert to/from seconds using tempo map

### Core entities
- `Project`
  - tempoMap[]
  - timeSignatures[]
  - tracks[]
- `Track`
  - clips[]
  - channel/instrument metadata
- `Clip`
  - startTick, endTick, loop info
  - notes[]
  - ccEvents[]
- `Note`
  - id, pitch, startTick, durationTick, velocity, channel
- `CCEvent`
  - tick, cc, value, channel

### History
- Command pattern (`apply`, `revert`)
- Batching for drag gestures (one gesture = one undo step)

---

## Architecture

### Frontend Stack
- React + TypeScript
- State: normalized store (Zustand/Redux Toolkit style)
- Rendering: Canvas2D initially, WebGL-ready abstraction

### Modules
1. `timeline-engine`
   - tick/pixel mapping
   - zoom + pan
2. `snap-engine`
   - quantization/snap targets
3. `selection-engine`
   - region + additive selection
4. `edit-commands`
   - move/resize/create/delete/transpose/velocity edits
5. `playback-engine`
   - transport state + lookahead scheduling
6. `io-midi`
   - MIDI parse/serialize
7. `history`
   - undo/redo stack

### Threading
- Main thread: interaction + render
- Worker: heavy transforms (quantize/humanize large sets)
- AudioWorklet (later step): tighter playback timing

---

## UX Details
- Tools: Select, Pencil, Erase, Split, Velocity, Mute
- Modifier behavior:
  - Shift = additive select
  - Alt/Option = duplicate-drag
  - Cmd/Ctrl + drag = constrained axis move
- Visual cues:
  - note color by velocity (optional)
  - selected notes with high-contrast outline
  - invalid overlap indicators optional

---

## Sprint Plan

### Sprint 0 (1-2 days)
- Project scaffold
- Transport skeleton
- Timeline + zoom/pan foundation
- Basic piano roll render pipeline

### Sprint 1 (3-4 days)
- Note create/move/resize/delete
- Multi-select + marquee
- Snap modes + grid drawing
- Undo/redo command framework

### Sprint 2 (3-4 days)
- Velocity lane editing
- Quantize + iterative quantize
- Humanize timing/velocity
- Keyboard shortcuts

### Sprint 3 (2-3 days)
- Playback integration
- MIDI import/export
- Performance pass + interaction polish

### Sprint 4 (optional hardening)
- Ghost notes
- Overlap tools
- Regression tests + stress testing

---

## Acceptance Criteria (Phase 1)
- Can edit dense MIDI clips smoothly at 60fps target on modern laptop
- Quantize/humanize produce deterministic results
- Undo/redo is stable under rapid gestures
- Imported MIDI round-trips with no note loss
- Playback aligns with visual playhead with no obvious drift in short loops

---

## Immediate Next Build Tasks
1. Create DAW app shell and module folders.
2. Implement timeline engine (tick↔pixel).
3. Implement canvas piano roll with note rendering.
4. Add note interaction command system.
5. Add snap engine and grid modes.
