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

MONARCH_ROOT = os.environ.get("MONARCH_ROOT")
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

def aquire_super_user_privileges():
    if not check_if_user_can_sudo():
        console.print("Use Self Service 'Temprorary Admin Privileges' to elevate admin rights", style="bold red")
        run_command(r"open /Applications/Self\ Service.app", success_msg="✅ Self Service opened successfully.", error_msg="❌ Failed to open Self Service")
        console.print("🔒 You need to have admin rights to run this script. Please enter your password.", style="bold red")
        
    run_command("sudo -v", success_msg="✅ Admin rights verified.", error_msg="❌ Failed to verify admin rights")

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

def prompt_for_license_key():
    return input("🔑 Please enter your DCM license key (or press Enter to skip): ").strip()

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

def install_rbenv(interactive=False):
    if check_and_install_tool("rbenv", lambda: brew_install("rbenv", "🧊 rbenv installed successfully.", "❌ Failed to install rbenv"), interactive):
        run_command("rbenv install 3.1.0", success_msg="✅ Ruby 3.1.0 installed successfully.", error_msg="❌ Failed to install Ruby 3.1.0")
        run_command("rbenv global 3.1.0", success_msg="✅ Ruby 3.1.0 set as global version.", error_msg="❌ Failed to set Ruby 3.1.0 as global version")

def install_bundler(interactive=False):
    check_and_install_tool("bundler", lambda: run_command("gem install bundler", success_msg="🔧 Bundler installed successfully.", error_msg="❌ Failed to install Bundler"), interactive)

def install_flutter(interactive=False):
    check_and_install_tool("fvm", lambda: brew_install("fvm", "🔧 FVM installed successfully.", "❌ Failed to install FVM"), interactive)

def install_android_studio(interactive=False):
    if os.path.exists("/Applications/Android Studio.app") and not DRY_RUN:
        console.print("🤖 Android Studio is already installed. Skipping.", style="yellow")
    elif confirm_installation("Android Studio") if interactive else True:
        brew_install("android-studio", "🤖 Android Studio installed successfully.", "❌ Failed to install Android Studio", is_cask=True)

def install_xcode(interactive=False):
    check_and_install_tool("xcode-select", lambda: run_command(
        "xcode-select --install",
        success_msg="🛠️ Xcode command line tools installed successfully.",
        error_msg="❌ Failed to install Xcode command line tools"
    ), interactive)

def install_cocoapods(interactive=False):
    check_and_install_tool("pod", lambda: brew_install("cocoapods", "🌱 CocoaPods installed successfully.", "❌ Failed to install CocoaPods"), interactive)

def install_fastlane(interactive=False):
    check_and_install_tool("fastlane", lambda: brew_install("fastlane", "🚀 Fastlane installed successfully.", "❌ Failed to install Fastlane"), interactive)    

def install_firebase_cli(interactive=False):
    if is_firebase_cli_installed() and not DRY_RUN:
        console.print("🔥 Firebase CLI is already installed. Skipping.", style="yellow")
    elif confirm_installation("Firebase CLI") if interactive else True:
        run_command("dart pub global activate flutterfire_cli", success_msg="🔥 Firebase CLI installed successfully.", error_msg="❌ Failed to install Firebase CLI")

def install_melos(interactive=False):
    check_and_install_tool("melos", lambda: run_command("fvm dart pub global activate melos", success_msg="🎛️ Melos installed successfully.", error_msg="❌ Failed to install Melos"), interactive)

def install_dcm(interactive=False):
    if check_and_install_tool("dcm", lambda: run_command("brew tap CQLabs/dcm", success_msg="✅ DCM repository tapped.", error_msg="❌ Failed to tap DCM repository"), interactive):
        brew_install("dcm", "✅ DCM installed successfully.", "❌ Failed to install DCM")
        license_key = prompt_for_license_key() if interactive else None
        if license_key:
            run_command(f"dcm activate --license-key={license_key}", success_msg="✅ DCM activated successfully.", error_msg="❌ Failed to activate DCM")

