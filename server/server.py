import tempfile
from pathlib import Path

import click
from flask import Flask, request, jsonify
from faster_whisper import WhisperModel

app = Flask(__name__)


def transcribe(model, audio_path, language):
    segments, info = model.transcribe(audio_path, language=language)
    transcriptions = [segment.text for segment in segments]
    return ''.join(transcriptions).strip()


@app.route('/v1/audio/transcriptions', methods=['POST'])
def transcriptions():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['file']

        # Save the audio file to a temporary location
        with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as tmp:
            tmp_path = Path(tmp.name)
            audio_file.save(tmp_path)

            # Transcribe the audio file
            transcription = transcribe(app.config['MODEL'], str(tmp_path), app.config['LANGUAGE'])

        # Return the transcription result as a single string
        return jsonify({"text": transcription}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Service is up and running"}), 200


@click.command()
@click.option('--host', default='0.0.0.0', help='Host to run the web service on.')
@click.option('--port', default=5000, help='Port to run the web service on.')
@click.option('--language', default='en', help='The language to expect.')
@click.option('--model', default='tiny', help='Whisper model to use (e.g., tiny, base, small, medium, large).')
@click.option('--device', default='cpu', help='Device to run the model on (e.g., cpu, cuda).')
def main(host, port, language, model, device):    
    app.config['MODEL'] = WhisperModel(model, device=device)
    app.config['LANGUAGE'] = language

    # Test transcription to ensure model works before exposing the service.
    test_audio_path = Path(__file__).resolve().parent / 'hi.wav'
    if test_audio_path.exists():
        print(transcribe(app.config['MODEL'], str(test_audio_path), language))
    
    app.run(host=host, port=port)


if __name__ == '__main__':
    main()
