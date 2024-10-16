import os
import cv2
import numpy as np
from datetime import datetime
from uuid import uuid4

# Create a folder to store images if it doesn't exist
IMAGE_DIR = "images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def take_picture(save_path):
    """Simulate taking a picture and saving it."""
    # Simulate camera capture
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        raise RuntimeError("Could not open the camera.")
    
    ret, frame = camera.read()
    if ret:
        cv2.imwrite(save_path, frame)
    else:
        raise RuntimeError("Failed to capture image.")
    
    camera.release()
    print(f"Picture saved at: {save_path}")

def detect_color(image_path):
    """Detect the dominant color in the image."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image from path: {image_path}")

    # Convert image to RGB and reshape for clustering
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = image.reshape((-1, 3))
    pixels = np.float32(pixels)

    # KMeans clustering to find the dominant color
    _, labels, centers = cv2.kmeans(pixels, 1, None, 
                                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2), 
                                    10, cv2.KMEANS_RANDOM_CENTERS)

    dominant_color = centers[0].astype(int)
    return f"Dominant color: RGB{tuple(dominant_color)}"

def get_response(user_input):
    """Capture an image and detect its dominant color."""
    # Define a unique name for the image based on timestamp and UUID
    image_filename = f"{uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    image_path = os.path.join(IMAGE_DIR, image_filename)

    # Take a picture and save it to the images folder
    take_picture(image_path)

    # Detect the dominant color
    color_info = detect_color(image_path)
    return color_info

if __name__ == "__main__":
    while True:
        user_input = input("Enter your question: ")
        try:
            # Process user input and capture image
            response = get_response(user_input)
            print(response)
        except Exception as e:
            print(f"Error: {e}")
        print("\n")
