# File: src/gui_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
import sys
import subprocess

from src.config_manager import ConfigManager
from src.mount_manager import MountManager
from src.dialogs import EditShareDialog

logger = logging.getLogger('SMBManager')

class GUIManager(tk.Tk):
    def __init__(self):
        logger.info("Starting GUI Manager initialization")
        try:
            super().__init__()
            
            logger.info("Setting up window properties")
            self.title("SMB Connection Manager")
            self.geometry("900x700")
            
            # Initialize managers
            logger.info("Initializing ConfigManager")
            self.config_manager = ConfigManager()
            logger.info("Initializing MountManager")
            self.mount_manager = MountManager()
            
            # Load configuration
            logger.info("Loading configuration")
            self.config = self.config_manager.load_config()
            
            # Initialize variables
            logger.info("Initializing variables")
            self.init_variables()
            
            # Setup UI
            logger.info("Setting up UI")
            self.setup_ui()
            logger.info("Setting up bindings")
            self.setup_bindings()
            
            # Load initial shares
            logger.info("Refreshing shares list")
            self.refresh_shares_list()
            
            # Center window
            logger.info("Centering window")
            self.center_window()
            
            logger.info("GUI Manager initialization complete")
            
        except Exception as e:
            logger.error(f"Error during GUI initialization: {str(e)}", exc_info=True)
            if not isinstance(e, tk.TclError):  # Only show message box if it's not a Tcl error
                messagebox.showerror("Initialization Error", f"Failed to initialize application: {str(e)}")
            sys.exit(1)
        self.title("SMB Connection Manager")
        self.geometry("900x700")
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.mount_manager = MountManager()
        
        # Load configuration
        self.config = self.config_manager.load_config()
        
        # Initialize variables
        self.init_variables()
        
        # Setup UI
        self.setup_ui()
        self.setup_bindings()
        
        # Load initial shares
        self.refresh_shares_list()
        
        # Center window
        self.center_window()

    def init_variables(self):
        """Initialize all tkinter variables"""
        self.hostname_var = tk.StringVar(value=self.config.get("hostname", ""))
        self.port_var = tk.StringVar(value=self.config.get("port", "8445"))
        self.autostart_var = tk.BooleanVar(value=self.config.get("autostart", False))
        self.use_tunnel_var = tk.BooleanVar(value=self.config.get("use_tunnel", True))
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.share_var = tk.StringVar()

    def setup_ui(self):
        """Setup the main user interface"""
        # Configure dark theme
        self.configure_theme()
        
        # Create main frame
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Create UI components
        self.setup_server_settings()
        self.setup_shares_list()
        self.setup_add_share_frame()
        self.setup_buttons()
        self.setup_context_menu()
        
        # Configure main window grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def configure_theme(self):
        """Configure the dark theme for the application"""
        self.style = ttk.Style()
        style_configs = {
            ".": {"background": "#2E2E2E", "foreground": "white"},
            "Treeview": {"background": "#2E2E2E", "fieldbackground": "#2E2E2E", "foreground": "white"},
            "TLabel": {"background": "#2E2E2E", "foreground": "white"},
            "TButton": {"background": "#404040"},
            "TFrame": {"background": "#2E2E2E"},
            "TLabelframe": {"background": "#2E2E2E", "foreground": "white"},
            "TLabelframe.Label": {"background": "#2E2E2E", "foreground": "white"}
        }
        
        for style, config in style_configs.items():
            self.style.configure(style, **config)
        
        self.configure(bg="#2E2E2E")
    def setup_server_settings(self):
        """Setup the server settings frame"""
        settings_frame = ttk.LabelFrame(self.main_frame, text="Server Settings", padding="5")
        settings_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Hostname
        ttk.Label(settings_frame, text="Hostname:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(settings_frame, textvariable=self.hostname_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        # Port
        ttk.Label(settings_frame, text="Port:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(settings_frame, textvariable=self.port_var).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        # Checkboxes frame
        checkbox_frame = ttk.Frame(settings_frame)
        checkbox_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Auto-start option
        ttk.Checkbutton(checkbox_frame, text="Start on login", 
                        variable=self.autostart_var,
                        command=self.toggle_autostart).grid(row=0, column=0, sticky=tk.W, padx=5)
        
        # Cloudflared tunnel option
        ttk.Checkbutton(checkbox_frame, text="Use Cloudflared tunnel", 
                        variable=self.use_tunnel_var,
                        command=self.toggle_tunnel).grid(row=0, column=1, sticky=tk.W, padx=5)
    def toggle_tunnel(self):
        """Toggle cloudflared tunnel usage"""
        try:
            if self.use_tunnel_var.get():
                self.mount_manager.start_cloudflared()
            else:
                self.mount_manager.stop_cloudflared()
            self.save_config()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle tunnel: {str(e)}")
            self.use_tunnel_var.set(not self.use_tunnel_var.get())  # Revert the checkbox
        
    def setup_shares_list(self):
        """Setup the shares list frame"""
        shares_frame = ttk.LabelFrame(self.main_frame, text="Configured Shares", padding="5")
        shares_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        shares_frame.grid_columnconfigure(0, weight=1)
        shares_frame.grid_rowconfigure(0, weight=1)
        
        # Create Treeview
        self.shares_tree = ttk.Treeview(shares_frame, 
                                      columns=("username", "share", "mount_point", "status"),
                                      show="headings", 
                                      selectmode="extended")
        
        # Configure columns
        columns = {
            "username": ("Username", 150),
            "share": ("Share Path", 250),
            "mount_point": ("Mount Point", 250),
            "status": ("Status", 100)
        }
        
        for col, (heading, width) in columns.items():
            self.shares_tree.heading(col, text=heading)
            self.shares_tree.column(col, width=width)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(shares_frame, orient=tk.VERTICAL, command=self.shares_tree.yview)
        self.shares_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid treeview and scrollbar
        self.shares_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def setup_add_share_frame(self):
        """Setup the add share frame"""
        share_frame = ttk.LabelFrame(self.main_frame, text="Add New Share", padding="5")
        share_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        share_frame.grid_columnconfigure(1, weight=1)
        
        # Username field
        ttk.Label(share_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(share_frame, textvariable=self.username_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        # Password field
        ttk.Label(share_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(share_frame, textvariable=self.password_var, show="*").grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        # Share path field
        ttk.Label(share_frame, text="Share Path:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(share_frame, textvariable=self.share_var).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

    def setup_buttons(self):
        """Setup the button frame"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Share management buttons
        share_mgmt_frame = ttk.Frame(button_frame)
        share_mgmt_frame.pack(side=tk.LEFT, padx=5)
        
        buttons = [
            ("Add Share", self.add_share),
            ("Edit", self.edit_share),
            ("Delete", self.remove_share)
        ]
        
        for text, command in buttons:
            ttk.Button(share_mgmt_frame, text=text, command=command).pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Action buttons
        ttk.Button(button_frame, text="Connect All", command=self.connect_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save", command=self.save_changes).pack(side=tk.LEFT, padx=2)

    def setup_context_menu(self):
        """Setup the right-click context menu"""
        self.context_menu = tk.Menu(self, tearoff=0)
        menu_items = [
            ("Edit", self.edit_share),
            ("Delete", self.remove_share),
            (None, None),  # Separator
            ("Mount", self.mount_selected),
            ("Unmount", self.unmount_selected)
        ]
        
        for label, command in menu_items:
            if label is None:
                self.context_menu.add_separator()
            else:
                self.context_menu.add_command(label=label, command=command)

    def setup_bindings(self):
        """Setup all event bindings"""
        self.shares_tree.bind("<Double-Button-1>", self.on_double_click)
        self.shares_tree.bind("<Delete>", self.on_delete)
        self.shares_tree.bind("<Button-3>", self.show_context_menu)

    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    # Event handlers
    def on_double_click(self, event):
        """Handle double-click event on shares tree"""
        region = self.shares_tree.identify_region(event.x, event.y)
        if region in ("cell", "tree"):
            item = self.shares_tree.identify_row(event.y)
            if item:
                self.shares_tree.selection_set(item)
                self.edit_share()

    def on_delete(self, event=None):
        """Handle delete key press"""
        self.remove_share()

    def show_context_menu(self, event):
        """Show context menu for right-click"""
        item = self.shares_tree.identify_row(event.y)
        if item:
            self.shares_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    # Action methods
    def add_share(self):
        """Add a new share"""
        username = self.username_var.get()
        password = self.password_var.get()
        share = self.share_var.get()
        
        if not all([username, password, share]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Store password in keyring
        self.config_manager.store_share_password(username, share, password)
        
        # Add to treeview
        mount_point = f"/Volumes/{os.path.basename(share)}"
        self.shares_tree.insert("", tk.END, values=(
            username,
            share,
            mount_point,
            "Not Mounted"
        ))
        
        # Clear entry fields
        self.username_var.set("")
        self.password_var.set("")
        self.share_var.set("")
        
        self.save_config()
        messagebox.showinfo("Success", "Share added successfully")

    def edit_share(self):
        """Edit selected share"""
        selected = self.shares_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a share to edit.")
            return
        
        item = selected[0]
        values = self.shares_tree.item(item)["values"]
        if not values:
            return
        
        username = values[0]
        share_path = values[1]
        
        # Get existing mount options
        existing_mount = None
        for share in self.config.get("shares", []):
            if share["username"] == username and share["share"] == share_path:
                existing_mount = share
                break
        
        dialog = EditShareDialog(self, username, share_path, existing_mount)
        self.wait_window(dialog.top)
        
        if dialog.result:
            self.update_share(item, dialog.result)
            self.refresh_shares_list()

    def remove_share(self):
        """Remove selected share(s)"""
        selected = self.shares_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a share to delete.")
            return
        
        share_count = len(selected)
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete the selected share{'s' if share_count > 1 else ''}?"):
            for item in selected:
                values = self.shares_tree.item(item)["values"]
                try:
                    self.config_manager.delete_share_password(values[0], values[1])
                except Exception as e:
                    print(f"Failed to delete keyring entry: {e}")
                
                self.shares_tree.delete(item)
            
            self.save_config()
            messagebox.showinfo("Success", f"Successfully deleted {share_count} share{'s' if share_count > 1 else ''}.")

    def save_config(self):
        """Save current configuration"""
        config = {
            "hostname": self.hostname_var.get(),
            "port": self.port_var.get(),
            "autostart": self.autostart_var.get(),
            "use_tunnel": self.use_tunnel_var.get(),
            "shares": []
        }
        
        for item in self.shares_tree.get_children():
            values = self.shares_tree.item(item)["values"]
            share_data = {
                "username": values[0],
                "share": values[1],
                "mount_point": values[2],
                "auto_mount": True,
                "readonly": False
            }
            config["shares"].append(share_data)
        
        self.config = config
        self.config_manager.save_config(config)

    def save_changes(self):
        """Save all current settings"""
        try:
            self.save_config()
            self.refresh_shares_list()
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def update_share(self, item, new_data):
        """Update a share with new data"""
        old_values = self.shares_tree.item(item)["values"]
        old_username = old_values[0]
        old_share = old_values[1]
        
        # Handle password update
        if new_data['password']:
            self.config_manager.delete_share_password(old_username, old_share)
            self.config_manager.store_share_password(
                new_data['username'],
                new_data['share'],
                new_data['password']
            )
        elif old_username != new_data['username'] or old_share != new_data['share']:
            # Move existing password if username or share changed
            try:
                password = self.config_manager.get_share_password(old_username, old_share)
                if password:
                    self.config_manager.delete_share_password(old_username, old_share)
                    self.config_manager.store_share_password(
                        new_data['username'],
                        new_data['share'],
                        password
                    )
            except:
                pass
        
        # Update treeview
        self.shares_tree.item(item, values=(
            new_data['username'],
            new_data['share'],
            new_data['mount_point'],
            "Not Mounted"
        ))
        
        self.save_config()
    def refresh_shares_list(self):
        """Refresh the shares list display"""
        for item in self.shares_tree.get_children():
            self.shares_tree.delete(item)
        
        for share in self.config.get("shares", []):
            share_path = share["share"]
            # Use the default mount point from the share config if available
            mount_point = share.get("mount_point", self.mount_manager.get_mount_point(share_path))
            status = "Mounted" if self.mount_manager.is_mounted(share_path) else "Not Mounted"
            
            self.shares_tree.insert("", tk.END, values=(
                share["username"],
                share_path,
                mount_point,
                status
            ))
    def mount_selected(self):
        """Mount selected shares"""
        selected = self.shares_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select shares to mount.")
            return
        
        hostname = self.hostname_var.get()
        port = self.port_var.get()
        
        for item in selected:
            values = self.shares_tree.item(item)["values"]
            username = values[0]
            share_path = values[1]
            
            password = self.config_manager.get_share_password(username, share_path)
            
            if not password:
                messagebox.showerror("Error", f"No password found for {share_path}")
                continue
            
            success, error = self.mount_manager.mount_share(
                hostname, port, share_path, None, username, password
            )
            
            if success:
                messagebox.showinfo("Success", f"Successfully mounted {share_path}")
            else:
                messagebox.showerror("Error", f"Failed to mount {share_path}: {error}")
        
        self.refresh_shares_list()


    def unmount_selected(self):
        """Unmount selected shares"""
        selected = self.shares_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select shares to unmount.")
            return
        
        for item in selected:
            values = self.shares_tree.item(item)["values"]
            share_path = values[1]
            
            success, error = self.mount_manager.unmount_share(share_path)
            
            if success:
                messagebox.showinfo("Success", f"Successfully unmounted {share_path}")
            else:
                messagebox.showerror("Error", f"Failed to unmount {share_path}: {error}")
        

    def toggle_autostart(self):
        """Toggle autostart functionality"""
        autostart_dir = os.path.expanduser("~/Library/LaunchAgents")
        plist_path = os.path.join(autostart_dir, "com.smbmanager.plist")
        
        if self.autostart_var.get():
            try:
                # Create LaunchAgent plist
                os.makedirs(autostart_dir, exist_ok=True)
                
                # Get the path to the app bundle
                if getattr(sys, 'frozen', False):
                    # We're running from the app bundle
                    app_path = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
                    executable_path = os.path.join(app_path, 'MacOS', 'SMB Manager')
                else:
                    # We're running in development
                    executable_path = sys.executable
                    script_path = os.path.abspath(__file__)
                    executable_path = f"{executable_path} {script_path}"
                
                plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.smbmanager</string>
        <key>ProgramArguments</key>
        <array>
            <string>{executable_path}</string>
            <string>--menubar</string>
        </array>
        <key>RunAtLoad</key>
        <true/>
        <key>KeepAlive</key>
        <true/>
    </dict>
    </plist>"""
                
                with open(plist_path, 'w') as f:
                    f.write(plist_content)
                
                os.chmod(plist_path, 0o644)
                subprocess.run(['launchctl', 'load', plist_path], check=True)
                messagebox.showinfo("Success", "App will now start automatically on login")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to enable auto-start: {str(e)}")
                self.autostart_var.set(False)
        else:
            try:
                if os.path.exists(plist_path):
                    subprocess.run(['launchctl', 'unload', plist_path], check=True)
                    os.remove(plist_path)
                    messagebox.showinfo("Success", "Auto-start disabled")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to disable auto-start: {str(e)}")
                self.autostart_var.set(True)
        

    def connect_all(self):
        """Connect all configured shares"""
        hostname = self.hostname_var.get()
        port = self.port_var.get()
        
        if not hostname or not port:
            messagebox.showerror("Error", "Please configure hostname and port first.")
            return
        
        success_count = 0
        error_messages = []
        
        for share in self.config.get("shares", []):
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
            else:
                error_messages.append(f"Failed to mount {share_path}: {error}")
        
        self.refresh_shares_list()
        
        if success_count > 0:
            message = f"Successfully mounted {success_count} share{'s' if success_count > 1 else ''}"
            if error_messages:
                message += f"\n\nErrors occurred:\n" + "\n".join(error_messages)
            messagebox.showinfo("Mount Status", message)
        elif error_messages:
            messagebox.showerror("Mount Status", "\n".join(error_messages))
    
     
