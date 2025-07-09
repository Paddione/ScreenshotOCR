#!/usr/bin/env python3
"""
ScreenshotOCR Windows Client
PyQt5-based desktop application for automated screenshot capture and analysis
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
from PyQt5.QtGui import QIcon, QFont, QPixmap, QTextCursor

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
    """Main screenshot client class"""
    
    def __init__(self):
        self.config = self.load_config()
        self.upload_queue = Queue()
        self.retry_queue = Queue()
        self.is_running = False
        self.hotkey_registered = False
        self.screenshot_count = 0
        self.upload_success_count = 0
        self.upload_failed_count = 0
        
        # Setup upload thread
        self.upload_thread = None
        self.start_upload_thread()
        
        logger.info("ScreenshotOCR Windows Client initialized")
    
    def load_config(self):
        """Load configuration from file"""
        config = ConfigParser()
        config_file = 'client_config.ini'
        
        # Default configuration
        default_config = {
            'server_url': 'https://web.korczewski.de',
            'api_token': '8BHxKkgbShG1vwhXje6MDnKYW5d55AwG47XuFma8c5cfNG5GUfJaopXz6cDuY0Df',
            'hotkey': 'ctrl+s',
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
            'verify_ssl': 'true'
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
        """Register global hotkey"""
        try:
            hotkey = self.config.get('client', 'hotkey', fallback='ctrl+s')
            
            if self.hotkey_registered:
                keyboard.unhook_all()
                self.hotkey_registered = False
            
            keyboard.add_hotkey(hotkey, self.capture_screenshot)
            self.hotkey_registered = True
            
            logger.info(f"Hotkey registered: {hotkey}")
            
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")
    
    def capture_screenshot(self):
        """Capture screenshot of active window"""
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
            
            # Process screenshot
            self.process_screenshot(image)
            
            self.screenshot_count += 1
            logger.info(f"Screenshot captured successfully (#{self.screenshot_count})")
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
    
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
                            logger.error(f"Max retries exceeded for {item['filename']}")
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Upload worker error: {e}")
                time.sleep(5)
    
    def upload_screenshot(self, item):
        """Upload screenshot to server"""
        try:
            server_url = self.config.get('client', 'server_url', fallback='https://web.korczewski.de')
            api_token = self.config.get('client', 'api_token', fallback='')
            
            if not api_token:
                logger.error("API token not configured")
                return False
            
            # Prepare image data
            from io import BytesIO
            image_buffer = BytesIO()
            item['image'].save(image_buffer, format='PNG')
            image_buffer.seek(0)
            
            # Prepare request
            url = f"{server_url}/api/screenshot"
            headers = {
                'Authorization': f'Bearer {api_token}',
                'User-Agent': 'ScreenshotOCR-WindowsClient/1.0'
            }
            
            files = {
                'image': (item['filename'], image_buffer, 'image/png')
            }
            
            data = {
                'timestamp': item['timestamp']
            }
            
            # Determine SSL verification based on URL
            # For IP addresses and localhost, disable SSL verification
            # For proper domains, enable SSL verification
            import re
            verify_ssl = self.config.getboolean('client', 'verify_ssl', fallback=True)
            
            # Check if URL contains IP address or localhost
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            if ('localhost' in server_url.lower() or 
                '127.0.0.1' in server_url or 
                re.search(ip_pattern, server_url) or
                not verify_ssl):
                ssl_verify = False
                logger.debug(f"SSL verification disabled for {server_url}")
                # Suppress SSL warnings for development
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            else:
                ssl_verify = True
                logger.debug(f"SSL verification enabled for {server_url}")
            
            # Make request
            response = requests.post(
                url, 
                headers=headers, 
                files=files, 
                data=data, 
                timeout=30,
                verify=ssl_verify
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
        
        capture_layout.addRow("Hotkey:", self.hotkey)
        capture_layout.addRow("Capture Delay:", self.capture_delay)
        capture_layout.addRow("Auto Upload:", self.auto_upload)
        
        capture_tab.setLayout(capture_layout)
        tab_widget.addTab(capture_tab, "Capture")
        
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
        self.tray_icon = None
        self.init_ui()
        self.init_tray()
        self.setup_timers()
        
        # Start client
        self.client.start()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("ScreenshotOCR Windows Client")
        self.setFixedSize(600, 500)
        
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
        button_layout = QHBoxLayout()
        
        self.capture_button = QPushButton("Take Screenshot")
        self.capture_button.clicked.connect(self.manual_capture)
        
        self.config_button = QPushButton("Configuration")
        self.config_button.clicked.connect(self.show_config)
        
        self.minimize_button = QPushButton("Minimize to Tray")
        self.minimize_button.clicked.connect(self.hide)
        
        button_layout.addWidget(self.capture_button)
        button_layout.addWidget(self.config_button)
        button_layout.addWidget(self.minimize_button)
        
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
