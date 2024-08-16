import json

# Load the JSON data
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Generate the HTML content
def generate_html(json_data):
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

    # Initialize to track when the heading level changes
    current_heading_1 = ""
    current_heading_2 = ""

    for entry in json_data:
        # If there's a new Heading Level 1 (e.g., "Characters"), print it
        if entry["Heading 1"] != current_heading_1:
            html_content += f'<h1>{entry["Heading 1"]}</h1>\n'
            current_heading_1 = entry["Heading 1"]

        # If there's a new Heading Level 2 (e.g., "Creation"), print it
        if entry["Heading 2"] != current_heading_2:
            html_content += f'<h2>{entry["Heading 2"]}</h2>\n'
            current_heading_2 = entry["Heading 2"]

        # Now list the items (e.g., Fighter, Begger)
        html_content += f'<ul>\n'
        html_content += f'<li>{entry["Item"]}<br>\n'

        # Add links to all PDF references for that item
        for reference in entry["References"]:
            pdf_file = reference.split("#")[0]
            html_content += f'<a href="{reference}" target="_blank">{pdf_file}</a>\n'

        html_content += '</li>\n'
        html_content += '</ul>\n'

    # Close the HTML content
    html_content += """
    </body>
    </html>
    """
    return html_content

# Write the HTML content to a file
def write_html_file(content, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(content)

# Main function to load JSON and generate HTML
def main():
    json_file = 'wfrp_rules_ref.json'  # Path to your JSON file
    output_file = 'index.html'         # Name of the HTML output file
    
    json_data = load_json(json_file)
    html_content = generate_html(json_data)
    write_html_file(html_content, output_file)
    print(f"HTML page generated: {output_file}")

if __name__ == "__main__":
    main()
