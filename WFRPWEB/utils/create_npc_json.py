import csv
import json
import uuid

# Default structure for each NPC
default_npc = {
    "id": "",
    "name": "",
    "description": "",
    "summary": "", 
    "info": "", 
    "image": "unknown.png",
    "title": "",
    "rank": "",
    "trappings": "",
    "stats": {
        "M": 4,
        "WS": 30,
        "BS": 30,
        "S": 30,
        "T": 30,
        "I": 30,
        "Ag": 30,
        "Dex": 30,
        "Int": 30,
        "WP": 30,
        "Fel": 30,
        "W": 10
    },
    "skills": [],
    "talents": [],
    "traits": [],
    "tags": []
}

# Function to create NPCs from CSV and add UUIDs
def create_npcs_from_csv(csv_file):
    npcs = []
    
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Create a copy of the default NPC template
            npc = default_npc.copy()
            
            # Generate a unique ID for the NPC
            npc_id = str(uuid.uuid4())[:8]
            
            # Update the NPC with data from CSV
            npc['id'] = npc_id
            npc['name'] = row['name']
            npc['image'] = row['image']
            
            # Append the new NPC to the list
            npcs.append(npc)
    
    return npcs

# Save to one big JSON file
def save_to_json(npcs, output_file):
    with open(output_file, mode='w', encoding='utf-8') as file:
        json.dump(npcs, file, indent=4)

# Example usage:
csv_file = 'npc-set.csv'  # Replace with your CSV filename
output_file = 'npc_data.json'

npcs = create_npcs_from_csv(csv_file)
save_to_json(npcs, output_file)

print(f"NPC data has been saved to {output_file}")
