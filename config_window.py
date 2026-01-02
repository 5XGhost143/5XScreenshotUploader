import tkinter as tk
from tkinter import ttk, messagebox
import threading
from uploader import ScreenshotUploader
from tray_icon import TrayIcon

class ConfigWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screenshot Uploader - Configuration")
        self.root.geometry("450x400")
        self.root.resizable(False, False)
        
        self.uploader = ScreenshotUploader()
        
        if self.uploader.config:
            self.start_with_existing_config()
        else:
            self.create_config_ui()
    
    def create_config_ui(self):
        title = tk.Label(self.root, text="Server Configuration", font=("Arial", 16, "bold"))
        title.pack(pady=20)
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Protocol:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.protocol_var = tk.StringVar(value="https")
        protocol_combo = ttk.Combobox(frame, textvariable=self.protocol_var, values=["http", "https"], state="readonly", width=30)
        protocol_combo.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Domain:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.domain_entry = ttk.Entry(frame, width=33)
        self.domain_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Port:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(frame, width=33)
        self.port_entry.insert(0, "443")
        self.port_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Username:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(frame, width=33)
        self.username_entry.grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text="Password:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(frame, width=33, show="*")
        self.password_entry.grid(row=4, column=1, pady=5)
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        test_btn = ttk.Button(button_frame, text="Test Connection", command=self.test_connection)
        test_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(button_frame, text="Save & Start", command=self.save_and_start)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.pack(pady=10)
    
    def test_connection(self):
        config = self.get_config_from_ui()
        
        if not self.validate_config(config):
            return
        
        self.status_label.config(text="Testing connection...", fg="blue")
        self.root.update()
        
        self.uploader.save_config(config)
        
        if self.uploader.login():
            self.status_label.config(text="✓ Connection successful!", fg="green")
            messagebox.showinfo("Success", "Connection to server successful!")
        else:
            self.status_label.config(text="✗ Connection failed", fg="red")
            messagebox.showerror("Error", "Connection failed. Please check your credentials.")
    
    def get_config_from_ui(self):
        password = self.password_entry.get()
        
        return {
            "protocol": self.protocol_var.get(),
            "domain": self.domain_entry.get().strip(),
            "port": self.port_entry.get().strip(),
            "username": self.username_entry.get().strip(),
            "password": password
        }
    
    def validate_config(self, config):
        if not config["domain"]:
            messagebox.showerror("Error", "Please enter a domain!")
            return False
        
        if not config["port"]:
            messagebox.showerror("Error", "Please enter a port!")
            return False
        
        try:
            int(config["port"])
        except ValueError:
            messagebox.showerror("Error", "Port must be a number!")
            return False
        
        if not config["username"]:
            messagebox.showerror("Error", "Please enter a username!")
            return False
        
        if not config["password"]:
            messagebox.showerror("Error", "Please enter a password!")
            return False
        
        return True
    
    def save_and_start(self):
        config = self.get_config_from_ui()
        
        if not self.validate_config(config):
            return
        
        self.uploader.save_config(config)
        
        if self.uploader.login():
            self.root.withdraw()
            self.start_monitoring()
        else:
            messagebox.showerror("Error", "Login failed. Please check your credentials.")
    
    def start_with_existing_config(self):
        self.root.withdraw()
        
        if self.uploader.login():
            self.start_monitoring()
        else:
            self.root.deiconify()
            self.create_config_ui()
            messagebox.showwarning("Warning", "Login failed. Please check your configuration.")
    
    def start_monitoring(self):
        self.uploader.start_monitoring()
        
        tray = TrayIcon(self.uploader)
        icon_thread = threading.Thread(target=tray.run, daemon=False)
        icon_thread.start()
        
        self.uploader.notify("Screenshot Uploader", "Application started")
    
    def run(self):
        self.root.mainloop()