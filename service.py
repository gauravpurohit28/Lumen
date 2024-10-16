import os
import json
import tempfile
from datetime import datetime
from uuid import uuid4
import cv2
import numpy as np
from picture import take_picture  # Assuming you have a local method to capture images
from text_to_speech import speak  # Assuming local text-to-speech functionality

# Local DB class using JSON for storage
class LocalDB:
    def __init__(self, db_path="local_data.json"):
        self.db_path = db_path
        self._ensure_db_file()

    def _ensure_db_file(self):
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as db_file:
                json.dump({}, db_file)

    def get_data(self, limit=100, descending=True):
        with open(self.db_path, 'r') as db_file:
            data = json.load(db_file)
        items = list(data.values())
        items.sort(key=lambda x: x['created_at'], reverse=descending)
        return items[:limit]

    def save_data(self, collection, data_id, data):
        with open(self.db_path, 'r') as db_file:
            current_data = json.load(db_file)
        current_data[data_id] = data
        with open(self.db_path, 'w') as db_file:
            json.dump(current_data, db_file)

# Initialize local database
db = LocalDB()

# Instruction system for the assistant
system_instruction = """
You are an AI assistant integrated into my smart glasses.
You see exactly what I see. Provide concise, real-time assistance based on my questions.
"""

def create_history_from_localdb(n=100):
    """Create history object from local JSON data."""
    items = db.get_data(limit=n)
    history = []
    for item in items:
        if (datetime.now() - datetime.fromisoformat(item["created_at"])).days < 2:
            history.append({"input": item["input_prompt"], "response": item["output_response"]})
    return history

# Simulate starting a chat based on local history
initial_history = create_history_from_localdb()

# def get_desktop_folder(folder_name):
    # """Get or create a folder on the desktop."""
    # desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    # folder_path = os.path.join(desktop_path, folder_name)
    # if not os.path.exists(folder_path):
    #     os.makedirs(folder_path)
    # return folder_path

def get_desktop_folder(folder_name):
    """Get or create a folder on the desktop."""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    folder_path = os.path.join(desktop_path, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def sanitize_input(input_text):
    """Sanitize user input for file naming."""
    return ''.join(e for e in input_text if e.isalnum() or e == ' ').replace(' ', '_')

def detect_color(image_path):
    """Detect the dominant color in an image."""
    image = cv2.imread(image_path)
    if image is None:
        return "Could not open image"
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = image.reshape((-1, 3))
    pixels = np.float32(pixels)
    _, labels, centers = cv2.kmeans(pixels, 1, None, 
                                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2), 
                                    10, cv2.KMEANS_RANDOM_CENTERS)
    
    dominant_color = centers[0].astype(int)
    return f"Dominant color: RGB{tuple(dominant_color)}"

def get_response(user_input):
    responses = {
        "what's the weather": "It's sunny!",
        "how are you": "I'm doing well, thank you!",
    }

    # Folder for saving images
    folder_name = "LumenImages"
    desktop_folder = get_desktop_folder(folder_name)
    sanitized_input = sanitize_input(user_input)
    filepath = os.path.join(desktop_folder, f'{sanitized_input}.jpg')
    
    # Take a picture and save locally
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        filepath = temp_file.name
        take_picture(filepath)
    
    print(f"Picture taken and saved as {filepath}")
    
    # Detect the dominant color in the image
    color_info = detect_color(filepath)
    print(f"Processing the image locally... {color_info}")

    # Return predefined response or color info
    return responses.get(user_input.lower(), f"{color_info}. Image saved at {filepath}.")

def save_query_to_localdb(prompt, response, image_url=None):
    data_id = uuid4().hex
    data = {
        "image_url": image_url,
        "created_at": datetime.now().isoformat(),
        "input_prompt": prompt,
        "output_response": response
    }
    db.save_data("data", data_id, data)
    print(f"Saved query to local DB: {data}")

if __name__ == "__main__":
    while True:
        user_input = input("Enter your question: ")
        response = get_response(user_input)
        print(response)
        save_query_to_localdb(user_input, response)
        print("\n")
