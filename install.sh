#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${2}$1${NC}"
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
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip and install build tools
    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade setuptools wheel

    # Install dependencies with PEP 517
    python3 -m pip install --use-pep517 \
        rumps \
        keyring \
        pyobjc-core \
        pyobjc-framework-Cocoa \
        pyobjc-framework-Security \
        py2app==0.28.6
    
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

clean_build_directory() {
    print_status "Cleaning build directory..." "$YELLOW"
    # Remove .DS_Store files
    find . -name ".DS_Store" -delete
    # Remove old build artifacts
    rm -rf build dist *.pyc __pycache__ .eggs *.egg-info
}

build_application() {
    print_status "Building SMB Manager application..." "$YELLOW"
    
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    
    # Clean before building
    clean_build_directory
    
    # Build the application without code signing
    python3 setup_app.py py2app --no-strip
    
    if [ $? -eq 0 ]; then
        print_status "Application built successfully!" "$GREEN"
    else
        print_status "Failed to build application" "$RED"
        exit 1
    fi
}

install_application() {
    print_status "Installing application..." "$YELLOW"
    
    APPLICATIONS_PATH="/Applications"
    
    if [ -d "dist/SMB Manager.app" ]; then
        # Remove .DS_Store files from the built app
        find "dist/SMB Manager.app" -name ".DS_Store" -delete
        
        # Remove existing application if it exists
        rm -rf "$APPLICATIONS_PATH/SMB Manager.app"
        
        # Copy the application
        cp -R "dist/SMB Manager.app" "$APPLICATIONS_PATH/"
        
        if [ $? -eq 0 ]; then
            # Set permissions
            chmod -R 755 "$APPLICATIONS_PATH/SMB Manager.app"
            print_status "Application installed successfully in $APPLICATIONS_PATH!" "$GREEN"
        else
            print_status "Failed to copy application to $APPLICATIONS_PATH" "$RED"
            exit 1
        fi
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
    
    # Clean any existing .DS_Store files
    clean_build_directory
    
    install_python_dependencies
    
    read -p "Do you want to install Cloudflared for tunnel support? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_cloudflared
    fi
    
    build_application
    install_application
    
    cd - > /dev/null
    rm -rf "$tmp_dir"
    
    print_status "Installation complete! You can find SMB Manager in your Applications folder." "$GREEN"
    print_status "To start the application, open Finder and navigate to /Applications/SMB Manager.app" "$GREEN"
}

main