import os
import json
import hashlib

APPDATA_DIR = os.path.join(os.getenv('APPDATA'), 'ScreenshotUploader')
CONFIG_FILE = os.path.join(APPDATA_DIR, 'config.json')

class Config:
    def __init__(self):
        os.makedirs(APPDATA_DIR, exist_ok=True)
        self.data = self.load()
    
    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def save(self, config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        self.data = config
    
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()