def setup_gpg(interactive=False):
    if check_and_install_tool("gpg", lambda: run_command("brew install gnupg", success_msg="🔐 GPG installed successfully.", error_msg="❌ Failed to install GPG"), interactive):
        console.print("🔧 Generating a new GPG key...", style="green")
        run_command("gpg --full-generate-key", success_msg="✅ GPG key generated successfully.", error_msg="❌ Failed to generate GPG key")
        run_command("git config --global commit.gpgsign true", success_msg="✅ Git configured to sign commits by default.", error_msg="❌ Failed to configure Git")
        console.print("\n⚙️  Next steps: Add your GPG key to your GitHub account.", style="bold")    

def setup_pre_commit_hooks(interactive=False):
    if check_and_install_tool("pre-commit", lambda: run_command("brew install pipx && pipx install pre-commit", success_msg="✅ Pre-commit installed successfully.", error_msg="❌ Failed to install pre-commit"), interactive):
        run_command("pre-commit install -t pre-commit -t commit-msg", success_msg="✅ Pre-commit hooks installed successfully.", error_msg="❌ Failed to install pre-commit hooks")

def setup_android_keystore(interactive=False):
    keystore_path = os.path.expanduser("~/keystores/monarch-ui.keystore")
    if os.path.exists(keystore_path) and not DRY_RUN:
        console.print(f"🔑 Android keystore already exists at {keystore_path}. Skipping setup.", style="yellow")
    elif confirm_installation("Android keystore setup") if interactive else True:
        console.print("🔧 Setting up Android keystore...", style="green")

        alias = "monarchui"
        key_password = input("🔐 Enter keystore password: ")
        key_confirm_password = input("🔐 Re-enter keystore password: ")
        if key_password != key_confirm_password:
            console.print("❌ Passwords do not match. Aborting keystore setup.", style="red")
            return

        details = {
            "first_last_name": input("❓ What is your first and last name? [Unknown]: "),
            "organizational_unit": input("❓ What is the name of your organizational unit? [Unknown]: "),
            "organization": input("❓ What is the name of your organization? [Unknown]: "),
            "city": input("❓ What is the name of your City or Locality? [Unknown]: "),
            "state": input("❓ What is the name of your State or Province? [Unknown]: "),
            "country_code": input("❓ What is the two-letter country code for this unit? [Unknown]: "),
        }

        keytool_command = (
            f"keytool -genkey -v -keystore {keystore_path} -alias {alias} "
            f"-keyalg RSA -keysize 2048 -validity 10000 "
            f"-storepass {key_password} -keypass {key_password} "
            f"-dname \"CN={details['first_last_name']}, OU={details['organizational_unit']}, O={details['organization']}, "
            f"L={details['city']}, ST={details['state']}, C={details['country_code']}\""
        )
        run_command(keytool_command, success_msg="✅ Keystore generated successfully.", error_msg="❌ Failed to generate keystore")

        local_properties_path = f"{MONARCH_ROOT}/app/android/local.properties"
        properties_content = f"\nANDROID_KEY_ALIAS={alias}\nANDROID_STORE_FILE={keystore_path}\nANDROID_STORE_PASSWORD={key_password}\nANDROID_KEY_PASSWORD={key_password}\n"
        modify_file(local_properties_path, properties_content)
        
def is_node_server_installed():
    return os.path.exists(f"{MONARCH_ROOT}/toolbelt/setup/node_server")

