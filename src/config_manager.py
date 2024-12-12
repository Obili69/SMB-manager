import json
import os
import keyring

class ConfigManager:
    def __init__(self):
        self.config_file = os.path.expanduser("~/.smb_manager_config.json")

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "hostname": "", 
            "port": "8445", 
            "shares": [], 
            "autostart": False,
            "use_tunnel": True  # Default to using tunnel
        }

    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    @staticmethod
    def store_share_password(username, share, password):
        keyring.set_password("SMBManager", f"{username}:{share}", password)

    @staticmethod
    def get_share_password(username, share):
        return keyring.get_password("SMBManager", f"{username}:{share}")

    @staticmethod
    def delete_share_password(username, share):
        try:
            keyring.delete_password("SMBManager", f"{username}:{share}")
        except:
            pass