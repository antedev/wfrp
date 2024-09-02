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

for index, row in df.iterrows():
    # Determine the IDs for this card (1-indexed)
    image_id = f"card_image_{index + 1}"
    name_id = f"card_name_{index + 1}"

    # Path to the original image
    original_image_path = os.path.join("images", row['image_filename'])

    # Check if the image file exists
    if not os.path.exists(original_image_path):
        print(f"Warning: Image file {original_image_path} not found!")
        continue  # Skip this iteration if the image is missing

    # Update the name inside the text element
    text_element = root.find(f".//svg:text[@id='{name_id}']", ns)
    if text_element is not None:
        # Clear existing content
        for tspan in text_element.findall('.//svg:tspan', ns):
            text_element.remove(tspan)

        # Split the text into two lines
        max_chars_per_line = 20  # Adjust this based on your design
        first_line, second_line = row['name'].rsplit(maxsplit=1) if len(row['name'].split()) > 1 else (row['name'], '')

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

    # Update the image
    image_element = root.find(f".//svg:rect[@id='{image_id}']", ns)
    if image_element is not None:
        # Get the x and y position from the original rectangle
        x = float(image_element.get('x'))
        y = float(image_element.get('y'))

        # Remove the existing rectangle
        parent = image_element.getparent()
        parent.remove(image_element)

        # Insert the image element before the frames (i.e., before any other elements)
        # Assuming frames are the subsequent siblings of the image placeholder
        frame_elements = parent.xpath(f".//svg:*[@id='frame_{index + 1}']", namespaces=ns)
        frame_element = frame_elements[0] if frame_elements else None

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

        if frame_element is not None:
            parent.insert(parent.index(frame_element), new_image)  # Insert image before frame
        else:
            parent.append(new_image)  # If no frame is found, append normally

# Save the updated SVG with proper XML formatting
output_filename = 'output_cards.svg'
tree.write(output_filename, xml_declaration=True, encoding='UTF-8', pretty_print=True)
print(f"Generated {output_filename}")
