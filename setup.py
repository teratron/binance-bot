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
from typing import List, Union


def check_uv_installed() -> bool:
    """Check if UV package manager is installed."""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def install_dependencies() -> None:
    """Install dependencies using UV directly without requirements.txt."""
    print("Installing dependencies using UV...")
    try:
        # Install packages directly without requirements.txt
        packages: List[Union[str, List[str]]] = [
            "binance-connector",
            "ta-lib",
            "https://github.com/cgohlke/talib-build/releases/download/v0.6.3/ta_lib-0.6.3-cp311-cp311-win_amd64.whl",
            "numpy",
            "pandas",
            ["--dev", "python-dotenv-vault"],
            ["--dev", "mypy"],
            ["--group", "lint", "ruff"],
        ]

        for package in packages:
            command: List[str] = ["uv", "add"]

            if isinstance(package, list):
                command.extend(package)
            elif isinstance(package, str):
                command.append(package)

            print(f"Installing {package}...")
            subprocess.run(command, check=True)

        print("Dependencies installed successfully!")
    except subprocess.SubprocessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)


def setup_environment() -> None:
    """Set up the project environment."""
    # Create logs directory if it doesn't exist
    logs_dir: Path = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print(f"Created logs directory: {logs_dir}")

    # Create .env file from example if it doesn't exist
    env_file: Path = Path(".env")
    env_example: Path = Path(".env.example")
    if not env_file.exists() and env_example.exists():
        with open(env_example, "r") as example, open(env_file, "w") as env:
            env.write(example.read())
        print("Created .env file from example")
        print("Please update the .env file with your Binance API credentials")


def main() -> None:
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