def setup_mkcert_and_node_server(interactive=False):
    if check_and_install_tool("mkcert", lambda: run_command("brew install mkcert", success_msg="🔧 MkCert installed successfully.", error_msg="❌ Failed to install MkCert"), interactive):
        if confirm_installation("MkCert and Node.js server setup") if interactive else True:
            console.print("🔧 Setting up MkCert for local HTTPS development...", style="green")
            run_command("brew install mkcert", success_msg="✅ MkCert installed successfully.", error_msg="❌ Failed to install MkCert")
            run_command("mkcert -install", success_msg="✅ Local root certificate installed successfully.", error_msg="❌ Failed to install local root certificate")
        else:
            console.print("🔧 MkCert is already installed. Skipping setup.", style="yellow")

    console.print("🔧 Updating /etc/hosts file for dev.monarchui.comcast.net...", style="green")
    hosts_entries = """
127.0.0.1 dev.monarchui.comcast.net
::1 dev.monarchui.comcast.net
"""
    hosts_file_path = "/etc/hosts"
    # Check if the entries already exist in the hosts file
    with open(hosts_file_path, "r") as file:
        current_contents = file.read()
    if any(line.strip() in current_contents for line in hosts_entries.splitlines()):
        console.print("⚠️ Some or all entries already exist in the /etc/hosts file.", style="yellow")
    else:
        modify_file(hosts_file_path, hosts_entries)
        run_command("sudo killall -HUP mDNSResponder", success_msg="✅ DNS cache cleaned.", error_msg="❌ Failed to clean DNS cache")

    if is_node_server_installed() and not DRY_RUN:
        console.print("🔧 Node.js server already exists. Skipping setup.", style="yellow")
    else:
        console.print("🔧 Setting up Node.js server for local HTTPS development...", style="green")
        install_path = f"{MONARCH_ROOT}/toolbelt/"
        run_command(f"cp -r {install_path}node_server {install_path}setup/node_server", success_msg="✅ Node.js server copied successfully.", error_msg="❌ Failed to copy Node.js server")
        run_command(f"cd {install_path}/setup/node_server && npm install", success_msg="✅ NPM packages installed.", error_msg="❌ Failed to install NPM packages")
        run_command(f"cd {install_path}/setup/node_server && mkcert dev.monarchui.comcast.net", success_msg="✅ Certificate generated for dev.monarchui.comcast.net.", error_msg="❌ Failed to generate certificate")

    # check if file is already modified
    if "XERXES_WEB_REDIRECT_URI" in open(f"{MONARCH_ROOT}/app/.env").read():
        console.print("⚠️ XERXES_WEB_REDIRECT_URI already exists in .env file.", style="yellow")
    else:
        console.print("🔧 Updating .env file with XERXES_WEB_REDIRECT_URI...", style="green")
        env_file_path = f"{MONARCH_ROOT}/app/.env"
        xerxes_web_redirect_uri = "https://dev.monarchui.comcast.net/oauth2redirect"
        modify_file(env_file_path, f"\nXERXES_WEB_REDIRECT_URI={xerxes_web_redirect_uri}\n")

def is_firebase_cli_installed():
    return subprocess.getoutput("dart pub global list | grep flutterfire_cli").strip() != ""

def get_firebase_cli_version():
    try:
        result = subprocess.getoutput("flutterfire --version")
        return result.splitlines()[0] if result else "Unknown"
    except Exception:
        return "Unknown"

def update_hosts_file(interactive=False):
    hosts_file_path = "/etc/hosts"
    hosts_entries_file = f"{MONARCH_ROOT}/toolbelt/hosts_entries.txt"  
    # Read host entries from file
    try:
        with open(hosts_entries_file, "r") as file:
            hosts_entries = file.read().strip()
    except FileNotFoundError:
        console.print(f"❌ {hosts_entries_file} not found. Please ensure the file exists.", style="red")
        return        
    
    with open(hosts_file_path, "r") as file:
        current_contents = file.read()
    if any(line.strip() in current_contents for line in hosts_entries.splitlines()):
        console.print("⚠️ Some or all entries already exist in the /etc/hosts file.", style="yellow")
        return
    
    if interactive and not confirm_installation("Update /etc/hosts file"):
        modify_file(hosts_file_path, hosts_entries)

