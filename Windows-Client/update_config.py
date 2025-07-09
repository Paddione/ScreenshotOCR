#!/usr/bin/env python3
"""
Configuration Update Script for ScreenshotOCR Windows Client
Updates existing configuration to use the correct domain
"""

import os
import configparser

def update_config():
    """Update existing configuration file to use correct domain"""
    config_file = 'client_config.ini'
    
    if not os.path.exists(config_file):
        print("No existing configuration file found. The client will create one with correct settings on first run.")
        return
    
    # Read existing config
    config = configparser.ConfigParser()
    config.read(config_file)
    
    # Check if update is needed
    current_url = config.get('client', 'server_url', fallback='')
    if current_url == 'https://10.0.0.44':
        print(f"Updating server URL from {current_url} to https://web.korczewski.de")
        config.set('client', 'server_url', 'https://web.korczewski.de')
        
        # Save updated config
        with open(config_file, 'w') as f:
            config.write(f)
        
        print("Configuration updated successfully!")
        print("You can now restart the Windows client and it should work correctly.")
    else:
        print(f"Configuration already uses correct domain: {current_url}")
        print("No update needed.")

if __name__ == "__main__":
    print("ScreenshotOCR Windows Client Configuration Updater")
    print("=" * 50)
    update_config()
    print("\nPress Enter to exit...")
    input() 