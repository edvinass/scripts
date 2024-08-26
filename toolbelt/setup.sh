#!/bin/bash

# Print a message about what the script is doing
echo "Setting up the Python environment and toolbelt command..."

# Determine the repository root path (one level up from where the script is located)
REPO_ROOT=$(dirname "$(pwd)")

# Print the detected repository path and ask for confirmation
echo "Detected repository root at: $REPO_ROOT"
read -p "Is this correct? (y/n): " CONFIRM

# If the user does not confirm, exit the setup script
if [[ "$CONFIRM" != "y" ]]; then
    echo "Setup aborted. Please move the script to the correct location or update the repository path."
    exit 1
fi

# Define the directory for the Python environment in the "toolbelt/setup" subdirectory
ENV_DIR="$REPO_ROOT/toolbelt/setup/toolbelt_python_env"

# Create the "toolbelt/setup" directory if it doesn't exist
mkdir -p "$REPO_ROOT/toolbelt/setup"

# Print a message about the environment setup
echo "Creating a virtual environment at $ENV_DIR..."

# Create the virtual environment in the specified directory
python3 -m venv $ENV_DIR

# Print a message about activating the virtual environment
echo "Activating the virtual environment..."

# Activate the virtual environment
source $ENV_DIR/bin/activate

# Print a message about upgrading pip
echo "Upgrading pip..."

# Upgrade pip
pip install --upgrade pip

# Print a message about installing dependencies
REQUIREMENTS_FILE="$REPO_ROOT/toolbelt/requirements.txt"
echo "Installing dependencies from $REQUIREMENTS_FILE..."

# Check if the requirements.txt file exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "ERROR: Could not find the requirements.txt file at $REQUIREMENTS_FILE"
    echo "Please ensure the file exists in the 'setup' subdirectory of 'toolbelt'."
    exit 1
fi

# Install the dependencies
pip install -r $REQUIREMENTS_FILE

# Determine the user's shell and corresponding configuration file
if [[ "$SHELL" == *"zsh"* ]]; then
    PROFILE_FILE="$HOME/.zshrc"
    echo "Detected zsh shell. Using $PROFILE_FILE for environment variables."
elif [[ "$SHELL" == *"bash"* ]]; then
    PROFILE_FILE="$HOME/.bashrc"
    echo "Detected bash shell. Using $PROFILE_FILE for environment variables."
else
    PROFILE_FILE="$HOME/.profile"
    echo "Unknown shell. Defaulting to $PROFILE_FILE for environment variables."
fi

# Print a message about adding MONARCH_ROOT environment variable
echo "Adding MONARCH_ROOT environment variable to $PROFILE_FILE..."

# Add MONARCH_ROOT environment variable to the user's shell configuration
echo "export MONARCH_ROOT=\"$REPO_ROOT\"" >> $PROFILE_FILE

# Create a simple wrapper script for the command named 'toolbelt'
TOOLBELT_COMMAND="$REPO_ROOT/toolbelt/setup/toolbelt"
echo "Creating the toolbelt command at $TOOLBELT_COMMAND..."

cat <<EOL > $TOOLBELT_COMMAND
#!/bin/bash
# Activate the virtual environment
source $ENV_DIR/bin/activate
# Run the Python script with the provided arguments
python $REPO_ROOT/toolbelt/toolbelt.py "\$@"
EOL

# Make the wrapper script executable
chmod +x $TOOLBELT_COMMAND

# Print a message about adding the script to the user's PATH
echo "Adding the toolbelt command to your PATH in $PROFILE_FILE..."

# Add the script to the user's PATH in their shell configuration
echo "export PATH=\"$REPO_ROOT/toolbelt/setup:\$PATH\"" >> $PROFILE_FILE

# Notify the user to reload their shell manually
echo "Setup complete. Please run the following command to reload your shell configuration:"
if [[ "$SHELL" == *"zsh"* ]]; then
    echo "source ~/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    echo "source ~/.bashrc"
else
    echo "source ~/.profile"
fi

echo "You can now use the 'toolbelt' command to run your script."
