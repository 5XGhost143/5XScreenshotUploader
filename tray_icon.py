import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw

class TrayIcon:
    def __init__(self, uploader):
        self.uploader = uploader
        self.icon = None
    
    def create_python_icon(self):
        icon_size = 64
        image = Image.new('RGB', (icon_size, icon_size), color='white')
        draw = ImageDraw.Draw(image)
        
        draw.ellipse([8, 8, 56, 56], fill='#3776ab')
        draw.ellipse([32, 16, 48, 32], fill='#ffd43b')
        draw.rectangle([20, 28, 44, 44], fill='white')
        draw.ellipse([26, 32, 38, 44], fill='#3776ab')
        
        return image
    
    def show_status(self):
        status = "Active" if self.uploader.is_running else "Inactive"
        network = "Connected" if self.uploader.network_status else "No Connection"
        msg = f"Status: {status}\nNetwork: {network}\nServer: {self.uploader.config['domain']}"
        self.uploader.notify("Status", msg)
    
    def quit_app(self):
        self.uploader.stop_monitoring()
        if self.icon:
            self.icon.stop()
    
    def run(self):
        icon_image = self.create_python_icon()
        
        menu = pystray.Menu(
            item('Status', lambda: self.show_status()),
            item('Exit', lambda: self.quit_app())
        )
        
        self.icon = pystray.Icon("screenshot_uploader", icon_image, "Screenshot Uploader", menu)
        self.icon.run()