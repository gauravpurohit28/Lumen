
import wave
import numpy as np
import struct
from pydub import AudioSegment

def read_audio(file_path):
    # Read the MP3 file
    audio = AudioSegment.from_mp3(file_path)
    
    audio_data = audio.raw_data
    channels = audio.channels
    sampwidth = audio.sample_width
    framerate = audio.frame_rate
    
    return audio_data, channels, sampwidth, framerate


def apply_fft(audio_data, framerate):
    spectrum = np.fft.fft(audio_data)
    freqs = np.fft.fftfreq(len(spectrum), 1 / framerate)
    return spectrum, freqs

def recognize_basic_word(spectrum, known_patterns):
    for word, pattern in known_patterns.items():
        if np.allclose(spectrum[:len(pattern)], pattern):
            return word
    return "Unknown word"

if __name__ == "__main__":
    audio_data, channels, sampwidth, framerate = read_audio('output.wav')
    spectrum, freqs = apply_fft(audio_data, framerate)
    
    known_patterns = {
        "hello": np.array([complex(1, 2), complex(3, 4)]),
        "yes": np.array([complex(5, 6), complex(7, 8)]),
    }
    
    word = recognize_basic_word(spectrum, known_patterns)
    print("Recognized word:", word)
