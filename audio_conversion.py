
from pydub import AudioSegment

# Load the .mp3 file
sound = AudioSegment.from_mp3("output.mp3")

# Export as .wav
sound.export("output.wav", format="wav")
