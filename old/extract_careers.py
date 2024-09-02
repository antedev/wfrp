import json

# Load the JSON file
with open('talents.json', 'r') as json_file:
    talents = json.load(json_file)

# Set to store unique names
unique_names = set()

# Iterate over each talent and extract the names in the "Who" clause
for talent in talents:
    for who in talent.get("Who", []):
        unique_names.add(who["name"])

# Print all unique names
print("Unique 'Who' names:")
for name in sorted(unique_names):
    print(name)
