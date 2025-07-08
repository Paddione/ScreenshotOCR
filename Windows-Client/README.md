# ScreenshotOCR Windows Client

A comprehensive Windows desktop application for automated screenshot capture and analysis, integrated with the ScreenshotOCR system.

## 🚀 Features

### Core Functionality
- **Global Hotkey Support**: Configurable hotkey for instant screenshot capture (default: Ctrl+S)
- **Active Window Capture**: High-quality screenshot capture using Win32 API
- **Automatic Upload**: Seamless integration with ScreenshotOCR server
- **Offline Queue**: Retry mechanism for failed uploads with configurable attempts
- **Local Storage**: Optional local saving of screenshots with compression
- **System Tray Integration**: Minimizes to system tray for background operation

### User Interface
- **Modern PyQt5 GUI**: Clean, responsive interface
- **Configuration Dialog**: Easy-to-use settings management
- **Real-time Statistics**: Live monitoring of capture and upload statistics
- **Activity Log**: Real-time log display with auto-scrolling
- **Tabbed Configuration**: Organized settings across multiple tabs

### Network & Storage
- **Secure Communication**: HTTPS with bearer token authentication
- **Configurable Retry Logic**: Customizable retry attempts and delays
- **Compression Options**: Adjustable image quality settings
- **Folder Organization**: Configurable local screenshot storage

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10 or later
- **Python**: 3.8 or later
- **Network**: Internet connection for server communication
- **System Tray**: Required for background operation

### Dependencies
All dependencies are listed in `requirements.txt`:
```
PyQt5==5.15.10
PyQt5-Qt5==5.15.2
PyQt5-sip==12.13.0
requests==2.31.0
Pillow==10.0.0
pywin32==306
keyboard==0.13.5
pystray==0.19.4
configparser==6.0.0
cryptography==41.0.7
```

## 🛠️ Installation

### Method 1: Using Python Environment
```bash
# Navigate to the Windows-Client directory
cd Windows-Client

# Install dependencies
pip install -r requirements.txt

# Run the application
python client.py
```

### Method 2: Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python client.py
```

### Method 3: Create Executable (Optional)
```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --icon=icon.ico client.py

# Run from dist folder
dist\client.exe
```

### 🔧 Troubleshooting Installation Issues

#### Python 3.13 Compatibility
If you encounter wheel building errors with Python 3.13, try these solutions:

**Solution 1: Updated Requirements (Recommended)**
The requirements.txt has been updated with Python 3.13 compatible versions. Try installing again:
```bash
pip install -r requirements.txt
```

**Solution 2: Use Python 3.11 or 3.12 (Most Stable)**
If you continue having issues, use a more stable Python version:
```bash
# Download Python 3.11 from python.org
# Then create virtual environment with Python 3.11
python3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Solution 3: Install Packages Individually**
If bulk installation fails, try installing packages one by one:
```bash
pip install PyQt5==5.15.11
pip install requests==2.32.3
pip install Pillow==10.4.0
pip install pywin32==308
pip install keyboard==0.13.5
pip install pystray==0.19.5
pip install configparser==6.0.1
pip install cryptography==43.0.1
```

**Solution 4: Alternative PyQt6 Installation**
If PyQt5 continues to cause issues, you can try PyQt6:
```bash
pip install PyQt6 requests Pillow pywin32 keyboard pystray configparser cryptography
```
*Note: This would require minor code modifications to import PyQt6 instead of PyQt5*

#### Common Installation Errors

**Error: "subprocess-exited-with-error"**
- This usually indicates a package doesn't have pre-compiled wheels for your Python version
- Try using Python 3.11 or 3.12 instead of 3.13
- Ensure you have the latest pip: `python -m pip install --upgrade pip`

**Error: "Microsoft Visual C++ 14.0 is required"**
This is the most common Windows installation error. Here are several solutions:

**Solution 1: Install Visual Studio Build Tools (Recommended)**
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Build Tools for Visual Studio 2022"
3. Select "C++ build tools" workload during installation
4. Restart command prompt and try again

**Solution 2: Use Pre-compiled Wheels (Fastest)**
```bash
python -m pip install --upgrade pip
pip install --only-binary=all PyQt5==5.15.10
pip install -r requirements.txt
```

