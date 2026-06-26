import logging
import mss
from PIL import Image

logger = logging.getLogger("KhmerOCR.Capture")

def capture_region(left: int, top: int, width: int, height: int) -> Image.Image:
    """
    Captures a region of the screen using mss and returns it as a Pillow Image.
    
    Args:
        left: X coordinate of the top-left corner
        top: Y coordinate of the top-left corner
        width: Width of the region
        height: Height of the region
        
    Returns:
        A PIL.Image.Image object containing the captured screenshot.
    """
    logger.info(f"Capturing screen region: left={left}, top={top}, width={width}, height={height}")
    try:
        with mss.mss() as sct:
            monitor = {
                "left": int(left),
                "top": int(top),
                "width": int(width),
                "height": int(height)
            }
            # Capture the region
            sct_img = sct.grab(monitor)
            
            # Convert mss image to PIL Image (raw BGRX to RGB)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            
            # Save a debug image to verify capture boundaries
            try:
                import config
                debug_path = config.LOG_DIR / "debug_capture.png"
                img.save(debug_path)
                logger.info(f"Saved debug capture to {debug_path}")
            except Exception as e:
                logger.warning(f"Failed to save debug capture image: {e}")
                
            logger.info("Screen region successfully captured.")
            return img
    except Exception as e:
        logger.error(f"Failed to capture screen region: {e}")
        raise
