
# Vision Relay

A small Flask + OpenCV app that streams your webcam through three rendering modes — a false-color "thermal" simulation, a green-channel night-vision look, and a normal passthrough.

**No thermal or infrared sensor is used.** Every effect here is computed in software from an ordinary RGB webcam. The "thermal" mode is a visual simulation (contrast enhancement + a JET colormap) meant to *look* like a thermal camera, not to measure real temperature.

## How it works

| Mode               | Technique                                                                                               |
| ------------------ | ------------------------------------------------------------------------------------------------------- |
| Thermal simulation | Gamma correction → CLAHE contrast boost on luminance → bilateral denoise → invert →`COLORMAP_JET` |
| Night vision       | Grayscale → CLAHE contrast boost → mapped onto the green channel only                                 |
| Normal             | Unprocessed camera frame                                                                                |

The backend exposes the processed feed as an MJPEG stream; the frontend is a single dashboard page with live mode switching.

### Isolating the subject from the background

By default, the effect is only rendered on whatever is moving in frame — the still background stays dark, closer to how a real thermal camera makes a warm body stand out against a cooler room. This is done with `cv2.createBackgroundSubtractorMOG2`: it learns what the static background looks like over the first second or two, then flags anything that differs from it (after cleaning up the mask with thresholding and morphological open/dilate) as foreground, and only that region gets the colormap — everything else is masked to black.

This is motion-based background subtraction, not person detection — it doesn't know what a person looks like, it just knows what's new. That means:

- It works best if the room is still for a moment when the stream starts, so it can learn the background.
- Anything that moves (a hand, a pet, a passing shadow) will also show up, not just you.
- If you stand completely still for a long time, you can gradually blend into the learned background and partially disappear — move around occasionally to stay "visible."

This can be toggled off from the dashboard (**Background** panel) to go back to rendering the effect over the whole frame.

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
