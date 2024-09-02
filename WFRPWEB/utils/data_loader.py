import json

def load_json(file_path):
    """Loads a JSON file from the given file path."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Preload data to use throughout the application
npcs_data = load_json('data/npcs.json')
talents_data = load_json('data/talents.json')
traits_data = load_json('data/creature_traits.json')
