import cv2
from time import sleep
from text_to_speech import speak
from PIL import Image

def take_picture(filepath: str):
    """Take a picture using the specified camera and save it to the provided file path."""
    speak("Alright, I'm taking a picture now.")
    print("Taking picture...")

    # Try opening the camera at index 0
    cap = cv2.VideoCapture(0)  
    sleep(2)  # Give time for camera to initialize
    
    if not cap.isOpened():
        print("Error: Camera failed to initialize.")
        speak("Sorry, I couldn't access the camera.")
        cap.release()
        return None

    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        speak("Sorry, I couldn't take a picture.")
        cap.release()
        return None

    cv2.imwrite(filepath, frame)
    print(f"Picture taken and saved as {filepath}")
    speak("Got it! I've taken the picture and saved it.")
    return f"Picture taken and saved as {filepath}"

def generate_image_description(image_path):
    """Generate a description of the image and return it as both text and audio."""
    try:
        image = Image.open(image_path)
        # Add your image processing or description logic here
        description = "You are wearing a blue shirt with black pants."
        
        # Print the description as written text
        print(f"Image description: {description}")
        
        # Speak the description as audio
        speak(description)
        
        return description
    except Exception as e:
        error_msg = "Could not identify the image."
        print(f"Error: {e}")
        speak(error_msg)
        return error_msg

# Main logic
if __name__ == "__main__":
    filepath = "/path/to/save/image.jpg"
    response = take_picture(filepath)
    
    if response:
        description = generate_image_description(filepath)
        # Both spoken and written response provided
