#!/usr/bin/env python

import tempfile

import click
from flask import Flask, request, jsonify, send_file
from whisperspeech.pipeline import Pipeline

app = Flask(__name__)


@app.route('/v1/audio/speech', methods=['POST'])
def speech_handler():
    data = request.get_json()

    if not data or 'input' not in data:
        return jsonify({"error": "Invalid request. 'input' field is required."}), 400

    text = data['input']

    language = app.config['LANGUAGE']
    model = app.config['TTS_MODEL']
    speed = app.config['TTS_SPEED']

    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        tmp_file_path = tmp_file.name

    model.generate_to_file(tmp_file_path, text, speaker=None, lang=language, cps=speed)

    return send_file(tmp_file_path, mimetype='audio/wav'), 200


@app.route('/status', methods=['GET'])
def status_handler():
    return jsonify({"status": "Service is up and running"}), 200


@click.command()
@click.option('--host', default='0.0.0.0', help='Host to run the web service on.')
@click.option('--port', default=5001, help='Port to run the web service on.')
@click.option('--language', default='en', help='The language to expect.')
@click.option('--tts_model', default='tiny', help='WhisperSpeech model to use (e.g., tiny, base, small, hq-fast).')
@click.option('--tts_speed', default=15, help='Characters per second to speak.')
def main(host, port, language, tts_model, tts_speed):

    model = Pipeline(
        t2s_ref=f"whisperspeech/whisperspeech:t2s-{tts_model}-en+pl.model",
        s2a_ref=f"whisperspeech/whisperspeech:s2a-q4-{tts_model}-en+pl.model",
        torch_compile=True
    )

    app.config['LANGUAGE'] = language
    app.config['TTS_MODEL'] = model
    app.config['TTS_SPEED'] = tts_speed

    # Test that models work before exposing the service.
    model.generate("this is a test", speaker=None, lang=language, cps=tts_speed)

    app.run(host=host, port=port)


if __name__ == '__main__':
    main()