**Solution 3: Force Wheel Installation**
```bash
pip install --only-binary=:all: -r requirements.txt
```

**Solution 4: Manual PyQt5 Installation**
```bash
pip install PyQt5==5.15.10 --find-links https://download.qt.io/official_releases/QtForPython/
```

**Error: "No module named 'PyQt5'"**
- Ensure virtual environment is activated
- Try installing PyQt5 separately: `pip install PyQt5==5.15.11`

#### System Requirements Check
```bash
# Check Python version
python --version

# Check pip version
pip --version

# Upgrade pip if needed
python -m pip install --upgrade pip
```

## ⚙️ Configuration

The client automatically creates a configuration file (`client_config.ini`) on first run with default settings.

### Default Configuration
```ini
[client]
server_url = https://10.0.0.44
api_token = 8BHxKkgbShG1vwhXje6MDnKYW5d55AwG47XuFma8c5cfNG5GUfJaopXz6cDuY0Df
hotkey = ctrl+s
capture_delay = 0.5
auto_upload = true
save_locally = true
local_folder = screenshots
retry_attempts = 3
retry_delay = 5
compression_quality = 85
capture_cursor = false
startup_minimized = true
notifications = true
verify_ssl = true
```

### Configuration Tabs

#### 1. Server Configuration
- **Server URL**: ScreenshotOCR server address
- **API Token**: Authentication token for server access

#### 2. Capture Settings
- **Hotkey**: Global hotkey combination (e.g., ctrl+s, alt+f1)
- **Capture Delay**: Delay before screenshot capture (in seconds)
- **Auto Upload**: Automatically upload captured screenshots

#### 3. Storage Settings
- **Save Locally**: Save screenshots to local disk
- **Local Folder**: Directory for local screenshot storage
- **Compression Quality**: Image compression level (1-100%)

#### 4. Network Settings
- **Retry Attempts**: Number of upload retry attempts
- **Retry Delay**: Delay between retry attempts (in seconds)
- **Verify SSL Certificates**: Enable/disable SSL certificate verification (disable for development with self-signed certificates)

## 🎯 Usage

### Basic Operation
1. **Launch the Application**: Run `python client.py`
2. **Configure Settings**: Click "Configuration" to setup server details
3. **Start Capturing**: Use the configured hotkey or click "Take Screenshot"
4. **Monitor Activity**: View statistics and logs in the main window
5. **Minimize to Tray**: Click "Minimize to Tray" for background operation

### Hotkey Combinations
Common hotkey formats:
- `ctrl+s` - Control + S
- `alt+f1` - Alt + F1
- `ctrl+shift+s` - Control + Shift + S
- `win+s` - Windows + S

### System Tray Menu
Right-click the tray icon for quick access to:
- **Show**: Restore main window
- **Take Screenshot**: Capture screenshot immediately
- **Configuration**: Open settings dialog
- **Quit**: Exit application

## 🔧 Integration with ScreenshotOCR System

### API Integration
The client communicates with the ScreenshotOCR server using the REST API:

```
POST /api/screenshot
Authorization: Bearer <API_TOKEN>
Content-Type: multipart/form-data

Form Data:
- image: PNG image file
- timestamp: Unix timestamp
```

### Processing Flow
```
Windows Client → Screenshot Capture → Local Storage (optional) → 
Server Upload → Redis Queue → OCR Processing → AI Analysis → 
Database Storage → Web Dashboard
```

### Authentication
The client uses the `API_AUTH_TOKEN` from the server configuration:
- Token is stored in the configuration file
- Sent as Bearer token in Authorization header
- Required for all API requests

### Error Handling
- **Connection Issues**: Automatic retry with exponential backoff
- **Authentication Errors**: Logged with detailed error messages
- **Server Errors**: Queued for retry with configurable attempts
- **Invalid Responses**: Comprehensive error logging

## 📊 Monitoring & Statistics

### Real-time Statistics
- **Screenshots Captured**: Total number of screenshots taken
- **Uploads Successful**: Number of successful server uploads
- **Uploads Failed**: Number of failed upload attempts
- **Queue Size**: Current number of items waiting for upload

