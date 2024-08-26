from utils import *
from install import *

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
    ]

    table = Table(title="Summary of Installed Tools")

    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Installed", justify="center")
    table.add_column("Version", justify="center")

    for tool in tools:
        installed_text = "✅ Yes" if tool["Installed"] else "❌ No"
        table.add_row(tool["Tool"], installed_text, tool["Version"])

    console.print(table)
    
def interactive_setup():
    """Guide the user through the setup process step by step."""
    steps = [
        ("🍺 Install Homebrew", install_homebrew),
        ("🔐 Set up GPG for commit signing", setup_gpg),
        ("🔧 Set up pre-commit hooks", setup_pre_commit_hooks),
    ]

    console.print(Panel.fit("🛠️ Starting interactive setup...", title="Interactive Setup", style="bold cyan"))
    for step_name, install_func in steps:
        print_rich_step(f"Step: {step_name}")
        install_func(interactive=True)