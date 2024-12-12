from setuptools import setup

APP = ['src/main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
        'LSBackgroundOnly': False,
        'CFBundleName': "SMB Manager",
        'CFBundleDisplayName': "SMB Manager",
        'CFBundleIdentifier': "com.smbmanager.app",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHighResolutionCapable': True,
    },
    'packages': ['rumps', 'keyring', 'src', 'tkinter'],
    'includes': [
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        '_tkinter',
        'json',
        'subprocess',
        'os',
        'sys',
        'pathlib',
        'logging'
    ],
    'excludes': ['PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'wx'],
    'resources': ['src'],
    'frameworks': [],
    'site_packages': True,
    'strip': False,  # Changed to False to help with debugging
    'arch': 'universal2',
    'semi_standalone': False,  # Changed to False for full bundling
}

setup(
    app=APP,
    name="SMB Manager",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'rumps',
        'keyring',
    ],
)