def switch_to_flutter_main(interactive=False):
    if subprocess.getoutput("flutter channel").strip() == "main":
        console.print("🔧 Flutter is already on the correct main revision (76fe247aae). Skipping.", style="yellow")
        return
    
    if interactive and not confirm_installation("Switch to Flutter main branch"):
        console.print("❌ Skipping switch to Flutter main branch.", style="red")
        return

    console.print("🔧 Switching to Flutter main for straight-up Flutter users...", style="green")
    run_command("flutter channel main --no-cache-artifacts", success_msg="✅ Switched to Flutter main channel.", error_msg="❌ Failed to switch to Flutter main channel")
    run_command("flutter upgrade", success_msg="✅ Flutter upgraded to the latest main version.", error_msg="❌ Failed to upgrade Flutter")

    flutter_bin_dir = subprocess.getoutput("which flutter | xargs dirname | xargs dirname")
    run_command(f"cd {flutter_bin_dir} && git checkout 76fe247aae", success_msg="✅ Checked out Flutter revision 76fe247aae.", error_msg="❌ Failed to check out the correct Flutter revision")
    
    
    # console.print("🔧 Switching to Flutter main using FVM...", style="green")
    # run_command("fvm use main", success_msg="✅ Switched to Flutter main using FVM.", error_msg="❌ Failed to switch to Flutter main using FVM")
    # run_command("fvm global main", success_msg="✅ Set Flutter main as global using FVM.", error_msg="❌ Failed to set Flutter main as global using FVM")
    
    run_command("flutter pub global activate melos", success_msg="✅ Melos activated globally.", error_msg="❌ Failed to activate Melos")

    console.print("🎉 Flutter is now on the correct main revision (76fe247aae).", style="bold green")
    console.print("run 'fvm global main' to set Flutter main as global using FVM.", style="bold green")
    console.print(f"run 'fvm use main' in {MONARCH_ROOT} to to set Flutter main for the project.", style="bold green")
    console.print("👉 Run `melos bs` to bootstrap Melos.", style="bold")

def print_step_descriptions():
    steps = [
        ("🍺 Install Homebrew", "Homebrew is a package manager for macOS that simplifies the installation of software. It's essential for installing many development tools."),
        ("🧊 Install rbenv and Ruby 3.1.0", "rbenv allows you to manage multiple Ruby versions. This step installs rbenv and sets up Ruby 3.1.0, which is required for some build tools."),
        ("🔧 Install Bundler", "Bundler is a Ruby gem that helps manage dependencies in Ruby projects. It ensures that you use the same versions of gems as specified in the project."),
        ("🔧 Install Flutter using FVM", "FVM (Flutter Version Manager) helps manage multiple versions of Flutter. This step ensures that the correct Flutter version is installed and used globally."),
        ("🤖 Install Android Studio", "Android Studio is the official IDE for Android development. It includes the Android SDK, which is required for building and running Flutter apps on Android."),
        ("🛠️ Install Xcode Command Line Tools", "Xcode Command Line Tools are necessary for iOS development. They provide essential tools for building and running Flutter apps on iOS."),
        ("🌱 Install CocoaPods", "CocoaPods is a dependency manager for iOS projects. It's required for integrating third-party libraries into iOS apps."),
        ("🚀 Install Fastlane", "Fastlane automates app releases and other development tasks. It's widely used for deploying Flutter apps to the App Store and Google Play."),
        ("🔥 Install Firebase CLI", "The Firebase CLI allows you to manage Firebase projects and interact with Firebase services. It's crucial for apps that use Firebase."),
        ("🎛️ Install and set up Melos", "Melos is a tool for managing monorepos in Dart and Flutter projects. This step ensures that Melos is installed and ready to use."),
        ("⚙️ Install DCM", "Dart Code Metrics (DCM) is a static analysis tool. This step installs DCM and optionally activates it using a license key."),
        ("🔐 Set up GPG for commit signing", "GPG ensures that all commits are signed and verifiable. This step installs GPG, generates a new GPG key, and configures Git to sign commits by default."),
        ("🔧 Set up pre-commit hooks", "Pre-commit hooks run checks before code is committed. This step installs pre-commit and sets up the hooks for the repository."),
        ("🔧 Set up Android keystore", "This step helps you create a keystore for Android release builds and configures the project to use it."),
        ("🔧 Set up MkCert and Node.js server for HTTPS", "This step installs MkCert for generating local HTTPS certificates, sets up a Node.js server, and configures the Flutter web app for local HTTPS development."),
        ("⚙️ Update /etc/hosts file", "This step updates the /etc/hosts file with the necessary domain entries, ensuring that your system resolves internal domains correctly."),
        ("🔧 Switch to Flutter main branch", "This step switches your local Flutter setup to the main branch and ensures that you're using the correct revision. This is necessary as part of the migration to Flutter main.")
    ]

    console.print(Panel.fit("\n🛠️ The interactive setup will guide you through the following steps:\n", title="Interactive Setup", style="bold"))
    for step_name, description in steps:
        console.print(f"[cyan]{step_name}[/cyan]: {description}")
    console.print(Panel.fit("\n⚠️ Once all steps are completed, you'll be ready to start development. Some steps require manual actions, so please follow the prompts carefully.\n", style="bold red"))

