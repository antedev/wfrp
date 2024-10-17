from flask import Flask, make_response, render_template, jsonify, send_from_directory, request, redirect, url_for, session  # Added redirect and url_for
import os
import json
import uuid
import re
from utils.data_loader import load_all_npcs, load_tags, load_talents, load_traits, load_careers
from utils.matchers import find_talent_description, find_trait_description
from utils.tag_handler import process_tags 
from urllib.parse import unquote
from openai_image_generator import generate_image
import requests

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.secret_key = os.urandom(24)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1

talents_data = load_talents()
traits_data = load_traits()
careers_data = load_careers()

# Serve static images from npcs folder
@app.route('/npcs/<path:filename>')
def serve_npc_images(filename):
    return send_from_directory('npcs', filename)


@app.route('/', methods=['GET'])
def npc_list():
    npcs = load_all_npcs()
    tags = load_tags()
    npcs_sorted = sorted(npcs, key=lambda x: x['name'])

    # Render the response and disable caching
    response = make_response(render_template('npc_list.html', npcs=npcs_sorted, tags=tags))
    response.headers['Cache-Control'] = 'no-store'

    return response

@app.route('/gallery', methods=['GET'])
def npc_gallery():
    npcs = load_all_npcs()
    tags = load_tags()
    npcs_sorted = sorted(npcs, key=lambda x: x['name'])

    # Render the response and disable caching
    response = make_response(render_template('npc_gallery.html', npcs=npcs_sorted, tags=tags))
    response.headers['Cache-Control'] = 'no-store'

    return response

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        tags = load_tags()
        talents = load_talents()
        traits = load_traits()
        npcs = load_all_npcs()

        return jsonify({
            "tags": tags,
            "talents": talents,
            "traits": traits,
            "npcs": [{"name": npc['name'], "id": npc['id']} for npc in npcs]  # Simplify NPC data for mentions
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/npc/<npc_id>')
def npc_viewer(npc_id):
    try:
        # Load all NPCs
        npcs_data = load_all_npcs()

        # Find the specific NPC by its ID
        npc_data = next((npc for npc in npcs_data if npc['id'] == npc_id), None)
        print(f"NPC Data: {npc_data}")

        if not npc_data:
            return "NPC not found", 404

        # Find talents and traits descriptions
        npc_talents = [{'name': t, 'description': find_talent_description(t, talents_data)} for t in npc_data.get('talents', [])]
        npc_traits = [{'name': t, 'description': find_trait_description(t, traits_data)} for t in npc_data.get('traits', [])]

        # Find all NPCs who mention this NPC
        referred_by = [npc for npc in npcs_data if npc_id in npc.get('mentions', [])]

        # Render the NPC and the list of referrers
        return render_template('npc_viewer.html',
                               npc=npc_data,
                               npc_talents=npc_talents,
                               npc_traits=npc_traits,
                               referred_by=referred_by)  # Pass the list of NPCs who mention this one
    except Exception as e:
        print(f"Error loading NPC: {str(e)}", flush=True)
        return "NPC not found", 404

@app.route('/save_tag', methods=['POST'])
def save_tag():
    try:
        data = request.get_json()
        new_tag = data.get('tag')

        # Load existing tags
        with open('data/tags.json', 'r', encoding='utf-8') as f:
            tags = json.load(f)

        # Add the new tag if it's not already present
        if new_tag not in tags:
            tags.append(new_tag)

            # Save the updated tags list back to the file
            with open('data/tags.json', 'w', encoding='utf-8') as f:
                json.dump(tags, f, ensure_ascii=False, indent=4)

            return jsonify({"message": "Tag saved successfully"})
        else:
            return jsonify({"message": "Tag already exists"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/playground', methods=['GET'])
def playground():
    return render_template('playground.html')

@app.route('/npc/new', methods=['POST'])
def create_npc():
    try:
        # Get the new NPC data from the request
        new_npc = request.get_json()

        # Load the current NPC data from the JSON file
        with open('npcs/npcs.json', 'r', encoding='utf-8') as f:
            npc_data = json.load(f)

        # Append the new NPC
        npc_data.append(new_npc)

        # Save the updated NPC list back to the file
        with open('npcs/npcs.json', 'w', encoding='utf-8') as f:
            json.dump(npc_data, f, ensure_ascii=False, indent=4)

        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500



@app.route('/save_npc', methods=['POST'])
def save_npc():
    print("Save NPC route hit", flush=True)
    data = request.get_json()  # Get data from JSON request
    print("Received data:", data, flush=True)

    try:
        # Get the NPC data from the request
        npc_data = data.get('npcData')
        if not npc_data:
            return jsonify({"error": "Missing NPC data"}), 400

        # Load all NPCs from the central JSON file
        with open('npcs/npcs.json', 'r', encoding='utf-8') as f:
            all_npcs = json.load(f)

        # Process tags and get tag IDs
        npc_tags = npc_data.get('tags', [])
        npc_tag_ids = process_tags(npc_tags)

        # Update the NPC data: save tag names in the 'tags' field and tag IDs in a new 'tag_ids' field
        npc_data['tags'] = npc_tags  # Keep the tag names for the frontend
        npc_data['tag_ids'] = npc_tag_ids  # Add the corresponding tag IDs to the NPC data


        # Check if this is a new NPC or an existing one
        npc_id = npc_data.get('id')

        if npc_id:
            # Try to find and update the existing NPC by ID
            for idx, npc in enumerate(all_npcs):
                if npc['id'] == npc_id:
                    # Merge old NPC data with new data (preserving any missing fields)
                    updated_npc = {**npc, **npc_data}
                    all_npcs[idx] = updated_npc
                    print(f"Updated NPC with ID: {npc_id}", flush=True)
                    break
            else:
                # If NPC with the ID is not found, append it as new
                print(f"No existing NPC with ID: {npc_id} found. Appending as new NPC.", flush=True)
                all_npcs.append(npc_data)
        else:
            # No ID means it's a new NPC, so generate an ID and append it
            npc_id = str(uuid.uuid4())[:8]
            npc_data['id'] = npc_id
            all_npcs.append(npc_data)
            print(f"Appended new NPC with generated ID: {npc_id}", flush=True)

        # Save the updated NPC list back to the central JSON file
        with open('npcs/npcs.json', 'w', encoding='utf-8') as outfile:
            json.dump(all_npcs, outfile, ensure_ascii=False, indent=4)
            print("NPC data saved to file", flush=True)

        return jsonify({"message": "NPC saved successfully"})

    except Exception as e:
        print(f"Error in save_npc: {str(e)}", flush=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/api/tags', methods=['GET'])
def get_tags():
    try:
        # Load the tags from the tags.json file
        with open('data/tags.json', 'r', encoding='utf-8') as f:
            tags = json.load(f)
        return jsonify({"tags": tags})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/generate_image', methods=['POST'])
def generate_image_route():
    print("Route hit")
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        npc_name = data.get('npc_name')  # Make sure you pass the NPC name from the frontend
        npc_id = data.get('npc_id')

        print(f"here is som generation data {str(data)}")

        if not prompt or not npc_name:
            return jsonify({"error": "Prompt or NPC name not provided"}), 400

        # Call the generate_image function to generate and download the image
        image_filename = generate_image(prompt, npc_name)

        if image_filename:
            # Load the existing NPC data from JSON
            with open('npcs/npcs.json', 'r', encoding='utf-8') as f:
                npc_data = json.load(f)

            # Find the NPC by name (or ID if available)
            for npc in npc_data:
                if npc['id'] == npc_id:
                    npc['image'] = image_filename  # Update the NPC's image field
                    break
        
                # Save the updated NPC data back to the file
                with open('npcs/npcs.json', 'w', encoding='utf-8') as f:
                    json.dump(npc_data, f, ensure_ascii=False, indent=4)

                return jsonify({"imageUrl": image_filename}), 200
            else:
                return jsonify({"error": "NPC not found"}), 404
        else:
            return jsonify({"error": "Failed to generate image"}), 500

    except Exception as e:
        print(f"Error in generate_image_route: {str(e)}", flush=True)
        return jsonify({"error": "An unexpected error occurred"}), 500



if __name__ == '__main__':
    app.run(debug=True)