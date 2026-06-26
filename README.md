# Offline Windows Khmer OCR Application

An open-source, high-performance, completely offline Windows desktop application that runs in the background, listens for a global system-wide hotkey (`Win + Shift + K`), and allows you to drag-select any screen region to instantly perform Optical Character Recognition (OCR) on Khmer text. The recognized text is automatically copied to your clipboard.

## Features
- **100% Offline & Private:** No internet connection required. Your screen captures and extracted text never leave your device.
- **Global Hotkey Integration:** Activate from anywhere using `Win + Shift + K` (customizable).
- **Multi-Monitor & High-DPI Aware:** Spans seamlessly across all connected monitors, automatically correcting for different DPI scaling factors (125%, 150%, 200%, etc.) to ensure pixel-perfect crops.
- **Snippet-Optimized OCR:** Uses Tesseract's Page Segmentation Mode 6 (PSM 6) to treat crops as a single uniform text block, which is highly accurate for short snippets.
- **Image Preprocessing Pipeline:** Converts screen crops to grayscale to eliminate background noise and scales them up by 200% using high-quality Lanczos interpolation to maximize character recognition on small fonts.
- **Silent Background Execution:** Runs quietly in the Windows System Tray with desktop notifications and no lingering console windows (utilizes `pythonw.exe`).

---

## Project Structure

```text
khmer-ocr/
│
├── config.py          # Configuration constants (paths, hotkeys, logs)
├── hotkey.py          # Win32 global hotkey message loop running in background QThread
├── capture.py         # Screen capture engine using mss with debug image output
├── ocr.py             # Image preprocessing and Tesseract OCR background runner
├── overlay.py         # Transparent, DPI-scaled PyQt6 selection overlay
├── main.py            # Main application manager and System Tray coordinator
├── install.ps1        # Automated PowerShell installer script
├── requirements.txt   # Python package dependencies
└── README.md          # Project documentation
```

---

## Quick Installation (PowerShell One-Liner)

You can automatically install the application and all its prerequisites (including Tesseract OCR, the Khmer language pack, Python 3, and dependencies) by running a single command. 

Open **PowerShell as Administrator** and execute:

```powershell
powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; irm 'https://raw.githubusercontent.com/OiiiSteav/khmer-ocr/main/install.ps1' | iex"
```

*This script will silently deploy the application to `%USERPROFILE%\KhmerOCR`, configure a virtual environment, install dependencies, download the high-accuracy `tessdata_best` Khmer language pack, and create startup and desktop shortcuts.*

---

## Manual Developer Setup

If you prefer to set up the project manually for development or customization, follow these steps:

### Prerequisites

1. **Tesseract OCR:** 
   - Download and run the Windows installer from [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki).
   - Default installation directory: `C:\Program Files\Tesseract-OCR`.
2. **High-Accuracy Khmer Language Pack (`khm.traineddata`):**
   - Download the LSTM-trained high-accuracy model: [khm.traineddata (tessdata_best)](https://github.com/tesseract-ocr/tessdata_best/raw/main/khm.traineddata).
   - Place the file inside Tesseract's `tessdata` folder: `C:\Program Files\Tesseract-OCR\tessdata\`.
3. **Python 3.11+:**
   - Install Python from the [official website](https://www.python.org/downloads/) (make sure to check **"Add Python to PATH"** during installation).

### Setup Instructions

1. Clone the repository:
   ```powershell
   git clone https://github.com/OiiiSteav/khmer-ocr.git
   cd khmer-ocr
   ```
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   # On Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # On Windows Command Prompt:
   .\venv\Scripts\activate.bat
   ```
3. Install the required Python packages:
   ```powershell
   pip install -r requirements.txt
   ```
4. Run the application:
   ```powershell
   python main.py
   ```

---

## How to Use

1. Once running, a **blue square icon with a white 'K'** will appear in your Windows System Tray (near the system clock).
2. Press **`Win + Shift + K`** (or click the tray icon).
3. The screen will dim, and your cursor will change to a crosshair.
4. **Click and drag** a rectangle over the Khmer text you want to extract.
5. **Release the mouse**. The overlay will disappear, and the OCR engine will process the crop in the background.
6. A Windows notification will appear: **"Copied to Clipboard!"** along with a text preview.
7. Paste (`Ctrl + V`) the Khmer text anywhere you like.
8. Press the **`ESC`** key at any time to cancel the selection.

---

## Configuration & Customization

You can customize the application behavior by editing `config.py`:

- **Custom Tesseract Path:** If Tesseract is installed in a non-standard location, set the environment variable `TESSERACT_PATH` to your `tesseract.exe` path, or edit the `TESSERACT_SEARCH_PATHS` list in `config.py`.
- **Modify the Global Hotkey:** To change the hotkey from `Win + Shift + K` to `Ctrl + Shift + K`, modify the variables in `config.py`:
  ```python
  HOTKEY_MODIFIERS = 0x0002 | 0x0004  # MOD_CONTROL | MOD_SHIFT
  HOTKEY_VK = 0x4B                     # Virtual key code for 'K'
  ```

---

## Troubleshooting

- **Image Capture Diagnostics:**
  The application automatically saves a copy of the last captured region to `logs/debug_capture.png` in the application directory. If the OCR is inaccurate, open this image to verify that the selection boundaries and scaling are correct.
- **Tesseract Executable Not Found:**
  Ensure Tesseract is installed. If it is in a custom path, update the search paths in `config.py` or set the `TESSERACT_PATH` environment variable.
- **Khmer Language Pack Missing:**
  Ensure `khm.traineddata` is present in your Tesseract `tessdata` folder. If it is missing, the application will display a critical error dialog on your first capture attempt.

---

## License

This project is open-source and licensed under the [MIT License](LICENSE). Contributions, bug reports, and feature requests are welcome.
