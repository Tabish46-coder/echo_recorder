import tempfile
import os
import numpy as np
from pydub import AudioSegment
import noisereduce as nr

def normalize_audio(input_io, output_io):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_in:
        temp_in.write(input_io.read())
        temp_input_path = temp_in.name

    try:
        audio = AudioSegment.from_file(temp_input_path)
        normalized_audio = audio.normalize()
        normalized_audio.export(output_io, format="mp3")
    finally:
        os.unlink(temp_input_path)


def remove_echo(input_io, output_io):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_in:
        temp_in.write(input_io.read())
        temp_input_path = temp_in.name

    try:
        audio = AudioSegment.from_file(temp_input_path)
        cleaned_audio = audio  # Placeholder: no actual echo cancellation
        cleaned_audio.export(output_io, format="mp3")
    finally:
        os.unlink(temp_input_path)


def remove_background_noise(input_io, output_io):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_in:
        temp_in.write(input_io.read())
        temp_input_path = temp_in.name

    try:
        audio = AudioSegment.from_file(temp_input_path)
        samples = np.array(audio.get_array_of_samples())

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
