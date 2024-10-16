import pyaudio
import numpy as np
import wave
import time
import struct

# Function to record audio and save it as a WAV file
def record_audio(filename, duration=3, rate=16000):
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=1024)

    print("Recording...")

    frames = []
    for _ in range(0, int(rate / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    print("Recording done.")

    stream.stop_stream()
    stream.close()
    pa.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

# Function to listen and process audio input
def listen_for_wake_word():
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

    print("Listening for the wake word...")
    
    while True:
        data = stream.read(1024)
        audio_data = np.frombuffer(data, dtype=np.int16)

        # Example: crude approach to detect wake word using volume (this is NOT accurate)
        volume_threshold = 2000
        if np.max(audio_data) > volume_threshold:
            print("Wake word detected!")
            return True

# Main function to either record a template or detect wake word
if __name__ == "__main__":
    print("1. Record wake word template\n2. Detect wake word")
    choice = input("Enter choice (1 or 2): ")

    if choice == "1":
        record_audio("wake_word_template.wav")
    elif choice == "2":
        listen_for_wake_word()
    else:
        print("Invalid choice")
