"""
Activity 2.1: Camera Service for Video Input.
Supports webcam capture (OpenCV VideoCapture), recorded video files,
or high-fidelity synthetic classroom stream fallback.
"""

import cv2
import time
import threading
import numpy as np
from .face_detection import FaceDetector, CentroidTracker
from ..utils.synthetic_feed import SyntheticClassroomGenerator


class CameraService:
    def __init__(self, camera_id=0, video_path=None, use_synthetic=False):
        self.camera_id = camera_id
        self.video_path = video_path
        self.use_synthetic = use_synthetic
        
        self.cap = None
        self.is_running = False
        self.detector = FaceDetector()
        self.tracker = CentroidTracker(max_disappeared=25, max_distance=120)
        self.synthetic_gen = SyntheticClassroomGenerator()
        
        self._lock = threading.Lock()
        self.current_raw_frame = None
        self.current_annotated_frame = None
        self.latest_tracks = {}
        self.last_frame_time = time.time()
        self._worker_thread = None

    def start(self):
        """Starts video source stream and background processing loop."""
        with self._lock:
            if self.is_running:
                return

            if not self.use_synthetic:
                target = self.video_path if self.video_path else self.camera_id
                self.cap = cv2.VideoCapture(target)
                if not self.cap.isOpened():
                    print(f"[CameraService] Unable to open capture source {target}. Falling back to Synthetic Classroom.")
                    self.use_synthetic = True
                    self.cap = None

            self.is_running = True
            self.last_frame_time = time.time()
            self._worker_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._worker_thread.start()
            print("[CameraService] Stream started successfully.")

    def stop(self):
        """Stops video stream and releases resources."""
        self.is_running = False
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)
            
        with self._lock:
            if self.cap:
                self.cap.release()
                self.cap = None
            self.current_raw_frame = None
            self.current_annotated_frame = None
            print("[CameraService] Stream stopped.")

    def _capture_loop(self):
        while self.is_running:
            now = time.time()
            dt = max(now - self.last_frame_time, 0.01)
            self.last_frame_time = now

            frame = None
            if self.use_synthetic:
                frame = self.synthetic_gen.generate_frame()
                time.sleep(0.04)  # ~25 fps
            elif self.cap and self.cap.isOpened():
                ret, captured = self.cap.read()
                if ret:
                    frame = captured
                else:
                    # Loop video if end of file reached
                    if self.video_path:
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret2, captured2 = self.cap.read()
                        if ret2:
                            frame = captured2
                    else:
                        time.sleep(0.05)

            if frame is not None:
                # Resize to standard analysis resolution
                frame_resized = cv2.resize(frame, (640, 480))
                
                # Detect and track
                detections = self.detector.process_frame(frame_resized)
                tracks = self.tracker.update(detections, dt=dt)
                
                annotated = self._draw_annotations(frame_resized.copy(), tracks)

                with self._lock:
                    self.current_raw_frame = frame_resized
                    self.current_annotated_frame = annotated
                    self.latest_tracks = tracks

    def _draw_annotations(self, frame, tracks):
        """
        Draws green bounding boxes, participant labels, and attention tags
        matching UI design (Page 39: '[1] 85% focused', '[2] 91% engaged').
        """
        for obj_id, track in tracks.items():
            x, y, w, h = track['bbox']
            pose = track.get('head_pose', 'forward')
            attn = int(track.get('attention_cue', 0.8) * 100)
            
            # Status tag
            if attn >= 80:
                tag = f"[{obj_id}] {attn}% focused"
                box_color = (60, 220, 100)  # Bright Green
            elif attn >= 55:
                tag = f"[{obj_id}] {attn}% engaged"
                box_color = (0, 200, 230)  # Teal / Cyan
            else:
                tag = f"[{obj_id}] {attn}% distracted"
                box_color = (60, 80, 240)  # Coral / Red

            # Bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
            
            # Label banner
            (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(frame, (x, max(0, y - th - 8)), (x + tw + 10, y), box_color, -1)
            cv2.putText(frame, tag, (x + 5, y - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)

        # Header HUD
        cv2.putText(frame, f"Active Tracks: {len(tracks)}", (15, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 180), 2, cv2.LINE_AA)
        return frame

    def get_frame(self):
        """Returns raw camera frame (BGR numpy array)."""
        with self._lock:
            return self.current_raw_frame.copy() if self.current_raw_frame is not None else None

    def get_annotated_frame(self):
        """Returns annotated camera frame (BGR numpy array)."""
        with self._lock:
            return self.current_annotated_frame.copy() if self.current_annotated_frame is not None else None

    def get_jpeg_bytes(self):
        """Encodes annotated frame as JPEG bytes for HTTP multipart streaming."""
        with self._lock:
            if self.current_annotated_frame is None:
                # Return placeholder frame if warming up
                blank = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(blank, "Connecting Video Feed...", (180, 240),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
                _, buffer = cv2.imencode('.jpg', blank)
                return buffer.tobytes()

            _, buffer = cv2.imencode('.jpg', self.current_annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            return buffer.tobytes()

    def get_latest_tracks(self):
        """Returns snapshot of current tracked participant states."""
        with self._lock:
            return dict(self.latest_tracks)
