import tkinter as tk
from tkinter import ttk
import os

class EditShareDialog:
    def __init__(self, parent, username="", share_path="", existing_mount=None):
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.title("Edit Share")
        self.top.geometry("500x300")
        
        self.top.transient(parent)
        self.top.grab_set()
        self.existing_mount = existing_mount
        
        self.setup_ui(username, share_path)
        self.center_on_parent(parent)

    def setup_ui(self, username, share_path):
        main_frame = ttk.Frame(self.top, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Username
        ttk.Label(main_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.username_var = tk.StringVar(value=username)
        ttk.Entry(main_frame, textvariable=self.username_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        
        # Share Path
        ttk.Label(main_frame, text="Share Path:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.share_var = tk.StringVar(value=share_path)
        ttk.Entry(main_frame, textvariable=self.share_var, width=40).grid(row=1, column=1, padx=5, pady=5)
        
        # Mount Options
        options_frame = ttk.LabelFrame(main_frame, text="Mount Options", padding="5")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Mount Point
        ttk.Label(options_frame, text="Mount Point:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.mount_point_var = tk.StringVar(value=f"/Volumes/{os.path.basename(share_path)}" if share_path else "")
        ttk.Entry(options_frame, textvariable=self.mount_point_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        
        # Options
        self.auto_mount_var = tk.BooleanVar(value=True)
        self.readonly_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(options_frame, text="Auto-mount on connect", 
                       variable=self.auto_mount_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Mount as read-only", 
                       variable=self.readonly_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Password
        ttk.Label(main_frame, text="New Password:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=40).grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(main_frame, text="(Leave empty to keep current password)").grid(row=4, column=1, padx=5, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        if self.existing_mount:
            self.load_existing_mount(self.existing_mount)

    def center_on_parent(self, parent):
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = 500
        dialog_height = 300
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.top.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    def load_existing_mount(self, mount_data):
        if 'mount_point' in mount_data:
            self.mount_point_var.set(mount_data['mount_point'])
        if 'auto_mount' in mount_data:
            self.auto_mount_var.set(mount_data['auto_mount'])
        if 'readonly' in mount_data:
            self.readonly_var.set(mount_data['readonly'])

    def save(self):
        self.result = {
            'username': self.username_var.get(),
            'share': self.share_var.get(),
            'password': self.password_var.get(),
            'mount_point': self.mount_point_var.get(),
            'auto_mount': self.auto_mount_var.get(),
            'readonly': self.readonly_var.get()
        }
        self.top.destroy()

    def cancel(self):
        self.top.destroy()