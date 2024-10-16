import pygame
import time


def play_wav(file_path):
    
    pygame.mixer.init()

    pygame.mixer.music.load(file_path)

    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(1)  # Wait for the audio to finish playing


wav_file = 'output.mp3'

play_wav(wav_file)
