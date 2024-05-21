#!/usr/bin/env python3
"""Script to capture a voice query from the microphone and save it to a file.

The script will prompt the user to speak and then record their voice. The
recording is saved to a file in the current directory. The file name is based
on the current date and time.
"""
import logging
import os

import click
import openai

from dotenv import load_dotenv
from fably import utils


# Load environment variables from .env file, if available
load_dotenv()

STT_MODEL = "whisper-1"
STT_URL = "https://api.openai.com/v1" # OpenAI cloud endpoint
SOUND_MODEL = "vosk-model-small-en-us-0.15"
LANGUAGE = "en"

@click.command()
@click.option(
    "--stt-url",
    default=STT_URL,
    help=f'The URL of the cloud endpoint for the LLM model. Defaults to "{STT_URL}".',
)
@click.option(
    "--stt-model",
    default=STT_MODEL,
    help=f'The STT model to use when generating stories. Defaults to "{STT_MODEL}".',
)
@click.option(
    "--sound-model",
    default=SOUND_MODEL,
    help=f'The model to use to discriminate speech in voice queries. Defaults to "{SOUND_MODEL}".',
)
@click.option(
    "--language",
    default=LANGUAGE,
    help=f'The language to use when generating stories. Defaults to "{LANGUAGE}".',
)
@click.option(
    "--sound-driver",
    type=click.Choice(["alsa", "sounddevice"], case_sensitive=False),
    default="alsa",
    help="Which driver to use to emit sound.",
)
@click.option(
    "--trim-first-frame",
    is_flag=True,
    default=False,
    help="Trim the first frame of recorded audio data. Useful if the mic has a click or hiss at the beginning of each recording.",
)
@click.option("--debug", is_flag=True, default=False, help="Enables debug logging.")
def main(stt_url, stt_model, sound_model, language, sound_driver, trim_first_frame, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError(
            "OPENAI_API_KEY environment variable not set or .env file not found."
        )

    stt_client = openai.Client(base_url=stt_url, api_key=api_key)
    recognizer = utils.get_speech_recognizer(utils.resolve("models"), sound_model)

    print("Say something...")

    voice_query, voice_query_sample_rate, query_local = utils.record_until_silence(
        recognizer, trim_first_frame
    )
    query_cloud, voice_query_file = utils.transcribe(
        stt_client,
        voice_query,
        stt_model=stt_model,
        language=language,
        sample_rate=voice_query_sample_rate,
    )

    utils.play_audio_file(voice_query_file, sound_driver)

    print(f"Local transcription: {query_local}")
    print(f"Cloud transcription: {query_cloud}")


if __name__ == "__main__":
    main()
