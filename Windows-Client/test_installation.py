#!/usr/bin/env python3
"""
Test script to verify Windows Client installation
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name} - FAILED: {e}")
        return False

def main():
    """Test all required packages"""
    print("ScreenshotOCR Windows Client - Installation Test")
    print("=" * 50)
    
    # List of required packages
    packages = [
        ("requests", "requests"),
        ("PIL", "Pillow"),
        ("pyautogui", "pyautogui"),
        ("keyboard", "keyboard"),
        ("psutil", "psutil"),
        ("win32clipboard", "pywin32"),
        ("win32gui", "pywin32"),
        ("win32con", "pywin32"),
        ("win32api", "pywin32"),
        ("dotenv", "python-dotenv"),
        ("schedule", "schedule"),
    ]
    
    print(f"Python version: {sys.version}")
    print()
    
    passed = 0
    total = len(packages)
    
    for module, package in packages:
        if test_import(module, package):
            passed += 1
    
    print()
    print("=" * 50)
    print(f"Test Results: {passed}/{total} packages installed successfully")
    
    if passed == total:
        print("🎉 All packages installed correctly!")
        print("The Windows Client should work properly.")
        return 0
    else:
        print("⚠️  Some packages failed to install.")
        print("Please run the installer again or try the alternative installer.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 