def print_status_table():
    console.print(Panel.fit("🔍 Checking status of installed tools...", style="bold cyan"))
    anrdoi_keystore_path = os.path.expanduser("~/keystores/monarch-ui.keystore")
    tools = [
        {"Tool": "Homebrew", "Installed": is_installed("brew", doctor=True), "Version": get_version("brew")},
        {"Tool": "rbenv", "Installed": is_installed("rbenv", doctor=True), "Version": get_version("rbenv")},
        {"Tool": "FVM", "Installed": is_installed("fvm", doctor=True), "Version": get_version("fvm")},
        {"Tool": "Flutter (fvm global)", "Installed": is_installed("flutter", doctor=True), "Version": get_version("flutter")},
        {"Tool": "Android Studio", "Installed": os.path.exists("/Applications/Android Studio.app"), "Version": "Check manually"},
        {"Tool": "Xcode Command Line Tools", "Installed": is_installed("xcode-select", doctor=True), "Version": get_version("xcode-select")},
        {"Tool": "CocoaPods", "Installed": is_installed("pod", doctor=True), "Version": get_version("pod")},
        {"Tool": "Fastlane", "Installed": is_installed("fastlane", doctor=True), "Version": get_version("fastlane")},
        {"Tool": "Firebase CLI", "Installed": is_firebase_cli_installed(), "Version": get_firebase_cli_version()},
        {"Tool": "Melos", "Installed": is_installed("melos", doctor=True), "Version": get_version("melos")},
        {"Tool": "Bundler", "Installed": is_installed("bundler", doctor=True), "Version": get_version("bundler")},
        {"Tool": "DCM", "Installed": is_installed("dcm", doctor=True), "Version": get_version("dcm")},
        {"Tool": "GPG", "Installed": is_installed("gpg", doctor=True), "Version": get_version("gpg")},
        {"Tool": "Pre-commit", "Installed": is_installed("pre-commit", doctor=True), "Version": get_version("pre-commit")},
        {"Tool": "MkCert", "Installed": is_installed("mkcert", doctor=True), "Version": get_version("mkcert")},
        {"Tool": "Node.js", "Installed": is_installed("node", doctor=True), "Version": get_version("node")},
        {"Tool": "Node.js server", "Installed": is_node_server_installed(), "Version": "Check manually"},
        {"Tool": "Android keystore", "Installed": os.path.exists(anrdoi_keystore_path), "Version": "Check manually"},
        {"Tool": "MkCert", "Installed": is_installed("mkcert", doctor=True), "Version": get_version("mkcert")},
        {"Tool": "Sky network", "Installed": is_connected_to_sky_network(), "Version": "Check manually"},
    ]

    table = Table(title="Summary of Installed Tools")

    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Installed", justify="center")
    table.add_column("Version", justify="center")

    for tool in tools:
        installed_text = "✅ Yes" if tool["Installed"] else "❌ No"
        table.add_row(tool["Tool"], installed_text, tool["Version"])

    console.print(table)

