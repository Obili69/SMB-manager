# File: src/mount_manager.py
import subprocess
import os
import shutil
from pathlib import Path
from src.config_manager import ConfigManager

class MountManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        # Initialize cloudflared only if tunnel is enabled
        if self.config.get('use_tunnel', True):
            self.start_cloudflared()

    def reload_config(self):
        """Reload the current configuration"""
        self.config = self.config_manager.load_config()
        
    def start_cloudflared(self):
        """Start cloudflared if it's not running"""
        try:
            hostname = self.config.get("hostname")
            if not hostname:
                print("No hostname configured, skipping cloudflared start")
                return

            # Check if cloudflared is already running
            result = subprocess.run(['pgrep', 'cloudflared'], capture_output=True, text=True)
            if result.returncode != 0:
                # Start cloudflared with the configured hostname
                subprocess.Popen(
                    ['cloudflared', 'access', 'tcp', 
                     '--hostname', hostname, 
                     '--url', f'localhost:{self.config.get("port", "8445")}'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"Started cloudflared tcp access tunnel for {hostname}")
        except Exception as e:
            print(f"Error starting cloudflared: {e}")

    def stop_cloudflared(self):
        """Stop cloudflared process if it's running"""
        try:
            subprocess.run(['pkill', 'cloudflared'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            print("Stopped cloudflared")
        except Exception as e:
            print(f"Error stopping cloudflared: {e}")

    def mount_share(self, hostname, port, share_path, mount_point, username, password):
        """Mount an SMB share using open command"""
        try:
            # Reload config to ensure we have the latest settings
            self.reload_config()
            
            if not mount_point:
                mount_point = self.get_mount_point(share_path)

            os.makedirs(mount_point, exist_ok=True)
            
            # Use localhost only if tunnel is enabled in config
            use_tunnel = self.config.get('use_tunnel', True)
            connect_host = "localhost" if use_tunnel else hostname
            
            # Build SMB URL (mask password in print)
            safe_url = f"smb://{username}:****@{connect_host}:{port}{share_path}"
            print(f"Opening connection to: {safe_url} (using tunnel: {use_tunnel})")
            
            # Use subprocess to open the SMB location
            smb_url = f"smb://{username}:{password}@{connect_host}:{port}{share_path}"
            
            result = subprocess.run(['open', smb_url], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Connection successful")
                return True, ""
            else:
                print(f"Connection failed: {result.stderr.strip()}")
                return False, result.stderr.strip()
                
        except Exception as e:
            print(f"Exception during connection: {str(e)}")
            return False, str(e)

    def get_mount_point(self, share_path):
        """Get the mount point for a share path"""
        return str(Path.home() / "SMBShares" / Path(share_path).name)

    def is_mounted(self, share_path):
        """Check if a share path is mounted"""
        mount_point = self.get_mount_point(share_path)
        try:
            with os.scandir(mount_point) as entries:
                next(entries, None)
            return True
        except:
            return False