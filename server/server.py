import logging

from pathlib import Path

import click
import soundfile as sf

from flask import Flask, request, jsonify
from faster_whisper import WhisperModel

app = Flask(__name__)


def transcribe(model, audio_path, language):
    segments, _ = model.transcribe(audio_path, language=language)
    fragments = [segment.text for segment in segments]
    return "".join(fragments).strip()


@app.route("/v1/audio/transcriptions", methods=["POST"])
def transcriptions():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["file"]
        audio_data, _ = sf.read(audio_file)
        transcription = transcribe(app.config["MODEL"], audio_data, app.config["LANGUAGE"])
        logging.info("Transcribed query: %s", transcription)

        return jsonify({"text": transcription}), 200

    except Exception as e:  # pylint: disable=broad-except
        return jsonify({"error": str(e)}), 500


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "Service is up and running"}), 200


@click.command()
@click.option("--host", default="0.0.0.0", help="Host to run the web service on.")
@click.option("--port", default=5000, help="Port to run the web service on.")
@click.option("--language", default="en", help="The language to expect.")
@click.option(
    "--model",
    default="tiny",
    help="Whisper model to use (e.g., tiny, base, small, medium, large).",
)
@click.option(
    "--device", default="cpu", help="Device to run the model on (e.g., cpu, cuda)."
)
def main(host, port, language, model, device):
    logging.basicConfig(level=logging.INFO)

    model = WhisperModel(model, device=device)

    # Test transcription to ensure model works (and trigger download) before exposing the service.
    test_audio_path = Path(__file__).resolve().parent / "hi.wav"
    if test_audio_path.exists():
        audio_data, _ = sf.read(test_audio_path)
        transcribe(model, audio_data, language)

    app.config["MODEL"] = model
    app.config["LANGUAGE"] = language

    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
