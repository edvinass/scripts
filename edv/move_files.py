#!/usr/bin/env python3
import os
import shutil
import json


def verify_params(current_dir, target_dir, input1, input2, dry_run=True):
    # Print params for debugging
    print(f"Current Directory: {current_dir}")
    print(f"Target Directory: {target_dir}")
    print(f"Input1: {input1}")
    print(f"Input2: {input2}")
    print(f"Dry Run: {dry_run}")
    

def move_files(current_dir: str, target_dir: str, input1: dict, input2: dict, copy=True, dry_run=True):
    verify_params(current_dir, target_dir, input1, input2, dry_run)
    """ Move files from the current directory structure to the target directory structure.
    Args:
        current_dir (str): The path to the current directory.
        target_dir (str): The path to the target directory.
        input1 (dict): The JSON representation of the current directory structure.
        input2 (dict): The JSON representation of the target directory structure.
        dry_run (bool, optional): If True, the files will not be moved. Defaults to True.
    """
    # Flatten the file structure of input1 to find the current location of each file
    current_locations: dict = {}
    flatten_structure(current_dir, input1, current_locations)
    
    # Flatten the file structure of input2 to find where each file should be moved
    target_locations: dict = {}
    flatten_structure(target_dir, input2, target_locations)
    
    # Move the files from current_locations to target_locations
    for file_name, target_path in target_locations.items():
        print(f"Moving {file_name} to {target_path}")
        if file_name in current_locations:
            current_path = current_locations[file_name]
            if not dry_run: 
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                if copy:
                    shutil.copy(current_path, target_path)
                    print(f"Copied {file_name} from {current_path} to {target_path}")
                else:
                    shutil.move(current_path, target_path)
                    print(f"Moved {file_name} from {current_path} to {target_path}")
        else:
            print(f"File {file_name} not found in current structure.")

def flatten_structure(base_path: str, structure: dict, file_locations: dict, current_path=""):
    """
    Recursively flatten the directory structure and collect the full paths of each file.
    """
    for key, value in structure.items():
        new_path = os.path.join(base_path, current_path, key)
        if isinstance(value, dict):
            flatten_structure(base_path, value, file_locations, os.path.join(current_path, key))
        else:
            file_locations[key] = new_path
