import subprocess
import tempfile
import os
import numpy as np
from pydub import AudioSegment
import noisereduce as nr

def normalize_audio(input_io, output_io, level):
    # Define normalization settings based on level (1-5)
    normalization_settings = {
        1: {'I': -23, 'TP': -3, 'LRA': 11},  # Light normalization
        2: {'I': -20, 'TP': -2.5, 'LRA': 9}, # Mild normalization
        3: {'I': -16, 'TP': -2, 'LRA': 7},   # Standard normalization
        4: {'I': -14, 'TP': -1.5, 'LRA': 5}, # Strong normalization
        5: {'I': -12, 'TP': -1, 'LRA': 3}    # Maximum normalization
    }

    settings = normalization_settings.get(level, normalization_settings[3])

    # Save input BytesIO to a temp file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_in:
        temp_in.write(input_io.read())
        temp_input_path = temp_in.name

    # Create an output temp file path
    temp_out = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    temp_output_path = temp_out.name
    temp_out.close()  # Close before FFmpeg uses it

    try:
        cmd = [
            'ffmpeg',
            '-i', temp_input_path,
            '-af', f'loudnorm=I={settings["I"]}:TP={settings["TP"]}:LRA={settings["LRA"]}',
            '-ar', '44100',
            '-y',
            temp_output_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        with open(temp_output_path, 'rb') as f:
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
