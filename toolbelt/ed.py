#!/usr/bin/env python3

import os
import click

from rich.console import Console

from utils import *
from install import *
from interactive import *

ED_ROOT = os.environ.get("ED_ROOT")
console = Console()

DRY_RUN = False

@click.group()
def cli():
    """Monarch Tool - A multitool for automating Monarch UI setup"""
    
@cli.command()
@click.option('--all', is_flag=True, help="Install all dependencies")
@click.option('--homebrew', is_flag=True, help="Install Homebrew")
@click.option('--android-studio', is_flag=True, help="Install Android Studio")
@click.option('--xcode', is_flag=True, help="Install Xcode command line tools")
@click.option('--cocoapods', is_flag=True, help="Install CocoaPods")
@click.option('--gpg', is_flag=True, help="Set up GPG for commit signing")
@click.option('--pre-commit', is_flag=True, help="Set up pre-commit hooks")

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

@cli.command()
def doctor():
    """Check status of installed tools"""
    print_status_table()
    
if __name__ == "__main__":
    cli()
