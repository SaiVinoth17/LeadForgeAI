"""
Build script for LeadForge AI.
Run this script to package the application into a standalone Windows executable.
Prerequisites: pip install pyinstaller
"""
import os
import subprocess
from pathlib import Path
from core.logger import logger

def create_version_info():
    version_info = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'LeadForge AI'),
        StringStruct('FileDescription', 'LeadForge AI CRM & Sales Intelligence'),
        StringStruct('FileVersion', '2.0.0'),
        StringStruct('InternalName', 'LeadForge_AI'),
        StringStruct('LegalCopyright', 'MIT License'),
        StringStruct('OriginalFilename', 'LeadForge_AI.exe'),
        StringStruct('ProductName', 'LeadForge AI'),
        StringStruct('ProductVersion', '2.0.0')])
      ]), 
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    with open("version.txt", "w") as f:
        f.write(version_info)

def build_executable():
    logger.info("Starting PyInstaller build process...")
    
    # Ensure assets directory exists for the icon
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    icon_path = assets_dir / "icon.ico"
    
    create_version_info()
    
    cmd = [
        r"C:\Users\user\AppData\Local\Python\pythoncore-3.14-64\Scripts\pyinstaller.exe",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "LeadForge_AI",
        "--add-data", "assets;assets",
        "--add-data", "data;data",
        "--hidden-import", "matplotlib",
        "--hidden-import", "matplotlib.backends.backend_tkagg",
        "--hidden-import", "tkintermapview",
        "--hidden-import", "playwright",
        "--hidden-import", "urllib3",
        "--version-file", "version.txt"
    ]
    
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
        
    cmd.append("app.py")
    
    logger.info(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, shell=True)
    logger.info("Build completed. Check the 'dist' folder.")
    
    if os.path.exists("version.txt"):
        os.remove("version.txt")

if __name__ == "__main__":
    build_executable()
