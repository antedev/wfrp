from flask import Flask, render_template, jsonify, send_from_directory, request  # Added request import
import os  # Added os import
import json  # Added json import
from utils.data_loader import npcs_data, talents_data, traits_data, load_json_from_folders
from utils.matchers import find_talent_description, find_trait_description
from urllib.parse import unquote
from flask import session  # Import session

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.secret_key = os.urandom(24) 

# Serve static images from npcs folder
@app.route('/npcs/<path:filename>')
def serve_npc_images(filename):
    return send_from_directory('npcs', filename)

@app.route('/')
def npc_list_viewer():
    return render_template('npc_list.html', npcs=npcs_data)


@app.route('/npc/<folder>/<npc_name>')
def npc_viewer(folder, npc_name):
    # Reload the latest NPC data from the JSON files
    npcs_data = load_json_from_folders('npcs')  # Load fresh data

    npc_data = npcs_data.get(folder, {}).get(npc_name)

    if not npc_data:
        return "NPC not found", 404

    # The path of the JSON file for this NPC
    file_path = f'npcs/{folder}/{npc_name}.json'

    # Store the file path in the session (or another persistent method)
    session['current_file_path'] = file_path

    npc_talents = [{'name': t, 'description': find_talent_description(t, talents_data)} for t in npc_data.get('talents', [])]
    npc_traits = [{'name': t, 'description': find_trait_description(t, traits_data)} for t in npc_data.get('traits', [])]

    return render_template('npc_viewer.html', 
                           npc=npc_data, 
                           npc_talents=npc_talents, 
                           npc_traits=npc_traits,
                           folder=folder)


@app.route('/save_npc', methods=['POST'])
def save_npc():
    print("Save NPC route hit", flush=True)
    data = request.get_json()
    print("Received data:", data, flush=True)

    try:
        # Get the updated NPC data from the request
        updated_npc_data = data.get('npcData')

        if not updated_npc_data:
            return jsonify({"error": "Missing NPC data"}), 400

        # Get the file path from the session
        file_path = session.get('current_file_path')
        print(f"Saving to file path: {file_path}", flush=True)

        if not file_path:
            return jsonify({"error": "File path is not set"}), 500

        # Save the updated NPC data to the JSON file
        with open(file_path, 'w', encoding='utf-8') as outfile:
            json.dump(updated_npc_data, outfile, ensure_ascii=False, indent=4)

        return jsonify({"message": "NPC saved successfully"})

    except Exception as e:
        print(f"Error in save_npc: {str(e)}", flush=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500







if __name__ == '__main__':
    app.run(debug=True)
