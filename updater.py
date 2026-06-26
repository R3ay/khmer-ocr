import logging
import urllib.request
import zipfile
import io
import os
import sys
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal
import config

logger = logging.getLogger("KhmerOCR.Updater")

class AutoUpdater(QThread):
    """
    Background worker that checks for updates on GitHub,
    downloads the latest code, overwrites local files,
    and signals the main thread to restart.
    """
    update_ready = pyqtSignal()
    no_update_needed = pyqtSignal()
    update_error = pyqtSignal(str)

    def __init__(self, target_dir: str):
        super().__init__()
        self.target_dir = target_dir

    def run(self):
        logger.info("Auto-updater thread started.")
        try:
            # 1. Fetch the remote version number
            remote_version_url = f"https://raw.githubusercontent.com/{config.GITHUB_REPO}/main/version.txt"
            logger.info(f"Checking remote version at: {remote_version_url}")
            
            req = urllib.request.Request(
                remote_version_url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                remote_version = response.read().decode('utf-8').strip()
            
            logger.info(f"Local version: {config.VERSION} | Remote version: {remote_version}")
            
            # Simple version comparison (e.g., "1.2.0" vs "1.1.0")
            if self._is_newer_version(config.VERSION, remote_version):
                logger.info("New update detected. Starting background download...")
                
                # 2. Download the latest source ZIP
                repo_zip_url = f"https://github.com/{config.GITHUB_REPO}/archive/refs/heads/main.zip"
                logger.info(f"Downloading ZIP from: {repo_zip_url}")
                
                zip_req = urllib.request.Request(
                    repo_zip_url,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                
                with urllib.request.urlopen(zip_req, timeout=30) as zip_response:
                    zip_data = zip_response.read()
                
                # 3. Extract ZIP and overwrite local python files
                logger.info("Extracting files and updating local files...")
                with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
                    # Find the root folder inside the ZIP (usually <repo>-main)
                    root_folder = zip_ref.namelist()[0].split('/')[0]
                    
                    for member in zip_ref.infolist():
                        # Skip directories
                        if member.is_dir():
                            continue
                        
                        # Get the relative path of the file inside the repository
                        member_path = member.filename
                        if member_path.startswith(root_folder + '/'):
                            relative_path = member_path[len(root_folder) + 1:]
                            
                            # Skip virtual environments, logs, and git folders
                            if (relative_path.startswith("venv/") or 
                                relative_path.startswith("logs/") or 
                                relative_path.startswith(".git/")):
                                continue
                            
                            # Determine the destination path on the local disk
                            dest_path = os.path.join(self.target_dir, relative_path)
                            
                            # Create parent directories if they don't exist
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            
                            # Read file content and write it to the destination
                            # Windows allows overwriting running .py files because they are read on startup
                            with zip_ref.open(member) as source_file:
                                content = source_file.read()
                                with open(dest_path, 'wb') as target_file:
                                    target_file.write(content)
                                    
                logger.info("Local files successfully updated. Running pip install...")
                
                # 4. Update dependencies (runs pip install in the background)
                requirements_path = os.path.join(self.target_dir, "requirements.txt")
                pip_path = os.path.join(self.target_dir, "venv", "Scripts", "pip.exe")
                
                if os.path.exists(pip_path) and os.path.exists(requirements_path):
                    # Run silently in background without showing command window
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    
                    subprocess.run(
                        [pip_path, "install", "-r", requirements_path],
                        startupinfo=startupinfo,
                        capture_output=True
                    )
                    logger.info("Dependencies updated successfully.")
                
                # 5. Signal success
                logger.info("Update fully applied.")
                self.update_ready.emit()
            else:
                logger.info("Application is up to date.")
                self.no_update_needed.emit()
                
        except Exception as e:
            err_msg = f"Auto-update failed: {str(e)}"
            logger.error(err_msg)
            self.update_error.emit(err_msg)

    def _is_newer_version(self, current: str, remote: str) -> bool:
        """Compares two semantic version strings. Returns True if remote is newer."""
        try:
            c_parts = [int(x) for x in current.split('.')]
            r_parts = [int(x) for x in remote.split('.')]
            
            # Pad with zeros if version format is shorter
            while len(c_parts) < 3: c_parts.append(0)
            while len(r_parts) < 3: r_parts.append(0)
            
            for c, r in zip(c_parts, r_parts):
                if r > c:
                    return True
                elif c > r:
                    return False
            return False
        except Exception:
            # Fallback to simple string check if parsing fails
            return current != remote
