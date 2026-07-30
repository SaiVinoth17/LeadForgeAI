# 📥 FORGE OS V6 Installation Guide

## System Requirements
- OS: Windows 10/11, macOS 12+, Ubuntu 22.04+
- Python: 3.10+
- Node.js: 18.0+

## Step-by-Step Installation

1. **Clone & Environment Setup**:
   ```bash
   git clone https://github.com/leadforge/forge-os-v6.git
   cd forge-os-v6
   ```

2. **Backend Dependencies**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install fastapi uvicorn sqlalchemy requests pydantic customtkinter flask
   ```

3. **Frontend Dependencies**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

4. **Launch Backend Application**:
   ```bash
   python app.py
   ```
