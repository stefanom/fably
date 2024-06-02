#!/usr/bin/env python

import tempfile
from pathlib import Path

import click

from flask import Flask, request, jsonify
from faster_whisper import WhisperModel

app = Flask(__name__)


def transcribe(model, audio_path, language):
    segments, _ = model.transcribe(audio_path, language=language)
    return ''.join(segment.text for segment in segments).strip()


@app.route('/v1/audio/transcriptions', methods=['POST'])
def transcriptions_handler():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files['file']

        # Save the audio file to a temporary location
        with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as tmp:
            tmp_path = Path(tmp.name)
            audio_file.save(tmp_path)

            # Transcribe the audio file
            transcription = transcribe(app.config['STT_MODEL'], str(tmp_path), app.config['LANGUAGE'])

        # Return the transcription result as a single string
        return jsonify({"text": transcription}), 200

    except Exception as e:  # pylint: disable=broad-except
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route('/status', methods=['GET'])
def status_handler():
    return jsonify({"status": "Service is up and running"}), 200


@click.command()
@click.option('--host', default='0.0.0.0', help='Host to run the web service on.')
@click.option('--port', default=5000, help='Port to run the web service on.')
@click.option('--language', default='en', help='The language to expect.')
@click.option('--stt_model', default='tiny', help='Whisper model to use (e.g., tiny, base, small, medium, large).')
def main(host, port, language, stt_model):
    app.config['LANGUAGE'] = language

    app.config['STT_MODEL'] = WhisperModel(stt_model)

    # Test that models work before exposing the service.
    test_audio_path = Path(__file__).resolve().parent / 'hi.wav'
    if test_audio_path.exists():
        transcribe(app.config['STT_MODEL'], test_audio_path, language)

    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
