import os
import json

# Define your main and restricted folders
MAIN_FOLDER = './'
RESTRICTED_FOLDER = './GM-stuff/'

# Get list of files in each folder
main_files = set(os.listdir(MAIN_FOLDER))
restricted_files = set(os.listdir(RESTRICTED_FOLDER))

# Function to load JSON data
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Function to sort the main JSON data by Heading 1 and Heading 2
def sort_main_json_data(json_data):
    return sorted(json_data, key=lambda x: (x['Heading 1'], x['Heading 2']))

# Function to sort the core JSON data by Page Number and then by Heading 1
def sort_core_json_data(json_data):
    def extract_page_number(reference):
        try:
            return int(reference[0].split('page=')[1])
        except IndexError:
            return 0
    
    return sorted(json_data, key=lambda x: (extract_page_number(x['References']), x['Heading 1']))

# Function to generate collapsible HTML sections
def generate_html(json_data, include_restricted=False):
    html_content = ""

    current_heading_1 = ""
    current_heading_2 = ""

    for entry in json_data:
        # Add Heading 1 if it's new
        if entry["Heading 1"] != current_heading_1:
            if current_heading_1 != "":
                html_content += '</ul>\n'  # Close the previous list
            html_content += f'<h2 class="collapsible">{entry["Heading 1"]}</h2>\n'
            html_content += '<ul class="content">\n'  # Start a new collapsible list
            current_heading_1 = entry["Heading 1"]

        # Add Heading 2 if it's new
        if entry["Heading 2"] != current_heading_2:
            html_content += f'<h3>{entry["Heading 2"]}</h3>\n'
            current_heading_2 = entry["Heading 2"]

        valid_references = []

        # Process the references (PDF links)
        for reference in entry["References"]:
            pdf_file = reference.split("#")[0]

            # Adjust paths based on whether we're generating gm.html or index.html
            if pdf_file in main_files:
                if include_restricted:  # For gm.html (in GM-stuff/ folder)
                    valid_references.append(f'../{pdf_file}#page={reference.split("#page=")[1]}')
                else:  # For index.html (in root folder)
                    valid_references.append(f'./{pdf_file}#page={reference.split("#page=")[1]}')

            # For restricted files (always local to GM-stuff/)
            elif include_restricted and pdf_file in restricted_files:
                # No need to append the folder name, as gm.html is already inside GM-stuff/
                valid_references.append(f'./{pdf_file}#page={reference.split("#page=")[1]}')


        # Only add items if there are valid references
        if valid_references:
            html_content += f'<li>{entry["Item"]}: '
            for reference in valid_references:
                page_number = reference.split('#page=')[1]
                pdf_name = reference.split("#")[0].split('/')[-1].replace("_", " ").replace(".pdf", "")  # Clean up the PDF name
                html_content += f'<a href="{reference}" target="_blank">{pdf_name} page {page_number}</a> '
            html_content += '</li>\n'

    html_content += "</ul>\n"  # Close the last list
    return html_content


# Function to add basic tabs and collapsible sections to the HTML page
def generate_html_with_tabs(core_html, main_html, gm_html):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WFRP Rules Reference</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.4;
                background-color: #f8f8f8;
                color: #333;
                padding: 20px;
            }

            h1 {
                color: #444;
                border-bottom: 2px solid #ccc;
                padding-bottom: 10px;
            }

            h2 {
                margin-top: 20px;
                color: #666;
                cursor: pointer;
                background-color: #ddd;
                padding: 10px;
                border-radius: 5px;
            }

            h2:hover {
                background-color: #ccc;
            }

            ul {
                margin-left: 20px;
                display: none; /* Initially hide all content */
            }

            ul li {
                margin-bottom: 5px; /* Reduce space between bullet points */
            }

            h3 {
                margin: 10px 0 5px 0; /* Tighten space above/below headings */
                color: #444;
            }

            a {
                color: #007bff;
                text-decoration: none;
            }

            a:hover {
                text-decoration: underline;
            }

            .tab-button {
                margin-right: 10px;
                cursor: pointer;
                padding: 8px 12px;
                background-color: #e0e0e0;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }

            .tab-button.active {
                background-color: #007bff;
                color: white;
            }

            .tab {
                display: none;
            }

            .tab.active {
                display: block;
            }
        </style>
        <script>
            // Function to switch between tabs
            function switchTab(tabId) {
                var tabs = document.getElementsByClassName('tab');
                var buttons = document.getElementsByClassName('tab-button');
                for (var i = 0; i < tabs.length; i++) {
                    tabs[i].classList.remove('active');
                    buttons[i].classList.remove('active');
                }
                document.getElementById(tabId).classList.add('active');
                document.getElementById(tabId + '-btn').classList.add('active');
            }

            // Function to toggle visibility of sections
            function toggleSection(event) {
                var content = event.target.nextElementSibling;
                if (content.style.display === "block") {
                    content.style.display = "none";
                } else {
                    content.style.display = "block";
                }
            }

            window.onload = function() {
                // Auto-activate Core Rules tab
                switchTab('core-tab');

                // Attach event listeners to all collapsible headings
                var collapsibles = document.getElementsByClassName('collapsible');
                for (var i = 0; i < collapsibles.length; i++) {
                    collapsibles[i].addEventListener('click', toggleSection);
                }
            }
        </script>
    </head>
    <body>

        <h1>WFRP Rules Reference</h1>

        <!-- Tab buttons -->
        <button id="core-tab-btn" class="tab-button active" onclick="switchTab('core-tab')">Core Rules</button>
        <button id="main-tab-btn" class="tab-button" onclick="switchTab('main-tab')">Main Rules</button>
        <button id="gm-tab-btn" class="tab-button" onclick="switchTab('gm-tab')">GM Rules</button>

        <!-- Core Rules Tab Content -->
        <div id="core-tab" class="tab active">
    """ + core_html + """
        </div>

        <!-- Main Rules Tab Content -->
        <div id="main-tab" class="tab">
    """ + main_html + """
        </div>

        <!-- GM Rules Tab Content -->
        <div id="gm-tab" class="tab">
    """ + gm_html + """
        </div>

    </body>
    </html>
    """
    return html_content

# Write the HTML content to a file
def write_html_file(content, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(content)

# Main function to generate all versions
def main():
    json_file = 'wfrp_rules_ref.json'  # Path to your main JSON file
    core_json_file = 'wfrp_core_rules_ref.json'  # Path to your core rules JSON file

    # Load and sort the JSON data
    json_data = sort_main_json_data(load_json(json_file))
    core_json_data = sort_core_json_data(load_json(core_json_file))

    # Generate the HTML for the core, main, and GM rules
    public_core_html = generate_html(core_json_data, include_restricted=False)
    public_main_html = generate_html(json_data, include_restricted=False)
    gm_core_html = generate_html(core_json_data, include_restricted=True)
    gm_main_html = generate_html(json_data, include_restricted=True)

    # Create the full HTML with tabs and collapsible sections
    public_html = generate_html_with_tabs(public_core_html, public_main_html, gm_core_html)
    gm_html = generate_html_with_tabs(gm_core_html, gm_main_html, gm_main_html)  # GM version includes everything

    # Write the HTML files
    write_html_file(public_html, 'index.html')
    print("Public HTML (index.html) generated.")

    write_html_file(gm_html, 'GM-stuff/gm.html')
    print("GM HTML (gm.html) generated.")

if __name__ == "__main__":
    main()