@click.group()
def cli():
    """Monarch Tool - A multitool for automating Monarch UI setup"""

@cli.command()
@click.option('--all', is_flag=True, help="Install all dependencies")
@click.option('--dry-run', is_flag=True, help="Perform a dry run without making changes")
@click.option('--homebrew', is_flag=True, help="Install Homebrew")
@click.option('--rbenv', is_flag=True, help="Install rbenv and Ruby 3.1.0")
@click.option('--flutter', is_flag=True, help="Install Flutter using FVM")
@click.option('--android-studio', is_flag=True, help="Install Android Studio")
@click.option('--xcode', is_flag=True, help="Install Xcode command line tools")
@click.option('--cocoapods', is_flag=True, help="Install CocoaPods")
@click.option('--fastlane', is_flag=True, help="Install Fastlane")
@click.option('--firebase-cli', is_flag=True, help="Install Firebase CLI")
@click.option('--melos', is_flag=True, help="Install and set up Melos")
@click.option('--bundler', is_flag=True, help="Install Bundler")
@click.option('--dcm', is_flag=True, help="Install DCM")
@click.option('--gpg', is_flag=True, help="Set up GPG for commit signing")
@click.option('--pre-commit', is_flag=True, help="Set up pre-commit hooks")
@click.option('--android-keystore', is_flag=True, help="Set up Android keystore")
@click.option('--mkcert-node', is_flag=True, help="Set up MkCert and Node.js server")
def install(all, dry_run, **kwargs):
    """Install dependencies"""
    if dry_run==True:
        global DRY_RUN
        DRY_RUN = dry_run

    steps = [
        ("🍺 Install Homebrew", kwargs['homebrew'], install_homebrew),
        ("🧊 Install rbenv and Ruby 3.1.0", kwargs['rbenv'], install_rbenv),
        ("📦 Install Bundler", kwargs['bundler'], install_bundler),
        ("🛠️ Install Flutter using FVM", kwargs['flutter'], install_flutter),
        ("🤖 Install Android Studio", kwargs['android_studio'], install_android_studio),
        ("🛠️ Install Xcode Command Line Tools", kwargs['xcode'], install_xcode),
        ("🌱 Install CocoaPods", kwargs['cocoapods'], install_cocoapods),
        ("🚀 Install Fastlane", kwargs['fastlane'], install_fastlane),
        ("🔥 Install Firebase CLI", kwargs['firebase_cli'], install_firebase_cli),
        ("🎛️ Install and set up Melos", kwargs['melos'], install_melos),
        ("⚙️ Install DCM", kwargs['dcm'], install_dcm),
        ("🔐 Set up GPG for commit signing", kwargs['gpg'], setup_gpg),
        ("🔧 Set up pre-commit hooks", kwargs['pre_commit'], setup_pre_commit_hooks),
        ("🔑 Set up Android keystore", kwargs['android_keystore'], setup_android_keystore),
        ("🔧 Set up MkCert and Node.js server for HTTPS", kwargs['mkcert_node'], setup_mkcert_and_node_server)
    ]

    for step_name, should_run, install_func in steps:
        if should_run or all:
            print_rich_step(step_name)
            install_func()

