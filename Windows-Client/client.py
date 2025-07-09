#!/usr/bin/env python3
"""
ScreenshotOCR Windows Client - Enhanced Edition
PyQt5-based desktop application for automated screenshot capture and analysis
Enhanced with additional hotkeys and productivity features
"""

import os
import sys
import json
import time
import logging
import traceback
import threading
import requests
import keyboard
import pystray
import subprocess
import numpy as np
from queue import Queue
from datetime import datetime
from configparser import ConfigParser
from PIL import Image, ImageGrab
import win32gui
import win32con
import win32ui
import win32api
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTextEdit, QCheckBox, QSpinBox,
    QGroupBox, QFormLayout, QTabWidget, QSystemTrayIcon, QMenu,
    QAction, QMessageBox, QComboBox, QProgressBar, QListWidget,
    QListWidgetItem, QDialog, QDialogButtonBox, QFileDialog
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QSettings
from PyQt5.QtGui import QIcon, QFont, QPixmap, QTextCursor, QClipboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('screenshot_client.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScreenshotClient:
    """Main screenshot client class with enhanced hotkey support"""
    
    def __init__(self):
        self.config = self.load_config()
        self.upload_queue = Queue()
        self.retry_queue = Queue()
        self.is_running = False
        self.hotkey_registered = False
        self.screenshot_count = 0
        self.upload_success_count = 0
        self.upload_failed_count = 0
        self.main_window = None  # Will be set by MainWindow
        
        # Setup upload thread
        self.upload_thread = None
        self.start_upload_thread()
        
        logger.info("ScreenshotOCR Windows Client Enhanced Edition initialized")
    
    def load_config(self):
        """Load configuration from file"""
        config = ConfigParser()
        config_file = 'client_config.ini'
        
        # Enhanced default configuration with new hotkeys
        default_config = {
            'server_url': 'https://web.korczewski.de',
            'api_token': '8BHxKkgbShG1vwhXje6MDnKYW5d55AwG47XuFma8c5cfNG5GUfJaopXz6cDuY0Df',
            'hotkey': 'ctrl+s',
            'clipboard_text_hotkey': 'ctrl+shift+t',
            'clipboard_image_hotkey': 'ctrl+shift+i',
            'screenshot_local_hotkey': 'ctrl+shift+s',
            'config_dialog_hotkey': 'ctrl+shift+c',
            'window_toggle_hotkey': 'ctrl+shift+h',
            'retry_uploads_hotkey': 'ctrl+shift+r',
            'toggle_local_saving_hotkey': 'ctrl+shift+l',
            'open_folder_hotkey': 'ctrl+shift+e',
            'toggle_auto_upload_hotkey': 'ctrl+shift+q',
            'capture_delay': '0.5',
            'auto_upload': 'true',
            'save_locally': 'true',
            'local_folder': 'screenshots',
            'retry_attempts': '3',
            'retry_delay': '5',
            'compression_quality': '85',
            'capture_cursor': 'false',
            'startup_minimized': 'true',
            'notifications': 'true',
            'verify_ssl': 'true',
            'clipboard_enabled': 'true',
            'enhanced_hotkeys_enabled': 'true'
        }
        
        if os.path.exists(config_file):
            config.read(config_file)
        else:
            config.read_dict({'client': default_config})
            self.save_config(config)
        
        return config
    
    def save_config(self, config):
        """Save configuration to file"""
        with open('client_config.ini', 'w') as f:
            config.write(f)
    
    def register_hotkey(self):
        """Register global hotkeys including enhanced ones"""
        try:
            if self.hotkey_registered:
                keyboard.unhook_all()
                self.hotkey_registered = False
            
            # Screenshot hotkey
            hotkey = self.config.get('client', 'hotkey', fallback='ctrl+s')
            keyboard.add_hotkey(hotkey, self.capture_screenshot)
            
            # Clipboard hotkeys
            if self.config.getboolean('client', 'clipboard_enabled', fallback=True):
                clipboard_text_hotkey = self.config.get('client', 'clipboard_text_hotkey', fallback='ctrl+shift+t')
                clipboard_image_hotkey = self.config.get('client', 'clipboard_image_hotkey', fallback='ctrl+shift+i')
                
                keyboard.add_hotkey(clipboard_text_hotkey, self.process_clipboard_text)
                keyboard.add_hotkey(clipboard_image_hotkey, self.process_clipboard_image)
                
                logger.info(f"Clipboard hotkeys registered: {clipboard_text_hotkey} (text), {clipboard_image_hotkey} (image)")
            
            # Enhanced hotkeys
            if self.config.getboolean('client', 'enhanced_hotkeys_enabled', fallback=True):
                # Screenshot local-only hotkey
                screenshot_local_hotkey = self.config.get('client', 'screenshot_local_hotkey', fallback='ctrl+shift+s')
                keyboard.add_hotkey(screenshot_local_hotkey, self.capture_screenshot_local_only)
                
                # Configuration dialog hotkey
                config_dialog_hotkey = self.config.get('client', 'config_dialog_hotkey', fallback='ctrl+shift+c')
                keyboard.add_hotkey(config_dialog_hotkey, self.show_config_dialog)
                
                # Window toggle hotkey
                window_toggle_hotkey = self.config.get('client', 'window_toggle_hotkey', fallback='ctrl+shift+h')
                keyboard.add_hotkey(window_toggle_hotkey, self.toggle_main_window)
                
                # Retry uploads hotkey
                retry_uploads_hotkey = self.config.get('client', 'retry_uploads_hotkey', fallback='ctrl+shift+r')
                keyboard.add_hotkey(retry_uploads_hotkey, self.retry_failed_uploads)
                
                # Toggle local saving hotkey
                toggle_local_hotkey = self.config.get('client', 'toggle_local_saving_hotkey', fallback='ctrl+shift+l')
                keyboard.add_hotkey(toggle_local_hotkey, self.toggle_local_saving)
                
                # Open folder hotkey
                open_folder_hotkey = self.config.get('client', 'open_folder_hotkey', fallback='ctrl+shift+e')
                keyboard.add_hotkey(open_folder_hotkey, self.open_local_folder)
                
                # Toggle auto-upload hotkey
                toggle_auto_upload_hotkey = self.config.get('client', 'toggle_auto_upload_hotkey', fallback='ctrl+shift+q')
                keyboard.add_hotkey(toggle_auto_upload_hotkey, self.toggle_auto_upload)
                
                logger.info(f"Enhanced hotkeys registered: {screenshot_local_hotkey} (local screenshot), {config_dialog_hotkey} (config), {window_toggle_hotkey} (toggle window), {retry_uploads_hotkey} (retry), {toggle_local_hotkey} (toggle local), {open_folder_hotkey} (open folder), {toggle_auto_upload_hotkey} (toggle auto-upload)")
            
            self.hotkey_registered = True
            logger.info(f"All hotkeys registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register hotkeys: {e}")
    
    def capture_screenshot(self):
        """Capture screenshot of active window with normal processing"""
        try:
            image = self._capture_active_window()
            if image:
                self.process_screenshot(image)
                self.screenshot_count += 1
                logger.info(f"Screenshot captured successfully (#{self.screenshot_count})")
                
                # Show notification if enabled
                if self.config.getboolean('client', 'notifications', fallback=True) and self.main_window:
                    self.main_window.show_notification("Screenshot captured", "Screenshot has been captured and queued for processing")
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
    
    def capture_screenshot_local_only(self):
        """Capture screenshot and save locally only (no upload)"""
        try:
            image = self._capture_active_window()
            if image:
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_local_{timestamp}.png"
                
                # Save locally regardless of settings
                local_folder = self.config.get('client', 'local_folder', fallback='screenshots')
                os.makedirs(local_folder, exist_ok=True)
                
                local_path = os.path.join(local_folder, filename)
                
                # Apply compression
                quality = int(self.config.get('client', 'compression_quality', fallback='85'))
                image.save(local_path, 'PNG', optimize=True, compress_level=quality//10)
                
                self.screenshot_count += 1
                logger.info(f"Screenshot saved locally only: {local_path}")
                
                # Show notification
                if self.config.getboolean('client', 'notifications', fallback=True) and self.main_window:
                    self.main_window.show_notification("Screenshot saved locally", f"Screenshot saved to {local_path}")
            
        except Exception as e:
            logger.error(f"Failed to capture local screenshot: {e}")
    
    def _capture_active_window(self):
        """Helper method to capture the active window"""
        try:
            # Add delay before capture
            delay = float(self.config.get('client', 'capture_delay', fallback='0.5'))
            time.sleep(delay)
            
            # Get active window
            hwnd = win32gui.GetForegroundWindow()
            
            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # Capture window
            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(bitmap)
            
            # Copy window content
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)
            
            # Convert to PIL Image
            bmp_info = bitmap.GetInfo()
            bmp_str = bitmap.GetBitmapBits(True)
            
            image = Image.frombuffer(
                'RGB',
                (bmp_info['bmWidth'], bmp_info['bmHeight']),
                bmp_str, 'raw', 'BGRX', 0, 1
            )
            
            # Cleanup
            win32gui.DeleteObject(bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to capture window: {e}")
            return None
    
    def show_config_dialog(self):
        """Show configuration dialog"""
        try:
            if self.main_window:
                self.main_window.show_config()
                logger.info("Configuration dialog opened via hotkey")
            else:
                logger.warning("Cannot open config dialog: main window not available")
        except Exception as e:
            logger.error(f"Failed to show config dialog: {e}")
    
    def toggle_main_window(self):
        """Toggle main window visibility"""
        try:
            if self.main_window:
                if self.main_window.isVisible():
                    self.main_window.hide()
                    logger.info("Main window hidden via hotkey")
                else:
                    self.main_window.show()
                    self.main_window.activateWindow()
                    self.main_window.raise_()
                    logger.info("Main window shown via hotkey")
            else:
                logger.warning("Cannot toggle window: main window not available")
        except Exception as e:
            logger.error(f"Failed to toggle main window: {e}")
    
    def retry_failed_uploads(self):
        """Retry all failed uploads"""
        try:
            retry_count = self.retry_queue.qsize()
            if retry_count > 0:
                logger.info(f"Retrying {retry_count} failed uploads via hotkey")
                
                # Process all items in retry queue immediately
                while not self.retry_queue.empty():
                    item = self.retry_queue.get()
                    self.upload_queue.put(item)
                
                # Show notification
                if self.config.getboolean('client', 'notifications', fallback=True) and self.main_window:
                    self.main_window.show_notification("Retrying uploads", f"Retrying {retry_count} failed uploads")
            else:
                logger.info("No failed uploads to retry")
                if self.main_window:
                    self.main_window.show_notification("No failed uploads", "No failed uploads to retry")
        except Exception as e:
            logger.error(f"Failed to retry uploads: {e}")
    
    def toggle_local_saving(self):
        """Toggle local saving on/off"""
        try:
            current_setting = self.config.getboolean('client', 'save_locally', fallback=True)
            new_setting = not current_setting
            
            self.config.set('client', 'save_locally', str(new_setting).lower())
            self.save_config(self.config)
            
            status = "enabled" if new_setting else "disabled"
            logger.info(f"Local saving {status} via hotkey")
            
            # Show notification
            if self.config.getboolean('client', 'notifications', fallback=True) and self.main_window:
                self.main_window.show_notification("Local saving toggled", f"Local saving is now {status}")
        except Exception as e:
            logger.error(f"Failed to toggle local saving: {e}")
    
    def open_local_folder(self):
        """Open local screenshots folder in explorer"""
        try:
            local_folder = self.config.get('client', 'local_folder', fallback='screenshots')
            
            # Create folder if it doesn't exist
            os.makedirs(local_folder, exist_ok=True)
            
            # Open folder in explorer
            if os.name == 'nt':  # Windows
                subprocess.run(['explorer', os.path.abspath(local_folder)])
            else:  # Other OS
                subprocess.run(['xdg-open', os.path.abspath(local_folder)])
            
            logger.info(f"Opened local folder: {local_folder}")
            
        except Exception as e:
            logger.error(f"Failed to open local folder: {e}")
    
    def toggle_auto_upload(self):
        """Toggle auto-upload on/off"""
        try:
            current_setting = self.config.getboolean('client', 'auto_upload', fallback=True)
            new_setting = not current_setting
            
            self.config.set('client', 'auto_upload', str(new_setting).lower())
            self.save_config(self.config)
            
            status = "enabled" if new_setting else "disabled"
            logger.info(f"Auto-upload {status} via hotkey")
            
            # Show notification
            if self.config.getboolean('client', 'notifications', fallback=True) and self.main_window:
                self.main_window.show_notification("Auto-upload toggled", f"Auto-upload is now {status}")
        except Exception as e:
            logger.error(f"Failed to toggle auto-upload: {e}")
    
    def process_screenshot(self, image):
        """Process and optionally save screenshot"""
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            # Save locally if enabled
            if self.config.getboolean('client', 'save_locally', fallback=True):
                local_folder = self.config.get('client', 'local_folder', fallback='screenshots')
                os.makedirs(local_folder, exist_ok=True)
                
                local_path = os.path.join(local_folder, filename)
                
                # Apply compression
                quality = int(self.config.get('client', 'compression_quality', fallback='85'))
                image.save(local_path, 'PNG', optimize=True, compress_level=quality//10)
            
            # Queue for upload if auto-upload is enabled
            if self.config.getboolean('client', 'auto_upload', fallback=True):
                self.upload_queue.put({
                    'image': image,
                    'filename': filename,
                    'timestamp': int(time.time())
                })
            
        except Exception as e:
            logger.error(f"Failed to process screenshot: {e}")
    
    def process_clipboard_text(self):
        """Process clipboard text content"""
        try:
            # Get clipboard text
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            
            if not text.strip():
                logger.warning("Clipboard is empty or contains no text")
                return
            
            # Limit text length
            max_length = 50000  # 50KB limit
            if len(text) > max_length:
                text = text[:max_length]
                logger.info(f"Clipboard text truncated to {max_length} characters")
            
            # Queue for upload if auto-upload is enabled
            if self.config.getboolean('client', 'auto_upload', fallback=True):
                self.upload_queue.put({
                    'type': 'clipboard_text',
                    'text': text,
                    'timestamp': int(time.time())
                })
            
            # Save locally if enabled
            if self.config.getboolean('client', 'save_locally', fallback=True):
                self.save_clipboard_text_locally(text)
            
            logger.info(f"Clipboard text processed successfully ({len(text)} characters)")
            
        except Exception as e:
            logger.error(f"Failed to process clipboard text: {e}")
    
    def process_clipboard_image(self):
        """Process clipboard image content"""
        try:
            # Get clipboard image
            clipboard = QApplication.clipboard()
            pixmap = clipboard.pixmap()
            
            if pixmap.isNull():
                logger.warning("Clipboard contains no image")
                return
            
            # Convert QPixmap to PIL Image
            image = self.qpixmap_to_pil(pixmap)
            
            # Queue for upload if auto-upload is enabled
            if self.config.getboolean('client', 'auto_upload', fallback=True):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"clipboard_image_{timestamp}.png"
                
                self.upload_queue.put({
                    'type': 'clipboard_image',
                    'image': image,
                    'filename': filename,
                    'timestamp': int(time.time())
                })
            
            # Save locally if enabled
            if self.config.getboolean('client', 'save_locally', fallback=True):
                self.save_clipboard_image_locally(image)
            
            logger.info("Clipboard image processed successfully")
            
        except Exception as e:
            logger.error(f"Failed to process clipboard image: {e}")
    
    def save_clipboard_text_locally(self, text):
        """Save clipboard text to local file"""
        try:
            local_folder = self.config.get('client', 'local_folder', fallback='screenshots')
            os.makedirs(local_folder, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clipboard_text_{timestamp}.txt"
            local_path = os.path.join(local_folder, filename)
            
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            logger.info(f"Clipboard text saved locally: {local_path}")
            
        except Exception as e:
            logger.error(f"Failed to save clipboard text locally: {e}")
    
    def save_clipboard_image_locally(self, image):
        """Save clipboard image to local file"""
        try:
            local_folder = self.config.get('client', 'local_folder', fallback='screenshots')
            os.makedirs(local_folder, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clipboard_image_{timestamp}.png"
            local_path = os.path.join(local_folder, filename)
            
            # Apply compression
            quality = int(self.config.get('client', 'compression_quality', fallback='85'))
            image.save(local_path, 'PNG', optimize=True, compress_level=quality//10)
            
            logger.info(f"Clipboard image saved locally: {local_path}")
            
        except Exception as e:
            logger.error(f"Failed to save clipboard image locally: {e}")
    
    def qpixmap_to_pil(self, pixmap):
        """Convert QPixmap to PIL Image"""
        try:
            # Convert QPixmap to QImage
            qimage = pixmap.toImage()
            
            # Convert QImage to PIL Image
            width = qimage.width()
            height = qimage.height()
            
            # Get image data as bytes
            ptr = qimage.bits()
            ptr.setsize(qimage.byteCount())
            arr = np.array(ptr).reshape(height, width, 4)  # RGBA
            
            # Convert to PIL Image
            image = Image.fromarray(arr, 'RGBA')
            
            # Convert to RGB
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to convert QPixmap to PIL Image: {e}")
            # Fallback: create a simple image
            return Image.new('RGB', (100, 100), color='white')
    
    def start_upload_thread(self):
        """Start the upload worker thread"""
        if self.upload_thread is None or not self.upload_thread.is_alive():
            self.upload_thread = threading.Thread(target=self.upload_worker, daemon=True)
            self.upload_thread.start()
            logger.info("Upload thread started")
    
    def upload_worker(self):
        """Background worker for uploading screenshots"""
        while True:
            try:
                # Check upload queue
                if not self.upload_queue.empty():
                    item = self.upload_queue.get(timeout=1)
                    success = self.upload_screenshot(item)
                    
                    if success:
                        self.upload_success_count += 1
                    else:
                        self.upload_failed_count += 1
                        # Add to retry queue
                        item['retry_count'] = item.get('retry_count', 0) + 1
                        max_retries = int(self.config.get('client', 'retry_attempts', fallback='3'))
                        
                        if item['retry_count'] <= max_retries:
                            self.retry_queue.put(item)
                
                # Check retry queue
                if not self.retry_queue.empty():
                    retry_delay = int(self.config.get('client', 'retry_delay', fallback='5'))
                    time.sleep(retry_delay)
                    
                    item = self.retry_queue.get(timeout=1)
                    success = self.upload_screenshot(item)
                    
                    if success:
                        self.upload_success_count += 1
                    else:
                        self.upload_failed_count += 1
                        # Re-queue if retries remaining
                        item['retry_count'] = item.get('retry_count', 0) + 1
                        max_retries = int(self.config.get('client', 'retry_attempts', fallback='3'))
                        
                        if item['retry_count'] <= max_retries:
                            self.retry_queue.put(item)
                        else:
                            logger.error(f"Max retries exceeded for {item.get('filename', 'unknown')}")
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Upload worker error: {e}")
                time.sleep(5)
    
    def upload_screenshot(self, item):
        """Upload screenshot or clipboard content to server"""
        try:
            server_url = self.config.get('client', 'server_url', fallback='https://web.korczewski.de')
            api_token = self.config.get('client', 'api_token', fallback='')
            
            if not api_token:
                logger.error("API token not configured")
                return False
            
            headers = {
                'Authorization': f'Bearer {api_token}',
                'User-Agent': 'ScreenshotOCR-WindowsClient/1.0'
            }
            
            # Handle different item types
            if item.get('type') == 'clipboard_text':
                # Handle clipboard text
                url = f"{server_url}/api/clipboard/text"
                data = {
                    'text': item['text'],
                    'timestamp': item['timestamp'],
                    'language': 'auto'
                }
                
                response = requests.post(
                    url, 
                    headers=headers, 
                    data=data, 
                    timeout=30,
                    verify=self.get_ssl_verify(server_url)
                )
                
                if response.status_code == 200:
                    logger.info(f"Clipboard text uploaded successfully ({len(item['text'])} chars)")
                    return True
                else:
                    logger.error(f"Clipboard text upload failed: {response.status_code} - {response.text}")
                    return False
                    
            elif item.get('type') == 'clipboard_image':
                # Handle clipboard image
                from io import BytesIO
                image_buffer = BytesIO()
                item['image'].save(image_buffer, format='PNG')
                image_buffer.seek(0)
                
                url = f"{server_url}/api/clipboard/image"
                files = {
                    'image': (item['filename'], image_buffer, 'image/png')
                }
                data = {
                    'timestamp': item['timestamp']
                }
                
                response = requests.post(
                    url, 
                    headers=headers, 
                    files=files, 
                    data=data, 
                    timeout=30,
                    verify=self.get_ssl_verify(server_url)
                )
                
                if response.status_code == 200:
                    logger.info(f"Clipboard image uploaded successfully: {item['filename']}")
                    return True
                else:
                    logger.error(f"Clipboard image upload failed: {response.status_code} - {response.text}")
                    return False
                    
            else:
                # Handle regular screenshot
                from io import BytesIO
                image_buffer = BytesIO()
                item['image'].save(image_buffer, format='PNG')
                image_buffer.seek(0)
                
                url = f"{server_url}/api/screenshot"
                files = {
                    'image': (item['filename'], image_buffer, 'image/png')
                }
                data = {
                    'timestamp': item['timestamp']
                }
                
                response = requests.post(
                    url, 
                    headers=headers, 
                    files=files, 
                    data=data, 
                    timeout=30,
                    verify=self.get_ssl_verify(server_url)
                )
                
                if response.status_code == 200:
                    logger.info(f"Screenshot uploaded successfully: {item['filename']}")
                    return True
                else:
                    logger.error(f"Upload failed: {response.status_code} - {response.text}")
                    return False
                
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return False
    
    def get_ssl_verify(self, server_url):
        """Determine SSL verification based on URL"""
        import re
        verify_ssl = self.config.getboolean('client', 'verify_ssl', fallback=True)
        
        # Check if URL contains IP address or localhost
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        if ('localhost' in server_url.lower() or 
            '127.0.0.1' in server_url or 
            re.search(ip_pattern, server_url) or
            not verify_ssl):
            logger.debug(f"SSL verification disabled for {server_url}")
            # Suppress SSL warnings for development
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            return False
        else:
            logger.debug(f"SSL verification enabled for {server_url}")
            return True
    
    def get_statistics(self):
        """Get client statistics"""
        return {
            'screenshots_captured': self.screenshot_count,
            'uploads_successful': self.upload_success_count,
            'uploads_failed': self.upload_failed_count,
            'queue_size': self.upload_queue.qsize(),
            'retry_queue_size': self.retry_queue.qsize()
        }
    
    def start(self):
        """Start the client"""
        self.is_running = True
        self.register_hotkey()
        logger.info("ScreenshotOCR Windows Client started")
    
    def stop(self):
        """Stop the client"""
        self.is_running = False
        if self.hotkey_registered:
            keyboard.unhook_all()
            self.hotkey_registered = False
        logger.info("ScreenshotOCR Windows Client stopped")

class ConfigDialog(QDialog):
    """Configuration dialog"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("ScreenshotOCR Configuration")
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout()
        
        # Create tabs
        tab_widget = QTabWidget()
        
        # Server tab
        server_tab = QWidget()
        server_layout = QFormLayout()
        
        self.server_url = QLineEdit(self.config.get('client', 'server_url', fallback=''))
        self.api_token = QLineEdit(self.config.get('client', 'api_token', fallback=''))
        self.api_token.setEchoMode(QLineEdit.Password)
        
        server_layout.addRow("Server URL:", self.server_url)
        server_layout.addRow("API Token:", self.api_token)
        
        server_tab.setLayout(server_layout)
        tab_widget.addTab(server_tab, "Server")
        
        # Capture tab
        capture_tab = QWidget()
        capture_layout = QFormLayout()
        
        self.hotkey = QLineEdit(self.config.get('client', 'hotkey', fallback='ctrl+s'))
        self.capture_delay = QSpinBox()
        self.capture_delay.setRange(0, 10)
        self.capture_delay.setValue(int(float(self.config.get('client', 'capture_delay', fallback='0.5')) * 10))
        self.capture_delay.setSuffix(" ms")
        
        self.auto_upload = QCheckBox()
        self.auto_upload.setChecked(self.config.getboolean('client', 'auto_upload', fallback=True))
        
        capture_layout.addRow("Screenshot Hotkey:", self.hotkey)
        capture_layout.addRow("Capture Delay:", self.capture_delay)
        capture_layout.addRow("Auto Upload:", self.auto_upload)
        
        capture_tab.setLayout(capture_layout)
        tab_widget.addTab(capture_tab, "Capture")
        
        # Clipboard tab
        clipboard_tab = QWidget()
        clipboard_layout = QFormLayout()
        
        self.clipboard_enabled = QCheckBox()
        self.clipboard_enabled.setChecked(self.config.getboolean('client', 'clipboard_enabled', fallback=True))
        
        self.clipboard_text_hotkey = QLineEdit(self.config.get('client', 'clipboard_text_hotkey', fallback='ctrl+shift+t'))
        self.clipboard_image_hotkey = QLineEdit(self.config.get('client', 'clipboard_image_hotkey', fallback='ctrl+shift+i'))
        
        clipboard_layout.addRow("Enable Clipboard:", self.clipboard_enabled)
        clipboard_layout.addRow("Text Hotkey:", self.clipboard_text_hotkey)
        clipboard_layout.addRow("Image Hotkey:", self.clipboard_image_hotkey)
        
        # Add help text
        help_label = QLabel("Hotkey examples: ctrl+s, alt+f1, ctrl+shift+t, win+c")
        help_label.setStyleSheet("color: #666; font-size: 10px;")
        clipboard_layout.addRow("", help_label)
        
        clipboard_tab.setLayout(clipboard_layout)
        tab_widget.addTab(clipboard_tab, "Clipboard")
        
        # Enhanced Hotkeys tab
        enhanced_tab = QWidget()
        enhanced_layout = QFormLayout()
        
        self.enhanced_hotkeys_enabled = QCheckBox()
        self.enhanced_hotkeys_enabled.setChecked(self.config.getboolean('client', 'enhanced_hotkeys_enabled', fallback=True))
        
        self.screenshot_local_hotkey = QLineEdit(self.config.get('client', 'screenshot_local_hotkey', fallback='ctrl+shift+s'))
        self.config_dialog_hotkey = QLineEdit(self.config.get('client', 'config_dialog_hotkey', fallback='ctrl+shift+c'))
        self.window_toggle_hotkey = QLineEdit(self.config.get('client', 'window_toggle_hotkey', fallback='ctrl+shift+h'))
        self.retry_uploads_hotkey = QLineEdit(self.config.get('client', 'retry_uploads_hotkey', fallback='ctrl+shift+r'))
        self.toggle_local_saving_hotkey = QLineEdit(self.config.get('client', 'toggle_local_saving_hotkey', fallback='ctrl+shift+l'))
        self.open_folder_hotkey = QLineEdit(self.config.get('client', 'open_folder_hotkey', fallback='ctrl+shift+e'))
        self.toggle_auto_upload_hotkey = QLineEdit(self.config.get('client', 'toggle_auto_upload_hotkey', fallback='ctrl+shift+q'))
        
        enhanced_layout.addRow("Enable Enhanced Hotkeys:", self.enhanced_hotkeys_enabled)
        enhanced_layout.addRow("Local Screenshot:", self.screenshot_local_hotkey)
        enhanced_layout.addRow("Config Dialog:", self.config_dialog_hotkey)
        enhanced_layout.addRow("Toggle Window:", self.window_toggle_hotkey)
        enhanced_layout.addRow("Retry Uploads:", self.retry_uploads_hotkey)
        enhanced_layout.addRow("Toggle Local Saving:", self.toggle_local_saving_hotkey)
        enhanced_layout.addRow("Open Folder:", self.open_folder_hotkey)
        enhanced_layout.addRow("Toggle Auto-Upload:", self.toggle_auto_upload_hotkey)
        
        # Add enhanced help text
        enhanced_help_label = QLabel("Enhanced hotkeys provide quick access to common functions")
        enhanced_help_label.setStyleSheet("color: #666; font-size: 10px;")
        enhanced_layout.addRow("", enhanced_help_label)
        
        enhanced_tab.setLayout(enhanced_layout)
        tab_widget.addTab(enhanced_tab, "Enhanced Hotkeys")
        
        # Storage tab
        storage_tab = QWidget()
        storage_layout = QFormLayout()
        
        self.save_locally = QCheckBox()
        self.save_locally.setChecked(self.config.getboolean('client', 'save_locally', fallback=True))
        
        self.local_folder = QLineEdit(self.config.get('client', 'local_folder', fallback='screenshots'))
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.local_folder)
        folder_button = QPushButton("Browse")
        folder_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(folder_button)
        
        self.compression_quality = QSpinBox()
        self.compression_quality.setRange(1, 100)
        self.compression_quality.setValue(int(self.config.get('client', 'compression_quality', fallback='85')))
        self.compression_quality.setSuffix("%")
        
        storage_layout.addRow("Save Locally:", self.save_locally)
        storage_layout.addRow("Local Folder:", folder_layout)
        storage_layout.addRow("Compression Quality:", self.compression_quality)
        
        storage_tab.setLayout(storage_layout)
        tab_widget.addTab(storage_tab, "Storage")
        
        # Network tab
        network_tab = QWidget()
        network_layout = QFormLayout()
        
        self.retry_attempts = QSpinBox()
        self.retry_attempts.setRange(1, 10)
        self.retry_attempts.setValue(int(self.config.get('client', 'retry_attempts', fallback='3')))
        
        self.retry_delay = QSpinBox()
        self.retry_delay.setRange(1, 60)
        self.retry_delay.setValue(int(self.config.get('client', 'retry_delay', fallback='5')))
        self.retry_delay.setSuffix(" seconds")
        
        self.verify_ssl = QCheckBox()
        self.verify_ssl.setChecked(self.config.getboolean('client', 'verify_ssl', fallback=True))
        self.verify_ssl.setToolTip("Disable for self-signed certificates (development only)")
        
        network_layout.addRow("Retry Attempts:", self.retry_attempts)
        network_layout.addRow("Retry Delay:", self.retry_delay)
        network_layout.addRow("Verify SSL Certificates:", self.verify_ssl)
        
        network_tab.setLayout(network_layout)
        tab_widget.addTab(network_tab, "Network")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def browse_folder(self):
        """Browse for local folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Screenshot Folder")
        if folder:
            self.local_folder.setText(folder)
    
    def get_config(self):
        """Get configuration from dialog"""
        config = ConfigParser()
        config.add_section('client')
        
        config.set('client', 'server_url', self.server_url.text())
        config.set('client', 'api_token', self.api_token.text())
        config.set('client', 'hotkey', self.hotkey.text())
        config.set('client', 'clipboard_enabled', str(self.clipboard_enabled.isChecked()).lower())
        config.set('client', 'clipboard_text_hotkey', self.clipboard_text_hotkey.text())
        config.set('client', 'clipboard_image_hotkey', self.clipboard_image_hotkey.text())
        config.set('client', 'enhanced_hotkeys_enabled', str(self.enhanced_hotkeys_enabled.isChecked()).lower())
        config.set('client', 'screenshot_local_hotkey', self.screenshot_local_hotkey.text())
        config.set('client', 'config_dialog_hotkey', self.config_dialog_hotkey.text())
        config.set('client', 'window_toggle_hotkey', self.window_toggle_hotkey.text())
        config.set('client', 'retry_uploads_hotkey', self.retry_uploads_hotkey.text())
        config.set('client', 'toggle_local_saving_hotkey', self.toggle_local_saving_hotkey.text())
        config.set('client', 'open_folder_hotkey', self.open_folder_hotkey.text())
        config.set('client', 'toggle_auto_upload_hotkey', self.toggle_auto_upload_hotkey.text())
        config.set('client', 'capture_delay', str(self.capture_delay.value() / 10))
        config.set('client', 'auto_upload', str(self.auto_upload.isChecked()).lower())
        config.set('client', 'save_locally', str(self.save_locally.isChecked()).lower())
        config.set('client', 'local_folder', self.local_folder.text())
        config.set('client', 'compression_quality', str(self.compression_quality.value()))
        config.set('client', 'retry_attempts', str(self.retry_attempts.value()))
        config.set('client', 'retry_delay', str(self.retry_delay.value()))
        config.set('client', 'verify_ssl', str(self.verify_ssl.isChecked()).lower())
        
        return config

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.client = ScreenshotClient()
        self.client.main_window = self # Set the client's main_window attribute
        self.tray_icon = None
        self.init_ui()
        self.init_tray()
        self.setup_timers()
        
        # Start client
        self.client.start()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("ScreenshotOCR Windows Client - Enhanced Edition")
        self.setFixedSize(700, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Status group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Client Status: Running")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        
        self.hotkey_label = QLabel(f"Hotkey: {self.client.config.get('client', 'hotkey', fallback='ctrl+s')}")
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.hotkey_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Statistics group
        stats_group = QGroupBox("Statistics")
        stats_layout = QFormLayout()
        
        self.screenshots_label = QLabel("0")
        self.uploads_success_label = QLabel("0")
        self.uploads_failed_label = QLabel("0")
        self.queue_size_label = QLabel("0")
        
        stats_layout.addRow("Screenshots Captured:", self.screenshots_label)
        stats_layout.addRow("Uploads Successful:", self.uploads_success_label)
        stats_layout.addRow("Uploads Failed:", self.uploads_failed_label)
        stats_layout.addRow("Queue Size:", self.queue_size_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Log group
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        # Primary buttons
        primary_button_layout = QHBoxLayout()
        
        self.capture_button = QPushButton("Take Screenshot")
        self.capture_button.clicked.connect(self.manual_capture)
        
        self.clipboard_text_button = QPushButton("Process Clipboard Text")
        self.clipboard_text_button.clicked.connect(self.manual_clipboard_text)
        
        self.clipboard_image_button = QPushButton("Process Clipboard Image")
        self.clipboard_image_button.clicked.connect(self.manual_clipboard_image)
        
        primary_button_layout.addWidget(self.capture_button)
        primary_button_layout.addWidget(self.clipboard_text_button)
        primary_button_layout.addWidget(self.clipboard_image_button)
        
        # Enhanced buttons
        enhanced_button_layout = QHBoxLayout()
        
        self.capture_local_button = QPushButton("Screenshot (Local Only)")
        self.capture_local_button.clicked.connect(self.manual_capture_local)
        
        self.retry_button = QPushButton("Retry Failed Uploads")
        self.retry_button.clicked.connect(self.manual_retry_uploads)
        
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self.manual_open_folder)
        
        enhanced_button_layout.addWidget(self.capture_local_button)
        enhanced_button_layout.addWidget(self.retry_button)
        enhanced_button_layout.addWidget(self.open_folder_button)
        
        # Control buttons
        control_button_layout = QHBoxLayout()
        
        self.config_button = QPushButton("Configuration")
        self.config_button.clicked.connect(self.show_config)
        
        self.toggle_auto_upload_button = QPushButton("Toggle Auto-Upload")
        self.toggle_auto_upload_button.clicked.connect(self.manual_toggle_auto_upload)
        
        self.toggle_local_saving_button = QPushButton("Toggle Local Saving")
        self.toggle_local_saving_button.clicked.connect(self.manual_toggle_local_saving)
        
        self.minimize_button = QPushButton("Minimize to Tray")
        self.minimize_button.clicked.connect(self.hide)
        
        control_button_layout.addWidget(self.config_button)
        control_button_layout.addWidget(self.toggle_auto_upload_button)
        control_button_layout.addWidget(self.toggle_local_saving_button)
        control_button_layout.addWidget(self.minimize_button)
        
        button_layout.addLayout(primary_button_layout)
        button_layout.addLayout(enhanced_button_layout)
        button_layout.addLayout(control_button_layout)
        
        layout.addLayout(button_layout)
        
        central_widget.setLayout(layout)
        
        # Add initial log entry
        self.add_log_entry("ScreenshotOCR Windows Client started")
    
    def init_tray(self):
        """Initialize system tray"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(self, "System Tray", "System tray is not available.")
            return
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        capture_action = QAction("Take Screenshot", self)
        capture_action.triggered.connect(self.manual_capture)
        tray_menu.addAction(capture_action)
        
        clipboard_text_action = QAction("Process Clipboard Text", self)
        clipboard_text_action.triggered.connect(self.manual_clipboard_text)
        tray_menu.addAction(clipboard_text_action)
        
        clipboard_image_action = QAction("Process Clipboard Image", self)
        clipboard_image_action.triggered.connect(self.manual_clipboard_image)
        tray_menu.addAction(clipboard_image_action)
        
        tray_menu.addSeparator()
        
        # Enhanced actions
        capture_local_action = QAction("Screenshot (Local Only)", self)
        capture_local_action.triggered.connect(self.manual_capture_local)
        tray_menu.addAction(capture_local_action)
        
        retry_action = QAction("Retry Failed Uploads", self)
        retry_action.triggered.connect(self.manual_retry_uploads)
        tray_menu.addAction(retry_action)
        
        open_folder_action = QAction("Open Local Folder", self)
        open_folder_action.triggered.connect(self.manual_open_folder)
        tray_menu.addAction(open_folder_action)
        
        tray_menu.addSeparator()
        
        # Toggle actions
        toggle_auto_upload_action = QAction("Toggle Auto-Upload", self)
        toggle_auto_upload_action.triggered.connect(self.manual_toggle_auto_upload)
        tray_menu.addAction(toggle_auto_upload_action)
        
        toggle_local_saving_action = QAction("Toggle Local Saving", self)
        toggle_local_saving_action.triggered.connect(self.manual_toggle_local_saving)
        tray_menu.addAction(toggle_local_saving_action)
        
        tray_menu.addSeparator()
        
        config_action = QAction("Configuration", self)
        config_action.triggered.connect(self.show_config)
        tray_menu.addAction(config_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Handle tray icon activation
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def setup_timers(self):
        """Setup update timers"""
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_statistics)
        self.stats_timer.start(1000)  # Update every second
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
    
    def manual_capture(self):
        """Manual screenshot capture"""
        self.client.capture_screenshot()
        self.add_log_entry("Manual screenshot captured")
    
    def manual_clipboard_text(self):
        """Manual clipboard text processing"""
        self.client.process_clipboard_text()
        self.add_log_entry("Manual clipboard text processed")
    
    def manual_clipboard_image(self):
        """Manual clipboard image processing"""
        self.client.process_clipboard_image()
        self.add_log_entry("Manual clipboard image processed")
    
    def manual_capture_local(self):
        """Manual local-only screenshot capture"""
        self.client.capture_screenshot_local_only()
        self.add_log_entry("Manual local-only screenshot captured")
    
    def manual_retry_uploads(self):
        """Manual retry failed uploads"""
        self.client.retry_failed_uploads()
        self.add_log_entry("Manual retry of failed uploads initiated")
    
    def manual_open_folder(self):
        """Manual open local folder"""
        self.client.open_local_folder()
        self.add_log_entry("Local folder opened")
    
    def manual_toggle_auto_upload(self):
        """Manual toggle auto-upload"""
        self.client.toggle_auto_upload()
        self.add_log_entry("Auto-upload toggled")
    
    def manual_toggle_local_saving(self):
        """Manual toggle local saving"""
        self.client.toggle_local_saving()
        self.add_log_entry("Local saving toggled")
    
    def show_notification(self, title, message):
        """Show system tray notification"""
        try:
            if self.tray_icon and self.tray_icon.isVisible():
                self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 3000)
            else:
                # Fallback to log entry
                self.add_log_entry(f"Notification: {title} - {message}")
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
    
    def show_config(self):
        """Show configuration dialog"""
        dialog = ConfigDialog(self.client.config, self)
        if dialog.exec_() == QDialog.Accepted:
            # Update configuration
            new_config = dialog.get_config()
            self.client.config = new_config
            self.client.save_config(new_config)
            
            # Re-register hotkey
            self.client.register_hotkey()
            self.hotkey_label.setText(f"Hotkey: {self.client.config.get('client', 'hotkey', fallback='ctrl+s')}")
            
            self.add_log_entry("Configuration updated")
    
    def update_statistics(self):
        """Update statistics display"""
        stats = self.client.get_statistics()
        
        self.screenshots_label.setText(str(stats['screenshots_captured']))
        self.uploads_success_label.setText(str(stats['uploads_successful']))
        self.uploads_failed_label.setText(str(stats['uploads_failed']))
        self.queue_size_label.setText(str(stats['queue_size']))
    
    def add_log_entry(self, message):
        """Add log entry to display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_text.append(log_entry)
        
        # Keep only last 100 entries
        if self.log_text.document().blockCount() > 100:
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, 1)
            cursor.movePosition(QTextCursor.StartOfBlock)
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
    
    def closeEvent(self, event):
        """Handle close event"""
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
            
            if self.client.config.getboolean('client', 'notifications', fallback=True):
                self.tray_icon.showMessage(
                    "ScreenshotOCR Client",
                    "Application was minimized to tray",
                    QSystemTrayIcon.Information,
                    2000
                )
        else:
            self.quit_application()
    
    def quit_application(self):
        """Quit application"""
        self.client.stop()
        QApplication.quit()

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Check for existing instance
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "System Tray", "System tray is not available on this system.")
        sys.exit(1)
    
    try:
        window = MainWindow()
        
        # Show window unless configured to start minimized
        if not window.client.config.getboolean('client', 'startup_minimized', fallback=True):
            window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        logger.error(traceback.format_exc())
        
        QMessageBox.critical(None, "Application Error", f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
