import numpy as np
from pyAudioAnalysis import audioSegmentation as aS
from pydub import AudioSegment

input_file_path = "audio_files/GMT20230427-145754_Recording.m4a"
output_file_path = "audio_files/GMT20230427-145754_Recording.wav"

# Convert the .m4a file to .wav format
audio = AudioSegment.from_file(input_file_path, format="m4a")
audio.export(output_file_path, format="wav")

# Perform speaker diarization using pyAudioAnalysis
speaker_labels = aS.speaker_diarization(output_file_path, n_speakers=0)
print(speaker_labels)