@cli.command()
@click.option('--all', is_flag=True, help="Install all dependencies")
@click.option('--homebrew', is_flag=True, help="Install Homebrew")
@click.option('--rbenv', is_flag=True, help="Install rbenv and Ruby 3.1.0")
@click.option('--flutter', is_flag=True, help="Install Flutter using FVM")
@click.option('--android-studio', is_flag=True, help="Install Android Studio")
@click.option('--xcode', is_flag=True, help="Install Xcode command line tools")
@click.option('--cocoapods', is_flag=True, help="Install CocoaPods")
@click.option('--fastlane', is_flag=True, help="Install Fastlane")
@click.option('--firebase-cli', is_flag=True, help="Install Firebase CLI")
@click.option('--melos', is_flag=True, help="Install and set up Melos")
@click.option('--bundler', is_flag=True, help="Install Bundler")
@click.option('--dcm', is_flag=True, help="Install DCM")
@click.option('--gpg', is_flag=True, help="Set up GPG for commit signing")
@click.option('--pre-commit', is_flag=True, help="Set up pre-commit hooks")
@click.option('--android-keystore', is_flag=True, help="Set up Android keystore")
@click.option('--mkcert-node', is_flag=True, help="Set up MkCert and Node.js server")
def install(all, **kwargs):
    """Install dependencies"""

    steps = [
        ("🍺 Install Homebrew", kwargs['homebrew'], install_homebrew),
        ("🧊 Install rbenv and Ruby 3.1.0", kwargs['rbenv'], install_rbenv),
        ("📦 Install Bundler", kwargs['bundler'], install_bundler),
        ("🛠️ Install Flutter using FVM", kwargs['flutter'], install_flutter),
        ("🤖 Install Android Studio", kwargs['android_studio'], install_android_studio),
        ("🛠️ Install Xcode Command Line Tools", kwargs['xcode'], install_xcode),
        ("🌱 Install CocoaPods", kwargs['cocoapods'], install_cocoapods),
        ("🚀 Install Fastlane", kwargs['fastlane'], install_fastlane),
        ("🔥 Install Firebase CLI", kwargs['firebase_cli'], install_firebase_cli),
        ("🎛️ Install and set up Melos", kwargs['melos'], install_melos),
        ("⚙️ Install DCM", kwargs['dcm'], install_dcm),
        ("🔐 Set up GPG for commit signing", kwargs['gpg'], setup_gpg),
        ("🔧 Set up pre-commit hooks", kwargs['pre_commit'], setup_pre_commit_hooks),
        ("🔑 Set up Android keystore", kwargs['android_keystore'], setup_android_keystore),
        ("🔧 Set up MkCert and Node.js server for HTTPS", kwargs['mkcert_node'], setup_mkcert_and_node_server)
    ]

    for step_name, should_run, install_func in steps:
        if should_run or all:
            print_rich_step(step_name)
            install_func()

@cli.command()
def doctor():
    """Check status of installed tools"""

    print_status_table()
    
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
    
def check_monrch_root():
    if not os.path.exists(MONARCH_ROOT):
        console.print("❌ Monarch UI root directory not found. Please ensure the toolbelt is located in the correct directory.", style="red")
        console.print(f"./setup.sh might not have been run", style="bold")
        console.print(f"Refer to the README.md for more information", style="bold")
        sys.exit(1)
    
def is_connected_to_sky_network():
    """Check if the user is connected to Sky network or VPN."""
    return can_reach_ip("10.72.126.93")

@cli.command()
def interactive():
    """Interactive step-by-step setup"""
    check_monrch_root()
    aquire_super_user_privileges()
    interactive_setup()

@cli.command()
def fix():
    """Fix broken dependencies"""

    console.print("Not implemented yet.", style="bold red")

@cli.command()
def update_hosts():
    """Update /etc/hosts file with required entries"""

    update_hosts_file(interactive=True)

@cli.command()
def start_node_server():
    """Start Node.js server for local HTTPS development"""

    console.print("🔧 Starting Node.js server...", style="green")
    run_command(f"cd {MONARCH_ROOT}/toolbelt/setup/node_server && node app.mjs", success_msg="✅ Node.js server started successfully.", error_msg="❌ Failed to start Node.js server")

