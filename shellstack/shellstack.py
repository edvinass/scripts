#!/usr/bin/env python3

import os
import click

from rich.console import Console

from utils import *
from install import *
from interactive import *
from openai_utils import *
from move_files import *

ED_ROOT = os.environ.get("SHELLSTACK_ROOT")
console = Console()

DRY_RUN = False

@click.group()
def cli():
    """ShellStack - A multitool for automating Monarch UI setup"""

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
    input_dict = json.loads(directory_to_json(dir))
    console.print(input_dict, style="blue")
    output_dict = json.loads(directory_suggestion(input_dict))
    console.print(output_dict, style="bold green")
    target_directory = dir + "_updated"
    print(f"Target Directory: {target_directory}")
    move_files(dir, target_directory, input_dict, output_dict, copy=True, dry_run=DRY_RUN)
    
if __name__ == "__main__":
    cli()
