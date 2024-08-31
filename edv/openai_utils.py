import json
from openai import OpenAI
import os

client = OpenAI()

def write_story():
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Write a haiku about recursion in programming."
            }
        ]
    )
    
    print(completion.choices[0].message.content)
    
def directory_suggestion(directory_structure):
    message = f"""
Task: Given the provided directory structure, reorganize the files and folders for improved clarity and efficiency. Create a JSON representation showing the updated directory structure after the changes. Consider organizing files by their type (e.g., documents, archives, code files) and grouping related items into subfolders.

Current Directory Structure:
{directory_structure}. 
Output Requirements:
- Provide a new directory structure in JSON format.
- Group similar items into folders (e.g., Documents, Archives, Code, etc.).
- Remove or consolidate unnecessary or redundant files.
- Ensure the new structure is logical and easy to navigate.
"""
    print(message)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": message
            }
        ]
    )
    return completion.choices[0].message.content

def get_directory_structure(root_dir):
    """
    Recursively builds a nested dictionary that represents the folder structure of root_dir.
    
    :param root_dir: The root directory to start scanning.
    :return: A nested dictionary representing the directory structure.
    """
    dir_structure = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Split the directory path into parts
        path_parts = os.path.relpath(dirpath, root_dir).split(os.sep)
        
        # Navigate through the nested dictionary to create or find the correct place
        current_level = dir_structure
        for part in path_parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
        
        # Add files to the current level
        for filename in filenames:
            current_level[filename] = None  # Files are leaf nodes, so set their value to None

    return dir_structure
            
def format_structure(dir_structure, indent=0):
    """same as print_directory_structure but returns a string instead of printing"""
    result = ""
    for key, value in dir_structure.items():
        result += '    ' * indent + str(key) + "\n"
        if isinstance(value, dict):
            result += format_structure(value, indent + 1)
    return result
    
def directory_to_json(path):
    def dir_to_dict(dir_path):
        structure = {}
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path):
                structure[item] = dir_to_dict(item_path)
            else:
                structure[item] = None  # Files are marked as None or can store file details
        return structure

    directory_structure = dir_to_dict(path)
    return json.dumps(directory_structure, indent=4)