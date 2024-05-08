#!/usr/bin/env python3
"""Script to capture a voice query from the microphone and save it to a file.

The script will prompt the user to speak and then record their voice. The
recording is saved to a file in the current directory. The file name is based
on the current date and time.
"""
import logging

import click

from dotenv import load_dotenv
from fably import utils


# Load environment variables from .env file, if available
load_dotenv()


@click.command()
@click.option(
    "--stt-model",
    default="whisper-1",
    help='The STT model to use when generating stories. Defaults to "whisper-1".',
)
@click.option(
    "--sound-model",
    default="vosk-model-small-en-us-0.15",
    help='The model to use to discriminate speech in voice queries. Defaults to "vosk-model-small-en-us-0.15".',
)
@click.option(
    "--language",
    default="en",
    help='The language to use when generating stories. Defaults to "en".',
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
def main(stt_model, sound_model, language, sound_driver, trim_first_frame, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    sync_client, _ = utils.get_openai_clients()
    recognizer = utils.get_speech_recognizer(utils.resolve("models"), sound_model)

    print("Say something...")

    voice_query, voice_query_sample_rate, query_local = utils.record_until_silence(
        recognizer, trim_first_frame
    )
    query_cloud, voice_query_file = utils.transcribe(
        sync_client,
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
