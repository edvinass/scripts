import os
import shutil
import json

def move_files(current_dir, target_dir, input1, input2):
    # Flatten the file structure of input1 to find the current location of each file
    current_locations = {}
    flatten_structure(current_dir, input1, current_locations)
    
    # Flatten the file structure of input2 to find where each file should be moved
    target_locations = {}
    flatten_structure(target_dir, input2, target_locations)
    
    # Move the files from current_locations to target_locations
    for file_name, target_path in target_locations.items():
        if file_name in current_locations:
            current_path = current_locations[file_name]
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.move(current_path, target_path)
            print(f"Moved {file_name} from {current_path} to {target_path}")
        else:
            print(f"File {file_name} not found in current structure.")

def flatten_structure(base_path, structure, file_locations, current_path=""):
    """
    Recursively flatten the directory structure and collect the full paths of each file.
    """
    for key, value in structure.items():
        new_path = os.path.join(base_path, current_path, key)
        if isinstance(value, dict):
            flatten_structure(base_path, value, file_locations, os.path.join(current_path, key))
        else:
            file_locations[key] = new_path

# Load the input JSON files
with open('input1.json', 'r') as f:
    input1 = json.load(f)

with open('input2.json', 'r') as f:
    input2 = json.load(f)

# Define the base directories for input1 and input2
current_directory = "path_to_current_directory"
target_directory = "path_to_target_directory"

# Move the files based on the input JSON structures
move_files(current_directory, target_directory, input1, input2)
