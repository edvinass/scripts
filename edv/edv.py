#!/usr/bin/env python3

import os
import click

from rich.console import Console

from utils import *
from install import *
from interactive import *
from openai_utils import *

ED_ROOT = os.environ.get("EDV_ROOT")
console = Console()

DRY_RUN = False

@click.group()
def cli():
    """Ed Tool - A multitool for automating Monarch UI setup"""

@cli.command()
@click.option('--all', is_flag=True, help="Install all dependencies")
@click.option('--homebrew', is_flag=True, help="Install Homebrew")
@click.option('--gpg', is_flag=True, help="Set up GPG for commit signing")
@click.option('--pre-commit', is_flag=True, help="Set up pre-commit hooks")
def install(all, **kwargs):
    """Install dependencies"""

    steps = [
        ("🍺 Install Homebrew", kwargs['homebrew'], install_homebrew),
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
    
@cli.command()
def interactive():
    """Interactive setup"""
    interactive_setup()
    
@cli.command()
def ai():
    """AI"""
    write_story()
    
@cli.command()
@click.argument('dir')
def directory(dir):
    """Directory"""
    sturcture = format_structure(get_directory_structure(dir))
    console.print(sturcture)
    console.print(directory_suggestion(sturcture), style="bold")
    
    
if __name__ == "__main__":
    cli()
