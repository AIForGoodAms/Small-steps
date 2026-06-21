# Small Steps — v2 (navigable board)

A browser-based recreation of Noor's eye-gaze AAC home screen and its sub-boards,
with dwell/eye-gaze selection. This is the **base** for integrating the sentence
**Builder** into the reserved column on the right of the Builder screen.

> **Codename only.** All real names are replaced by the codename in `NAME` (one
> constant in `index.html`). No real names, faces, or contact photos are in this repo.

## Run it

```bash
cd v2
python3 -m http.server 8000
# open http://localhost:8000
```

It runs out of the box: where the real pictogram crops aren't present, each tile
**falls back to its Dutch text label**, so the full navigation still works.

## What's here

```
v2/
├── index.html        # the whole app: boards data + navigator + dwell/gaze + Builder screen
├── tools/slice_any.py# slices a flat board screenshot into per-cell PNGs
└── boards/           # per-board cell images (gitignored — see "Pictograms" below)
```

## Pictograms (important — licensing)

The real device uses **PCS** (Picture Communication Symbols), which are **licensed
(Tobii/Mayer-Johnson) and must not be committed to this public repo**. So `boards/`
is gitignored. The app degrades gracefully to text labels without them.

To get the real look **locally**:
1. Take a flat, straight-on screenshot of each board.
2. `python3 tools/slice_any.py <screenshot.png> <board-id>` → writes
   `boards/<board-id>/r{row}c{col}.png` (auto-detects which cells are filled).
3. Reload. Crops take precedence over the text fallback.

The grid geometry (`COLS`/`ROWS` in `slice_any.py`) is fixed for the Tellus screen
(1280×800, 16:10) and is shared by every board.

## How the app works

- **`BOARDS`** (top of `index.html`) is the whole model. Each board is a list of
  cells on a 6×6 grid:
  - `r,c` — row/col (1-indexed)
  - `say` — Dutch text spoken on select
  - `to` — navigate to another board id (a folder)
  - `back:true` — the "Terug" tile (pops the nav stack)
  - `text` — render a generated text card instead of an image (used for identity tiles)
  - `img` — custom image override
  - `action:"toggleGaze"` — the `Oogbesturing` tile toggles eye tracking on/off
- **Navigation** is a simple stack: `home → personen → familie`, with `Terug`/`Esc`
  to go back.
- **Selection** = dwell: rest on a tile `DWELL_DELAY` (1s) then a `DWELL` (0.85s)
  fill, then it fires. Works with mouse-hover and with real gaze.
- **Eye tracking** (optional) streams from an EyeTrax webcam bridge over
  `ws://localhost:8765`. Toggle with the `Oogbesturing` tile or the `G` key.
  Keys: `G` gaze on/off · `D` dwell on/off · `Esc`/`Backspace` back.

## ⬅️ Where to integrate the Builder (your task)

The **Builder screen** is `home` rendered at the **same screen dimensions** with a
**7th column added on the right** as reserved white space:

- `BOARDS.builder = { split:true }` is the entry; the **Builder** tile on the home
  board (`to:"builder"`) opens it.
- `renderBuilder()` builds the 7-column board and appends the reserved
  **`.buildspace`** column (currently: empty white space + a `←` back arrow at the
  bottom that returns home).

**Hook your builder UI into `renderBuilder()` / `.buildspace`.** Today, selecting a
tile on the Builder screen just speaks it (see the `onActivate` passed to
`makeCell` inside `renderBuilder`) — repoint that to push the selected tile into
your builder, assemble the sentence in the column, and read it back (browser
`speechSynthesis`, or wire ElevenLabs/Claude).
