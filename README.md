# SMB Manager for macOS

A powerful and user-friendly macOS application that provides simple management of SMB network shares through both a GUI interface and a menubar app. Perfect for users who need to regularly connect to SMB shares and want a streamlined experience. It lets you connect to a nas that uses a coudflared or directly to a ip/hostname. 

## Features

- **Dual Interface Options**:
  - Full GUI window for comprehensive management
  - Menubar quick access for convenient connections
  
- **Advanced Connection Management**:
  - Secure password storage using system keyring
  - Support for Cloudflared tunnels
  - Custom mount points
  - Auto-mount capabilities
  
- **Security**:
  - Credentials stored securely in macOS Keychain
  - Support for encrypted tunnel connections
  - No plaintext password storage
  
- **System Integration**:
  - Native macOS menubar integration
  - Launch at login option
  - Native SMB mounting using system commands

## Images
Streamlined integration
<img width="865" alt="Screenshot 2024-12-12 at 11 59 44" src="https://github.com/user-attachments/assets/1a8cdc59-a5c0-464f-b711-e840b6f6d491" />
Simple GUI
<img width="936" alt="Screenshot 2024-12-12 at 12 00 00" src="https://github.com/user-attachments/assets/fba6af53-8d7b-4ccf-aa09-fa38e521f0d7" />

## Prerequisites

- macOS 10.13 or later
- Python 3.6 or later
- Git (for installation)
- Xcode Command Line Tools

## Installation

### Method 1: Using the Installer Script (Recommended)

1. Download the installer script:
```bash
curl -O https://raw.githubusercontent.com/yourusername/smb-manager/main/install.sh
```

2. Make the script executable:
```bash
chmod +x install.sh
```

3. Run the installer:
```bash
./install.sh
```

The installer will:
- Check for system requirements
- Install necessary dependencies
- Optionally install Cloudflared for tunnel support
- Build the application
- Create a symlink in your Applications folder

After installation, you can find SMB Manager in your Applications folder.

### Method 2: Manual Installation

If you prefer to install manually or need to customize the installation:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smb-manager
cd smb-manager
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Build the application:
```bash
python setup_app.py py2app
```

The built application will be available in the `dist` directory.

### Optional: Installing Cloudflared

If you plan to use tunnel connections and didn't install it through the installer script:

```bash
# Using Homebrew
brew install cloudflare/cloudflare/cloudflared

# Verify installation
cloudflared --version
```

## Usage

### Starting the Application

There are two ways to start SMB Manager:

1. **Using the Application Bundle (Recommended)**:
- Open Finder
- Navigate to Applications folder
- Double-click "SMB Manager"

2. **Running from Source (Development)**:
```bash
# Menubar Mode (Default)
python src/main.py

# GUI Mode
python src/main.py --gui
```

### Initial Setup

1. Launch the application
2. Click "Open Manager" from the menubar icon
3. Configure your server settings:
   - Hostname (SMB server address)
   - Port (default: 8445)
   - Optional: Enable Cloudflared tunnel
   - Optional: Enable start at login

### Adding Shares

1. Open the manager window
2. Fill in the "Add New Share" section:
   - Username
   - Password
   - Share Path
3. Click "Add Share"

### Connecting to Shares

**Via GUI**:
- Select shares in the list
- Click "Connect All" or use the context menu to mount individual shares

**Via Menubar**:
- Click the menubar icon
- Select "Connect All" or manage individual shares

## Troubleshooting

### Common Issues

1. **Installation Problems**:
   - Make sure Xcode Command Line Tools are installed: `xcode-select --install`
   - Ensure you have Python 3.6 or later: `python3 --version`
   - Check if Git is installed: `git --version`

2. **Share Won't Mount**:
   - Verify server address and port
   - Check credentials
   - Ensure the share path is correct
   - Verify network connectivity

3. **Tunnel Connection Fails**:
   - Verify Cloudflared is installed
   - Check hostname configuration
   - Ensure Cloudflared has necessary permissions

4. **Password Not Saving**:
   - Grant keychain access when prompted
   - Try removing and re-adding the share

### Logs

Logs are stored in:
```
~/Library/Logs/SMBManager/smbmanager_YYYYMMDD.log
```

## Uninstallation

To uninstall SMB Manager:

1. Remove the application:
```bash
rm -rf ~/Applications/SMB\ Manager.app
```

2. Remove configuration files:
```bash
rm -rf ~/.smb_manager_config.json
```

3. Remove logs:
```bash
rm -rf ~/Library/Logs/SMBManager
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and feature requests, please create an issue in the GitHub repository.
