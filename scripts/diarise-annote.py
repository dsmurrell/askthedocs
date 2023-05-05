import pickle
import sys
from pathlib import Path

from pyannote.audio import Pipeline

# from pydub import AudioSegment  # needed to convert to wav format

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import config

# # Convert the .m4a file to .wav format
# input_file_path = "audio_files/GMT20230427-145754_Recording.m4a"
output_file_path = "audio_files/GMT20230427-145754_Recording.wav"
# audio = AudioSegment.from_file(input_file_path, format="m4a")
# audio.export(output_file_path, format="wav")

# Instantiate pretrained speaker diarization pipeline
# Replace "ACCESS_TOKEN_GOES_HERE" with your actual access token
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
    use_auth_token=config["hugging_face_key"],
)

# Apply pretrained pipeline
diarization = pipeline(output_file_path)

# Save diarization to disk
with open("diarization.pkl", "wb") as f:
    pickle.dump(diarization, f)

# Print the result
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
