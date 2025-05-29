import tempfile
import base64
import os
import time
import traceback
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from picture import take_picture
from pydub import AudioSegment
import speech_recognition as sr
import google.generativeai as genai
from google.cloud import texttospeech
from config import GOOGLE_API_KEY

# Initialize Gemini
genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

global_last_image_path = None

def gemini_image_caption(image_path):
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([
        {"mime_type": "image/jpeg", "data": image_bytes},
        "Describe this image for a blind user. Limit your description to 30 words or less."
    ])
    description = response.text.strip()
    # Truncate to 30 words if needed
    words = description.split()
    if len(words) > 30:
        description = ' '.join(words[:30]) + '...'
    return description

def gemini_vqa(image_path, question):
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([
        {"mime_type": "image/jpeg", "data": image_bytes},
        question
    ])
    return response.text.strip()

@app.post("/api/capture")
async def api_capture():
    global global_last_image_path
    try:
        image_folder = os.path.join(os.getcwd(), "CapturedImages")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        image_path = os.path.join(image_folder, f"capture_{int(time.time())}.jpg")
        take_picture(image_path)
        global_last_image_path = image_path
        description = gemini_image_caption(image_path)
        # Optionally, return base64 for frontend display
        with open(image_path, "rb") as img_file:
            image_b64 = base64.b64encode(img_file.read()).decode("utf-8")
        return {"image_b64": image_b64, "description": description}
    except Exception as e:
        print("/api/capture error:", e)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/question")
async def api_question(request: Request):
    global global_last_image_path
    try:
        data = await request.json()
        question = data.get("question", "")
        if not global_last_image_path or not os.path.exists(global_last_image_path):
            return JSONResponse(status_code=400, content={"error": "No image captured yet."})
        answer = gemini_vqa(global_last_image_path, question)
        return {"answer": answer}
    except Exception as e:
        print("/api/question error:", e)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/question-audio")
async def api_question_audio(audio: UploadFile = File(...)):
    global global_last_image_path
    try:
        upload_folder = os.path.join(os.getcwd(), "CapturedImages")
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        webm_path = os.path.join(upload_folder, f"question_{int(time.time())}.webm")
        with open(webm_path, "wb") as f:
            f.write(await audio.read())
        wav_path = webm_path.replace(".webm", ".wav")
        sound = AudioSegment.from_file(webm_path)
        sound.export(wav_path, format="wav")
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
        try:
            question = recognizer.recognize_google(audio_data)
            print(f"Transcribed question: {question}")
        except sr.UnknownValueError:
            return JSONResponse(status_code=400, content={"error": "Sorry, I could not understand your speech. Please try again."})
        except sr.RequestError as e:
            return JSONResponse(status_code=500, content={"error": f"Speech recognition error: {e}"})
        if not global_last_image_path or not os.path.exists(global_last_image_path):
            return JSONResponse(status_code=400, content={"error": "No image captured yet."})
        answer = gemini_vqa(global_last_image_path, question)
        return {"answer": answer}
    except Exception as e:
        print("/api/question-audio error:", e)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/tts")
async def api_tts(request: Request):
    try:
        data = await request.json()
        text = data.get("text", "")
        if not text:
            return JSONResponse(status_code=400, content={"error": "No text provided."})
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out:
            out.write(response.audio_content)
            temp_audio_path = out.name
        return FileResponse(temp_audio_path, media_type="audio/wav", filename="output.wav")
    except Exception as e:
        print("/api/tts error:", e)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)}) 