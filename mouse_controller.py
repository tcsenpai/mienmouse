import pyautogui
import numpy as np
from screeninfo import get_monitors
import time
import winsound

class MouseController:
    def __init__(self, config_manager):
        # Get primary monitor resolution
        self.monitors = get_monitors()
        self.primary_monitor = self.monitors[0]
        self.screen_width = self.primary_monitor.width
        self.screen_height = self.primary_monitor.height
        
        # Configure PyAutoGUI
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.0
        
        # Get config values
        self.velocity_scale = config_manager.config["mouse"]["velocity_scale"]
        self.max_velocity = config_manager.config["mouse"]["max_velocity"]
        self.deadzone = config_manager.config["mouse"]["deadzone"]
        self.click_cooldown = config_manager.config["mouse"]["click_cooldown"]
        
        # Get thresholds
        self.MOUTH_OPEN_THRESHOLD = config_manager.config["thresholds"]["mouth_open"]
        self.EYEBROW_RAISE_THRESHOLD = config_manager.config["thresholds"]["eyebrow_raise"]
        self.EYE_CLOSED_THRESHOLD = config_manager.config["thresholds"]["eye_closed"]
        self.NOSE_MOVEMENT_THRESHOLD = config_manager.config["thresholds"]["nose_movement"]
        
        # Smoothing
        self.velocity_buffer = [(0, 0)] * 5
        self.smoothing = config_manager.config["smoothing"]
        
        # Gesture state tracking
        self.is_left_clicking = False
        self.is_right_clicking = False
        self.is_dragging = False
        self.tracking_enabled = True
        self.last_click_time = 0
        
        # Mode settings
        self.precision_mode = False
        self.audio_feedback = True
        
        # Screen mapping
        self.x_scale = 2.0
        self.y_scale = 2.0
        
    def update_mouse(self, results):
        if not self.tracking_enabled or not results.multi_face_landmarks:
            return
            
        landmarks = results.multi_face_landmarks[0].landmark
        current_time = time.time()
        
        # Get key facial features for tracking
        left_eye = landmarks[33]    # Left eye outer corner
        right_eye = landmarks[263]  # Right eye outer corner
        nose_bridge = landmarks[6]  # Nose bridge
        
        # Calculate head pose
        face_center_x = (left_eye.x + right_eye.x) / 2
        face_center_y = (left_eye.y + right_eye.y + nose_bridge.y) / 3
        
        # Calculate offset from center (0.5, 0.5)
        offset_x = face_center_x - 0.5
        offset_y = face_center_y - 0.5
        
        # Apply deadzone
        offset_x = 0 if abs(offset_x) < self.deadzone else offset_x
        offset_y = 0 if abs(offset_y) < self.deadzone else offset_y
        
        # Convert offset to velocity
        velocity_x = offset_x * self.velocity_scale
        velocity_y = offset_y * self.velocity_scale
        
        # Clamp velocity
        velocity_x = max(min(velocity_x, self.max_velocity), -self.max_velocity)
        velocity_y = max(min(velocity_y, self.max_velocity), -self.max_velocity)
        
        # Update velocity buffer
        self.velocity_buffer.pop(0)
        self.velocity_buffer.append((velocity_x, velocity_y))
        
        # Calculate smoothed velocity
        smooth_vx = sum(v[0] for v in self.velocity_buffer) / len(self.velocity_buffer)
        smooth_vy = sum(v[1] for v in self.velocity_buffer) / len(self.velocity_buffer)
        
        # Get current mouse position
        current_x, current_y = pyautogui.position()
        
        # Update position
        new_x = current_x + smooth_vx
        new_y = current_y + smooth_vy
        
        # Ensure within screen bounds
        new_x = max(0, min(new_x, self.screen_width - 1))
        new_y = max(0, min(new_y, self.screen_height - 1))
        
        # Move mouse if there's significant movement
        if abs(smooth_vx) > 0 or abs(smooth_vy) > 0:
            pyautogui.moveTo(int(new_x), int(new_y))
        
        # Handle gestures (keep your existing gesture code)
        upper_lip = landmarks[13]
        lower_lip = landmarks[14]
        left_eyebrow = landmarks[282]
        right_eyebrow = landmarks[52]
        left_eye_top = landmarks[386]
        left_eye_bottom = landmarks[374]
        right_eye_top = landmarks[159]
        right_eye_bottom = landmarks[145]
        
        # Calculate gestures
        mouth_open = (lower_lip.y - upper_lip.y) > self.MOUTH_OPEN_THRESHOLD
        left_eye_open = abs(left_eye_top.y - left_eye_bottom.y)
        right_eye_open = abs(right_eye_top.y - right_eye_bottom.y)
        eyes_closed = (left_eye_open < self.EYE_CLOSED_THRESHOLD or 
                      right_eye_open < self.EYE_CLOSED_THRESHOLD)
        
        eyebrows_raised = False
        if not eyes_closed:
            eyebrows_raised = (
                (left_eye_top.y - left_eyebrow.y) > self.EYEBROW_RAISE_THRESHOLD and
                (right_eye_top.y - right_eyebrow.y) > self.EYEBROW_RAISE_THRESHOLD
            )
        
        self._handle_gestures(mouth_open, eyebrows_raised, current_time)
        
    def _handle_gestures(self, mouth_open, eyebrows_raised, current_time):
        # Double click (both gestures)
        if mouth_open and eyebrows_raised:
            if current_time - self.last_click_time > self.click_cooldown:
                pyautogui.doubleClick()
                if self.audio_feedback:
                    winsound.Beep(900, 100)
                self.last_click_time = current_time
            return
            
        # Left click/drag (mouth open)
        if mouth_open and not self.is_left_clicking:
            self.is_left_clicking = True
            pyautogui.mouseDown()
            if self.audio_feedback:
                winsound.Beep(800, 100)
            self.is_dragging = True
            
        # Right click (eyebrows)
        elif eyebrows_raised and not mouth_open:
            if not self.is_right_clicking and current_time - self.last_click_time > self.click_cooldown:
                pyautogui.rightClick()
                if self.audio_feedback:
                    winsound.Beep(1200, 100)
                self.is_right_clicking = True
                self.last_click_time = current_time
                
        # Release
        elif not mouth_open and not eyebrows_raised:
            if self.is_left_clicking:
                pyautogui.mouseUp()
                self.is_dragging = False
                self.is_left_clicking = False
            self.is_right_clicking = False

    def _significant_movement(self, x, y):
        """Check if movement is significant enough"""
        if not hasattr(self, 'last_pos'):
            self.last_pos = (x, y)
            return False
            
        dx = abs(x - self.last_pos[0])
        dy = abs(y - self.last_pos[1])
        
        if dx > self.NOSE_MOVEMENT_THRESHOLD or dy > self.NOSE_MOVEMENT_THRESHOLD:
            self.last_pos = (x, y)
            return True
        return False
        
    def recenter(self):
        """Recenter the neutral position for head tracking"""
        self.center_x = 0.5
        self.center_y = 0.5
        self.current_x = self.screen_width // 2
        self.current_y = self.screen_height // 2
        self.movement_buffer = []  # Clear movement buffer
        
        # Reset mouse to center of screen
        pyautogui.moveTo(self.current_x, self.current_y)