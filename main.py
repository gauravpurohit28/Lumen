import cv2
import numpy as np
import speech_recognition as sr
from transformers import pipeline
import pyttsx3

# YOLO Configuration files for object detection
YOLO_CONFIG_PATH = "yolo_files/yolov3-tiny.cfg"
YOLO_WEIGHTS_PATH = "yolo_files/yolov3-tiny.weights"
YOLO_COCO_NAMES_PATH = "yolo_files/coco.names"

# Initialize TTS engine
engine = pyttsx3.init()

# YOLO model for object detection
net = cv2.dnn_DetectionModel(YOLO_CONFIG_PATH, YOLO_WEIGHTS_PATH)
net.setInputSize(416, 416)
net.setInputScale(1.0 / 255)
net.setInputSwapRB(True)

with open(YOLO_COCO_NAMES_PATH, "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Color for bounding boxes
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

def detect_top_colors(image_path, top_n=3):
    """ Detects the top N dominant colors in the image """
    image = cv2.imread(image_path)
    if image is None:
        return "Could not open image"
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = image.reshape((-1, 3))
    pixels = np.float32(pixels)
    
    # KMeans clustering to find top N dominant colors
    _, labels, centers = cv2.kmeans(pixels, top_n, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2), 10, cv2.KMEANS_RANDOM_CENTERS)
    dominant_colors = [tuple(map(int, center)) for center in centers]
    
    return f"Top {top_n} dominant colors: {dominant_colors}"

def detect_objects(image_path):
    """ Detects objects in the image using YOLO """
    image = cv2.imread(image_path)
    if image is None:
        return "Could not open image", None
    
    # Detect objects using YOLO
    class_ids, confidences, boxes = net.detect(image, confThreshold=0.5, nmsThreshold=0.4)

    detected_objects = []
    for class_id, confidence, box in zip(class_ids.flatten(), confidences.flatten(), boxes):
        x, y, w, h = box
        label = str(classes[class_id])
        detected_objects.append(label)
        color = COLORS[class_id]
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    
    output_image_path = "detected_objects.jpg"
    cv2.imwrite(output_image_path, image)
    return detected_objects, output_image_path

# Load Hugging Face Transformers model
qa_pipeline = pipeline("question-answering")

def get_huggingface_response(question, context):
    """ Gets a response using Hugging Face Transformers """
    result = qa_pipeline(question=question, context=context)
    return result['answer']

def get_voice_input():
    """ Capture user input via microphone """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        user_input = recognizer.recognize_google(audio)
        print(f"User said: {user_input}")
        return user_input
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand what you said.")
        return ""
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service.")
        return ""

def speak(text):
    """ Convert text to speech """
    engine.say(text)
    engine.runAndWait()  # Wait until the speech is finished

def main():
    context = "You are currently in a room filled with books and a computer."  # Example context
    while True:
        print("Please speak your question or type 'exit' to quit:")
        user_input = get_voice_input()  # Capture user input via voice
        
        if user_input.lower() == "exit":
            break
        
        response = get_huggingface_response(user_input, context)
        print(f"Assistant: {response}")
        speak(response)  # Speak the response

if __name__ == "__main__":
    main()
