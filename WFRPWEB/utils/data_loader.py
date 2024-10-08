import json
import os

def load_json_from_folders(root_folder):
    """Loads all JSON files from subdirectories of a root folder."""
    data = {}
    
    # Walk through the directory structure
    for folder_name, subdirs, files in os.walk(root_folder):
        folder_npcs = {}
        
        # For each file in the folder
        for file_name in files:
            if file_name.endswith('.json'):
                file_path = os.path.join(folder_name, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    npc_data = json.load(f)
                    folder_npcs[file_name.replace('.json', '')] = npc_data
        
        # If there are NPCs in this folder, add them under the folder's name
        if folder_npcs:
            folder_key = os.path.basename(folder_name)  # Use the folder name as a key
            data[folder_key] = folder_npcs
    
    return data

# Load NPCs from npcs folder
npcs_data = load_json_from_folders('npcs')

# Load shared JSON data
talents_data = json.load(open('data/talents.json', 'r', encoding='utf-8'))
traits_data = json.load(open('data/creature_traits.json', 'r', encoding='utf-8'))
careers_data = json.load(open('data/careers.json', 'r', encoding='utf-8'))
