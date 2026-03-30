Markdown
# ✦ BG Eraser — Offline AI Background Remover

**Developed by:** Muhammad TAHA  
**Tech Stack:** Python, CustomTkinter, Rembg (U²-Net), ONNX Runtime, PyInstaller, NSIS.

A blazing-fast, lightweight, and **100% offline** desktop application for Windows that uses Deep Learning to remove backgrounds from images. Built to ensure complete privacy, zero cloud dependency, and highly optimized bulk processing.

---

## 🚀 Project Overview

This project was built to solve the latency and privacy issues of cloud-based background removers. By utilizing the U²-Net neural network locally via the ONNX runtime, this application achieves pixel-perfect edge detection (even for hair and fur) entirely on the user's CPU or GPU.

**Key Features:**
* **Instant Offline Processing:** No internet connection or API keys required after the initial AI model download.
* **Modern GUI:** Built with `customtkinter` for a sleek, responsive, and threaded dark-mode interface.
* **Lazy Loading:** AI models are dynamically imported only when triggered, reducing app launch time to under 1 second.
* **Threaded Inference:** The UI remains completely responsive with animated progress bars during heavy AI computations.
* **Multiple Output Formats:** Save results as Transparent PNGs, White Backgrounds, or Black Backgrounds.

---

## 🛠️ Step-by-Step Guide: How to Build & Run the App

Follow these steps to set up the development environment and run the source code on your local machine.

### Phase 1: Environment Setup
1. **Install Python:** Ensure you have Python 3.10+ installed on your Windows machine. Check the "Add Python to PATH" box during installation.
2. **Clone the Repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/bg-eraser.git](https://github.com/YOUR_USERNAME/bg-eraser.git)
   cd bg-eraser
Create a Virtual Environment: It is highly recommended to isolate dependencies to avoid version conflicts.

Bash
python -m venv venv
venv\Scripts\activate
Phase 2: Installing Dependencies
With your virtual environment activated, install the required libraries. The core dependencies are rembg for the AI model, customtkinter for the UI, and Pillow for image handling.

Bash
pip install -r requirements.txt
Phase 3: Running the Application
To launch the GUI, simply run the main Python file:

Bash
python app.py
Note: The very first time you click "Remove Background" on an image, the app will download the U²-Net AI model (u2net.onnx, ~170MB) to your local machine. All subsequent uses will be instant and completely offline.

📦 Packaging the App into a Standalone .exe
To distribute this software to users who do not have Python installed, the app is compiled using PyInstaller.

Install PyInstaller inside your virtual environment:

Bash
pip install pyinstaller
Run the Build Spec: This project uses a custom bg_remover.spec file. It includes a critical fix (copy_metadata) to ensure the pymatting library is correctly bundled alongside the AI weights.

Bash
pyinstaller bg_remover.spec
Locate the Build: Once finished, your standalone executable will be located inside the generated dist/BGEraser folder.

💽 Creating the Windows Installer (Setup.exe)
For a professional user experience, the raw PyInstaller output and the AI model are bundled together into a single, one-click installer using NSIS (Nullsoft Scriptable Install System).

This ensures the user's app is 100% offline from the very first click, as the AI model is pre-packaged.

Locate the downloaded u2net.onnx model on your PC (usually in C:\Users\YourName\.u2net\).

Copy u2net.onnx into the root folder of this project.

Download and install NSIS.

Right-click the installer.nsi file provided in this repository and select "Compile NSIS Script".

The compiler will compress the application and the AI model into a single BG_Eraser_Setup.exe file, complete with Start Menu and Desktop shortcuts
