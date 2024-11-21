import cv2
import mediapipe as mp
import numpy as np
from mouse_controller import MouseController
from config_manager import ConfigManager
import time

class FaceTracker:
    def __init__(self, config_manager):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_draw.DrawingSpec(thickness=1, circle_radius=1)
        
        self.mouse_controller = MouseController(config_manager)
        
        # UI state
        self.show_controls = True
        self.show_confidence = True
        self.show_prediction = True
        self.last_fps_time = time.time()
        self.frame_count = 0
        self.fps = 0
        
    def process_frame(self, frame):
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_time > 1:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
            
        frame = self._enhance_frame(frame)
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        
        self._draw_ui(frame, results)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            # Draw minimal face mesh for feedback
            self._draw_tracking_points(frame, face_landmarks)
            
            # Process mouse control
            self.mouse_controller.update_mouse(results)
            
            # Show gesture feedback
            self._draw_gesture_feedback(frame)
                
        return frame
        
    def _enhance_frame(self, frame):
        """Apply image processing to improve face detection"""
        # Convert to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        
        # Merge channels
        limg = cv2.merge((cl,a,b))
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        return enhanced
        
    def _draw_ui(self, frame, results):
        height, width = frame.shape[:2]
        
        # Draw FPS
        cv2.putText(frame, f"FPS: {self.fps}", (width-120, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw confidence if face detected
        if self.show_confidence and results.multi_face_landmarks:
            cv2.putText(frame, "Face Detected", (width-200, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Draw mode indicators
        self._draw_mode_indicators(frame)
        
        # Draw controls if enabled
        if self.show_controls:
            self._draw_controls(frame)
            
    def _draw_mode_indicators(self, frame):
        modes = [
            ("Precision Mode", self.mouse_controller.precision_mode),
            ("Audio Feedback", self.mouse_controller.audio_feedback),
            ("Tracking", self.mouse_controller.tracking_enabled)
        ]
        
        for i, (mode, active) in enumerate(modes):
            color = (0, 255, 0) if active else (128, 128, 128)
            cv2.putText(frame, f"{mode}: {'ON' if active else 'OFF'}", 
                       (10, 30 + i*25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                       
    def _draw_tracking_points(self, frame, face_landmarks):
        """Draw facial tracking points"""
        h, w = frame.shape[:2]
        
        # Key points to track
        points = {
            'nose': 4,
            'upper_lip': 13,
            'lower_lip': 14,
            'left_eyebrow': 282,
            'right_eyebrow': 52,
            'left_eye': 386,
            'right_eye': 159
        }
        
        # Draw points
        for name, idx in points.items():
            point = face_landmarks.landmark[idx]
            x = int(point.x * w)
            y = int(point.y * h)
            
            # Different colors for different features
            if 'nose' in name:
                color = (0, 255, 255)  # Yellow
                size = 5
            elif 'lip' in name:
                color = (0, 0, 255)    # Red
                size = 3
            else:
                color = (0, 255, 0)    # Green
                size = 3
                
            cv2.circle(frame, (x, y), size, color, -1)
            
        # Draw mouth and eyebrow lines
        self._draw_feature_lines(frame, face_landmarks, points, w, h)
        
    def _draw_feature_lines(self, frame, face_landmarks, points, w, h):
        # Draw mouth line
        upper_lip = face_landmarks.landmark[points['upper_lip']]
        lower_lip = face_landmarks.landmark[points['lower_lip']]
        cv2.line(frame, 
                 (int(upper_lip.x * w), int(upper_lip.y * h)),
                 (int(lower_lip.x * w), int(lower_lip.y * h)),
                 (0, 0, 255), 2)
        
        # Draw eyebrow lines
        for side in ['left', 'right']:
            eyebrow = face_landmarks.landmark[points[f'{side}_eyebrow']]
            eye = face_landmarks.landmark[points[f'{side}_eye']]
            cv2.line(frame,
                    (int(eyebrow.x * w), int(eyebrow.y * h)),
                    (int(eye.x * w), int(eye.y * h)),
                    (0, 255, 0), 2)
        
    def _draw_gesture_feedback(self, frame):
        height = frame.shape[0]
        
        if self.mouse_controller.is_left_clicking:
            status = "Dragging" if self.mouse_controller.is_dragging else "Left Click"
            cv2.putText(frame, status, (10, height-160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        if self.mouse_controller.is_right_clicking:
            cv2.putText(frame, "Right Click", (10, height-120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                       
    def _draw_controls(self, frame):
        height = frame.shape[0]
        controls = [
            "Controls:",
            "Move: Move head from center position",
            "Left click: Open mouth",
            "Right click: Raise eyebrows",
            "Double click: Open mouth + raise eyebrows",
            "Drag: Keep mouth open while moving",
            "'R': Recenter head position",
            "'P': Toggle precision mode",
            "'A': Toggle audio feedback",
            "'T': Toggle tracking",
            "'H': Hide/show controls",
            "ESC: Quit"
        ]
        
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, height-240), (400, height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        # Draw controls text
        for i, text in enumerate(controls):
            cv2.putText(frame, text, (10, height-220+i*20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def main():
    config_manager = ConfigManager()
    
    # Initialize camera with saved index
    cap = cv2.VideoCapture(config_manager.config["webcam_index"])
    if not cap.isOpened():
        print(f"Error: Could not open camera {config_manager.config['webcam_index']}")
        return

    tracker = FaceTracker(config_manager)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
            
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Process the frame
        frame = tracker.process_frame(frame)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('p'):
            tracker.mouse_controller.precision_mode = not tracker.mouse_controller.precision_mode
        elif key == ord('a'):
            tracker.mouse_controller.audio_feedback = not tracker.mouse_controller.audio_feedback
        elif key == ord('t'):
            tracker.mouse_controller.tracking_enabled = not tracker.mouse_controller.tracking_enabled
        elif key == ord('r'):
            tracker.mouse_controller.recenter()
        elif key == ord('h'):
            tracker.show_controls = not tracker.show_controls
            
        cv2.imshow('Face Tracking', frame)
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()