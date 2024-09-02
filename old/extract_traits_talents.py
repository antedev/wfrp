import pytesseract
from PIL import Image
import re

# Configure Tesseract path (adjust this if necessary)
# For example: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# If already in PATH, you don't need this line
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

def extract_text_from_image(image_path):
    """Extract text from an image using OCR."""
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

def extract_traits_and_talents(text):
    """Extract 'Traits' and 'Talents' from the text."""
    traits = re.search(r'Traits:(.*?)(Talents|$)', text, re.DOTALL)
    talents = re.search(r'Talents:(.*?)(Trappings|$)', text, re.DOTALL)

    extracted_traits = traits.group(1).strip() if traits else "No Traits found"
    extracted_talents = talents.group(1).strip() if talents else "No Talents found"

    return extracted_traits, extracted_talents

def process_stat_block_image(image_path):
    """Process an image of a stat block and extract Traits and Talents."""
    text = extract_text_from_image(image_path)
    traits, talents = extract_traits_and_talents(text)
    
    return {
        "Traits": traits,
        "Talents": talents
    }

# Example usage with a screenshot of a stat block
image_path = "C:/Users/ante/Pictures/Screenshots/Screenshot 2024-08-16 224325.png"
result = process_stat_block_image(image_path)

# Output the extracted Traits and Talents
print("Traits:", result["Traits"])
print("Talents:", result["Talents"])