@cli.command()
def switch_to_flutter_main_cmd():
    """Switch to Flutter main branch and set up environment"""

    switch_to_flutter_main(interactive=True)

def print_rich_step(step_name):
    """Print a rich-styled separator for each step."""
    console.print(Panel(step_name, style="bold yellow"))

def interactive_setup():
    """Guide the user through the setup process step by step."""
    steps = [
        ("🍺 Install Homebrew", install_homebrew),
        ("🧊 Install rbenv and Ruby 3.1.0", install_rbenv),
        ("🔧 Install Bundler", install_bundler),
        ("🔧 Install Flutter using FVM", install_flutter),
        ("🤖 Install Android Studio", install_android_studio),
        ("🛠️ Install Xcode Command Line Tools", install_xcode),
        ("🌱 Install CocoaPods", install_cocoapods),
        ("🚀 Install Fastlane", install_fastlane),
        ("🔥 Install Firebase CLI", install_firebase_cli),
        ("🎛️ Install and set up Melos", install_melos),
        ("⚙️ Install DCM", install_dcm),
        ("🔐 Set up GPG for commit signing", setup_gpg),
        ("🔧 Set up pre-commit hooks", setup_pre_commit_hooks),
        ("🔧 Set up Android keystore", setup_android_keystore),
        ("🔧 Set up MkCert and Node.js server for HTTPS", setup_mkcert_and_node_server),
        ("⚙️ Update /etc/hosts file", update_hosts_file),
        ("🔧 Switch to Flutter main branch", switch_to_flutter_main)
    ]

    console.print(Panel.fit("🛠️ Starting interactive setup...", title="Interactive Setup", style="bold cyan"))
    for step_name, install_func in steps:
        print_rich_step(f"Step: {step_name}")
        install_func(interactive=True)

    print_rich_step("📄 Manual Step: Copy the .env File")
    console.print("📝 Copy the `.env-example` file to `/app/.env` and request the required secrets from the team.", style="bold")
    if not os.path.exists(f"{MONARCH_ROOT}/app/.env"):
        run_command(f"cp {MONARCH_ROOT}/app/.env-example {MONARCH_ROOT}/app/.env", success_msg="✅ .env file copied successfully.", error_msg="❌ Failed to copy .env file")
    else:
        console.print("⚠️ The .env file already exists. Please ensure it has the correct secrets.", style="yellow")
    run_command(f"open {MONARCH_ROOT}/app/.env")
    input("❓ Press Enter once you have completed this step...")

    print_rich_step("📄 Manual Step: Set up iOS Certificate and Provisioning Profile")
    console.print("📝 Request the `.p12` private key for the signing certificate and its passphrase from the team. Then, follow the steps in the README to configure Xcode.", style="bold")
    run_command(f"open {MONARCH_ROOT}/app/ios/Runner.xcworkspace")
    input("❓ Press Enter once you have completed this step...")

    print_rich_step("🔍 Testing Step: Check Status of Installed Tools")
    console.print("🔧 Check status of installed tools.", style="bold")
    print_status_table()

    print_rich_step("🛠️ Testing Step: Run the App")
    run_command(f"cd {MONARCH_ROOT}/app && melos bs", success_msg="✅ App ran successfully.", error_msg="❌ Failed to run the app")
    console.print("🚀 Run 'flutter run' to test your app on iOS, Android, and Web.", style="bold")
    run_command(f"cd {MONARCH_ROOT}/app && fvm flutter run", success_msg="✅ App ran successfully.", error_msg="❌ Failed to run the app")
    input("❓ Press Enter once you've confirmed the app works on all platforms...")

    console.print(Panel.fit("🎉 Interactive setup and testing complete!", style="bold green"))

if __name__ == "__main__":
    cli()
