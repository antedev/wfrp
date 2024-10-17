# tag_handler.py

import json
import uuid

def process_tags(npc_tags):
    """
    Process tags: map tag names to IDs, update tags.json and tag_id.json.
    """
    # Load tag IDs mapping from tag_id.json and tag names from tags.json
    with open('data/tag_id.json', 'r', encoding='utf-8') as f:
        tag_id_mapping = json.load(f)

    with open('data/tags.json', 'r', encoding='utf-8') as f:
        tags_json = json.load(f)

    tag_ids = []
    for tag_name in npc_tags:
        # If the tag doesn't exist in the mapping, create a new ID for it
        if tag_name not in tag_id_mapping:
            new_tag_id = str(uuid.uuid4())[:8]  # Generate a short UUID for the new tag
            tag_id_mapping[tag_name] = new_tag_id

        # If the tag doesn't exist in the tags.json list, add it there
        if tag_name not in tags_json:
            tags_json.append(tag_name)

        tag_ids.append(tag_id_mapping[tag_name])

    # Save the updated tag ID mapping back to tag_id.json
    with open('data/tag_id.json', 'w', encoding='utf-8') as f:
        json.dump(tag_id_mapping, f, indent=4)

    # Save the updated tag names back to tags.json
    with open('data/tags.json', 'w', encoding='utf-8') as f:
        json.dump(tags_json, f, ensure_ascii=False, indent=4)

    return tag_ids
