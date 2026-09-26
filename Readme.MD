# Vision Relay

A small Flask + OpenCV app that streams your webcam through three rendering modes — a false-color "thermal" simulation, a green-channel night-vision look, and a normal passthrough.

**No thermal or infrared sensor is used.** Every effect here is computed in software from an ordinary RGB webcam. The "thermal" mode is a visual simulation (contrast enhancement + a JET colormap) meant to *look* like a thermal camera, not to measure real temperature.

## How it works

| Mode | Technique |
|---|---|
| Thermal simulation | Gamma correction → CLAHE contrast boost on luminance → bilateral denoise → invert → `COLORMAP_JET` |
| Night vision | Grayscale → CLAHE contrast boost → mapped onto the green channel only |
| Normal | Unprocessed camera frame |

The backend exposes the processed feed as an MJPEG stream; the frontend is a single dashboard page with live mode switching.

## Project structure

```
vision-relay/
├── app.py
├── templates/
│   └── index.html
└── README.md
```

## Requirements

- Python 3.8+
- A connected webcam
- `pip install flask opencv-python numpy`

## Running it

```bash
python app.py
```

Then open `http://localhost:5000` in a browser. Use the buttons in the **Rendering mode** panel to switch between thermal simulation, night vision, and normal view.

## Notes on the bug fixes from the original version

- The frame generator used to permanently end the video stream after a single failed camera read (`break`). It now skips bad reads and only reopens the camera after a run of consistent failures.
- The camera is now lazily opened/reopened through `get_camera()` instead of being grabbed once at import time, so a disconnected camera can recover without restarting the server.
- `imencode` failures are now handled instead of assumed to always succeed.
- `/set_mode/<mode>` now returns a proper error status for an invalid mode instead of silently ignoring it.
- Added a `/status` endpoint reporting the active mode and whether the camera is currently connected.
- The Flask server now runs with `threaded=True` so the page and the video stream can be served at the same time, and the camera is released on shutdown.

## Limitations

- Single shared mode: all viewers of the page see the same mode, since there's one global camera state (fine for a personal/demo setup, not for multiple simultaneous users who want independent views).
- Thermal and night-vision effects are purely aesthetic approximations — don't rely on this for anything safety- or measurement-related.