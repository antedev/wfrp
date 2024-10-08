import re

import re

def strip_specifics(text):
    """Strips parentheses, numbers, and trailing symbols like '+' for matching purposes."""
    text = text.strip()  # Ensure no leading/trailing spaces
    #print(f"Original text: '{text}'")  # Debug: Print the original text
    
    # Remove anything from the first parenthesis onwards (including the parentheses)
    stripped_text = re.sub(r'\(.*$', '', text)
    
    # If no parenthesis is found, remove trailing '+' and numbers (like "Weapon +5")
    stripped_text = re.sub(r'\s*\+.*$', '', stripped_text)
    
    # Also remove any trailing numbers (like "2" in "Etiquette 2")
    stripped_text = re.sub(r'\s*\d+$', '', stripped_text)
    
    stripped_text = stripped_text.strip()  # Final strip to remove extra spaces
   #print(f"Stripped text for matching: '{stripped_text}'")  # Debug: Print the stripped text
    return stripped_text


def find_talent_description(talent_name, talents_data):
    """Finds the description for a given talent from the talents JSON data."""
    stripped_talent = strip_specifics(talent_name)
    for talent in talents_data:
        json_talent_name = strip_specifics(talent['Name'])  # Strip spaces and parentheses from the JSON data too
        #print(f"Trying to match: '{stripped_talent}' with talent: '{json_talent_name}'")  # Debug: Print the matching process
        
        if stripped_talent == json_talent_name:
            #print(f"Match found for talent: '{talent['Name']}'")  # Debug: Successful match
            return talent['Description']
    
    #print(f"No match found for talent: '{stripped_talent}'")  # Debug: No match found
    return None

def find_trait_description(trait_name, traits_data):
    """Finds the description for a given trait from the traits JSON data."""
    stripped_trait = strip_specifics(trait_name)
    for trait in traits_data:
        json_trait_name = strip_specifics(trait['Name'])  # Strip spaces and parentheses from the JSON data too
        #print(f"Trying to match: '{stripped_trait}' with trait: '{json_trait_name}'")  # Debug: Print the matching process
        
        if stripped_trait == json_trait_name:
            #print(f"Match found for trait: '{trait['Name']}'")  # Debug: Successful match
            return trait['Description']
    
    #print(f"No match found for trait: '{stripped_trait}'")  # Debug: No match found
    return None

