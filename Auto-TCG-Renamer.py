# Display starting message
print("Script is starting up...")

import os
import cv2
import easyocr
import requests
import logging
import re
import unicodedata
import shutil
import base64
import json
import sys
from pathlib import Path

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Set up logging
log_file_path = os.path.join('log.txt')

# Configure logging to output to both console and log file
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create handlers
file_handler = logging.FileHandler(log_file_path)
console_handler = logging.StreamHandler()

# Set level for handlers
file_handler.setLevel(logging.INFO)
console_handler.setLevel(logging.WARNING)

# Create formatters and add them to handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def sanitize_filename(name):
    name = name.replace('&', 'and')
    nfkd_form = unicodedata.normalize('NFD', name)
    sanitized_name = ''.join([c for c in nfkd_form if not unicodedata.combining(c)])
    sanitized_name = re.sub(r'[^a-zA-Z0-9 \-\.]', '', sanitized_name)
    return sanitized_name

def preprocess_file_names(directory):
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ['Processed', 'Error']]
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                original_path = os.path.join(root, file)
                directory = os.path.dirname(original_path)
                file_extension = os.path.splitext(original_path)[1]
                sanitized_name = sanitize_filename(os.path.splitext(file)[0])
                new_file_name = f"{sanitized_name}{file_extension}"
                new_file_path = os.path.join(directory, new_file_name)
                
                counter = 1
                while os.path.exists(new_file_path):
                    new_file_name = f"{sanitized_name}_{counter}{file_extension}"
                    new_file_path = os.path.join(directory, new_file_name)
                    counter += 1
                
                if original_path != new_file_path:
                    os.rename(original_path, new_file_path)
                    logging.info(f"Preprocessed {original_path} to {new_file_path}")

def get_card_name(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        result = reader.readtext(image, detail=0)
        
        card_text = result[0] if result else ''
        
        logging.debug(f"Extracted text from {image_path}: {card_text}")
        
        response = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={card_text}')
        
        if response.status_code == 200:
            card_data = response.json()
            card_name = card_data['name']
            logging.info(f"Identified card '{card_name}' for image {image_path}")
            return card_name
        else:
            logging.warning(f"Card not found for text: {card_text} in image {image_path}")
            return None
    except Exception as e:
        logging.error(f"Error processing image {image_path}: {e}")
        return None

def rename_card_image(image_path, card_name):
    try:
        sanitized_card_name = sanitize_filename(card_name)
        
        directory = os.path.dirname(image_path)
        file_extension = os.path.splitext(image_path)[1]
        
        new_file_name = f"{sanitized_card_name}{file_extension}"
        new_file_path = os.path.join(directory, new_file_name)
        
        counter = 1
        while os.path.exists(new_file_path):
            new_file_name = f"{sanitized_card_name}_{counter}{file_extension}"
            new_file_path = os.path.join(directory, new_file_name)
            counter += 1
        
        os.rename(image_path, new_file_path)
        logging.info(f"Renamed {image_path} to {new_file_path}")
        
        return new_file_path
    except Exception as e:
        logging.error(f"Error renaming image {image_path} to {new_file_name}: {e}")
        return None

def move_file(file_path, destination_folder):
    try:
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        
        destination_path = os.path.join(destination_folder, os.path.basename(file_path))
        
        counter = 1
        while os.path.exists(destination_path):
            base, ext = os.path.splitext(os.path.basename(file_path))
            destination_path = os.path.join(destination_folder, f"{base}_{counter}{ext}")
            counter += 1
        
        shutil.move(file_path, destination_path)
        logging.info(f"Moved {file_path} to {destination_path}")
    except Exception as e:
        logging.error(f"Error moving file {file_path} to {destination_folder}: {e}")

def process_magic_directory(directory):
    no_new_files = True
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ['Processed', 'Error']]
        
        if root == directory:
            continue
        print(f"Now processing {root}")
        logging.info(f"Now processing {root}")
        processed_folder = os.path.join(root, 'Processed')
        error_folder = os.path.join(root, 'Error')
        
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                no_new_files = False
                try:
                    image_path = os.path.join(root, file)
                    logging.debug(f"Processing {image_path}")
                    
                    card_name = get_card_name(image_path)
                    
                    if card_name:
                        new_file_path = rename_card_image(image_path, card_name)
                        if new_file_path:
                            move_file(new_file_path, processed_folder)
                        else:
                            move_file(image_path, error_folder)
                    else:
                        move_file(image_path, error_folder)
                except Exception as e:
                    logging.error(f"Error processing file {file}: {e}")
                    print("Error: Please check Log.txt for details")
                    move_file(os.path.join(root, file), error_folder)
        print("Complete!")
    return no_new_files

