# File: src/mount_manager.py
import subprocess
import os
from pathlib import Path
import logging
from src.config_manager import ConfigManager

logger = logging.getLogger('SMBManager')

class MountManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        if self.config.get('use_tunnel', True):
            self.start_cloudflared()

    def reload_config(self):
        self.config = self.config_manager.load_config()

    def mount_share(self, hostname, port, share_path, mount_point, username, password):
        """Mount an SMB share using open command"""
        try:
            self.reload_config()
            
            # Use localhost if tunnel is enabled
            use_tunnel = self.config.get('use_tunnel', True)
            connect_host = "localhost" if use_tunnel else hostname
            
            # Build the SMB URL
            smb_url = f"smb://{username}:{password}@{connect_host}:{port}{share_path}"
            
            # Log the attempt (without password)
            safe_url = f"smb://{username}:****@{connect_host}:{port}{share_path}"
            logger.info(f"Attempting to mount {safe_url}")
            
            # Execute open command
            result = subprocess.run(
                ['open', smb_url],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully mounted {share_path}")
                return True, ""
            else:
                error_msg = f"Mount failed: {result.stderr.strip()}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Mount error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def unmount_share(self, share_path):
        """Unmount a share"""
        try:
            mount_point = f"/Volumes/{Path(share_path).name}"
            if self.is_mounted(mount_point):
                result = subprocess.run(['umount', mount_point], capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"Successfully unmounted {mount_point}")
                    return True, ""
                else:
                    # Try with sudo if regular unmount fails
                    sudo_result = subprocess.run(['sudo', 'umount', mount_point], capture_output=True, text=True)
                    if sudo_result.returncode == 0:
                        logger.info(f"Successfully unmounted {mount_point} using sudo")
                        return True, ""
                    error_msg = f"Unmount failed: {sudo_result.stderr.strip()}"
                    logger.error(error_msg)
                    return False, error_msg
            return True, "Not mounted"
        except Exception as e:
            error_msg = f"Unmount error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_mount_point(self, share_path):
        """Get the mount point for a share path"""
        return f"/Volumes/{Path(share_path).name}"

    def is_mounted(self, mount_point):
        """Check if a mount point is mounted"""
        try:
            return os.path.ismount(mount_point)
        except Exception:
            return False

    def start_cloudflared(self):
        """Start cloudflared tunnel if needed"""
        try:
            hostname = self.config.get("hostname")
            if not hostname:
                logger.warning("No hostname configured, skipping cloudflared")
                return

            if subprocess.run(['pgrep', 'cloudflared'], capture_output=True).returncode != 0:
                subprocess.Popen(
                    ['cloudflared', 'access', 'tcp', 
                     '--hostname', hostname, 
                     '--url', f'localhost:{self.config.get("port", "8445")}'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                logger.info(f"Started cloudflared tunnel for {hostname}")
        except Exception as e:
            logger.error(f"Cloudflared error: {str(e)}")

    def stop_cloudflared(self):
        """Stop cloudflared tunnel"""
        try:
            subprocess.run(['pkill', 'cloudflared'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            logger.info("Stopped cloudflared")
        except Exception as e:
            logger.error(f"Error stopping cloudflared: {str(e)}")