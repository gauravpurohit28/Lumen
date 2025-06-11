# Lumen: Accessible Visual Q&A for the Blind

Lumen is an accessibility-focused system designed for blind and visually impaired users. It captures images, describes them, and allows users to ask questions about the image using their voice. All interactions are accessible via audio, making the system easy to use with minimal prompts.

---

## Features
- Real-time image capture and description
- Voice-based Q&A about the captured image
- Audio output for both descriptions and answers
- Simple, accessible prompts for blind users
- "New Image" button to recapture and restart the flow
- All interactions logged to Firebase (images and Q&A)
- Web-based frontend for easy interaction

---

## Hardware Requirements
- Raspberry Pi (model 4 or newer) **or** any computer
- Webcam (Logitech recommended)
- USB microphone (Mini USB mic recommended)
- Headphones (Sony or similar, with jack)
- (For Pi) Monitor, keyboard, and mouse for setup

---

## Software Requirements
- **Python 3.8+** (backend)
- **Node.js** (frontend)
- **ffmpeg** (for audio conversion)
- See `requirements.txt` and `requirements-pi.txt` for Python dependencies
- See `frontend/package.json` for frontend dependencies

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/gauravpurohit28/Lumen.git
cd Lumen
```

### 2. Backend Setup
#### a. Install Python Dependencies
```bash
pip install -r requirements.txt
# On Raspberry Pi:
pip install -r requirements-pi.txt
```
#### b. Install ffmpeg
- **Windows:** Download from https://ffmpeg.org/download.html and add to PATH
- **Linux:** `sudo apt install ffmpeg`
- **Mac:** `brew install ffmpeg`

#### c. Add API Keys and Credentials
- Edit `backend/config.py` and fill in your Gemini, Firebase, and other API credentials.
- Place your Firebase credentials in `backend/firebase_creds.json` and Google Cloud Storage credentials in `backend/storage_creds.json`.

#### d. Start the Backend Server
```bash
uvicorn backend.api_server:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```

---

## Usage
- Open the frontend in your browser (usually at http://localhost:3000)
- Press the main button to capture an image and hear its description
- After a short pause, ask a question about the image aloud
- The system will transcribe your question, send it to Gemini, and speak the answer
- Use the "New Image" button to restart the process

---

## Configuration
- Edit `backend/config.py` for API keys and settings
- Place Firebase and Google Cloud credentials in the backend directory as required

---

## Dependencies

### Backend (Python)
- fastapi
- uvicorn
- pvporcupine
- google-generativeai
- SpeechRecognition
- firebase-admin
- google-cloud-texttospeech
- opencv-python
- Pillow
- pydub
- simpleaudio
- pyttsx3
- numpy
- picamera2 *(Raspberry Pi only)*

### Frontend (Node.js)
- @emotion/react
- @emotion/styled
- @mui/icons-material
- @mui/material
- axios
- react
- react-dom
- react-scripts

---

## Accessibility
- All prompts and outputs are spoken
- Minimal interaction required (single button for main flow)
- Designed for screen reader compatibility and keyboard navigation

---

## License
This project is licensed under the Gauravpurohit - see the [LICENSE](LICENSE) file for details. 