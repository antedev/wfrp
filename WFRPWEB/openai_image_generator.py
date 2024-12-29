import requests
import os
import json


URL = 'https://api.openai.com/v1/images/generations'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json',
}

def generate_image(prompt, npc_name):
    input_prompt = prompt + " A portrait in style of hand-drawn, painterly style that aligns with the Warhammer Fantasy Roleplay aesthetic, a bit like 1600-1700 Germany rich linework, muted earthy tones, dramatic lighting, and exaggerated features."

    data = {
        'prompt': input_prompt,
        'n': 1,
        'size': '1024x1024',
        'model': 'dall-e-3'
    }

    print(data['prompt'])

    try:
        # Send request to OpenAI API to generate the image
        response = requests.post(URL, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            image_url = response_data['data'][0]['url']

            # Download the image from the URL
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                # Create the filename based on the NPC name
                sanitized_name = npc_name.lower().replace(" ", "-")
                image_filename = f"{sanitized_name}.png"

                # Ensure the 'npcs/images/' directory exists
                image_dir = os.path.join("npcs", "images")
                os.makedirs(image_dir, exist_ok=True)

                # Save the image locally
                image_path = os.path.join(image_dir, image_filename)
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)

                print(f"Image saved as {image_path}")

                return image_filename  # Return the local filename instead of URL
            else:
                print(f"Failed to download the image: {image_response.status_code}", flush=True)
                return None
        else:
            print(f"Error: {response.status_code} - {response.text}", flush=True)
            return None
    except Exception as e:
        print(f"Error generating image: {str(e)}", flush=True)
        return None
