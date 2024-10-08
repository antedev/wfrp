import pytesseract
from PIL import Image, ImageFilter, ImageOps
import json
import os
import re

# Path to the folder containing the images and the target folder for json output
image_folder = "./statblocks"
npcs_folder = "./npcs"

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

    return img

def extract_title_and_rank(text):
    """ Extract the character's name, title, and rank (status) """
    title_rank_match = re.search(r'([A-Z,\s-]+)\s\((GOLD|SILVER|BRASS|COLD)\s*(\d+)\)', text)
    print(title_rank_match)
    if title_rank_match:
        full_name = title_rank_match.group(1).strip()
        rank = f"{title_rank_match.group(2)} {title_rank_match.group(3)}"
        rank = rank.title()
        if ' - ' in full_name:
            name, title = full_name.split(' - ', 1)
            name = name.strip().title()
            title = title.strip().title()
        else:
            name = full_name.title()
            title = "Unknown"
        return name, title, rank
    else: # Try monster statblock
        print(text)
        monster_stat = re.search(r'(?:(\d+)\s+)?([A-Za-z\s-]+?)(?:\s+-\s+([A-Za-z\s-]+))?(?=\n|$)', text)

        print(monster_stat)
        if monster_stat.group(3):
            name = monster_stat.group(2).strip().title()
            creature_type = monster_stat.group(3).strip().title()
            return name, creature_type, ""
        else: 
            name = monster_stat.group(2).strip().title()
            return name, "", ""


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
    numbers = re.findall(r'\d+', text)
    numbers = [num for num in numbers if num != '1']

    if len(numbers) >= 12:
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
    # Debug: Print the full extracted text
    #print(f"Extracted Text from {image_path}:")
    #print(text)

    # Extract title and rank before cleaning the text
    name, title, rank = extract_title_and_rank(text)

    # Extract the text after the name and rank
    stat_block_start = text.find(rank) + len(rank)
    text_after_rank = text[stat_block_start:]

    # Clean the text after the title
    cleaned_text = clean_ocr_text(text_after_rank)
    
    # Debug: Print the cleaned text
    #print("Cleaned OCR Text:")
    #print(cleaned_text)

    # Extract the stats using the new function
    stats = extract_stats(cleaned_text)

    # Extract Skills, Talents, and Traits as lists
    skills_match = re.search(r'Skills:\s*(.+?)(?=Traits:|Talents:|Trappings:|$)', cleaned_text, re.DOTALL)
    skills = parse_list_section(skills_match.group(1)) if skills_match else []

     # Debug: Print Skills Match
    #print("Skills Found:")
    #print(skills)


    talents_match = re.search(r'Talents:\s*(.+?)(?=Traits:|Trappings:|$)', cleaned_text, re.DOTALL)
    talents = parse_list_section(talents_match.group(1)) if talents_match else []

    traits_match = re.search(r'Traits:\s*(.+?)(?=Trappings:|$)', cleaned_text, re.DOTALL)
    traits = parse_list_section(traits_match.group(1)) if traits_match else []

    # Extract Trappings if present
    trappings_match = re.search(r'Trappings:\s*(.+)', cleaned_text, re.DOTALL)
    trappings = trappings_match.group(1).strip() if trappings_match else None
    
    # Generate image filename from the name
    image_filename = re.sub(r'[^a-zA-Z0-9\s-]', '', name).lower().replace(' ', '-')

    # Return the structured data
    return {
        "name": name,
        "title": title,
        "rank": rank,
        "stats": stats,
        "skills": skills,
        "talents": talents,
        "traits": traits,
        "trappings": trappings,
        "image": f"{image_filename}.png"
    }

def save_json(data, folder, file_name):
    """ Save the extracted data to a JSON file in the appropriate folder """
    if not os.path.exists(folder):
        os.makedirs(folder)

    file_path = os.path.join(folder, file_name)
    
    if os.path.exists(file_path):
        print(f"File {file_name} already exists, skipping.")
        return

    with open(file_path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
        print(f"Saved {file_name}")

# Process each image in the folder and its subfolders
for root, dirs, files in os.walk(image_folder):
    for image_file in files:
        if image_file.endswith('.png') or image_file.endswith('.jpg'):
            image_path = os.path.join(root, image_file)
            
            # Parse the image and extract data
            character_data = parse_image(image_path)

            # Determine the relative path within the statblocks folder
            relative_path = os.path.relpath(root, image_folder)

            # Set the target folder in npcs to mirror the structure of statblocks
            folder_path = os.path.join(npcs_folder, relative_path)

            # Ensure the name of the JSON file is formatted correctly.
            json_file_name = re.sub(r'[\n\r]+', ' ', character_data['name'].lower()).replace(' ', '-').replace(',', '') + '.json'

            # Save the character data into npcs folder structure
            save_json(character_data, folder_path, json_file_name)
