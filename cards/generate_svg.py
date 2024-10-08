import pandas as pd
from lxml import etree as ET
import os

# Load data from CSV with semicolon as delimiter
df = pd.read_csv('cards_data.csv', delimiter=';')

# Load the SVG template
tree = ET.parse('card_template.svg')
root = tree.getroot()

# Define the SVG namespace
ns = {'svg': 'http://www.w3.org/2000/svg'}
xlink_ns = "http://www.w3.org/1999/xlink"

# Function to split text with better breaks
def split_text(text, max_chars_per_line):
    if len(text) <= max_chars_per_line:
        return text, ''  # No need to split if it's short enough
    
    words = text.split()
    first_line = ''
    second_line = ''
    
    # Build the first line, prioritize breaking at spaces
    for word in words:
        if len(first_line) + len(word) + 1 <= max_chars_per_line:
            if first_line:
                first_line += ' ' + word
            else:
                first_line = word
        else:
            break
    
    # Remaining words go to the second line
    remaining_words = words[len(first_line.split()):]
    second_line = ' '.join(remaining_words)
    
    return first_line, second_line

for index, row in df.iterrows():
    # Determine the IDs for this card (1-indexed)
    image_id = f"card_image_{index + 1}"
    name_id = f"card_name_{index + 1}"

    # Ensure image_filename is not NaN or missing
    if pd.isna(row['image_filename']) or not isinstance(row['image_filename'], str):
        print(f"Warning: Missing or invalid image filename for {row.get('name', 'Unnamed Character')}")
        continue  # Skip this iteration if there's no valid image filename

    # Path to the original image
    original_image_path = os.path.join("images", row['image_filename'])

    # Check if the image file exists
    if not os.path.exists(original_image_path):
        print(f"Warning: Image file {original_image_path} not found!")
        continue  # Skip this iteration if the image is missing

    # Update the image
    image_element = root.find(f".//svg:rect[@id='{image_id}']", ns)
    if image_element is not None:
        # Get the x and y position from the original rectangle
        x = float(image_element.get('x'))
        y = float(image_element.get('y'))

        # Remove the existing rectangle
        parent = image_element.getparent()
        parent.remove(image_element)

        # Create the new image element
        new_image = ET.Element('{http://www.w3.org/2000/svg}image', {
            'id': image_id,
            '{http://www.w3.org/1999/xlink}href': original_image_path,
            'x': str(x),
            'y': str(y),
            'width': '60',  # Use just the numerical value
            'height': '60',  # Use just the numerical value
            'transform': f'rotate(-90, {x + 30}, {y + 30})',  # Rotate around the center
            'preserveAspectRatio': 'xMidYMid slice'  # Scale and crop to fit the 60x60 box
        })

        parent.append(new_image)  # Append normally

    # Handle missing names: don't add text if name is missing or empty
    if not pd.isna(row['name']) and isinstance(row['name'], str) and row['name'].strip():
        # Update the name inside the text element
        text_element = root.find(f".//svg:text[@id='{name_id}']", ns)
        if text_element is not None:
            # Clear existing content
            for tspan in text_element.findall('.//svg:tspan', ns):
                text_element.remove(tspan)

            # Handle manual line breaks in CSV or split automatically
            first_line, second_line = row['name'].split('\\', 1) if '\\' in row['name'] else split_text(row['name'], max_chars_per_line=30)

            # Insert the first line
            tspan1 = ET.SubElement(text_element, '{http://www.w3.org/2000/svg}tspan', {
                'x': text_element.get('x'),
                'dy': "0em"
            })
            tspan1.text = first_line

            # Insert the second line, if any
            if second_line:
                tspan2 = ET.SubElement(text_element, '{http://www.w3.org/2000/svg}tspan', {
                    'x': text_element.get('x'),
                    'dy': "1.2em"  # Adjust line spacing as needed
                })
                tspan2.text = second_line

# Save the updated SVG with proper XML formatting
output_filename = 'output_cards.svg'
tree.write(output_filename, xml_declaration=True, encoding='UTF-8', pretty_print=True)
print(f"Generated {output_filename}")
