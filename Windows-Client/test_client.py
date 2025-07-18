#!/usr/bin/env python3
"""
Test script for ScreenshotOCR Windows Client
Tests API connection and basic functionality
"""

import os
import sys
import requests
import configparser
from datetime import datetime

def test_api_connection():
    """Test connection to ScreenshotOCR API"""
    print("Testing API Connection...")
    
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    api_url = config.get('API', 'api_url')
    api_token = config.get('API', 'api_token')
    timeout = int(config.get('Performance', 'timeout'))
    
    print(f"API URL: {api_url}")
    print(f"API Token: {api_token[:10]}...")
    
    try:
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        # Test health endpoint
        response = requests.get(
            f"{api_url}/health",
            headers=headers,
            timeout=timeout
        )
        
        if response.status_code == 200:
            print("✅ API connection successful")
            result = response.json()
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Message: {result.get('message', 'unknown')}")
            return True
        else:
            print(f"❌ API connection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def test_screenshot_endpoint():
    """Test screenshot upload endpoint"""
    print("\nTesting Screenshot Upload Endpoint...")
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    api_url = config.get('API', 'api_url')
    api_token = config.get('API', 'api_token')
    timeout = int(config.get('Performance', 'timeout'))
    
    try:
        # Create a test image
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple test image
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add some text
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "ScreenshotOCR Test Image", fill='black', font=font)
        draw.text((50, 100), f"Generated: {datetime.now()}", fill='black', font=font)
        
        # Convert to bytes
        import io
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Prepare request
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        files = {
            'image': ('test_screenshot.png', img_byte_arr, 'image/png')
        }
        
        data = {
            'timestamp': int(datetime.now().timestamp())
        }
        
        # Make request
        response = requests.post(
            f"{api_url}/screenshot",
            headers=headers,
            files=files,
            data=data,
            timeout=timeout
        )
        
        if response.status_code == 200:
            print("✅ Screenshot upload test successful")
            result = response.json()
            print(f"   Message: {result.get('message', 'unknown')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Screenshot upload test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Screenshot upload test error: {e}")
        return False

def test_clipboard_text_endpoint():
    """Test clipboard text upload endpoint"""
    print("\nTesting Clipboard Text Upload Endpoint...")
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    api_url = config.get('API', 'api_url')
    api_token = config.get('API', 'api_token')
    timeout = int(config.get('Performance', 'timeout'))
    
    try:
        # Test text
        test_text = f"This is a test clipboard text for ScreenshotOCR.\nGenerated at: {datetime.now()}\n\nThis text will be processed by the AI analysis system."
        
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        data = {
            'text': test_text,
            'language': 'auto',
            'timestamp': int(datetime.now().timestamp())
        }
        
        response = requests.post(
            f"{api_url}/clipboard/text",
            headers=headers,
            data=data,
            timeout=timeout
        )
        
        if response.status_code == 200:
            print("✅ Clipboard text upload test successful")
            result = response.json()
            print(f"   Message: {result.get('message', 'unknown')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Text Length: {result.get('text_length', 'unknown')}")
            return True
        else:
            print(f"❌ Clipboard text upload test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Clipboard text upload test error: {e}")
        return False

def test_clipboard_image_endpoint():
    """Test clipboard image upload endpoint"""
    print("\nTesting Clipboard Image Upload Endpoint...")
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    api_url = config.get('API', 'api_url')
    api_token = config.get('API', 'api_token')
    timeout = int(config.get('Performance', 'timeout'))
    
    try:
        # Create a test image
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (600, 400), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Clipboard Image Test", fill='black', font=font)
        draw.text((50, 100), f"Generated: {datetime.now()}", fill='black', font=font)
        draw.text((50, 150), "This image will be processed by OCR", fill='black', font=font)
        draw.text((50, 200), "and then analyzed by AI.", fill='black', font=font)
        
        # Convert to bytes
        import io
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        headers = {
            'Authorization': f'Bearer {api_token}'
        }
        
        files = {
            'image': ('test_clipboard_image.png', img_byte_arr, 'image/png')
        }
        
        data = {
            'timestamp': int(datetime.now().timestamp())
        }
        
        response = requests.post(
            f"{api_url}/clipboard/image",
            headers=headers,
            files=files,
            data=data,
            timeout=timeout
        )
        
        if response.status_code == 200:
            print("✅ Clipboard image upload test successful")
            result = response.json()
            print(f"   Message: {result.get('message', 'unknown')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Clipboard image upload test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Clipboard image upload test error: {e}")
        return False

def main():
    """Run all tests"""
    print("ScreenshotOCR Windows Client Test Suite")
    print("=======================================")
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Check if config file exists
    if not os.path.exists('config.ini'):
        print("❌ Configuration file 'config.ini' not found!")
        print("Please run the client first to create the default configuration.")
        return 1
    
    # Run tests
    tests = [
        test_api_connection,
        test_screenshot_endpoint,
        test_clipboard_text_endpoint,
        test_clipboard_image_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The client should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check your configuration and server status.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 