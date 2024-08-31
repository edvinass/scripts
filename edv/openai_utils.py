import json
from openai import OpenAI
import os
import json

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
    """Return json representation of the updated directory structure"""
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
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": message
            }
        ]
    )
    return completion.choices[0].message.content
    
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