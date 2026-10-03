import time

import cv2
import numpy as np
from flask import Flask, Response, jsonify, render_template

app = Flask(__name__)

VALID_MODES = ("thermal", "night_vision", "normal")
current_mode = "thermal"
isolate_subject = True

camera = None
clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)
morph_kernel = np.ones((5, 5), np.uint8)


def get_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
    return camera


def adjust_gamma(image, gamma=2.0):
    inv_gamma = 1.0 / gamma
    table = np.array(
        [((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]
    ).astype("uint8")
    return cv2.LUT(image, table)


def render_thermal(frame):
    brightened = adjust_gamma(frame, gamma=2.0)
    ycrcb = cv2.cvtColor(brightened, cv2.COLOR_BGR2YCrCb)
    y, _, _ = cv2.split(ycrcb)
    enhanced_y = clahe.apply(y)
    denoised_y = cv2.bilateralFilter(enhanced_y, d=5, sigmaColor=50, sigmaSpace=50)
    inverted_y = cv2.bitwise_not(denoised_y)
    return cv2.applyColorMap(inverted_y, cv2.COLORMAP_JET)


def render_night_vision(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    enhanced = clahe.apply(gray)
    output_frame = np.zeros_like(frame)
    output_frame[:, :, 1] = enhanced
    return output_frame


def update_subject_mask(frame):
    raw_mask = bg_subtractor.apply(frame)
    _, clean_mask = cv2.threshold(raw_mask, 200, 255, cv2.THRESH_BINARY)
    clean_mask = cv2.morphologyEx(clean_mask, cv2.MORPH_OPEN, morph_kernel)
    clean_mask = cv2.morphologyEx(clean_mask, cv2.MORPH_DILATE, morph_kernel, iterations=2)
    return clean_mask


def render_frame(frame, mode):
    if mode == "thermal":
        return render_thermal(frame)
    if mode == "night_vision":
        return render_night_vision(frame)
    return frame


def generate_frames():
    global current_mode
    consecutive_failures = 0

    while True:
        cam = get_camera()
        success, frame = cam.read()

        if not success:
            consecutive_failures += 1
            if consecutive_failures > 30:
                camera_release()
                time.sleep(0.5)
                consecutive_failures = 0
            continue

        consecutive_failures = 0
        frame = cv2.flip(frame, 1)

        subject_mask = update_subject_mask(frame)

        try:
            output_frame = render_frame(frame, current_mode)
        except cv2.error:
            output_frame = frame

        if isolate_subject:
            mask_3ch = cv2.cvtColor(subject_mask, cv2.COLOR_GRAY2BGR)
            output_frame = cv2.bitwise_and(output_frame, mask_3ch)

        ok, buffer = cv2.imencode(".jpg", output_frame)
        if not ok:
            continue

        frame_bytes = buffer.tobytes()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


def camera_release():
    global camera
    if camera is not None:
        camera.release()
        camera = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/set_mode/<mode>")
def set_mode(mode):
    global current_mode
    if mode not in VALID_MODES:
        return jsonify(status="error", message="unknown mode", mode=current_mode), 400
    current_mode = mode
    return jsonify(status="success", mode=current_mode)


@app.route("/set_isolate/<state>")
def set_isolate(state):
    global isolate_subject
    if state not in ("on", "off"):
        return jsonify(status="error", message="use on or off", isolate=isolate_subject), 400
    isolate_subject = state == "on"
    return jsonify(status="success", isolate=isolate_subject)


@app.route("/status")
def status():
    cam = get_camera()
    return jsonify(
        mode=current_mode,
        camera_connected=cam.isOpened(),
        sensor="simulated (standard RGB webcam)",
        isolate_subject=isolate_subject,
    )


@app.teardown_appcontext
def cleanup(exception=None):
    pass


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    finally:
        camera_release()