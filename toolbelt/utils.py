#!/usr/bin/env python3

import os
import subprocess
import click
import sys
import shutil
import re

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

ED_ROOT = os.environ.get("ED_ROOT")
console = Console()

DRY_RUN = False

# Command Execution Utilities
def run_command(command, success_msg=None, error_msg=None):
    if DRY_RUN:
        console.print(f"[dry-run] {command}", style="yellow", highlight=True)
        if success_msg:
            console.print(f"[dry-run] {success_msg}")
    else:
        try:
            subprocess.run(command, shell=True, check=True, stdin=subprocess.DEVNULL)
            if success_msg:
                console.print(f"✅ {success_msg}")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ {error_msg or 'Error while running command'}: {e}")
            sys.exit(1)
    
def check_if_user_can_sudo():
    try:
        subprocess.check_output("sudo -n true", stderr=subprocess.STDOUT, shell=True)    
        return True
    except subprocess.CalledProcessError:
        return False

def is_installed(command, doctor=False):
    if DRY_RUN and not doctor:
        console.print(f"[dry-run] Checking if '{command}' is installed...")
        return False
    return shutil.which(command) is not None

def get_version(command, version_flag="--version"):
    try:
        result = subprocess.getoutput(f"{command} {version_flag}")
        version_pattern = r"(\d+\.\d+(\.\d+)?)"
        match = re.search(version_pattern, result)
        if match:
            return match.group(0)
        else:
            return result.splitlines()[0] if result else "Unknown"
    except Exception as e:
        return f"Error: {str(e)}"

# User Interaction Utilities
def confirm_installation(tool_name):
    while True:
        choice = input(f"❓ Do you want to install {tool_name}? (y/n): ").strip().lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            print("⚠️ Invalid input. Please enter 'y' for yes or 'n' for no.")

# Installation Helpers
def brew_install(package_name, success_msg, error_msg, is_cask=False):
    cmd = f"brew install --cask {package_name}" if is_cask else f"brew install {package_name}"
    run_command(cmd, success_msg=success_msg, error_msg=error_msg)

def setup_path_for_tool(path_command, success_msg, error_msg, skip_if_already_configured=True):
    """Add tool path to the system PATH."""
    if skip_if_already_configured and path_command in subprocess.getoutput("cat ~/.zshrc"):
        console.print(f"⚙️ Path is atready configured: {path_command}. Skipping setup.", style="yellow")
    elif DRY_RUN:
        console.print(f"[dry-run] Adding '{path_command}' to ~/.zshrc")
        console.print(f"[dry-run] {success_msg}")
    else:
        run_command(f'echo {path_command} >> ~/.zshrc', success_msg=success_msg, error_msg=error_msg)

def modify_file(file_path, content):
    if DRY_RUN:
        console.print(f"[dry-run] Modifying {file_path}:")
        try:
            with open(file_path, "r") as file:
                before_content = file.read()
            console.print("[dry-run] File content before modification:")
            console.print(before_content)
        except FileNotFoundError:
            console.print("[dry-run] File not found. It would be created.")

        console.print(f"[dry-run] Appending the following content:\n{content}")
        
        # Simulate the new file content
        new_content = before_content + "\n" + content if 'before_content' in locals() else content
        console.print("[dry-run] File content after modification:")
        console.print(new_content)
    else:
        with open(file_path, "a") as file:
            file.write(content)
        console.print(f"✅ {file_path} updated successfully.")

def check_and_install_tool(tool_name, install_func, interactive=False):
    if is_installed(tool_name):
        console.print(f"⚙️ {tool_name.capitalize()} is already installed. Skipping.", style="yellow")
    elif interactive and not confirm_installation(tool_name.capitalize()):
        console.print(f"❌ Skipping installation of {tool_name.capitalize()}.", style="red")
    else:
        install_func()
        return True
    return False

# Specific Installation Functions with Checks
def install_homebrew(interactive=False):
    check_and_install_tool("brew", lambda: run_command(
        '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        success_msg="🍺 Homebrew installed successfully.",
        error_msg="❌ Failed to install Homebrew"
    ), interactive)
    
def print_rich_step(step_name):
    """Print a rich-styled separator for each step."""
    console.print(Panel(step_name, style="bold yellow"))
    
def can_reach_ip(ip_address):
    try:
        # Execute ping command with 1 packet and a timeout of 2 seconds
        response = subprocess.run(
            ["ping", "-c", "1", "-W", "2", ip_address],
            stdout=subprocess.DEVNULL,  # Ignore the command output
            stderr=subprocess.DEVNULL  # Ignore any errors printed to the console
        )
        
        # Check the return code. 0 means the ping was successful.
        if response.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        console.print(f"Error checking reachability: {str(e)}", style="red")
        return False