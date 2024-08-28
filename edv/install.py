from utils import *
    
# Specific Installation Functions with Checks
def install_homebrew(interactive=False):
    check_and_install_tool("brew", lambda: run_command(
        '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        success_msg="🍺 Homebrew installed successfully.",
        error_msg="❌ Failed to install Homebrew"
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