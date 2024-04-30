"""
Generate a sound file from text.
"""

import logging
import os

import click
import openai

from dotenv import load_dotenv

# Load environment variables from .env file
script_dir = os.path.dirname(os.path.realpath(__file__))
load_dotenv(os.path.join(script_dir, "../.env"), override=True)


@click.command()
@click.argument("text")
@click.argument("output_file")
@click.option(
    "--model",
    default="tts-1-hd",
    help='The TTS model to use when generating stories. Defaults to "tts-1-hd".',
)
@click.option(
    "--voice",
    default="nova",
    help='The TTS voice to use when generating stories. Defaults to "nova".',
)
@click.option(
    "--audio_format",
    default="wav",
    help='The TTS format to use when generating stories. Defaults to "wav".',
)
@click.option("--debug", is_flag=True, default=False, help="Enables debug logging.")
# pylint: disable=too-many-arguments
def main(
    text,
    output_file,
    model,
    voice,
    audio_format,
    debug,
):

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai_client = openai.Client()

    logging.debug("Generating audio for '%s' with voice '%s' from model '%s' and format '%s...", text, voice, model, audio_format)
    response = openai_client.audio.speech.create(
        input=text, model=model, voice=voice, response_format=audio_format
    )

    response.write_to_file(output_file)
    logging.debug("Audio saved at %s", output_file)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
