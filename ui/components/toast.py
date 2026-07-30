import customtkinter as ctk
import queue
from core.config import COLORS, FONTS, SPACING, RADIUS
from core.logger import logger

class ToastNotification(ctk.CTkToplevel):
    def __init__(self, master, message, variant="info"):
        super().__init__(master)
        
        self.message = message
        self.variant = variant
        
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.config(bg="#000001")
        self.wm_attributes("-transparentcolor", "#000001")
        
        color_map = {
            "success": COLORS["success"],
            "error": COLORS["danger"],
            "warning": COLORS["warning"],
            "info": COLORS["primary"]
        }
        icon_map = {
            "success": "✓ ",
            "error": "✕ ",
            "warning": "⚠ ",
            "info": "ℹ "
        }
        border_color = color_map.get(variant, COLORS["primary"])
        prefix = icon_map.get(variant, "")
        
        self.frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], border_width=2, border_color=border_color, corner_radius=12)
        self.frame.pack(padx=SPACING["sm"], pady=SPACING["sm"], fill="both", expand=True)
        
        lbl = ctk.CTkLabel(self.frame, text=f"{prefix}{message}", font=FONTS["body"], text_color=COLORS["text"], justify="left")
        lbl.pack(padx=SPACING["lg"], pady=SPACING["lg"])
        
        self.update_idletasks()
        
        # Position bottom right
        x = self.winfo_screenwidth() - self.winfo_width() - 20
        y = self.winfo_screenheight() - self.winfo_height() - 60
        self.geometry(f"+{x}+{y}")
        
        # Fade out timer
        self.after(3000, self.fade_out)
        
        # Start completely transparent
        self.attributes("-alpha", 0.0)
        self.fade_in()

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.1
            self.attributes("-alpha", alpha)
            self.after(20, self.fade_in)
            
    def fade_out(self):
        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha -= 0.1
            self.attributes("-alpha", alpha)
            self.after(20, self.fade_out)
        else:
            self.destroy()

class ToastManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ToastManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.master = None
            cls._instance.queue = queue.Queue()
            cls._instance.is_showing = False
        return cls._instance
        
    def init(self, master):
        self.master = master
        
    def show(self, message, variant="info"):
        if not self.master:
            logger.warning("ToastManager not initialized with master. Cannot show toast.")
            return
        self.queue.put((message, variant))
        if not self.is_showing:
            self._process_queue()
            
    def _process_queue(self):
        if self.queue.empty():
            self.is_showing = False
            return
            
        self.is_showing = True
        message, variant = self.queue.get()
        toast = ToastNotification(self.master, message, variant)
        
        # Check queue again after this toast finishes its lifetime (approx 3.5s total)
        self.master.after(3500, self._process_queue)

toast_manager = ToastManager()
