# Tesseract OCR Custom Khmer Font Training Guide

This directory contains the tools and step-by-step instructions to train the offline Tesseract OCR engine to recognize a custom or unique Khmer font with high accuracy.

---

## How Tesseract Training Works (LSTM Fine-Tuning)

Tesseract 5.0+ uses an LSTM (Long Short-Term Memory) neural network. To train it on a new font, we perform **incremental training** (fine-tuning). This process feeds images of the new font into the existing `khm.traineddata` model, adjusting the neural network's weights so it learns the new font shapes while retaining its general Khmer language knowledge.

---

## Step 1: Generate Training Data (.tif and .box)

Tesseract requires training data in pairs:
1. **`.tif` (Image):** A high-resolution, uncompressed TIFF image showing lines of Khmer text in your custom font.
2. **`.box` (Coordinates):** A text file mapping the exact pixel coordinates of every single character in the TIFF image to its corresponding Unicode letter.

We have provided an automated script, `generate_training_data.py`, which renders a Khmer text corpus using your custom `.ttf` font file and automatically generates both the `.tif` and `.box` files with perfect pixel accuracy.

### Run the Generator:
1. Place your custom font file (e.g., `my_custom_font.ttf`) in this directory.
2. Open a terminal in this folder and run the script:
   ```bash
   python generate_training_data.py --font my_custom_font.ttf --text corpus.txt --output khm.customfont.exp0
   ```
   *(If you do not specify a `--text` file, the script will automatically use a built-in high-density Khmer training corpus).*

This will produce:
* `khm.customfont.exp0.tif`
* `khm.customfont.exp0.box`

---

## Step 2: Install Tesseract Training Tools

To compile the training files and run the neural network training, you must install the Tesseract training build:

### On Windows (via Winget):
Ensure you have the full Tesseract development tools. The standard UB-Mannheim installer includes them, but you must ensure the Tesseract directory is in your System PATH.
To verify, open PowerShell and run:
```powershell
tesseract --version
```
Confirm that the output lists `libarchive` and other training libraries.

---

## Step 3: Run the Fine-Tuning Process

Once you have your `.tif` and `.box` files, run these commands in your terminal to train the model:

### 1. Generate LSTM Reference Files:
Convert the `.box` and `.tif` files into Tesseract's internal `.lstmf` training format:
```bash
tesseract khm.customfont.exp0.tif khm.customfont.exp0 lstm.train
```

### 2. Extract the Existing LSTM Model:
Extract the base neural network from your existing high-accuracy `khm.traineddata` model (located in your Tesseract `tessdata` folder):
```bash
combine_tessdata -e "C:\Program Files\Tesseract-OCR\tessdata\khm.traineddata" khm.lstm
```

### 3. Run the Training Iterations:
Run the LSTM training. This will adjust the weights of `khm.lstm` using your new `.lstmf` data:
```bash
lstmtraining \
  --model_output output_model \
  --continue_from khm.lstm \
  --traineddata "C:\Program Files\Tesseract-OCR\tessdata\khm.traineddata" \
  --train_listfile khm.customfont.exp0.lstmf \
  --max_iterations 400
```
*(You can increase `--max_iterations` to `1000` or more for higher accuracy, depending on your dataset size).*

### 4. Compile the Final Model:
Combine the trained weights back into a deployable `.traineddata` file:
```bash
lstmtraining \
  --stop_training \
  --continue_from output_model_checkpoint \
  --traineddata "C:\Program Files\Tesseract-OCR\tessdata\khm.traineddata" \
  --model_output khm.traineddata
```

---

## Step 4: Deploy Your Trained Font Model

Copy your newly compiled `khm.traineddata` file and overwrite the one in your active Tesseract installation directory:

* **Windows Path:** `C:\Program Files\Tesseract-OCR\tessdata\khm.traineddata`
* **macOS Path:** `/opt/homebrew/share/tessdata/khm.traineddata`

Restart the Khmer OCR application. It will instantly start recognizing your custom font with maximum accuracy.
