from io import BytesIO
import os
from flask import request, jsonify, send_file
from app import app
from werkzeug.utils import secure_filename
from app.helpers import normalize_audio,remove_echo,remove_background_noise

@app.route('/api/normalize-audio', methods=['POST'])
def normalize_audio_api():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Process in memory
        input_audio = BytesIO(file.read())
        output_audio = BytesIO()
        normalize_audio(input_audio, output_audio)
        output_audio.seek(0)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return send_file(output_audio, as_attachment=True, download_name='normalized.mp3', mimetype='audio/mpeg')


@app.route('/api/remove-echo', methods=['POST'])
def remove_echo_api():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        input_audio = BytesIO(file.read())
        output_audio = BytesIO()
        remove_echo(input_audio, output_audio)
        output_audio.seek(0)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return send_file(output_audio, as_attachment=True, download_name='echo_removed.mp3', mimetype='audio/mpeg')


@app.route('/api/remove-background-noise', methods=['POST'])
def remove_background_noise_api():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        input_audio = BytesIO(file.read())
        output_audio = BytesIO()
        remove_background_noise(input_audio, output_audio)
        output_audio.seek(0)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return send_file(output_audio, as_attachment=True, download_name='cleaned.mp3', mimetype='audio/mpeg')