#!/usr/bin/env python3
"""
ScreenshotOCR Windows Client
A background service that captures screenshots and clipboard content,
then forwards them to the ScreenshotOCR webapp for AI analysis.
"""

import os
import sys
import time
import json
import logging
import configparser
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import requests
import keyboard
import pyautogui
from PIL import Image, ImageGrab
import win32clipboard
import win32gui
import win32con
import win32api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ScreenshotOCRClient:
    """Main client class for ScreenshotOCR Windows client"""
    
    def __init__(self, config_path: str = "config.ini"):
        """Initialize the client with configuration"""
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # API configuration
        self.api_url = self.config.get('API', 'api_url')
        self.api_token = self.config.get('API', 'api_token')
        self.timeout = int(self.config.get('Performance', 'timeout'))
        self.max_retries = int(self.config.get('Performance', 'max_retries'))
        self.retry_delay = int(self.config.get('Performance', 'retry_delay'))
        
        # Settings
        self.enable_screenshots = self.config.getboolean('Settings', 'enable_screenshots')
        self.enable_clipboard_text = self.config.getboolean('Settings', 'enable_clipboard_text')
        self.enable_clipboard_image = self.config.getboolean('Settings', 'enable_clipboard_image')
        self.save_locally = self.config.getboolean('Settings', 'save_locally')
        self.local_save_path = self.config.get('Settings', 'local_save_path')
        self.default_folder_id = self.config.get('Settings', 'default_folder_id')
        self.ocr_language = self.config.get('Settings', 'ocr_language')
        
        # Hotkeys
        self.screenshot_hotkey = self.config.get('Hotkeys', 'screenshot_hotkey')
        self.clipboard_text_hotkey = self.config.get('Hotkeys', 'clipboard_text_hotkey')
        self.clipboard_image_hotkey = self.config.get('Hotkeys', 'clipboard_image_hotkey')
        
        # Create local save directory if needed
        if self.save_locally and self.local_save_path:
            Path(self.local_save_path).mkdir(parents=True, exist_ok=True)
        
        self.logger.info("ScreenshotOCR Windows Client initialized")
        self.logger.info(f"API URL: {self.api_url}")
        self.logger.info(f"Features enabled - Screenshots: {self.enable_screenshots}, "
                        f"Clipboard Text: {self.enable_clipboard_text}, "
                        f"Clipboard Image: {self.enable_clipboard_image}")
    
    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        """Load configuration from file"""
        config = configparser.ConfigParser()
        
        if not os.path.exists(config_path):
            self._create_default_config(config_path)
        
        config.read(config_path)
        return config
    
    def _create_default_config(self, config_path: str):
        """Create default configuration file"""
        config = configparser.ConfigParser()
        
        config['API'] = {
            'api_url': 'http://10.0.0.44/api',
            'api_token': '8BHxKkgbShG1vwhXje6MDnKYW5d55AwG47XuFma8c5cfNG5GUfJaopXz6cDuY0Df'
        }
        
        config['Hotkeys'] = {
            'screenshot_hotkey': 'ctrl+s',
            'clipboard_text_hotkey': 'ctrl+alt+t',
            'clipboard_image_hotkey': 'ctrl+alt+i'
        }
        
        config['Settings'] = {
            'screenshot_format': 'PNG',
            'screenshot_quality': '95',
            'save_locally': 'false',
            'local_save_path': 'screenshots/',
            'default_folder_id': '',
            'ocr_language': 'auto',
            'enable_screenshots': 'true',
            'enable_clipboard_text': 'true',
            'enable_clipboard_image': 'true',
            'log_level': 'INFO',
            'log_file': 'screenshot_client.log'
        }
        
        config['Performance'] = {
            'timeout': '30',
            'max_retries': '3',
            'retry_delay': '2',
            'max_file_size': '10'
        }
        
        with open(config_path, 'w') as f:
            config.write(f)
        
        print(f"Created default configuration file: {config_path}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config.get('Settings', 'log_level', fallback='INFO')
        log_file = self.config.get('Settings', 'log_file', fallback='screenshot_client.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _get_clipboard_text(self) -> Optional[str]:
        """Get text from clipboard"""
        try:
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    return data if data else None
                elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                    data = win32clipboard.GetClipboardData(win32con.CF_TEXT)
                    return data.decode('utf-8') if data else None
            finally:
                win32clipboard.CloseClipboard()
        except Exception as e:
            self.logger.error(f"Error getting clipboard text: {e}")
            return None
    
    def _get_clipboard_image(self) -> Optional[Image.Image]:
        """Get image from clipboard"""
        try:
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB):
                    data = win32clipboard.GetClipboardData(win32con.CF_DIB)
                    # Convert DIB to PIL Image
                    import io
                    from PIL import Image
                    
                    # Create a temporary file to save the DIB data
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.bmp') as tmp_file:
                        tmp_file.write(data)
                        tmp_file_path = tmp_file.name
                    
                    try:
                        image = Image.open(tmp_file_path)
                        return image
                    finally:
                        os.unlink(tmp_file_path)
            finally:
                win32clipboard.CloseClipboard()
        except Exception as e:
            self.logger.error(f"Error getting clipboard image: {e}")
            return None
    
    def _take_screenshot(self) -> Optional[Image.Image]:
        """Take a screenshot of the entire screen"""
        try:
            screenshot = pyautogui.screenshot()
            self.logger.info("Screenshot captured successfully")
            return screenshot
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return None
    
    def _save_image_locally(self, image: Image.Image, prefix: str = "screenshot") -> Optional[str]:
        """Save image locally if enabled"""
        if not self.save_locally or not self.local_save_path:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.png"
            filepath = os.path.join(self.local_save_path, filename)
            
            image.save(filepath, "PNG", quality=95)
            self.logger.info(f"Image saved locally: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error saving image locally: {e}")
            return None
    
    def _upload_screenshot(self, image: Image.Image) -> bool:
        """Upload screenshot to ScreenshotOCR API"""
        try:
            # Convert PIL image to bytes
            import io
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {self.api_token}'
            }
            
            # Prepare files
            files = {
                'image': ('screenshot.png', img_byte_arr, 'image/png')
            }
            
            # Prepare data
            data = {
                'timestamp': int(time.time())
            }
            
            if self.default_folder_id:
                data['folder_id'] = self.default_folder_id
            
            # Make request
            response = requests.post(
                f"{self.api_url}/screenshot",
                headers=headers,
                files=files,
                data=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Screenshot uploaded successfully: {result.get('message', '')}")
                return True
            else:
                self.logger.error(f"Screenshot upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error uploading screenshot: {e}")
            return False
    
    def _upload_clipboard_text(self, text: str) -> bool:
        """Upload clipboard text to ScreenshotOCR API"""
        try:
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {self.api_token}'
            }
            
            # Prepare data
            data = {
                'text': text,
                'language': self.ocr_language,
                'timestamp': int(time.time())
            }
            
            if self.default_folder_id:
                data['folder_id'] = self.default_folder_id
            
            # Make request
            response = requests.post(
                f"{self.api_url}/clipboard/text",
                headers=headers,
                data=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Clipboard text uploaded successfully: {result.get('message', '')}")
                return True
            else:
                self.logger.error(f"Clipboard text upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error uploading clipboard text: {e}")
            return False
    
    def _upload_clipboard_image(self, image: Image.Image) -> bool:
        """Upload clipboard image to ScreenshotOCR API"""
        try:
            # Convert PIL image to bytes
            import io
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {self.api_token}'
            }
            
            # Prepare files
            files = {
                'image': ('clipboard_image.png', img_byte_arr, 'image/png')
            }
            
            # Prepare data
            data = {
                'timestamp': int(time.time())
            }
            
            if self.default_folder_id:
                data['folder_id'] = self.default_folder_id
            
            # Make request
            response = requests.post(
                f"{self.api_url}/clipboard/image",
                headers=headers,
                files=files,
                data=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Clipboard image uploaded successfully: {result.get('message', '')}")
                return True
            else:
                self.logger.error(f"Clipboard image upload failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error uploading clipboard image: {e}")
            return False
    
    def _handle_screenshot_hotkey(self):
        """Handle screenshot hotkey press"""
        if not self.enable_screenshots:
            return
        
        self.logger.info("Screenshot hotkey pressed")
        
        # Take screenshot
        screenshot = self._take_screenshot()
        if not screenshot:
            self.logger.error("Failed to capture screenshot")
            return
        
        # Save locally if enabled
        self._save_image_locally(screenshot, "screenshot")
        
        # Upload to API
        success = self._upload_screenshot(screenshot)
        if success:
            self.logger.info("Screenshot processed successfully")
        else:
            self.logger.error("Failed to upload screenshot")
    
    def _handle_clipboard_text_hotkey(self):
        """Handle clipboard text hotkey press"""
        if not self.enable_clipboard_text:
            return
        
        self.logger.info("Clipboard text hotkey pressed")
        
        # Get clipboard text
        text = self._get_clipboard_text()
        if not text:
            self.logger.warning("No text found in clipboard")
            return
        
        self.logger.info(f"Clipboard text length: {len(text)} characters")
        
        # Upload to API
        success = self._upload_clipboard_text(text)
        if success:
            self.logger.info("Clipboard text processed successfully")
        else:
            self.logger.error("Failed to upload clipboard text")
    
    def _handle_clipboard_image_hotkey(self):
        """Handle clipboard image hotkey press"""
        if not self.enable_clipboard_image:
            return
        
        self.logger.info("Clipboard image hotkey pressed")
        
        # Get clipboard image
        image = self._get_clipboard_image()
        if not image:
            self.logger.warning("No image found in clipboard")
            return
        
        self.logger.info(f"Clipboard image size: {image.size}")
        
        # Save locally if enabled
        self._save_image_locally(image, "clipboard")
        
        # Upload to API
        success = self._upload_clipboard_image(image)
        if success:
            self.logger.info("Clipboard image processed successfully")
        else:
            self.logger.error("Failed to upload clipboard image")
    
    def _test_api_connection(self) -> bool:
        """Test connection to ScreenshotOCR API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}'
            }
            
            response = requests.get(
                f"{self.api_url}/health",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.logger.info("API connection test successful")
                return True
            else:
                self.logger.error(f"API connection test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"API connection test error: {e}")
            return False
    
    def start(self):
        """Start the ScreenshotOCR client service"""
        self.logger.info("Starting ScreenshotOCR Windows Client...")
        
        # Test API connection
        if not self._test_api_connection():
            self.logger.error("Failed to connect to ScreenshotOCR API. Please check your configuration.")
            return False
        
        # Register hotkeys
        if self.enable_screenshots:
            keyboard.add_hotkey(self.screenshot_hotkey, self._handle_screenshot_hotkey)
            self.logger.info(f"Screenshot hotkey registered: {self.screenshot_hotkey}")
        
        if self.enable_clipboard_text:
            keyboard.add_hotkey(self.clipboard_text_hotkey, self._handle_clipboard_text_hotkey)
            self.logger.info(f"Clipboard text hotkey registered: {self.clipboard_text_hotkey}")
        
        if self.enable_clipboard_image:
            keyboard.add_hotkey(self.clipboard_image_hotkey, self._handle_clipboard_image_hotkey)
            self.logger.info(f"Clipboard image hotkey registered: {self.clipboard_image_hotkey}")
        
        self.logger.info("ScreenshotOCR Windows Client is running.")
        self.logger.info("Note: Ctrl+C is used for clipboard text upload, so the client will continue running.")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    
    def stop(self):
        """Stop the ScreenshotOCR client service"""
        self.logger.info("Stopping ScreenshotOCR Windows Client...")
        keyboard.unhook_all()


def main():
    """Main entry point"""
    print("ScreenshotOCR Windows Client")
    print("============================")
    print("This client will run in the background and capture:")
    print("- Screenshots (Ctrl+S)")
    print("- Clipboard text (Ctrl+Alt+T)")
    print("- Clipboard images (Ctrl+Alt+I)")
    print("")
    print("Note: Ctrl+C is used for clipboard text upload, so the client will continue running.")
    print("To stop the client, close this window or use Task Manager.")
    print("")
    
    # Create and start client
    client = ScreenshotOCRClient()
    
    try:
        client.start()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 