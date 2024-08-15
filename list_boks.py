import json
import re

def extract_unique_pdf_names(json_file):
    # Load the JSON data
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    pdf_set = set()  # Use a set to store unique PDF names
    
    # Loop through each entry in the JSON data
    for entry in data:
        for reference in entry["References"]:
            # Extract only the PDF file name (before the "#page=" part)
            pdf_name = re.match(r"([A-Za-z ]+\.pdf)#page=\d+", reference)
            if pdf_name:
                pdf_set.add(pdf_name.group(1))  # Add to the set (ensures uniqueness)
    
    return pdf_set

# Example usage:
json_file = "output.json"  # Path to the JSON file
unique_pdf_names = extract_unique_pdf_names(json_file)

# Print the list of unique PDF names
for pdf in sorted(unique_pdf_names):  # Sorted for easier readability
    print(pdf)
