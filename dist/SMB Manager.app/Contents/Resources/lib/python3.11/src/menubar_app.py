# File: src/menubar_app.py
import rumps
import subprocess
import sys
import os
import logging
from pathlib import Path

logger = logging.getLogger('SMBManager')

class SMBMenuBar(rumps.App):
    def __init__(self):
        super().__init__("SMB")
        
        # Initialize managers
        from src.config_manager import ConfigManager
        from src.mount_manager import MountManager
        
        self.config_manager = ConfigManager()
        self.mount_manager = MountManager()
        self.config = self.config_manager.load_config()
        
        # Setup menu
        self.menu = [
            rumps.MenuItem("Open Manager", callback=self.show_manager),
            None,  # Separator
            rumps.MenuItem("Connect All", callback=self.connect_all),
            rumps.MenuItem("Disconnect All", callback=self.disconnect_all),
        ]

    def show_manager(self, _):
        """Launch the GUI manager window"""
        try:
            logger.info("Attempting to launch GUI manager")
            
            # Get the current executable path
            if getattr(sys, 'frozen', False):
                # We're running in a bundle
                current_app = sys.executable
            else:
                # We're running in development mode
                current_app = os.path.abspath(__file__)
            
            logger.info(f"Current executable path: {current_app}")
            
            # Launch a new Python process running the GUI directly
            cmd = [sys.executable, '-c', """
import sys
import tkinter as tk
from src.gui_manager import GUIManager
app = GUIManager()
app.mainloop()
"""]
            
            env = os.environ.copy()
            if getattr(sys, 'frozen', False):
                # If we're in a bundle, add the bundle's Python path
                bundle_dir = os.path.dirname(os.path.dirname(current_app))
                env['PYTHONPATH'] = os.path.join(bundle_dir, 'Resources/lib/python3.9/site-packages')
            
            logger.info(f"Launching GUI with command: {cmd}")
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Log any immediate errors
            stdout, stderr = process.communicate(timeout=1)
            if stderr:
                logger.error(f"GUI launch stderr: {stderr.decode()}")
            if stdout:
                logger.info(f"GUI launch stdout: {stdout.decode()}")
                
            logger.info("GUI launch command executed successfully")

        except Exception as e:
            error_msg = f"Error launching manager: {str(e)}"
            logger.error(error_msg, exc_info=True)
            rumps.notification("SMB Manager", "Error", error_msg)

    def connect_all(self, _):
        hostname = self.config.get("hostname", "")
        port = self.config.get("port", "8445")
        
        if not hostname:
            rumps.notification("SMB Manager", "Error", "Please configure hostname in the manager")
            return
        
        success_count = 0
        error_messages = []
        
        shares = self.config.get("shares", [])
        
        for i, share in enumerate(shares, 1):
            username = share["username"]
            share_path = share["share"]
            mount_point = share.get("mount_point", f"/Volumes/{os.path.basename(share_path)}")
            
            password = self.config_manager.get_share_password(username, share_path)
            
            if not password:
                error_messages.append(f"No password found for {share_path}")
                continue
            
            success, error = self.mount_manager.mount_share(
                hostname, port, share_path, mount_point, username, password
            )
            
            if success:
                success_count += 1
                rumps.notification("SMB Manager", "Progress", 
                                f"Mounted {i}/{len(shares)}: {share_path}")
            else:
                error_messages.append(f"Failed to mount {share_path}: {error}")
            
            # Add 5 second delay between mounts, but not after the last one
            if i < len(shares):
                import time
                time.sleep(2)  # 5 second delay
        
        if success_count > 0:
            rumps.notification("SMB Manager", "Success", 
                            f"Mounted {success_count} share{'s' if success_count > 1 else ''}")
        if error_messages:
            rumps.notification("SMB Manager", "Errors Occurred", "\n".join(error_messages[:3]))

    def disconnect_all(self, _):
        unmounted = 0
        errors = []
        
        for share in self.config.get("shares", []):
            share_path = share["share"]
            if self.mount_manager.is_mounted(share_path):
                success, error = self.mount_manager.unmount_share(share_path)
                if success:
                    unmounted += 1
                else:
                    errors.append(f"Failed to unmount {share_path}: {error}")
        
        if unmounted > 0:
            rumps.notification("SMB Manager", "Success", 
                             f"Unmounted {unmounted} share{'s' if unmounted > 1 else ''}")
        if errors:
            rumps.notification("SMB Manager", "Errors Occurred", "\n".join(errors[:3]))

def main():
    app = SMBMenuBar()
    app.run()

if __name__ == '__main__':
    main()