### Activity Log
- **Timestamped Entries**: All activities with precise timestamps
- **Auto-scrolling**: Latest entries automatically visible
- **Log Rotation**: Maintains last 100 entries for performance
- **Detailed Logging**: Comprehensive error and status information

### Log Files
- **screenshot_client.log**: Persistent log file for troubleshooting
- **Automatic Rotation**: Log file management for disk space
- **Error Tracking**: Detailed error traces and stack dumps

## 🔒 Security Features

### Authentication
- **Bearer Token**: Secure API token authentication
- **Token Encryption**: Configuration file protection
- **HTTPS Communication**: All server communication encrypted

### Privacy
- **Local Storage**: Screenshots stored locally if configured
- **Configurable Upload**: Optional automatic upload
- **Data Control**: Full control over data transmission

### Error Recovery
- **Offline Queue**: Works without internet connection
- **Retry Logic**: Automatic retry for failed uploads
- **Graceful Degradation**: Continues operating during server issues

## 🐛 Troubleshooting

### Common Issues

#### 1. Hotkey Not Working
- **Check Conflicts**: Ensure hotkey isn't used by another application
- **Administrator Rights**: Run as administrator if required
- **Keyboard Hook**: Restart application to re-register hotkey

#### 2. Upload Failures
- **Server Status**: Verify ScreenshotOCR server is running
- **Network Connection**: Check internet connectivity
- **API Token**: Verify token is correct in configuration
- **Firewall**: Ensure application can access the internet

#### 2.1. SSL Certificate Errors
If you encounter SSL certificate verification errors (especially with IP addresses like `10.0.0.44`):

**Error Message Example:**
```
SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate'))
```

**Solutions:**
1. **Automatic Detection (Recommended)**: The client automatically disables SSL verification for IP addresses and localhost
2. **Manual Configuration**: In Configuration → Network → Uncheck "Verify SSL Certificates"
3. **Development Servers**: SSL verification is automatically disabled for:
   - IP addresses (e.g., `10.0.0.44`, `192.168.1.100`)
   - Localhost (`localhost`, `127.0.0.1`)
   - When `verify_ssl=false` in configuration

**Note**: SSL verification is automatically enabled for proper domain names to maintain security.

#### 3. Screenshot Capture Issues
- **Window Focus**: Ensure target window is active
- **Resolution**: High-resolution displays may cause issues
- **Permissions**: Check Windows permissions for screen capture

#### 4. System Tray Issues
- **System Tray Service**: Ensure Windows system tray is enabled
- **Notification Area**: Check hidden icons in notification area
- **Restart Required**: Restart application if tray icon doesn't appear

### Log Analysis
Check `screenshot_client.log` for detailed error information:
```bash
# View recent log entries
tail -f screenshot_client.log

# Search for errors
grep "ERROR" screenshot_client.log

# Check upload failures
grep "Upload failed" screenshot_client.log
```

### Configuration Reset
To reset configuration to defaults:
1. Close the application
2. Delete `client_config.ini`
3. Restart the application

## 🔄 Updates & Maintenance

### Update Process
1. **Backup Configuration**: Save `client_config.ini`
2. **Download Updates**: Get latest version from repository
3. **Install Dependencies**: Run `pip install -r requirements.txt`
4. **Restore Configuration**: Replace configuration file if needed

### Maintenance Tasks
- **Log Cleanup**: Periodically clean old log files
- **Screenshot Cleanup**: Remove old local screenshots
- **Configuration Review**: Verify settings are current
- **Performance Monitoring**: Check statistics for unusual patterns

## 📞 Support

### Getting Help
- **Documentation**: Check README.md and configuration files
- **Log Files**: Review screenshot_client.log for error details
- **System Requirements**: Verify all dependencies are installed
- **Server Status**: Check ScreenshotOCR server health

### Reporting Issues
When reporting issues, include:
1. **Error Message**: Complete error text from logs
2. **Configuration**: Relevant configuration settings (without API token)
3. **System Information**: Windows version, Python version
4. **Steps to Reproduce**: Detailed steps that cause the issue

---

**Note**: This Windows client is designed specifically for the ScreenshotOCR system and requires a running ScreenshotOCR server instance for full functionality. 