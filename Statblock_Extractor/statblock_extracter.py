import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import json
import os
import re

# Path to the folder containing the images
image_folder = "./statblocks"
output_json = {}

def preprocess_image(img_path):
    """ Function to preprocess the image to improve OCR accuracy """
    img = Image.open(img_path)

    # Convert to grayscale
    img = img.convert('L')

    # Apply adaptive thresholding to binarize the image
    img = ImageOps.autocontrast(img)  # Enhance contrast
    img = ImageOps.invert(img)  # Invert colors (make background white)

    # Apply sharpening and blur filters to reduce noise
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.MedianFilter(size=3))  # Median blur to remove noise

    # Optional: Deskew the image (if OCR consistently misaligns rows)
    img = img.rotate(-0.5, expand=True)  # Adjust this angle based on the image

    return img

def extract_title_and_rank(text):
    """ Extract the character's name, title, and rank (status) """
    title_rank_match = re.search(r'([A-Z,\s-]+)\s\((GOLD|SILVER|BRASS|COLD)\s*(\d+)\)', text)
    if title_rank_match:
        full_name = title_rank_match.group(1).strip()
        rank = f"{title_rank_match.group(2)} {title_rank_match.group(3)}"
        if ' - ' in full_name:
            name, title = full_name.split(' - ', 1)
            name = name.strip()
            title = title.strip()
        else:
            name = full_name
            title = "Unknown"
        return name, title, rank
    return "Unknown", "Unknown", "Unknown"

def clean_ocr_text(text):
    """ Clean the OCR text after the title and rank have been extracted """
    text = text.replace('|', ' ')  # Replace vertical pipes with spaces
    text = text.replace('[', '')  # Remove square brackets
    text = text.replace(']', '')  # Remove square brackets
    text = text.replace('!', 'I')  # Replace misrecognized exclamation points as 'I'
    text = text.replace('´', "'")  # Replace accent with standard apostrophe
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space

    return text

def parse_list_section(text_section):
    """ Function to split the section into a list based on commas """
    if text_section:
        return [item.strip() for item in text_section.split(',')]
    return []

def extract_stats(text):
    """ Function to extract stats by finding the first valid sequence of 12 numbers """
    # Use regex to extract all sequences of numbers
    numbers = re.findall(r'\d+', text)

    # Filter out the first '1' or misrecognized 'I', if it's an extra number
    numbers = [num for num in numbers if num != '1']

    # Correct for misplaced stats, especially movement (M)
    if len(numbers) >= 12:
        # Movement (M) should be a single-digit number; check if the first number is out of place
        if int(numbers[0]) > 9 and len(numbers) > 12:
            # Move the first single-digit number (likely M) to the correct position
            m_stat = next((num for num in numbers if int(num) < 10), None)
            if m_stat:
                numbers.remove(m_stat)
                numbers = [m_stat] + numbers[:11]
        else:
            numbers = numbers[:12]  # Take the first 12 valid numbers

        # Map the numbers to the corresponding stat labels
        return {
            "M": int(numbers[0]),
            "WS": int(numbers[1]),
            "BS": int(numbers[2]),
            "S": int(numbers[3]),
            "T": int(numbers[4]),
            "I": int(numbers[5]),
            "Ag": int(numbers[6]),
            "Dex": int(numbers[7]),
            "Int": int(numbers[8]),
            "WP": int(numbers[9]),
            "Fel": int(numbers[10]),
            "W": int(numbers[11])
        }
    return {}

def parse_image(image_path):
    # Preprocess the image before OCR
    img = preprocess_image(image_path)

    # Perform OCR on the image
    text = pytesseract.image_to_string(img, config='--psm 6')  # Set OCR to treat the text as a block (PSM 6)

    # Extract title and rank before cleaning the text
    name, title, rank = extract_title_and_rank(text)

    # Extract the text after the name and rank
    stat_block_start = text.find(rank) + len(rank)
    text_after_rank = text[stat_block_start:]

    # Clean the text after the title
    cleaned_text = clean_ocr_text(text_after_rank)

    # Extract the stats using the new function
    stats = extract_stats(cleaned_text)

    # Extract Skills, Talents, and Traits as lists
    skills_match = re.search(r'Skills:\s*(.+?)(?=Traits:|Talents:|Trappings:|$)', cleaned_text, re.DOTALL)
    skills = parse_list_section(skills_match.group(1)) if skills_match else []

    talents_match = re.search(r'Talents:\s*(.+?)(?=Traits:|Trappings:|$)', cleaned_text, re.DOTALL)
    talents = parse_list_section(talents_match.group(1)) if talents_match else []

    traits_match = re.search(r'Traits:\s*(.+?)(?=Trappings:|$)', cleaned_text, re.DOTALL)
    traits = parse_list_section(traits_match.group(1)) if traits_match else []

    # Extract Trappings if present
    trappings_match = re.search(r'Trappings:\s*(.+)', cleaned_text, re.DOTALL)
    trappings = trappings_match.group(1).strip() if trappings_match else None
    
    # Return the structured data
    return {
        "name": name,
        "title": title,
        "rank": rank,
        "stats": stats,
        "skills": skills,
        "talents": talents,
        "traits": traits,
        "trappings": trappings
    }

# Process each image in the folder
for image_file in os.listdir(image_folder):
    if image_file.endswith('.png') or image_file.endswith('.jpg'):
        image_path = os.path.join(image_folder, image_file)
        
        # Parse the image and extract data
        character_data = parse_image(image_path)
        
        # Add the character data to the output JSON
        output_json[character_data['name']] = character_data

# Save the output as a JSON file with proper encoding handling
with open('character_data.json', 'w', encoding='utf-8') as outfile:
    json.dump(output_json, outfile, ensure_ascii=False, indent=4)

print("JSON file created successfully!")
