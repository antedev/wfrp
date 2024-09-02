import json

# Load the JSON file for talents and careers
with open('talents.json', 'r') as json_file:
    talents = json.load(json_file)

with open('careers.json', 'r') as json_file:
    careers = json.load(json_file)

# Read both HTML templates
with open('template.html', 'r') as template_file:
    base_html_template = template_file.read()

with open('template_search.html', 'r') as search_template_file:
    search_html_template = search_template_file.read()

# Convert the JSON data into properly formatted strings for JavaScript
talents_json = json.dumps(talents, indent=4)
careers = json.dumps(careers['careers'], indent=4)

# Generate the base HTML file (for the careers dropdown view)
base_final_html = base_html_template.replace('{{json_data}}', talents_json).replace('{{careers}}', careers)

# Generate the search HTML file (for the search and autocomplete view)
search_final_html = search_html_template.replace('{{json_data}}', talents_json)

# Write the final HTML to new files
with open('talents_viewer.html', 'w') as output_base_file:
    output_base_file.write(base_final_html)

with open('talents_search.html', 'w') as output_search_file:
    output_search_file.write(search_final_html)

print("HTML files 'talents_viewer.html' and 'talents_search.html' have been generated.")
