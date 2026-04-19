"""Vision Engine using MediaPipe Tasks API for the Eye Monitor application."""
# pylint: disable=no-member

import time
import threading

import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from utils import calculate_ear, LEFT_EYE_INDICES, RIGHT_EYE_INDICES

class VisionEngine:
    """Computer vision pipeline for detecting eyes and triggering alerts."""

    def __init__(
        self,
        update_ui_callback,
        alert_callback,
        alert_stop_callback,
        alert_threshold=60.0,
        ear_threshold=0.2
    ):
        self.update_ui_callback = update_ui_callback
        self.alert_callback = alert_callback
        self.alert_stop_callback = alert_stop_callback
        self.alert_threshold = alert_threshold
        self.ear_threshold = ear_threshold

        self.running = False
        self.cap = None
        self.thread = None

        base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)

        self.eyes_closed_start_time = None
        self.closed_duration = 0.0
        self.alert_triggered = False

    def _equalize_histogram_color(self, frame):
        """Applies histogram equalization to the Y channel for low-light mode."""
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        channels = list(cv2.split(ycrcb))
        channels[0] = cv2.equalizeHist(channels[0])
        ycrcb = cv2.merge(channels)
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    def _get_landmark_point(self, landmark, w, h):
        """Converts normalized landmarks to pixel coordinates."""
        return (int(landmark.x * w), int(landmark.y * h))

    def start(self):
        """Starts the vision pipeline in a background thread."""
        if not self.running:
            self.running = True
            self.cap = cv2.VideoCapture(0)
            self.eyes_closed_start_time = None
            self.closed_duration = 0.0
            self.alert_triggered = False
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

    def stop(self):
        """Stops the vision pipeline and releases the camera."""
        self.running = False
        if self.alert_triggered:
            self.alert_stop_callback()
            self.alert_triggered = False
        if self.thread is not None:
            self.thread.join()
        if self.cap is not None:
            self.cap.release()

    def _run_loop(self):
        """Main active loop for fetching frames and computing EAR."""
        face_centers = []

        while self.running:
            if self.cap is None:
                break

            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            enhanced_frame = self._equalize_histogram_color(frame)
            rgb_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            detection_result = self.detector.detect(mp_image)

            ear = 0.0
            face_detected = False
            is_static_photo = False

            if detection_result.face_landmarks:
                face_detected = True
                landmarks = detection_result.face_landmarks[0]

                cx = sum([l.x for l in landmarks]) / len(landmarks)
                cy = sum([l.y for l in landmarks]) / len(landmarks)
                face_centers.append((cx, cy))
                if len(face_centers) > 30:
                    face_centers.pop(0)

                if len(face_centers) == 30:
                    var_x = np.var([c[0] for c in face_centers])
                    var_y = np.var([c[1] for c in face_centers])
                    if var_x < 1e-6 and var_y < 1e-6:
                        is_static_photo = True

                if not is_static_photo:
                    left_eye = [
                        self._get_landmark_point(landmarks[i], w, h)
                        for i in LEFT_EYE_INDICES
                    ]
                    right_eye = [
                        self._get_landmark_point(landmarks[i], w, h)
                        for i in RIGHT_EYE_INDICES
                    ]

                    left_ear = calculate_ear(left_eye)
                    right_ear = calculate_ear(right_eye)
                    ear = (left_ear + right_ear) / 2.0

                    for point in left_eye + right_eye:
                        cv2.circle(frame, point, 1, (0, 255, 0), -1)

                    if ear < self.ear_threshold:
                        if self.eyes_closed_start_time is None:
                            self.eyes_closed_start_time = time.time()
                        self.closed_duration = time.time() - self.eyes_closed_start_time

                        if self.closed_duration >= self.alert_threshold:
                            if not self.alert_triggered:
                                self.alert_callback(self.closed_duration)
                                self.alert_triggered = True
                    else:
                        if self.alert_triggered:
                            self.alert_stop_callback()
                        self.eyes_closed_start_time = None
                        self.closed_duration = 0.0
                        self.alert_triggered = False
                else:
                    if self.alert_triggered:
                        self.alert_stop_callback()
                    cv2.putText(
                        frame,
                        "STATIC PHOTO DETECTED",
                        (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2
                    )
                    self.eyes_closed_start_time = None
                    self.closed_duration = 0.0
                    self.alert_triggered = False
            else:
                if self.alert_triggered:
                    self.alert_stop_callback()
                self.eyes_closed_start_time = None
                self.closed_duration = 0.0
                self.alert_triggered = False

            ui_stats = {
                'ear': ear,
                'closed_duration': self.closed_duration,
                'face_detected': face_detected,
                'is_static_photo': is_static_photo
            }
            self.update_ui_callback(frame, ui_stats)
            time.sleep(0.03)
