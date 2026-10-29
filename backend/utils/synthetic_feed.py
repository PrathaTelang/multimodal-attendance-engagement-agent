"""
Synthetic Classroom Video and Audio Stream Generator.
Provides realistic simulated classroom feeds with animated faces,
movement, head poses, and attention shifts for offline testing,
evaluations, and environments where physical webcams are unavailable.
"""

import cv2
import numpy as np
import time
import math


class SyntheticClassroomGenerator:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.start_time = time.time()
        
        # Simulated students in the classroom
        self.students = [
            {
                "id": 1,
                "name": "Priya Sharma",
                "base_x": 180,
                "base_y": 240,
                "color": (230, 200, 180),
                "shirt_color": (180, 80, 60),
                "focus_profile": "attentive"
            },
            {
                "id": 2,
                "name": "Kumar Patel",
                "base_x": 460,
                "base_y": 240,
                "color": (210, 185, 170),
                "shirt_color": (40, 120, 200),
                "focus_profile": "variable"
            }
        ]

    def generate_frame(self):
        """
        Renders a simulated classroom frame with students listening to lecture.
        Simulates natural blinking, head tilting, slight movements, and periodic distraction.
        """
        now = time.time()
        t = now - self.start_time
        
        # Classroom background (dark stylish classroom interior matching EduSense)
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Gradient background
        for y in range(self.height):
            v = int(25 + 15 * (y / self.height))
            frame[y, :] = [v, v + 5, v + 10]

        # Draw classroom chalkboard / screen in background
        cv2.rectangle(frame, (80, 40), (560, 180), (45, 50, 48), -1)
        cv2.rectangle(frame, (78, 38), (562, 182), (100, 110, 105), 2)
        cv2.putText(frame, "CS101: Multimodal AI & Learning Systems", (100, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Lecture Time: {int(t // 60):02d}:{int(t % 60):02d}", (100, 115),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 210, 180), 1, cv2.LINE_AA)
        
        # Draw desks
        cv2.rectangle(frame, (40, 340), (600, 470), (40, 35, 30), -1)
        cv2.line(frame, (40, 340), (600, 340), (70, 65, 60), 2)

        for s in self.students:
            bx, by = s["base_x"], s["base_y"]
            profile = s["focus_profile"]

            # Movement dynamics
            if profile == "attentive":
                # Slight natural breathing and small head movements
                dx = int(4 * math.sin(t * 1.2))
                dy = int(3 * math.cos(t * 0.9))
                head_angle = 2 * math.sin(t * 0.5)
            else:
                # Variable focus: sometimes turns away or looks down
                distracted = int(t // 8) % 3 == 0
                if distracted:
                    dx = int(18 * math.sin(t * 0.8))
                    dy = int(12 * math.cos(t * 0.5))
                    head_angle = 15
                else:
                    dx = int(5 * math.sin(t * 1.5))
                    dy = int(4 * math.cos(t * 1.1))
                    head_angle = -3

            cx = bx + dx
            cy = by + dy

            # Body / Torso
            cv2.ellipse(frame, (cx, cy + 90), (70, 50), 0, 0, 360, s["shirt_color"], -1)
            cv2.ellipse(frame, (cx, cy + 90), (70, 50), 0, 0, 360, (30, 30, 30), 2)

            # Neck
            cv2.rectangle(frame, (cx - 15, cy + 30), (cx + 15, cy + 60), s["color"], -1)

            # Face oval (simulates realistic skin tone and face proportions)
            cv2.ellipse(frame, (cx, cy), (42, 52), int(head_angle), 0, 360, s["color"], -1)
            cv2.ellipse(frame, (cx, cy), (42, 52), int(head_angle), 0, 360, (50, 40, 35), 2)

            # Hair
            cv2.ellipse(frame, (cx, cy - 25), (44, 28), int(head_angle), 180, 360, (20, 15, 10), -1)

            # Eyes (blinking simulation)
            blink = (int(t * 3) % 15 == 0)
            eye_offset_x = int(math.cos(math.radians(head_angle)) * 16)
            eye_offset_y = -6

            if not blink:
                # Left eye
                cv2.circle(frame, (cx - eye_offset_x, cy + eye_offset_y), 4, (40, 30, 20), -1)
                cv2.circle(frame, (cx - eye_offset_x, cy + eye_offset_y), 2, (250, 250, 250), -1)
                # Right eye
                cv2.circle(frame, (cx + eye_offset_x, cy + eye_offset_y), 4, (40, 30, 20), -1)
                cv2.circle(frame, (cx + eye_offset_x, cy + eye_offset_y), 2, (250, 250, 250), -1)
            else:
                # Blinking line
                cv2.line(frame, (cx - eye_offset_x - 4, cy + eye_offset_y), (cx - eye_offset_x + 4, cy + eye_offset_y), (30, 20, 15), 2)
                cv2.line(frame, (cx + eye_offset_x - 4, cy + eye_offset_y), (cx + eye_offset_x + 4, cy + eye_offset_y), (30, 20, 15), 2)

            # Nose
            cv2.line(frame, (cx, cy), (cx, cy + 8), (140, 110, 95), 2)

            # Mouth (smile or neutral)
            cv2.ellipse(frame, (cx, cy + 22), (12, 6), int(head_angle), 0, 180, (130, 70, 70), 2)

            # Name watermark
            cv2.putText(frame, s["name"], (cx - 40, cy + 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)

        return frame
