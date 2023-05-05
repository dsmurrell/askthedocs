import os

from pydub import AudioSegment
from pydub.effects import strip_silence


def split_audio(
    input_file,
    output_dir,
    max_size_bytes=25 * 1024 * 1024,
    silence_threshold=-50,
    silence_duration=1000,
):
    # Load the audio file
    audio = AudioSegment.from_file(input_file, format="m4a")

    # Remove silence from the beginning and end of the audio
    audio = strip_silence(
        audio, silence_len=silence_duration, silence_thresh=silence_threshold
    )

    # Calculate the audio bitrate
    file_size = os.path.getsize(input_file)
    audio_bitrate = (file_size * 8) / (len(audio) / 1000)  # in kbps

    # Calculate the chunk length in milliseconds based on the maximum size and audio bitrate
    chunk_length_ms = ((max_size_bytes * 8) / audio_bitrate) * 1000  # in milliseconds

    # Split the audio into chunks
    num_chunks = int(len(audio) // chunk_length_ms) + 1
    chunks = [
        audio[i * chunk_length_ms : (i + 1) * chunk_length_ms]
        for i in range(num_chunks)
    ]

    # Export the audio chunks
    os.makedirs(output_dir, exist_ok=True)
    for i, chunk in enumerate(chunks):
        output_file = os.path.join(output_dir, f"chunk_{i+1}.mp3")
        chunk.export(output_file, format="mp3", codec="libmp3lame")

    print(
        f"Audio file has been split into {len(chunks)} chunks and saved in '{output_dir}'"
    )


if __name__ == "__main__":
    input_file = "audio_files/GMT20230427-145754_Recording.m4a"
    base_output_dir = "audio_splits"
    input_file_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(base_output_dir, input_file_name)

    split_audio(input_file, output_dir)
