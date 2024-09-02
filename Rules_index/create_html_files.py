import os
import json

# Define your main and restricted folders
MAIN_FOLDER = 'pdfs/'
RESTRICTED_FOLDER = 'pdfs/restricted/'

# Get list of files in each folder
main_files = set(os.listdir(MAIN_FOLDER))
restricted_files = set(os.listdir(RESTRICTED_FOLDER))

# Function to load JSON data
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Function to generate HTML (with optional PDF filtering)
def generate_html(json_data, include_restricted=False):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WFRP Rules Reference</title>
        <style>
            body { font-family: Arial, sans-serif; }
            h1, h2 { color: #333; }
            ul { list-style-type: none; padding-left: 0; }
            li { margin-bottom: 10px; }
            a { margin-right: 10px; }
        </style>
    </head>
    <body>
        <h1>WFRP Rules Reference</h1>
    """

    current_heading_1 = ""
    current_heading_2 = ""

    for entry in json_data:
        if entry["Heading 1"] != current_heading_1:
            html_content += f'<h1>{entry["Heading 1"]}</h1>\n'
            current_heading_1 = entry["Heading 1"]

        if entry["Heading 2"] != current_heading_2:
            html_content += f'<h2>{entry["Heading 2"]}</h2>\n'
            current_heading_2 = entry["Heading 2"]

        valid_references = []

        # Process the references (PDF links)
        for reference in entry["References"]:
            pdf_file = reference.split("#")[0]

            # Check if the file is in the main folder or restricted folder
            if pdf_file in main_files:
                valid_references.append(f'./{MAIN_FOLDER}{pdf_file}#page={reference.split("#page=")[1]}')
            elif include_restricted and pdf_file in restricted_files:
                valid_references.append(f'./{RESTRICTED_FOLDER}{pdf_file}#page={reference.split("#page=")[1]}')

        # Only add items if there are valid references
        if valid_references:
            html_content += f'<ul><li>{entry["Item"]}: '
            for reference in valid_references:
                page_number = reference.split('#page=')[1]
                pdf_name = reference.split("#")[0].split('/')[-1].replace("_", " ").replace(".pdf", "")  # Clean up the PDF name
                html_content += f'<a href="{reference}" target="_blank">{pdf_name} page {page_number}</a> '
            html_content += '</li></ul>'

    html_content += "</body></html>"
    return html_content

# Write the HTML content to a file
def write_html_file(content, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(content)

# Main function to generate both public and GM versions
def main():
    json_file = 'wfrp_rules_ref.json'  # Path to your JSON file

    # Load the JSON data
    json_data = load_json(json_file)

    # Generate the public version (without restricted PDFs)
    public_html = generate_html(json_data, include_restricted=False)
    write_html_file(public_html, 'index.html')
    print("Public HTML (index.html) generated.")

    # Generate the GM version (with all PDFs)
    gm_html = generate_html(json_data, include_restricted=True)
    write_html_file(gm_html, 'gm.html')
    print("GM HTML (gm.html) generated.")

if __name__ == "__main__":
    main()
