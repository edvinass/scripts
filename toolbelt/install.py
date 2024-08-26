from utils import *

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
    
def setup_gpg(interactive=False):
    if check_and_install_tool("gpg", lambda: run_command("brew install gnupg", success_msg="🔐 GPG installed successfully.", error_msg="❌ Failed to install GPG"), interactive):
        console.print("🔧 Generating a new GPG key...", style="green")
        run_command("gpg --full-generate-key", success_msg="✅ GPG key generated successfully.", error_msg="❌ Failed to generate GPG key")
        run_command("git config --global commit.gpgsign true", success_msg="✅ Git configured to sign commits by default.", error_msg="❌ Failed to configure Git")
        console.print("\n⚙️  Next steps: Add your GPG key to your GitHub account.", style="bold")    

def setup_pre_commit_hooks(interactive=False):
    if check_and_install_tool("pre-commit", lambda: run_command("brew install pipx && pipx install pre-commit", success_msg="✅ Pre-commit installed successfully.", error_msg="❌ Failed to install pre-commit"), interactive):
        run_command("pre-commit install -t pre-commit -t commit-msg", success_msg="✅ Pre-commit hooks installed successfully.", error_msg="❌ Failed to install pre-commit hooks")

def install(all, **kwargs):
    """Install dependencies"""

    steps = [
        ("🍺 Install Homebrew", kwargs['homebrew'], install_homebrew),
        ("🧊 Install rbenv and Ruby 3.1.0", kwargs['rbenv'], install_rbenv),
        ("📦 Install Bundler", kwargs['bundler'], install_bundler),
        ("🛠️ Install Flutter using FVM", kwargs['flutter'], install_flutter),
        ("🤖 Install Android Studio", kwargs['android_studio'], install_android_studio),
        ("🛠️ Install Xcode Command Line Tools", kwargs['xcode'], install_xcode),
        ("🔐 Set up GPG for commit signing", kwargs['gpg'], setup_gpg),
        ("🔧 Set up pre-commit hooks", kwargs['pre_commit'], setup_pre_commit_hooks),
    ]

    for step_name, should_run, install_func in steps:
        if should_run or all:
            print_rich_step(step_name)
            install_func()