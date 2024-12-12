#!/usr/bin/env python3
import argparse
import sys
import os
import logging
from datetime import datetime
import tkinter as tk

# Set up logging
log_dir = os.path.expanduser('~/Library/Logs/SMBManager')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'smbmanager_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('SMBManager')

def check_tk():
    """Test if Tk is working properly"""
    try:
        root = tk.Tk()
        root.withdraw()
        return True
    except Exception as e:
        logger.error(f"Tk initialization failed: {str(e)}", exc_info=True)
        return False

def main():
    try:
        logger.info("Starting SMB Manager")
        parser = argparse.ArgumentParser(description='SMB Connection Manager')
        parser.add_argument('--gui', action='store_true', help='Launch GUI')
        parser.add_argument('--menubar', action='store_true', help='Launch menubar app')
        args = parser.parse_args()

        # If no arguments provided, default to menubar mode
        if not (args.gui or args.menubar):
            args.menubar = True
        
        logger.info(f"Arguments parsed: gui={args.gui}, menubar={args.menubar}")

        if args.gui:
            logger.info("Checking Tk availability")
            if not check_tk():
                logger.error("Tk not available - cannot start GUI")
                sys.exit(1)
                
            logger.info("Initializing GUI")
            from src.gui_manager import GUIManager
            app = GUIManager()
            logger.info("Running GUI")
            app.mainloop()
        elif args.menubar:
            logger.info("Initializing menubar app")
            from src.menubar_app import SMBMenuBar
            app = SMBMenuBar()
            logger.info("Running menubar app")
            app.run()

    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Uncaught exception: {str(e)}", exc_info=True)
        sys.exit(1)