import customtkinter as ctk
import subprocess
import threading
import os
from core.config import COLORS, FONTS
from database.crud import get_setting, set_setting
from ui.components.toast import toast_manager

class PlaywrightInstallerModal(ctk.CTkToplevel):
    def __init__(self, master, on_success_callback=None):
        super().__init__(master)
        
        self.on_success = on_success_callback
        
        self.title("Screenshot Engine Required")
        self.geometry("500x300")
        self.transient(master)
        self.grab_set()
        
        self.configure(fg_color=COLORS["background"])
        
        # UI Elements
        self.header = ctk.CTkLabel(self, text="Chromium Required", font=FONTS["heading1"], text_color=COLORS["text"])
        self.header.pack(pady=(30, 10))
        
        msg = ("LeadForge AI requires the Chromium browser engine to capture\n"
               "high-quality screenshots of leads' websites.\n\n"
               "Click below to download and install it automatically.\n"
               "This is a one-time operation (~150MB).")
        self.desc = ctk.CTkLabel(self, text=msg, font=FONTS["body"], text_color=COLORS["text_muted"])
        self.desc.pack(pady=10)
        
        self.progress = ctk.CTkProgressBar(self, width=300)
        self.progress.set(0)
        
        self.install_btn = ctk.CTkButton(self, text="Install Chromium", font=FONTS["body"], command=self.start_install)
        self.install_btn.pack(pady=20)
        
    def start_install(self):
        self.install_btn.configure(state="disabled", text="Installing...")
        self.progress.pack(pady=10)
        self.progress.start()
        
        thread = threading.Thread(target=self._run_install, daemon=True)
        thread.start()
        
    def _run_install(self):
        try:
            # Setting PLAYWRIGHT_BROWSERS_PATH to 0 forces local install, 
            # but for simplicity we'll let playwright install it into the default %USERPROFILE%\AppData\Local\ms-playwright
            cmd = ["playwright", "install", "chromium"]
            
            # Since playwright might not be a global executable if installed in a venv,
            # we should run it via python module
            cmd = ["python", "-m", "playwright", "install", "chromium"]
            
            # Hide console window on Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            subprocess.run(cmd, check=True, startupinfo=startupinfo)
            
            # Success
            self.after(0, self._install_success)
        except Exception as e:
            self.after(0, self._install_failed, str(e))
            
    def _install_success(self):
        self.progress.stop()
        set_setting("chromium_installed", "true")
        toast_manager.show("Chromium installed successfully!", "success")
        if self.on_success:
            self.on_success()
        self.destroy()
        
    def _install_failed(self, err):
        self.progress.stop()
        self.install_btn.configure(state="normal", text="Retry Install")
        toast_manager.show(f"Failed to install Chromium: {err}", "error")

def check_playwright_installed():
    return get_setting("chromium_installed", "false") == "true"
