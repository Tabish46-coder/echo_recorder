from io import BytesIO
import io
from flask import request, jsonify, send_file
from app import app
from pydub import AudioSegment
from app.helpers import normalize_audio, remove_echo, remove_background_noise
import os
UPLOAD_FOLDER = 'audio_files'
CONVERTED_FOLDER = 'converted'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)
@app.route("/api/normalize-audio", methods=["POST"])
def normalize_audio_api():
    # 1️⃣ File field ---------------------------------------------------------
    if "file" not in request.files or request.files["file"].filename == "":
        return jsonify({"error": "No file provided"}), 400
    audio_file = request.files["file"]

    # 2️⃣ Level field --------------------------------------------------------
    level = request.form.get("level")             # multipart / form-data
    if level is None and request.is_json:         # raw JSON body
        level = request.get_json().get("level")

    if level is None:
        return jsonify({"error": "Level parameter is required (1-5)"}), 400

    try:
        level = int(level)
        if not 1 <= level <= 5:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Level must be an integer between 1 and 5"}), 400

    # 3️⃣ Normalise ----------------------------------------------------------
    try:
        input_audio  = BytesIO(audio_file.read())
        output_audio = BytesIO()
        normalize_audio(input_audio, output_audio, level)
        output_audio.seek(0)
        return send_file(
            output_audio,
            as_attachment=True,
            download_name="normalized.mp3",
            mimetype="audio/mpeg",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/remove-echo', methods=['POST'])
def remove_echo_api():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'error': 'No file provided'}), 400

    try:
        input_audio = BytesIO(request.files['file'].read())
        output_audio = BytesIO()
        remove_echo(input_audio, output_audio)
        output_audio.seek(0)
        return send_file(output_audio, as_attachment=True, download_name='echo_removed.mp3', mimetype='audio/mpeg')
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
        return send_file(output_audio, as_attachment=True, download_name='cleaned.mp3', mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@app.route('/convert_audio', methods=['POST'])
def convert_audio():
    if 'audio' not in request.files or 'name' not in request.form or 'extension' not in request.form:
        return jsonify({'error': 'Missing required parameters (audio, name, extension)'}), 400

    audio_file = request.files['audio']
    name = request.form['name']
    extension = request.form['extension'].lower()

    if extension != 'm4a':
        return jsonify({'error': 'Only .m4a extension is supported for input'}), 400

    try:
        # Read audio into pydub from the file stream
        audio = AudioSegment.from_file(audio_file, format='m4a')

        # Export to BytesIO buffer as WAV
        wav_io = io.BytesIO()
        audio.export(wav_io, format='wav')
        wav_io.seek(0)

        return send_file(
            wav_io,
            mimetype="audio/wav",
            as_attachment=True,
            download_name=f"{name}.wav"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
