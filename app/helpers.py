import subprocess
import tempfile
import os
import numpy as np
from pydub import AudioSegment
import noisereduce as nr

def apply_volume(input_io, output_io, level) -> None:
    """Mute or amplify the whole track based on a 0-5 scale."""
    volume_factors = {
        0: 0,     # mute
        1: 0.20,  # whisper-quiet
        2: 0.40,
        3: 0.70,
        4: 1.00,  # original loudness
        5: 3.00   # “extra loud” (≈ +6 dB)
    }
    factor = volume_factors[level]

    # write the uploaded stream to a temp file …
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_in:
        temp_in.write(input_io.read())
        temp_input_path = temp_in.name

    # prepare an output temp file for ffmpeg …
    temp_out = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    temp_output_path = temp_out.name
    temp_out.close()

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i", temp_input_path,
                "-filter:a", f"volume={factor}",
                "-ar", "44100",         # keep sample-rate consistent
                "-y",                   # overwrite
                temp_output_path,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # send processed bytes back to the API
        with open(temp_output_path, "rb") as f:
            output_io.write(f.read())
    finally:
        os.unlink(temp_input_path)
        os.unlink(temp_output_path)


def remove_echo(input_io, output_io):
    # Save to temp file first
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_in:
        temp_in.write(input_io.read())
        temp_input_path = temp_in.name

    try:
        audio = AudioSegment.from_file(temp_input_path)
        cleaned_audio = audio  # Dummy logic — replace with actual echo cancellation if desired
        cleaned_audio.export(output_io, format="mp3")
    finally:
        os.unlink(temp_input_path)


def remove_background_noise(input_io, output_io):
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_in:
        temp_in.write(input_io.read())
        temp_input_path = temp_in.name

    try:
        audio = AudioSegment.from_file(temp_input_path)
        samples = np.array(audio.get_array_of_samples())

        # Stereo handling
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))
            reduced = np.stack([
                nr.reduce_noise(y=samples[:, 0], sr=audio.frame_rate),
                nr.reduce_noise(y=samples[:, 1], sr=audio.frame_rate)
            ], axis=1).astype(np.int16)
        else:
            reduced = nr.reduce_noise(y=samples, sr=audio.frame_rate).astype(np.int16)

        raw_data = reduced.tobytes()

        cleaned_audio = AudioSegment(
            data=raw_data,
            sample_width=audio.sample_width,
            frame_rate=audio.frame_rate,
            channels=audio.channels
        )

        cleaned_audio.export(output_io, format="mp3")
    finally:
        os.unlink(temp_input_path)
