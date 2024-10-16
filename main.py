
import os
import cv2
import numpy as np

def get_desktop_folder(folder_name):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    folder_path = os.path.join(desktop_path, folder_name)
    return folder_path

def sanitize_input(input_text):
    return ''.join(e for e in input_text if e.isalnum() or e == ' ').replace(' ', '_')

def detect_color(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return "Could not open image"
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = image.reshape((-1, 3))
    pixels = np.float32(pixels)
    _, labels, centers = cv2.kmeans(pixels, 1, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2), 10, cv2.KMEANS_RANDOM_CENTERS)
    dominant_color = centers[0].astype(int)
    
    return f"Dominant color: RGB{tuple(dominant_color)}"

def get_response(user_input):
    responses = {
        "what's the weather": "It's sunny!",
        "how are you": "I'm doing well, thank you!",
    }
    
    folder_name = "LumenImages"
    desktop_folder = get_desktop_folder(folder_name)
    sanitized_input = sanitize_input(user_input)
    filepath = os.path.join(desktop_folder, f'{sanitized_input}.jpg')
    blank_image = np.zeros((100, 100, 3), np.uint8)
    cv2.imwrite(filepath, blank_image)
    color_info = detect_color(filepath)
    
    return responses.get(user_input.lower(), f"{color_info}. Image saved at {filepath}.")

def main():
    while True:
        user_input = input("Enter your question: ")
        if user_input.lower() == "exit":
            break
        response = get_response(user_input)
        print(f"Assistant: {response}")

if __name__ == "__main__":
    main()
