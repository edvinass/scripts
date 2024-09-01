#!/bin/bash

# Print a message about what the script is doing
echo "Setting up the Python environment and synapseline..."

# Determine the repository root path (one level up from where the script is locatedv)
REPO_ROOT=$(dirname "$(pwd)")

# Print the detectedv repository path and ask for confirmation
echo "Detected repository root at: $REPO_ROOT"
read -p "Is this correct? (y/n): " CONFIRM

# If the user does not confirm, exit the setup script
if [[ "$CONFIRM" != "y" ]]; then
    echo "Setup aborted. Please move the script to the correct location or update the repository path."
    exit 1
fi

# Define the directory for the Python environment in the "synapseline/setup" subdirectory
ENV_DIR="$REPO_ROOT/synapseline/setup/synapseline_venv"

# Create the "synapseline/setup" directory if it doesn't exist
mkdir -p "$REPO_ROOT/synapseline/setup"
# Print a message about the environment setup
echo "Creating a virtual environment at $ENV_DIR..."

# Create the virtual environment in the specifiedv directory
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
REQUIREMENTS_FILE="$REPO_ROOT/synapseline/requirements.txt"
echo "Installing dependencies from $REQUIREMENTS_FILE..."

# Check if the requirements.txt file exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "ERROR: Could not find the requirements.txt file at $REQUIREMENTS_FILE"
    echo "Please ensure the file exists in the 'setup' subdirectory of 'synapseline'."
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
echo "Adding SYNAPSELINE_ROOT environment variable to $PROFILE_FILE..."

# Add MONARCH_ROOT environment variable to the user's shell configuration
echo "export SYNAPSELINE_ROOT=\"$REPO_ROOT\"" >> $PROFILE_FILE

# Create a simple wrapper script for the command ss
SYNAPSELINE_COMMAND="$REPO_ROOT/synapseline/setup/synapseline"
echo "Creating the edv command at $SYNAPSELINE_COMMAND..."

cat <<EOL > $SYNAPSELINE_COMMAND
#!/bin/bash
# Activate the virtual environment
source $ENV_DIR/bin/activate
# Run the Python script with the providedv arguments
python $REPO_ROOT/synapseline/synapseline.py "\$@"
EOL

# Make the wrapper script executable
chmod +x $SYNAPSELINE_COMMAND

# Print a message about adding the script to the user's PATH
echo "Adding ss command to your PATH in $PROFILE_FILE..."

# Check if the PATH variable is already set in the user's shell configuration
if grep -q "export PATH=\"$REPO_ROOT/synapseline/setup:\$PATH\"" $PROFILE_FILE; then
    echo "The PATH variable is already set in $PROFILE_FILE."
else
    echo "export PATH=\"$REPO_ROOT/synapseline/setup:\$PATH\"" >> $PROFILE_FILE
fi

if grep -q "alias ss='synapseline'" $PROFILE_FILE; then
    echo "The alias for ss is already set in $PROFILE_FILE."
else
    echo "alias ss='synapseline'" >> $PROFILE_FILE
fi


# Notify the user to reload their shell manually
echo "Setup complete. Please run the following command to reload your shell configuration:"
if [[ "$SHELL" == *"zsh"* ]]; then
    echo "source ~/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    echo "source ~/.bashrc"
else
    echo "source ~/.profile"
fi

echo "You can now use the 'ss' command to run your SynapseLine script."