def read_api_key(config_file):
    if not os.path.exists(config_file):
        logging.error(f"Configuration file '{config_file}' not found. Exiting...")
        input("Press Enter to exit...")
        sys.exit(1)
    
    with open(config_file, 'r') as file:
        for line in file:
            if line.startswith('api_key'):
                return line.split('=')[1].strip()
    
    logging.error(f"API key not found in '{config_file}'. Exiting...")
    input("Press Enter to exit...")
    sys.exit(1)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_pokemon_image(image_path, api_key, root):
    base64_image = encode_image(image_path)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a Pokemon trading card game expert that responds in JSON."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please identify this card. Only return the name of the card, and the series its from."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    log_message = "Submitting picture for review..."
    print(log_message)
    logging.info(log_message)
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        response_data = response.json()
        
        try:
            content = response_data['choices'][0]['message']['content']
            card_data = json.loads(content.strip('```json').strip('```'))
            card_name = card_data.get('name', '')
            series = card_data.get('series', '')

            if card_name and series:
                sanitized_name = sanitize_filename(f"{card_name} - {series}.jpg")
                directory, original_file_name = os.path.split(image_path)
                new_image_path = os.path.join(directory, sanitized_name)
                os.rename(image_path, new_image_path)
                rename_message = f"Renamed '{original_file_name}' to '{os.path.basename(new_image_path)}'"
                print(rename_message)
                logging.info(rename_message)
                move_file(new_image_path, os.path.join(root, 'Processed'))
            else:
                error_message = "Failed to parse the response."
                print(error_message)
                logging.error(error_message)
                move_file(image_path, os.path.join(root, 'Error'))
        except KeyError:
            error_message = f"Unexpected response format: {response_data}"
            print(error_message)
            logging.error(error_message)
            move_file(image_path, os.path.join(root, 'Error'))
        except json.JSONDecodeError:
            error_message = "Failed to decode the JSON response."
            print(error_message)
            logging.error(error_message)
            move_file(image_path, os.path.join(root, 'Error'))
    else:
        error_message = f"Request failed with status code {response.status_code}"
        print(error_message)
        logging.error(error_message)
        move_file(image_path, os.path.join(root, 'Error'))

def process_pokemon_directory(directory, api_key):
    no_new_files = True
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ['Processed', 'Error']]
        
        if root == directory:
            continue
        print(f"Now processing {root}")
        logging.info(f"Now processing {root}")
        
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                no_new_files = False
                try:
                    image_path = os.path.join(root, file)
                    logging.debug(f"Processing {image_path}")
                    
                    process_pokemon_image(image_path, api_key, root)
                except Exception as e:
                    logging.error(f"Error processing file {file}: {e}")
                    print("Error: Please check Log.txt for details")
                    move_file(image_path, os.path.join(root, 'Error'))
        print("Complete!")
    return no_new_files

def main():
    logging.info("Script is starting up...")
    
    pokemon_folder = "Pokemon"
    magic_folder = "Magic"
    
    config_file = "tcg.cfg"
    api_key = read_api_key(config_file)
    
    no_new_files = True

    if os.path.exists(pokemon_folder):
        logging.info("Pokemon folder detected. Running OpenAI submission script.")
        preprocess_file_names(pokemon_folder)
        no_new_files = process_pokemon_directory(pokemon_folder, api_key) and no_new_files
    
    if os.path.exists(magic_folder):
        logging.info("Magic folder detected. Running EasyOCR script.")
        preprocess_file_names(magic_folder)
        no_new_files = process_magic_directory(magic_folder) and no_new_files
    
    if no_new_files:
        print("No new files detected.")
        logging.info("No new files detected.")
    
    if not os.path.exists(pokemon_folder) and not os.path.exists(magic_folder):
        logging.error("No folder detected. Please create 'Pokemon' or 'Magic' folder.")
        print("No folder detected. Please create 'Pokemon' or 'Magic' folder.")
    
    logging.info("Processing complete. Exiting gracefully.")
    print("Processing complete. Press Enter to exit.")
    input()

if __name__ == "__main__":
    main()
