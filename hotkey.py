import ctypes
from ctypes import wintypes
import logging
from PyQt6.QtCore import QThread, pyqtSignal
import config

logger = logging.getLogger("KhmerOCR.Hotkey")

# Windows Win32 constants
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT)
    ]

class HotkeyListener(QThread):
    """
    A background QThread that registers a global hotkey with Windows
    and emits a signal when the hotkey is pressed.
    """
    triggered = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._running = True
        self._thread_id = None
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32

    def run(self):
        self._thread_id = self.kernel32.GetCurrentThreadId()
        logger.info(f"Hotkey thread started with ID: {self._thread_id}")

        # Register the global hotkey (Win + Shift + K by default)
        # hWnd is NULL (None) so the hotkey is associated with the current thread's message queue
        success = self.user32.RegisterHotKey(
            None, 
            config.HOTKEY_ID, 
            config.HOTKEY_MODIFIERS, 
            config.HOTKEY_VK
        )
        
        if not success:
            error_code = self.kernel32.GetLastError()
            logger.error(f"Failed to register global hotkey. Error code: {error_code}. "
                         f"The hotkey (Win+Shift+K) may already be in use.")
            return

        logger.info("Global hotkey successfully registered.")
        
        msg = MSG()
        try:
            # Win32 Message Loop
            # GetMessage blocks until a message is received
            while self._running:
                res = self.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if res <= 0:
                    # WM_QUIT or error
                    break
                
                if msg.message == WM_HOTKEY:
                    if msg.wParam == config.HOTKEY_ID:
                        logger.info("Hotkey triggered.")
                        self.triggered.emit()
                
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
        except Exception as e:
            logger.exception("Error in hotkey message loop.")
        finally:
            # Always unregister the hotkey on exit
            self.user32.UnregisterHotKey(None, config.HOTKEY_ID)
            logger.info("Global hotkey unregistered. Hotkey thread exiting.")

    def stop(self):
        """Signals the message loop to stop and posts a WM_QUIT message to wake it up."""
        self._running = False
        if self._thread_id:
            # Post WM_QUIT to the thread's message queue to unblock GetMessageW
            self.user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            self.wait() # Wait for thread to exit
