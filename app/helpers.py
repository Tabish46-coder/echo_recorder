import subprocess
import tempfile
import os
import numpy as np
from pydub import AudioSegment
import noisereduce as nr

def normalize_audio(input_io,output_io,level) -> None:
    

    if level not in range(1, 6):
        raise ValueError("level must be an integer from 1 to 5")

    # Map level → Integrated Loudness (LUFS) target.
    #   Every step = +3 dB (roughly 2× perceived loudness every 2 steps).
    #   Feel free to tweak these targets for your use-case.
    target_I = -24 + (level - 1) * 3   # -24,-21,-18,-15,-12

    # Write the uploaded buffer to a temporary file so FFmpeg can read it
    with tempfile.NamedTemporaryFile(suffix=".input", delete=False) as temp_in:
        temp_in.write(input_io.read())
        temp_input_path = temp_in.name

    # Prepare an output temp file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_out:
        temp_output_path = temp_out.name

    try:
        cmd = [
            "ffmpeg",
            "-i", temp_input_path,
            "-af", f"loudnorm=I={target_I}:TP=-2:LRA=7",
            "-ar", "44100",          # resample if you like; remove if not needed
            "-y",                    # overwrite output if it exists
            temp_output_path
        ]

        # Run FFmpeg and capture its output for easier debugging
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Copy the normalized result back into the caller-supplied buffer
        with open(temp_output_path, "rb") as f:
            output_io.write(f.read())

    finally:
        # Always remove temp files, even on error
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
