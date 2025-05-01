from pydub import AudioSegment
import subprocess
import noisereduce as nr
import numpy as np
from io import BytesIO
import tempfile
import os

def normalize_audio(input_io, output_io):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_in:
        temp_in.write(input_io.read())
        temp_in.flush()

        temp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_out.close()

        cmd = [
            'ffmpeg',
            '-i', temp_in.name,
            '-af', 'loudnorm=I=-16:TP=-2:LRA=7:measured_I=-23:measured_TP=-5:measured_LRA=14:measured_thresh=-35:offset=0.5:linear=true',
            '-ar', '44100',
            '-y',
            temp_out.name
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            with open(temp_out.name, 'rb') as f:
                output_io.write(f.read())
        finally:
            os.unlink(temp_in.name)
            os.unlink(temp_out.name)


def remove_echo(input_io, output_io):
    audio = AudioSegment.from_file(input_io)
    
    # Apply echo removal logic here (placeholder: pass-through)
    cleaned_audio = audio

    cleaned_audio.export(output_io, format="mp3")


def remove_background_noise(input_io, output_io):
    audio = AudioSegment.from_file(input_io)

    samples = np.array(audio.get_array_of_samples())

    # Stereo handling
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
        reduced = np.stack([
            nr.reduce_noise(y=samples[:, 0], sr=audio.frame_rate),
            nr.reduce_noise(y=samples[:, 1], sr=audio.frame_rate)
        ], axis=1).astype(np.int16)
        raw_data = reduced.tobytes()
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