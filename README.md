# Small Steps — STYX

A faster way for a non-verbal, eye-gaze AAC user to say what **she** means.

> Status: local prototype (not yet pushed). Built at AI for Good Amsterdam.

## The problem

**How might we enable our user to deliver her own thoughts as fast?**

She communicates only through eye-gaze on a symbol board (a Jabbla Tellus running
Mind Express). She does **not read, write, or spell**. Today, reaching a single
intent can take a very long time, and the people around her often end up guessing.

## Our approach

Two ideas layered on a faithful clone of her Mind Express board:

1. **Idiosyncratic dictionary** — her own symbol-combinations mapped to what she
   actually means ("she says X and means Y").
2. **Predictive pictogram keyboard ("pinyin for STYX")** — she gives a fragment;
   the system predicts full spoken sentences, biased by context and her personal
   dictionary; she confirms by ear.

Everything stays text-free: **input = symbols + gaze, output = spoken Dutch.**

## Run the web demo

The interface is a single self-contained file.

```bash
cd web
python3 -m http.server 8000
# open http://localhost:8000
```

- Toggle **Slim** to show the before/after (old way vs. prediction).
- Click a **context** chip to see context-aware prediction.
- **Dwell** (hover) selects a cell, simulating eye-gaze.

## Real webcam eye-tracking (EyeTrax)

Optional. Drives selection with your actual gaze via a local Python bridge.

```bash
cd eyetrax_bridge
pip install -r requirements.txt
python gaze_server.py     # opens 9-point calibration, then streams gaze
```

Then open the web demo (ideally fullscreen / maximized) and click
**👁️ Eye tracking**. Gaze is streamed to the browser over `ws://localhost:8765`
and drives dwell-selection.

## Stack

- **Web:** vanilla HTML/CSS/JS, no build step
- **Pictograms:** [ARASAAC](https://arasaac.org) (CC BY-NC-SA), with emoji fallback
- **Speech:** Web Speech API (`nl-NL`)
- **Eye tracking:** [EyeTrax](https://github.com/ck-zhang/EyeTrax) → WebSocket bridge

## Repo layout

```
web/                 self-contained demo (index.html)
eyetrax_bridge/      gaze_server.py + requirements.txt
```
