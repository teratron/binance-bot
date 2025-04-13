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
from typing import Any


def build_command_list(source: str | list[str], *args: str | list[str]) -> list[str]:
    """Build a unified command list from various input formats.

    Examples:
        >>> build_command_list("uv add", "package")
        >>> build_command_list(["uv", "add"], "package")
        >>> build_command_list("uv", ["add", "package"], "--dev")
    """

    command: list[str] = []

    # Process args parameter
    for arg in args:
        if isinstance(arg, list):
            command.extend(arg)
        elif isinstance(arg, str):
            command.append(arg)

    # Process source parameter
    if isinstance(source, list):
        command.extend(source)
    elif isinstance(source, str):
        source = source.strip()
        if " " in source:
            command.extend(source.split(" "))
        else:
            command.append(source)

    return command


def check_existing(service: str | list[str], *args: str | list[str], **kwargs: Any) -> bool:
    """Check if a service with the given name is already running."""

    try:
        subprocess.run(build_command_list(service, *args), check=True, **kwargs)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def check_uv_installed() -> bool:
    """Check if UV package manager is installed."""

    if check_existing(["uv", "version"], capture_output=True):
        return True

    match sys.platform:
        case "win32" | "win64":
            command: str = (
                'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
            )
            return check_existing(command)
        case "linux" | "darwin":
            if check_existing("curl --version"):
                return check_existing("curl -LsSf https://astral.sh/uv/install.sh | sh")
            if check_existing("wget --version"):
                return check_existing("wget -qO- https://astral.sh/uv/install.sh | sh")

    return False


def install_dependencies() -> None:
    """Install dependencies using UV."""

    print("Installing dependencies using UV...")

    # Install packages
    packages: list[str | list[str]] = [
        "binance-connector",
        "lightweight-charts",
        "ta-lib",
        # pylint: disable=line-too-long
        "https://github.com/cgohlke/talib-build/releases/download/v0.6.3/ta_lib-0.6.3-cp311-cp311-win_amd64.whl",
        "numpy",
        "pandas",
        "--dev pandas-stubs",
        "--dev python-dotenv-vault",
        ["--dev", "mypy"],
        "--group lint ruff",
    ]

    try:
        for package in packages:
            print(f"Installing {package}...")
            _ = check_existing(["uv", "add"], package)

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
        with (
            open(env_example, "r", encoding="utf-8") as example,
            open(env_file, "w", encoding="utf-8") as env,
        ):
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
