import os
import sys
import glob
import argparse
from PIL import Image, ImageDraw, ImageFont

# Import fontTools to inspect the font's Unicode character map (cmap)
try:
    from fontTools.ttLib import TTFont
except ImportError:
    print("Error: The 'fonttools' library is required to scan system fonts.")
    print("Please install it in your virtual environment by running:")
    print("  pip install fonttools")
    sys.exit(1)

# Import the core rendering function from generate_training_data
from generate_training_data import generate_box_and_tif, DEFAULT_KHMER_CORPUS

def get_system_font_directories():
    """Returns a list of directories where system fonts are stored based on the OS."""
    dirs = []
    if sys.platform == "win32":
        # System-wide fonts
        dirs.append(os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts"))
        # User-specific fonts (Windows 10/11)
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            dirs.append(os.path.join(local_appdata, "Microsoft", "Windows", "Fonts"))
    elif sys.platform == "darwin":
        # macOS font directories
        dirs.extend([
            "/Library/Fonts",
            "/System/Library/Fonts",
            os.path.expanduser("~/Library/Fonts")
        ])
    else:
        # Linux / Unix font directories
        dirs.extend([
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts")
        ])
    return [d for d in dirs if os.path.exists(d)]

def supports_khmer(font_path):
    """
    Opens the font file and checks its Character Map (cmap) 
    to verify if it supports the Khmer Unicode range (specifically character 0x1780 'ក').
    """
    try:
        font = TTFont(font_path, fontNumber=0, lazy=True)
        # Check all cmap tables for the Khmer Unicode letter 'ក' (0x1780)
        for table in font['cmap'].tables:
            if 0x1780 in table.cmap:
                return True
    except Exception:
        pass
    return False

def scan_and_generate(output_dir):
    print("==================================================")
    print("  Smart System Font Khmer OCR Training Generator  ")
    print("==================================================")
    
    # 1. Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # 2. Locate font directories
    font_dirs = get_system_font_directories()
    print(f"Scanning system font directories:\n - " + "\n - ".join(font_dirs))
    
    # 3. Scan for TrueType (.ttf) and OpenType (.otf) files
    font_paths = []
    for d in font_dirs:
        for ext in ("*.ttf", "*.otf", "*.TTF", "*.OTF"):
            font_paths.extend(glob.glob(os.path.join(d, "**", ext), recursive=True))
            
    # De-duplicate paths
    font_paths = list(set(font_paths))
    print(f"Found {len(font_paths)} total system font files. Filtering for Khmer support...")
    
    # 4. Filter fonts that support the Khmer script
    khmer_fonts = []
    for path in font_paths:
        if supports_khmer(path):
            khmer_fonts.append(path)
            
    print(f"Detected {len(khmer_fonts)} installed fonts supporting the Khmer script!")
    if not khmer_fonts:
        print("No Khmer fonts detected on this device. Exiting.")
        return
        
    print("\nStarting automatic training data generation...")
    generated_count = 0
    lstm_list_lines = []
    
    # 5. Generate TIFF/Box training pairs for each Khmer font
    for path in khmer_fonts:
        # Extract a clean, safe filename from the font path to use as the Tesseract font identifier
        base_name = os.path.splitext(os.path.basename(path))[0]
        safe_font_id = "".join([c if c.isalnum() else "_" for c in base_name]).lower()
        
        # Output base path: e.g., output_dir/khm.fontname.exp0
        output_base_name = f"khm.{safe_font_id}.exp0"
        output_path = os.path.join(output_dir, output_base_name)
        
        print(f"\n[{generated_count + 1}/{len(khmer_fonts)}] Generating data for font: {base_name}")
        success = generate_box_and_tif(path, DEFAULT_KHMER_CORPUS, output_path)
        
        if success:
            generated_count += 1
            # Record the expected .lstmf file path for Tesseract training list
            lstm_list_lines.append(f"{output_base_name}.lstmf")
            
    # 6. Generate the training file list (train_listfile.txt)
    if lstm_list_lines:
        list_file_path = os.path.join(output_dir, "train_listfile.txt")
        with open(list_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lstm_list_lines) + "\n")
            
        print("\n==================================================")
        print("  Smart Generation Complete!")
        print("==================================================")
        print(f"Successfully generated training pairs for {generated_count} Khmer fonts.")
        print(f"All files are saved in the directory: {os.path.abspath(output_dir)}")
        print(f"Created training list file: {os.path.abspath(list_file_path)}")
        print("\nTo train Tesseract on ALL of these fonts simultaneously:")
        print(" 1. Run the tesseract command to convert all pairs to .lstmf files.")
        print(" 2. Run the lstmtraining command, passing this file as --train_listfile:")
        print(f"    --train_listfile \"{list_file_path}\"")
        print("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan all installed system fonts, detect Khmer-supporting ones, and generate Tesseract training data automatically.")
    parser.add_argument("--output-dir", default="system_training_data", help="Directory where generated training files will be saved.")
    args = parser.parse_args()
    
    scan_and_generate(args.output_dir)
