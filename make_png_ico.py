import os
import sys
import struct
from io import BytesIO
from PIL import Image

def save_png_ico(img_path, output_ico_path, sizes=[16, 24, 32, 48, 64, 128, 256]):
    print(f"Compiling PNG-only ICO from '{img_path}' to '{output_ico_path}'...")
    # 1. Load the transparent circular PNG
    img = Image.open(img_path).convert("RGBA")
    
    png_datas = []
    # 2. Generate PNG data for each size
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        buf = BytesIO()
        resized.save(buf, format="PNG")
        png_datas.append(buf.getvalue())
        
    # 3. Write the ICONHEADER (6 bytes)
    # idReserved = 0, idType = 1 (Icon), idCount = number of sizes
    header = struct.pack("<HHH", 0, 1, len(sizes))
    
    # 4. Compile the ICONDIRENTRY array (16 bytes per entry)
    dir_entries = []
    current_offset = 6 + 16 * len(sizes) # Offset where image data starts
    
    for i, size in enumerate(sizes):
        png_data = png_datas[i]
        # Width and height of 256 is represented by 0 in the byte field
        size_byte = 0 if size >= 256 else size
        
        # Format:
        # bWidth (1B), bHeight (1B), bColorCount (1B, 0 for >256 colors), bReserved (1B, 0),
        # wPlanes (2B, 1), wBitCount (2B, 32 for RGBA), dwBytesInRes (4B), dwImageOffset (4B)
        entry = struct.pack(
            "<BBBBHHII",
            size_byte, size_byte, 0, 0,
            1, 32,
            len(png_data),
            current_offset
        )
        dir_entries.append(entry)
        current_offset += len(png_data)
        
    # 5. Write the finished binary ICO file
    with open(output_ico_path, "wb") as f:
        f.write(header)
        for entry in dir_entries:
            f.write(entry)
        for png_data in png_datas:
            f.write(png_data)
            
    print(f"Successfully compiled PNG-only transparent ICO: {output_ico_path}")

def main():
    scratch_logo = r"C:\Users\R3AY\.gemini\antigravity\scratch\khmer_ocr_app\logo.png"
    scratch_ico = r"C:\Users\R3AY\.gemini\antigravity\scratch\khmer_ocr_app\logo_v5.ico"
    
    deployed_logo = r"C:\Users\R3AY\KhmerOCR\logo.png"
    deployed_ico = r"C:\Users\R3AY\KhmerOCR\logo_v5.ico"
    
    if os.path.exists(scratch_logo):
        save_png_ico(scratch_logo, scratch_ico)
        
    if os.path.exists(deployed_logo):
        save_png_ico(deployed_logo, deployed_ico)

if __name__ == "__main__":
    main()
