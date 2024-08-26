# Monarch Tool Setup

This repository contains the `Monarch Tool`, a multitool for automating Monarch UI setup and environment configuration.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Commands](#commands)

## Requirements

Ensure you have the following installed on your machine:

- Python 3.x
- Git

If you don't have `pip` installed, follow the instructions [here](https://pip.pypa.io/en/stable/installation/).

## Installation

Follow these steps to set up your environment:

1. **Set up the Python virtual environment:**
   This repository comes with a `setup.sh` script that handles setting up a virtual environment and installing the required Python packages.

   To execute the setup script from monarch repo, run:

   ```bash
   cd <monarch_repo>/toolbelt
   ./setup.sh
   source ~/.zshrc
   ```

## Usage

Once the environment is set up, you can use the `Monarch Tool` by running the `toolbelt` command. It supports several commands for installing dependencies, checking the environment, and interactive setup.

### Running the tool:

```bash
toolbelt <command>
```

### Example:

```bash
toolbelt interactive
```

## Commands

Here is a list of the available commands in `toolbelt`:

- `install`  
  Install various dependencies. You can use the `--all` flag to install everything or specific flags to install individual components.

  Example:

  ```bash
  toolbelt install --homebrew
  ```

- `doctor`  
  Check the status of installed tools and their versions.

  Example:

  ```bash
  toolbelt doctor
  ```

- `interactive`  
  Run an interactive step-by-step setup guide.

  Example:

  ```bash
  toolbelt interactive
  ```

- `fix`  
  Fix broken dependencies (not implemented yet).

  Example:

  ```bash
  toolbelt fix
  ```

- `update-hosts`  
  Update the `/etc/hosts` file with required entries.

  Example:

  ```bash
  toolbelt update-hosts
  ```

- `switch-to-flutter-main`  
   Switch to the Flutter main branch and set up the environment.

  Example:

  ```bash
  toolbelt switch-to-flutter-main
  ```
