#!/usr/bin/env python3
"""
Enhanced Windows Client Setup Script
Sets up the ScreenshotOCR Windows Client with all enhanced features
"""

import os
import sys
import subprocess
import configparser
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("ScreenshotOCR Windows Client - Enhanced Edition Setup")
    print("=" * 60)
    print()

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("📋 Checking dependencies...")
    
    required_packages = [
        'PyQt5',
        'requests',
        'Pillow',
        'pywin32',
        'keyboard',
        'pystray',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies are installed!")
    return True

def create_enhanced_config():
    """Create enhanced configuration file"""
    print("\n⚙️ Creating enhanced configuration...")
    
    config = configparser.ConfigParser()
    config.add_section('client')
    
    # Enhanced configuration with all new hotkeys
    enhanced_config = {
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
    
    for key, value in enhanced_config.items():
        config.set('client', key, value)
    
    # Write configuration file
    with open('client_config.ini', 'w') as f:
        config.write(f)
    
    print("✅ Enhanced configuration created: client_config.ini")
    return True

def create_screenshots_folder():
    """Create screenshots folder"""
    print("\n📁 Creating screenshots folder...")
    
    screenshots_folder = Path('screenshots')
    screenshots_folder.mkdir(exist_ok=True)
    
    print(f"✅ Screenshots folder created: {screenshots_folder.absolute()}")
    return True

def print_hotkey_reference():
    """Print hotkey reference"""
    print("\n🔥 Enhanced Hotkeys Reference")
    print("-" * 40)
    print("Core Hotkeys:")
    print("  Ctrl+S           - Take screenshot")
    print("  Ctrl+Shift+T     - Process clipboard text")
    print("  Ctrl+Shift+I     - Process clipboard image")
    print()
    print("Enhanced Hotkeys:")
    print("  Ctrl+Shift+S     - Screenshot (local only)")
    print("  Ctrl+Shift+C     - Open configuration")
    print("  Ctrl+Shift+H     - Show/hide window")
    print("  Ctrl+Shift+R     - Retry failed uploads")
    print("  Ctrl+Shift+L     - Toggle local saving")
    print("  Ctrl+Shift+E     - Open screenshots folder")
    print("  Ctrl+Shift+Q     - Toggle auto-upload")
    print()

def print_usage_guide():
    """Print usage guide"""
    print("📖 Quick Start Guide")
    print("-" * 40)
    print("1. Run the client:")
    print("   python client.py")
    print()
    print("2. Configure settings (if needed):")
    print("   - Click 'Configuration' or press Ctrl+Shift+C")
    print("   - Set your server URL and API token")
    print("   - Customize hotkeys if desired")
    print()
    print("3. Start using enhanced features:")
    print("   - Take screenshots: Ctrl+S")
    print("   - Process clipboard: Ctrl+Shift+T / Ctrl+Shift+I")
    print("   - Local screenshots: Ctrl+Shift+S")
    print("   - Toggle settings: Ctrl+Shift+L / Ctrl+Shift+Q")
    print()
    print("4. System Tray:")
    print("   - Minimize to tray for background operation")
    print("   - Right-click tray icon for quick access")
    print()

def run_client():
    """Ask if user wants to run the client"""
    print("🚀 Setup Complete!")
    print("-" * 40)
    
    while True:
        choice = input("Do you want to run the enhanced client now? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            print("\nStarting ScreenshotOCR Windows Client - Enhanced Edition...")
            try:
                subprocess.run([sys.executable, 'client.py'], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Error starting client: {e}")
                return False
            except KeyboardInterrupt:
                print("\n👋 Client stopped by user")
                return True
            return True
        elif choice in ['n', 'no']:
            print("\n👋 Setup complete! Run 'python client.py' when ready.")
            return True
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def main():
    """Main setup function"""
    print_banner()
    
    # Check if we're in the right directory
    if not os.path.exists('client.py'):
        print("❌ Error: client.py not found!")
        print("Please run this script from the Windows-Client directory.")
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Create enhanced configuration
    if not create_enhanced_config():
        return False
    
    # Create screenshots folder
    if not create_screenshots_folder():
        return False
    
    # Print reference guides
    print_hotkey_reference()
    print_usage_guide()
    
    # Ask to run client
    return run_client()

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Enhanced Windows Client setup completed successfully!")
        else:
            print("\n❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1) 