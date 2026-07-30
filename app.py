import sys
import ctypes
# Set COM thread model to STA for WebView2 compatibility with Tkinter BEFORE threading is imported
sys.coinit_flags = 2
try:
    ctypes.windll.ole32.CoInitializeEx(None, 2)
except Exception:
    pass

import os
# Add root directory to python path if run directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


import customtkinter as ctk
from core.config import APPEARANCE_MODE, THEME_COLOR, COLORS
from core.logger import logger
from ui.main_window import MainWindow
from ui.components.toast import toast_manager
import clr

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("LeadForge AI")
        self.geometry("1440x900")
        self.minsize(1100, 750)
        
        # Set theme
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(THEME_COLOR)
        
        # Override window background
        self.configure(fg_color=COLORS["background"])
        
        # Root grid config
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Main Layout
        self.main_window = MainWindow(self)
        self.main_window.grid(row=0, column=0, sticky="nsew")
        
        # Initialize Toast Manager
        toast_manager.init(self)
        
        logger.info("LeadForge AI started successfully.")

if __name__ == "__main__":
    # Ensure CLR System.Threading is available
    clr.AddReference('System.Threading')
    from System.Threading import Thread, ApartmentState, ThreadStart
    
    def run_main():
        app = App()
        app.mainloop()
        
    t = Thread(ThreadStart(run_main))
    t.ApartmentState = ApartmentState.STA
    t.Start()
    t.Join()

