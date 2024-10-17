import openai
import json
import os

# Load your API key from an environment variable or a configuration file
api_key = "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"
if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key

# Define the path to your JSON file
NPC_JSON_PATH = 'npcs/npcs.json'

def generate_npc(name, traits):
    """
    Generate an NPC with the given name and traits.
    
    Parameters:
    - name (str): The name of the NPC.
    - traits (str): A short description or traits of the NPC (e.g., 'grumpy merchant with a scar').
    
    Returns:
    - dict: A dictionary with the generated NPC details.
    """
    prompt = f"Create a detailed description of a character named {name}. This character is {traits}. Include personality, background, and notable features."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.7
        )
        
        npc_description = response.choices[0].message['content'].strip()
        npc = {
            "name": name,
            "traits": traits,
            "description": npc_description,
            "image": "placeholder.png"  # Placeholder for image generation, to be updated later.
        }
        
        save_npc_to_json(npc)
        return npc
    except openai.OpenAIError as e:
        print(f"Error generating NPC: {e}")
        return None

def save_npc_to_json(npc):
    """
    Save the generated NPC to the JSON file.
    
    Parameters:
    - npc (dict): The NPC data to save.
    """
    try:
        if not os.path.exists(NPC_JSON_PATH):
            with open(NPC_JSON_PATH, 'w') as json_file:
                json.dump({}, json_file)

        with open(NPC_JSON_PATH, 'r') as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                data = {}

        data[npc['name'].upper()] = npc

        with open(NPC_JSON_PATH, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    except IOError as e:
        print(f"Error saving NPC to JSON: {e}")

if __name__ == "__main__":
    # Example usage
    npc_name = "Hans Gruber"
    npc_traits = "An old fence in Ubersreik"
    generated_npc = generate_npc(npc_name, npc_traits)
    if generated_npc:
        print(json.dumps(generated_npc, indent=4))