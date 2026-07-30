import tkinter as tk
import customtkinter as ctk
import os
import clr

def test_embed():
    from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime
    root = ctk.CTk()
    root.geometry("800x600")

    if not have_runtime():
        install_runtime()
        
    frame = ctk.CTkFrame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    
    html_path = os.path.abspath("command_center.html")
    webview = WebView2(frame, 800, 600)
    webview.pack(fill=tk.BOTH, expand=True)
    webview.load_url(f"file:///{html_path}")
    
    root.mainloop()

if __name__ == "__main__":
    clr.AddReference('System.Threading')
    from System.Threading import Thread, ApartmentState, ThreadStart
    
    def go():
        test_embed()
        
    t = Thread(ThreadStart(go))
    t.ApartmentState = ApartmentState.STA
    t.Start()
    t.Join()

