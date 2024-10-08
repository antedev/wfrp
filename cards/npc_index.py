import os

# Assuming all images are in the current working directory or specify the directory
image_directory = "./images"
output_file = "npc_base_repository.md"

npc_entries = []

for filename in os.listdir(image_directory):
    if filename.endswith(".png"):
        # Extract name from filename, remove file extension
        name = filename.replace(".png", "")
        # Split by hyphens, capitalize each part
        formatted_name = " ".join([part.capitalize() for part in name.split("-")])
        # Handle special characters, ensuring correct Unicode formatting
        formatted_name = formatted_name.encode('utf-8').decode('utf-8')
        # Create markdown entry
        npc_entry = f"### {formatted_name}\n![{formatted_name}]({os.path.join(image_directory, filename)})\n"
        npc_entries.append(npc_entry)

# Write all entries to a markdown file
with open(output_file, "w", encoding='utf-8') as file:
    file.write("# NPC Base Repository\n\n")
    for entry in npc_entries:
        file.write(entry + "\n")

print(f"NPC repository created: {output_file}")