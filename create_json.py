import re
import json

def parse_text_file(file_path):
    data = []
    current_heading_1 = ""
    current_heading_2 = ""
    
    # Open the file with the ISO-8859-1 encoding
    with open(file_path, 'r', encoding='ISO-8859-1') as file:
        lines = file.readlines()
    
    for line in lines:
        line = line.strip()

        # Detecting Level 1 and Level 2 headings based on '@' and '@@'
        if line.startswith("@@"):  # Level 2 heading
            current_heading_2 = line.lstrip("@@").strip()
        elif line.startswith("@"):  # Level 1 heading
            current_heading_1 = line.lstrip("@").strip()
        elif "%" in line:  # Bullet points with references
            # Split the item name from the references
            item_name, references = line.split("%", 1)
            item_name = item_name.strip()
            
            # Extracting and trimming PDF references
            reference_list = [ref.strip() for ref in re.findall(r"([A-Za-z ]+\.pdf#page=\d+)", references)]
            
            # Storing the structured data
            data.append({
                "Heading 1": current_heading_1,
                "Heading 2": current_heading_2,
                "Item": item_name,
                "References": reference_list
            })
    
    return data

# Example usage:
file_path = "wfrp_ref.txt"  # Path to the plain text file
parsed_data = parse_text_file(file_path)

# Convert parsed data to JSON
json_output = json.dumps(parsed_data, indent=4)

# Save to a JSON file
with open("output.json", "w", encoding="utf-8") as json_file:
    json_file.write(json_output)

print("Data has been successfully saved to output.json")
