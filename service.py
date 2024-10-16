import os
import tempfile
from datetime import datetime
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from picture import take_picture  # Assuming you have a method to capture images from the camera

# Create a folder to store images in the current directory
def get_image_folder(folder_name="CapturedImages"):
    """Create a folder for storing captured images in the current directory."""
    folder_path = os.path.join(os.getcwd(), folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

# Initialize the image captioning model from Hugging Face
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_image_description(image_path):
    """Generate a description for a given image."""
    image = Image.open(image_path)
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    description = processor.decode(out[0], skip_special_tokens=True)
    return description

def get_response(user_input):
    """Capture an image, generate a description, and return the response."""
    # Folder for saving images
    folder_name = "CapturedImages"
    image_folder = get_image_folder(folder_name)

    # Take a picture and save locally
    sanitized_input = ''.join(e for e in user_input if e.isalnum() or e == ' ').replace(' ', '_')
    filepath = os.path.join(image_folder, f'{sanitized_input}.jpg')
    
    # Simulating the take_picture functionality
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        filepath = temp_file.name
        take_picture(filepath)
    
    print(f"Picture taken and saved as {filepath}")
    
    # Generate a description of the image
    description = generate_image_description(filepath)
    print(f"Generated description: {description}")

    return f"Assistant: {description}. Image saved at {filepath}."

# Main loop to capture user input and respond with the image description
if __name__ == "__main__":
    while True:
        user_input = input("Enter your question: ")
        response = get_response(user_input)
        print(response)
        print("\n")
