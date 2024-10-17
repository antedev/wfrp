import json
import os

def load_all_npcs():
    try:
        with open('npcs/npcs.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading npcs: {str(e)}", flush=True)
        return []

def load_tags():
    try:
        with open('data/tags.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading tags: {str(e)}", flush=True)
        return []

# Load shared JSON data
def load_talents():
    try:
        with open('data/talents.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading talents: {str(e)}", flush=True)
        return []

def load_traits():
    try:
        with open('data/creature_traits.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading traits: {str(e)}", flush=True)
        return []

def load_careers():
    try:
        with open('data/careers.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading careers: {str(e)}", flush=True)
        return []