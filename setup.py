#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup script for Binance Trading Bot.

This script helps with setting up the project environment using UV package manager.
It provides instructions and commands for installing dependencies.
"""

import subprocess
import sys
from pathlib import Path


def check_uv_installed():
    """Check if UV package manager is installed."""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def install_dependencies():
    """Install dependencies using UV directly without requirements.txt."""
    print("Installing dependencies using UV...")
    try:
        # Install packages directly without requirements.txt
        packages = [
            "binance-connector>=3.0.0",
            "ta-lib>=0.4.28",
            "numpy>=1.24.0",
            "pandas>=2.0.0",
            "python-dotenv-vault>=0.6.0",
            "ruff>=0.1.0"
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            subprocess.run(["uv", "pip", "install", package], check=True)
            
        print("Dependencies installed successfully!")
    except subprocess.SubprocessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)


def setup_environment():
    """Set up the project environment."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print(f"Created logs directory: {logs_dir}")
    
    # Create .env file from example if it doesn't exist
    env_file = Path(".env")
    env_example = Path(".env.example")
    if not env_file.exists() and env_example.exists():
        with open(env_example, "r") as example, open(env_file, "w") as env:
            env.write(example.read())
        print("Created .env file from example")
        print("Please update the .env file with your Binance API credentials")


def main():
    """Main function to set up the project."""
    print("Setting up Binance Trading Bot environment...")
    
    # Check if UV is installed
    if not check_uv_installed():
        print("UV package manager is not installed.")
        print("Please install UV using the following command:")
        print("  pip install uv")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Set up environment
    setup_environment()
    
    print("\nSetup complete! You can now run the bot using:")
    print("  python main.py")
    print("\nMake sure to update your .env file with your Binance API credentials.")


if __name__ == "__main__":
    main()