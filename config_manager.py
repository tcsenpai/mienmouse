import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "webcam_index": 0,
            "smoothing": 0.5,
            "thresholds": {
                "mouth_open": 0.017,
                "eyebrow_raise": 0.023,
                "eye_closed": 0.02,
                "nose_movement": 0.015
            },
            "mouse": {
                "velocity_scale": 55.0,
                "max_velocity": 110,
                "deadzone": 0.07,
                "click_cooldown": 0.3
            }
        }
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.default_config.copy()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)