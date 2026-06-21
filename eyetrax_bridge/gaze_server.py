"""
EyeTrax -> WebSocket bridge for the Small Steps STYX demo.

Runs webcam gaze tracking with EyeTrax (https://github.com/ck-zhang/EyeTrax),
calibrates once, then streams the predicted gaze as normalized coordinates to
any connected browser at ws://localhost:8765.

The browser (web/index.html) maps {nx, ny} -> viewport pixels, moves a gaze
cursor, and uses dwell-on-gaze to select cells.

Run:
    pip install -r requirements.txt
    python gaze_server.py
A 9-point calibration window opens first. Look at each dot. Then open the web
demo (ideally fullscreen) and click "Eye tracking".

Message format (JSON, ~30 Hz):
    {"nx": 0.0-1.0, "ny": 0.0-1.0, "blink": bool}
nx/ny are fractions of screen width/height, so keep the browser maximized for
the closest mapping between where you look and where the cursor lands.
"""

import asyncio
import json
import threading

import cv2
import websockets
from eyetrax import GazeEstimator, run_9_point_calibration

HOST, PORT = "localhost", 8765
EMA = 0.35  # gaze smoothing on the server side (browser smooths again)

# Shared state between the tracking thread and the asyncio broadcaster.
latest = {"nx": 0.5, "ny": 0.5, "blink": False}
clients: set = set()


def screen_size():
    """Best-effort screen resolution; EyeTrax calibrates across the full screen."""
    try:
        import tkinter as tk
        root = tk.Tk()
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        root.destroy()
        return w, h
    except Exception:
        return 1920, 1080


def tracking_loop():
    screen_w, screen_h = screen_size()
    estimator = GazeEstimator()

    print("Starting 9-point calibration - look at each dot...")
    run_9_point_calibration(estimator)
    print(f"Calibration done. Streaming gaze (screen {screen_w}x{screen_h}).")

    cap = cv2.VideoCapture(0)
    sx, sy = 0.5, 0.5
    while True:
        ok, frame = cap.read()
        if not ok:
            continue
        features, blink = estimator.extract_features(frame)
        if features is not None and not blink:
            x, y = estimator.predict([features])[0]
            nx = min(max(x / screen_w, 0.0), 1.0)
            ny = min(max(y / screen_h, 0.0), 1.0)
            sx = EMA * nx + (1 - EMA) * sx
            sy = EMA * ny + (1 - EMA) * sy
            latest.update(nx=sx, ny=sy, blink=False)
        else:
            latest["blink"] = bool(blink)


async def broadcaster():
    while True:
        if clients:
            msg = json.dumps(latest)
            await asyncio.gather(*[c.send(msg) for c in list(clients)],
                                 return_exceptions=True)
        await asyncio.sleep(1 / 30)


async def handler(ws):
    clients.add(ws)
    try:
        await ws.wait_closed()
    finally:
        clients.discard(ws)


async def main():
    threading.Thread(target=tracking_loop, daemon=True).start()
    async with websockets.serve(handler, HOST, PORT):
        print(f"WebSocket gaze server on ws://{HOST}:{PORT}")
        await broadcaster()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
