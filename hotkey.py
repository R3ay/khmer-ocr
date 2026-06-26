import logging
from PyQt6.QtCore import QThread, pyqtSignal
from pynput import keyboard

logger = logging.getLogger("KhmerOCR.Hotkey")

class HotkeyListener(QThread):
    """
    A cross-platform global hotkey listener using pynput.
    Supports Windows and macOS.
    """
    triggered = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.listener = None

    def run(self):
        logger.info("Starting cross-platform hotkey listener thread...")
        
        # pynput abstract representation: '<cmd>' represents:
        # - Windows key on Windows
        # - Command key on macOS
        # This registers Cmd + Shift + K on Mac, and Win + Shift + K on Windows!
        hotkey_str = '<cmd>+<shift>+k'
        
        try:
            self.listener = keyboard.GlobalHotKeys({
                hotkey_str: self._on_triggered
            })
            # This blocks the QThread and runs the native platform-specific hook
            self.listener.start()
            logger.info(f"Global hotkey registered: {hotkey_str}")
            self.listener.join()
        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}")
            logger.info("Attempting fallback hotkey '<ctrl>+<shift>+k'...")
            try:
                self.listener = keyboard.GlobalHotKeys({
                    '<ctrl>+<shift>+k': self._on_triggered
                })
                self.listener.start()
                self.listener.join()
            except Exception as fe:
                logger.error(f"Fallback hotkey also failed: {fe}")

    def _on_triggered(self):
        logger.info("Hotkey triggered.")
        self.triggered.emit()

    def stop(self):
        logger.info("Stopping hotkey listener...")
        if self.listener:
            self.listener.stop()
            self.wait()
        logger.info("Hotkey listener thread stopped.")
