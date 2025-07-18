# ScreenshotOCR Windows Client

A background service that captures screenshots and clipboard content, then forwards them to the ScreenshotOCR webapp for AI analysis.

## Features

- **Screenshot Capture**: Take screenshots with hotkey (Ctrl+S by default)
- **Clipboard Text Processing**: Send clipboard text for AI analysis (Ctrl+Shift+T)
- **Clipboard Image Processing**: Send clipboard images for OCR and AI analysis (Ctrl+Shift+I)
- **Background Operation**: Runs silently in the background
- **Configurable Hotkeys**: Customize keyboard shortcuts
- **Local Backup**: Optional local saving of captured content
- **Comprehensive Logging**: Detailed logs for troubleshooting

## Prerequisites

- Windows 10/11
- Python 3.8 or higher
- Internet connection to reach the ScreenshotOCR server

## Installation

### Quick Install

1. **Download and Extract**: Extract the Windows-Client folder to your desired location
2. **Run Installer**: Double-click `install.bat` to install dependencies
3. **Verify Installation**: The installer will automatically test all packages
4. **Configure**: Edit `config.ini` if needed (see Configuration section)
5. **Start Client**: Double-click `start_client.bat` or run `python screenshot_client.py`

### Alternative Installation

If the standard installation fails, try the alternative installer:
1. **Run Alternative Installer**: Double-click `install_alternative.bat`
2. **Choose Installation Method**: Select the appropriate option based on your system
3. **Follow Instructions**: The installer will guide you through the process

### Manual Install

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test Installation** (optional):
   ```bash
   python test_installation.py
   ```

3. **Configure the Client**:
   - Edit `config.ini` to set your API URL and token
   - Customize hotkeys and settings as needed

4. **Start the Client**:
   ```bash
   python screenshot_client.py
   ```

## Configuration

The client uses `config.ini` for configuration. Key settings:

### API Configuration
```ini
[API]
api_url = http://10.0.0.44/api
api_token = 8BHxKkgbShG1vwhXje6MDnKYW5d55AwG47XuFma8c5cfNG5GUfJaopXz6cDuY0Df
```

### Hotkeys
```ini
[Hotkeys]
screenshot_hotkey = ctrl+s
clipboard_text_hotkey = ctrl+alt+t
clipboard_image_hotkey = ctrl+alt+i
```

### Settings
```ini
[Settings]
# Enable/disable features
enable_screenshots = true
enable_clipboard_text = true
enable_clipboard_image = true

# Local backup settings
save_locally = false
local_save_path = screenshots/

# OCR language (auto, eng, deu)
ocr_language = auto

# Logging
log_level = INFO
log_file = screenshot_client.log
```

## Usage

### Starting the Client

1. **Quick Start**: Double-click `start_client.bat`
2. **Command Line**: Run `python screenshot_client.py`
3. **Background Service**: The client will run silently in the background

### Using the Hotkeys

- **Ctrl+S**: Take a screenshot of the entire screen
- **Ctrl+Alt+T**: Send clipboard text for AI analysis
- **Ctrl+Alt+I**: Send clipboard image for OCR and AI analysis

### Stopping the Client

- Close the command window
- Or use Task Manager to end the process
- Note: Ctrl+C is used for clipboard text upload, so it won't stop the client

## How It Works

1. **Screenshot Capture**: When you press the screenshot hotkey, the client captures the entire screen
2. **Clipboard Processing**: When you press clipboard hotkeys, the client reads text or images from the clipboard
3. **API Upload**: Content is automatically uploaded to the ScreenshotOCR API
4. **AI Processing**: The server processes the content using OCR and AI analysis
5. **Results**: Results are stored in the database and available in the web interface

## Troubleshooting

### Installation Issues

1. **"Getting requirements to build wheel did not run successfully"**
   - Try the alternative installer: `install_alternative.bat`
   - Upgrade pip: `pip install --upgrade pip`
   - Install Visual Studio Build Tools (for Windows)
   - Try user installation: `pip install --user -r requirements.txt`

2. **"Python is not installed or not in PATH"**
   - Download and install Python 3.8+ from https://python.org
   - Make sure to check "Add Python to PATH" during installation
   - Restart your command prompt after installation

3. **"Permission denied" errors**
   - Run the installer as administrator
   - Use user installation: `pip install --user -r requirements.txt`
   - Check Windows Defender or antivirus settings

### Runtime Issues

1. **"Failed to connect to API"**
   - Check your internet connection
   - Verify the API URL in `config.ini`
   - Ensure the ScreenshotOCR server is running

2. **"No text found in clipboard"**
   - Make sure you have text copied to the clipboard
   - Try copying the text again

3. **"No image found in clipboard"**
   - Make sure you have an image copied to the clipboard
   - Try copying the image again

4. **Hotkeys not working**
   - Check if other applications are using the same hotkeys
   - Modify hotkeys in `config.ini`
   - Ensure the client is running with administrator privileges if needed

### Logs

Check the log file (`screenshot_client.log` by default) for detailed error messages and debugging information.

### Performance

- The client uses minimal system resources
- Screenshots are processed quickly and uploaded asynchronously
- Network timeouts are configurable in `config.ini`

## Security

- The client uses secure API token authentication
- No sensitive data is stored locally (unless explicitly configured)
- All communication with the server is over HTTP/HTTPS
- The API token should be kept secure and not shared

## Advanced Configuration

### Custom Hotkeys

You can customize hotkeys in `config.ini`:
```ini
[Hotkeys]
screenshot_hotkey = f12
clipboard_text_hotkey = ctrl+alt+t
clipboard_image_hotkey = ctrl+alt+i
```

### Local Backup

Enable local backup to save captured content:
```ini
[Settings]
save_locally = true
local_save_path = C:\Screenshots\
```

### Performance Tuning

Adjust performance settings:
```ini
[Performance]
timeout = 30
max_retries = 3
retry_delay = 2
max_file_size = 10
```

## Support

For issues and questions:
1. Check the log file for error messages
2. Verify your configuration in `config.ini`
3. Ensure the ScreenshotOCR server is accessible
4. Check the main ScreenshotOCR documentation

## License

This client is part of the ScreenshotOCR project and follows the same license terms. 