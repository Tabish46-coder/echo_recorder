import os
from flask import request, jsonify, send_file
from app import app
from werkzeug.utils import secure_filename
from app.helpers import normalize_audio,remove_echo,remove_background_noise

UPLOAD_FOLDER = 'E:/Side Work/Audio_backend/audio_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/api/normalize-audio', methods=['POST'])
def normalize_audio_api():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ['mp4', 'm4a', 'wav', 'mp3']:
        return jsonify({'error': 'Unsupported file format'}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    output_filename = f"normalized_{filename.rsplit('.', 1)[0]}.mp3"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    try:
        normalize_audio(input_path, output_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return send_file(output_path, as_attachment=True)



@app.route('/api/remove-echo', methods=['POST'])
def remove_echo_api():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    output_ext = filename.rsplit('.', 1)[-1].lower()
    output_path = os.path.join(UPLOAD_FOLDER, f"cleaned_{filename}")

    try:
        remove_echo(input_path, output_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    if not os.path.exists(output_path):
        return jsonify({'error': 'Output file was not created'}), 500

    return send_file(output_path, as_attachment=True)



@app.route('/api/remove-background-noise', methods=['POST'])
def remove_background_noise_api():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower()
    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    output_path = os.path.join(UPLOAD_FOLDER, f"cleaned_{filename}")

    try:
        remove_background_noise(input_path, output_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return send_file(output_path, as_attachment=True)