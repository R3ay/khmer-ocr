#!/bin/bash
# install.sh - Automated installer for macOS
# Silently deploys Python virtual environment, Homebrew Tesseract, and Khmer language packs.

set -e

# Configuration
TARGET_DIR="$HOME/KhmerOCR"
TESSDATA_BEST_URL="https://github.com/tesseract-ocr/tessdata_best/raw/main/khm.traineddata"
REPO_ZIP_URL="https://github.com/OiiiSteav/khmer-ocr/archive/refs/heads/main.zip"

echo "==============================================="
echo "  Offline Khmer OCR Installer for macOS"
echo "==============================================="

# Step 1: Check and Install Homebrew & Tesseract
echo -e "\n[1/5] Checking Tesseract OCR installation..."
if command -v tesseract &> /dev/null; then
    echo "Tesseract OCR is already installed."
else
    echo "Tesseract OCR not found. Checking for Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Error: Homebrew is not installed on your system."
        echo "Please install Homebrew first by running:"
        echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        exit 1
    fi
    echo "Installing Tesseract via Homebrew..."
    brew install tesseract
fi

# Step 2: Locate Homebrew tessdata and download Khmer language pack
echo -e "\n[2/5] Setting up Khmer language pack..."
# Detect Homebrew prefix (Apple Silicon vs Intel)
BREW_PREFIX=$(brew --prefix)
TESSDATA_DIR="$BREW_PREFIX/share/tessdata"

if [ ! -d "$TESSDATA_DIR" ]; then
    echo "Creating tessdata directory at $TESSDATA_DIR..."
    mkdir -p "$TESSDATA_DIR"
fi

KHM_FILE="$TESSDATA_DIR/khm.traineddata"
if [ -f "$KHM_FILE" ]; then
    echo "Khmer language pack (tessdata_best) is already present."
else
    echo "Downloading high-accuracy khm.traineddata from GitHub..."
    curl -L -o "$KHM_FILE" "$TESSDATA_BEST_URL"
    echo "Khmer language pack successfully installed at $KHM_FILE."
fi

# Step 3: Deploy Application Files
echo -e "\n[3/5] Setting up application directory..."
mkdir -p "$TARGET_DIR"

# If running locally from the repository, copy files. Otherwise, download ZIP.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
if [ -f "$SCRIPT_DIR/main.py" ]; then
    echo "Copying local project files..."
    cp -R "$SCRIPT_DIR/"* "$TARGET_DIR/"
    # Clean up local virtual env copy if exists
    rm -rf "$TARGET_DIR/venv" "$TARGET_DIR/logs"
else
    echo "Downloading application source code..."
    ZIP_PATH="/tmp/khmer_ocr.zip"
    curl -L -o "$ZIP_PATH" "$REPO_ZIP_URL"
    
    # Extract to temp directory to handle nested folder
    TEMP_EXTRACT="/tmp/khmer_ocr_extracted"
    rm -rf "$TEMP_EXTRACT"
    mkdir -p "$TEMP_EXTRACT"
    unzip -q "$ZIP_PATH" -d "$TEMP_EXTRACT"
    
    # Find nested directory and move contents
    NESTED_DIR=$(find "$TEMP_EXTRACT" -maxdepth 1 -type d | grep -v "^$TEMP_EXTRACT$" | head -n 1)
    cp -R "$NESTED_DIR/"* "$TARGET_DIR/"
    
    # Clean up
    rm -rf "$ZIP_PATH" "$TEMP_EXTRACT"
fi
echo "Application deployed to: $TARGET_DIR"

# Step 4: Configure Python Virtual Environment
echo -e "\n[4/5] Creating Python virtual environment..."
cd "$TARGET_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
echo "Virtual environment configured."

echo "Installing Python dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
echo "Dependencies successfully installed."

# Step 5: Create Desktop App Launcher
echo -e "\n[5/5] Creating Desktop Launcher..."
LAUNCHER_PATH="$HOME/Desktop/Khmer OCR.command"

cat <<EOF > "$LAUNCHER_PATH"
#!/bin/bash
cd "$TARGET_DIR"
./venv/bin/python main.py
EOF

chmod +x "$LAUNCHER_PATH"
echo "Launcher created on Desktop: 'Khmer OCR.command'"

echo "==============================================="
echo "  Installation Complete!"
echo "==============================================="
echo "  To run the application, double-click the 'Khmer OCR.command' file on your Desktop."
echo "  Press Cmd + Shift + K to capture Khmer text."
echo ""
echo "  IMPORTANT NOTE FOR macOS:"
echo "  Because this app listens to global hotkeys, macOS will ask for 'Accessibility' permissions."
echo "  When prompted, open 'System Settings' -> 'Privacy & Security' -> 'Accessibility'"
echo "  and toggle the switch next to 'Terminal' (or the app launcher) to ALLOW it."
echo "==============================================="
echo "Press Enter to exit..."
read -r
