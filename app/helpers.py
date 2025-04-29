from pydub import AudioSegment,effects
from pydub.effects import normalize
import os
import subprocess
import noisereduce as nr
import numpy as np


def normalize_audio(input_path, output_path):
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-af', 'loudnorm=I=-16:TP=-2:LRA=7:measured_I=-23:measured_TP=-5:measured_LRA=14:measured_thresh=-35:offset=0.5:linear=true',
        '-ar', '44100',  # keep sampling rate consistent
        '-y',  # overwrite output
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("FFmpeg normalization failed:", e.stderr.decode())
        raise

    if not os.path.exists(output_path):
        raise FileNotFoundError(f"Normalized file not found: {output_path}")


def remove_echo(input_path, output_path):
    # Example logic – replace with your actual echo removal process
    audio = AudioSegment.from_file(input_path)

    # Simulate echo removal (you can use noise reduction logic or convolution filters)
    # For now, we just return the same audio
    cleaned_audio = audio

    ext = output_path.rsplit('.', 1)[-1].lower()

    if ext == "m4a":
        cleaned_audio.export(output_path, format="ipod", codec="aac")
    else:
        cleaned_audio.export(output_path, format=ext)




def remove_background_noise(input_path, output_path):
    audio = AudioSegment.from_file(input_path)

    samples = np.array(audio.get_array_of_samples())

    # Handle stereo audio
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

    # Export in original format (e.g., WAV or M4A depending on input)
    ext = output_path.rsplit(".", 1)[-1].lower()
    format_map = {"m4a": "ipod"}
    cleaned_audio.export(output_path, format=format_map.get(ext, ext))