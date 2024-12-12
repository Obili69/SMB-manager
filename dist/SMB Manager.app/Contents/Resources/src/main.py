#!/usr/bin/env python3
import sys
import os
import logging
from datetime import datetime

# Set up logging first
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
        # Add version check
        if sys.version_info < (3, 6):
            raise RuntimeError("Python 3.6 or higher is required")
            
        # Import dependencies with error handling
        try:
            import rumps
            import keyring
        except ImportError as e:
            logger.error(f"Failed to import required dependencies: {str(e)}")
            sys.exit(1)
            
        # Continue with normal startup
        import argparse
        parser = argparse.ArgumentParser(description='SMB Connection Manager')
        parser.add_argument('--gui', action='store_true', help='Launch GUI')
        parser.add_argument('--menubar', action='store_true', help='Launch menubar app')
        args = parser.parse_args()

        if not (args.gui or args.menubar):
            args.menubar = True

        logger.info(f"Starting in {'GUI' if args.gui else 'menubar'} mode")

        if args.gui:
            from src.gui_manager import GUIManager
            app = GUIManager()
            app.mainloop()
        else:
            from src.menubar_app import SMBMenuBar
            app = SMBMenuBar()
            app.run()

    except Exception as e:
        logger.error(f"Fatal error during startup: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()



