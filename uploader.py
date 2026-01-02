import time
import requests
import hashlib
import socket
import threading
import gc
from PIL import ImageGrab, Image, ImageDraw
from datetime import datetime
import io
from plyer import notification
from config import Config

class ScreenshotUploader:
    def __init__(self):
        self.config_manager = Config()
        self.config = self.config_manager.data
        self.token = None
        self.is_running = False
        self.last_image_hash = None
        self.icon = None
        self.network_status = True
        self.session = None
    
    def get_image_hash(self, image):
        return hashlib.md5(image.tobytes()).hexdigest()
    
    def check_network(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def notify(self, title, message):
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Screenshot Uploader",
                timeout=3
            )
        except:
            pass
    
    def get_session(self):
        if not self.session:
            self.session = requests.Session()
        return self.session
    
    def login(self):
        try:
            url = f"{self.config['protocol']}://{self.config['domain']}:{self.config['port']}/v1/api/login"
            response = self.get_session().post(url, json={
                "username": self.config['username'],
                "password": self.config['password']
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('token')
                    return True
            return False
        except:
            return False
    
    def upload_screenshot(self, image):
        if not self.token:
            if not self.login():
                self.notify("Upload Failed", "Authentication failed")
                return None
        
        try:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG', optimize=True)
            img_byte_arr.seek(0)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            url = f"{self.config['protocol']}://{self.config['domain']}:{self.config['port']}/v1/api/upload"
            
            files = {'file': (filename, img_byte_arr, 'image/png')}
            data = {'is_private': 'true'}
            headers = {'Authorization': f'Bearer {self.token}'}
            
            response = self.get_session().post(url, files=files, data=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    download_url = result.get('download_url')
                    full_url = f"{self.config['protocol']}://{self.config['domain']}:{self.config['port']}/{download_url}"
                    return full_url
            elif response.status_code == 401:
                self.token = None
                if self.login():
                    return self.upload_screenshot(image)
            
            return None
        except:
            return None
    
    def copy_to_clipboard(self, text):
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
            return True
        except:
            return False
    
    def get_clipboard_image(self):
        try:
            return ImageGrab.grabclipboard()
        except:
            return None
    
    def check_network_status(self):
        while self.is_running:
            time.sleep(120)
            
            new_status = self.check_network()
            
            if new_status != self.network_status:
                self.network_status = new_status
                if not new_status:
                    self.notify("No Connection", "No internet connection")
                else:
                    self.notify("Connection Restored", "Internet connection restored")
    
    def monitor_clipboard(self):
        while self.is_running:
            if not self.network_status:
                time.sleep(2)
                continue
            
            current_image = self.get_clipboard_image()
            
            if current_image is not None:
                current_hash = self.get_image_hash(current_image)
                
                if current_hash != self.last_image_hash:
                    self.last_image_hash = current_hash
                    
                    url = self.upload_screenshot(current_image)
                    
                    del current_image
                    gc.collect()
                    
                    if url:
                        if self.copy_to_clipboard(url):
                            self.notify("Upload Successful", "URL copied to clipboard")
                        else:
                            self.notify("Upload Successful", f"URL: {url}")
                    else:
                        self.notify("Upload Failed", "Could not upload screenshot")
            
            time.sleep(1)
    
    def start_monitoring(self):
        if self.is_running:
            return
        
        self.is_running = True
        
        network_thread = threading.Thread(target=self.check_network_status, daemon=True)
        network_thread.start()
        
        monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        monitor_thread.start()
    
    def stop_monitoring(self):
        self.is_running = False
        if self.session:
            self.session.close()
    
    def save_config(self, config):
        self.config_manager.save(config)
        self.config = config