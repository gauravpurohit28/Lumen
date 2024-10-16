
import os
import wave
import numpy as np
from time import sleep
import simpleaudio as sa

def generate_wave(text):
    # Simulate text-to-speech conversion by generating a simple wave sound for each letter/word
    framerate = 44100
    t = np.linspace(0, 1, framerate, False)
    audio_data = np.sin(440 * 2 * np.pi * t) * 32767
    audio_data = audio_data.astype(np.int16)
    
    temp_wave = 'temp_output.wav'
    
    with wave.open(temp_wave, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        wf.writeframes(audio_data.tobytes())
    
    return temp_wave

def play_audio(file_path):
    wave_obj = sa.WaveObject.from_wave_file(file_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def speak(text: str):
    temp_file_path = generate_wave(text)
    
    print(f"Audio content generated for text: '{text}'")

    play_audio(temp_file_path)

    os.remove(temp_file_path)

if __name__ == "__main__":
    speak("Hello, how are you?")
