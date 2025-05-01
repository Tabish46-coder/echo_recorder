from io import BytesIO
from flask import request, jsonify, send_file
from app import app
from app.helpers import normalize_audio, remove_echo, remove_background_noise

@app.route('/api/normalize-audio', methods=['POST'])
def normalize_audio_api():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'error': 'No file provided'}), 400

    try:
        input_audio = BytesIO(request.files['file'].read())
        output_audio = BytesIO()
        normalize_audio(input_audio, output_audio)
        output_audio.seek(0)
        return send_file(output_audio, as_attachment=True, download_name='normalized.wav', mimetype='audio/wav')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/remove-echo', methods=['POST'])
def remove_echo_api():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'error': 'No file provided'}), 400

    try:
        input_audio = BytesIO(request.files['file'].read())
        output_audio = BytesIO()
        remove_echo(input_audio, output_audio)
        output_audio.seek(0)
        return send_file(output_audio, as_attachment=True, download_name='echo_removed.wav', mimetype='audio/wav')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/remove-background-noise', methods=['POST'])
def remove_background_noise_api():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'error': 'No file provided'}), 400

    try:
        input_audio = BytesIO(request.files['file'].read())
        output_audio = BytesIO()
        remove_background_noise(input_audio, output_audio)
        output_audio.seek(0)
        return send_file(output_audio, as_attachment=True, download_name='cleaned.wav', mimetype='audio/wav')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
