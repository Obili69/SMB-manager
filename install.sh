#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${2}$1${NC}"
}

# Get the localized Applications folder path
get_applications_path() {
    # First try to get the localized path
    local apps_path="$(osascript -e 'POSIX path of (path to applications folder)')"
    
    if [ -z "$apps_path" ]; then
        # Fallback to checking common locations
        if [ -d "/Applications" ]; then
            echo "/Applications"
        elif [ -d "/Programme" ]; then
            echo "/Programme"
        else
            echo "/Applications"  # Default fallback
        fi
    else
        echo "$apps_path"
    fi
}

check_python_version() {
    if command -v python3 >/dev/null 2>&1; then
        major=$(python3 -c 'import sys; print(sys.version_info.major)')
        minor=$(python3 -c 'import sys; print(sys.version_info.minor)')
        
        if [ "$major" -eq 3 ] && [ "$minor" -ge 6 ] || [ "$major" -gt 3 ]; then
            return 0
        fi
    fi
    return 1
}

install_python_dependencies() {
    print_status "Installing Python dependencies..." "$YELLOW"
    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install --upgrade pip
    python3 -m pip install rumps keyring py2app setuptools wheel
    if [ $? -eq 0 ]; then
        print_status "Python dependencies installed successfully!" "$GREEN"
    else
        print_status "Failed to install Python dependencies" "$RED"
        exit 1
    fi
}

install_cloudflared() {
    print_status "Installing Cloudflared..." "$YELLOW"
    if ! command -v brew >/dev/null 2>&1; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install cloudflare/cloudflare/cloudflared
}

build_application() {
    print_status "Building SMB Manager application..." "$YELLOW"
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    python3 setup_app.py py2app
    if [ $? -eq 0 ]; then
        print_status "Application built successfully!" "$GREEN"
    else
        print_status "Failed to build application" "$RED"
        exit 1
    fi
}

create_applications_symlink() {
    print_status "Creating application symlink..." "$YELLOW"
    
    # Get the localized Applications folder path
    APPLICATIONS_PATH=$(get_applications_path)
    print_status "Using Applications folder: $APPLICATIONS_PATH" "$YELLOW"
    
    if [ -d "dist/SMB Manager.app" ]; then
        mkdir -p "$APPLICATIONS_PATH"
        rm -f "$APPLICATIONS_PATH/SMB Manager.app"
        ln -s "$(pwd)/dist/SMB Manager.app" "$APPLICATIONS_PATH/"
        print_status "Application symlink created in $APPLICATIONS_PATH!" "$GREEN"
    else
        print_status "Application bundle not found in dist directory" "$RED"
        exit 1
    fi
}

main() {
    print_status "Starting SMB Manager installation..." "$YELLOW"
    
    if [[ "$(uname)" != "Darwin" ]]; then
        print_status "This installer only supports macOS" "$RED"
        exit 1
    fi
    
    python_version=$(python3 --version)
    print_status "Detected Python version: $python_version" "$YELLOW"
    
    if ! check_python_version; then
        print_status "Python 3.6 or later is required. Please install it first." "$RED"
        exit 1
    fi
    
    tmp_dir=$(mktemp -d)
    cd "$tmp_dir"
    
    print_status "Cloning repository..." "$YELLOW"
    git clone https://github.com/Obili69/SMB-manager.git .
    
    if [ $? -ne 0 ]; then
        print_status "Failed to clone repository" "$RED"
        exit 1
    fi
    
    install_python_dependencies
    
    read -p "Do you want to install Cloudflared for tunnel support? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_cloudflared
    fi
    
    build_application
    create_applications_symlink
    
    cd - > /dev/null
    rm -rf "$tmp_dir"
    
    # Get the localized path for the success message
    APPLICATIONS_PATH=$(get_applications_path)
    print_status "Installation complete! You can find SMB Manager in your $APPLICATIONS_PATH folder." "$GREEN"
    print_status "To start the application, open finder and navigate to $APPLICATIONS_PATH/SMB Manager.app" "$GREEN"
}

main
