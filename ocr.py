import logging
import pytesseract
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal
import config

logger = logging.getLogger("KhmerOCR.OCR")

# Set the Tesseract executable path in pytesseract
pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

class OCRWorker(QThread):
    """
    A QThread worker to perform offline OCR using Tesseract in the background
    to avoid freezing the main application GUI.
    """
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, image: Image.Image):
        super().__init__()
        self.image = image

    def run(self):
        logger.info("OCR worker thread started.")
        try:
            # Image preprocessing to optimize OCR accuracy for complex/stylized Khmer fonts:
            # 1. Convert to grayscale (L mode) to eliminate color noise and backgrounds
            processed_img = self.image.convert('L')
            
            # 2. Scale the image up by 2x using high-quality Lanczos interpolation.
            # Tesseract OCR engine performs best when characters are at least 30-40 pixels tall.
            w, h = processed_img.size
            processed_img = processed_img.resize((w * 2, h * 2), Image.Resampling.LANCZOS)
            
            # PSM 6 assumes a single uniform block of text, which is highly optimized for cropped snippets
            custom_config = r"--psm 6"
            
            logger.info(f"Running Tesseract with lang='{config.OCR_LANG}'...")
            text = pytesseract.image_to_string(
                processed_img, 
                lang=config.OCR_LANG,
                config=custom_config
            )
            
            # Clean up the output text
            cleaned_text = text.strip()
            
            logger.info(f"OCR complete. Characters recognized: {len(cleaned_text)}")
            self.finished.emit(cleaned_text)
            
        except pytesseract.TesseractNotFoundError:
            err_msg = (
                f"Tesseract executable not found at: '{config.TESSERACT_CMD}'.\n"
                "Please make sure Tesseract is installed and the path in config.py is correct."
            )
            logger.error(err_msg)
            self.error.emit(err_msg)
            
        except pytesseract.TesseractError as te:
            err_msg = str(te)
            # If the error is due to missing language pack
            if "Error opening data file" in err_msg or config.OCR_LANG not in err_msg:
                err_msg = (
                    f"Tesseract failed. The '{config.OCR_LANG}' language pack might be missing.\n"
                    f"Please download '{config.OCR_LANG}.traineddata' and place it in your Tesseract 'tessdata' folder.\n\n"
                    f"Details: {err_msg}"
                )
            else:
                err_msg = f"Tesseract OCR Error: {err_msg}"
            logger.error(err_msg)
            self.error.emit(err_msg)
            
        except Exception as e:
            err_msg = f"An unexpected error occurred during OCR: {str(e)}"
            logger.exception(err_msg)
            self.error.emit(err_msg)
