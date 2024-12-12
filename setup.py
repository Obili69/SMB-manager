from setuptools import setup, find_packages

setup(
    name="smb-manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'rumps',
        'keyring',
    ],
    entry_points={
        'console_scripts': [
            'smb-manager=src.main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="SMB Connection Manager for macOS",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/smb-manager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires='>=3.6',
)