"""
Fably's Command line interface.
"""

import asyncio
import logging
import sys

import click

from dotenv import load_dotenv

from fably import fably
from fably import utils
from fably.cli_utils import pass_context


# Load environment variables from .env file, if available
load_dotenv()


@click.command()
@click.option("--query", default=None, help="The story to tell.")
@click.option(
    "--prompt-file",
    default="./prompt.txt",
    help='The file to use as the prompt when generating stories. Defaults to "./prompt.txt".',
)
@click.option(
    "--sample-rate",
    default=24000,
    help="The sample rate to use when generating stories. Defaults to 24000.",
)
@click.option(
    "--queries-path",
    default="./queries",
    help='The directory to store the recorded voice queries in. Defaults to "./queries".',
)
@click.option(
    "--stories-path",
    default="./stories",
    help='The directory to store the generated stories in. Defaults to "./stories".',
)
@click.option(
    "--models-path",
    default="./models",
    help='The directory to store the downloaded models running locally. Defaults to "./models".',
)
@click.option(
    "--sound-model",
    default="vosk-model-small-en-us-0.15",
    help='The model to use to discriminate speech in voice queries. Defaults to "vosk-model-small-en-us-0.15".',
)
@click.option(
    "--stt-model",
    default="whisper-1",
    help='The STT model to use when generating stories. Defaults to "whisper-1".',
)
@click.option(
    "--llm-model",
    default="gpt-3.5-turbo",
    help='The LLM model to use when generating stories. Defaults to "gpt-3.5-turbo".',
)
@click.option(
    "--temperature",
    type=float,
    default=1.0,
    help="The temperature to use when generating stories. Defaults to 1.0.",
)
@click.option(
    "--max-tokens",
    type=int,
    default=1600,
    help="The maximum number of tokens to use when generating stories. Defaults to 1600.",
)
@click.option(
    "--tts-model",
    default="tts-1",
    help='The TTS model to use when generating stories. Defaults to "tts-1".',
)
@click.option(
    "--tts-voice",
    default="nova",
    help='The TTS voice to use when generating stories. Defaults to "nova".',
)
@click.option(
    "--tts-format",
    default="mp3",
    help='The TTS format to use when generating stories. Defaults to "mp3".',
)
@click.option(
    "--language",
    default="en",
    help='The language to use when generating stories. Defaults to "en".',
)
@click.option(
    "--query-guard",
    default="tell me a story about",
    help='The text each query has to start with. Defaults to "Tell me a story about".',
)
@click.option("--debug", is_flag=True, default=False, help="Enables debug logging.")
@click.option(
    "--ignore_cache",
    is_flag=True,
    default=False,
    help="Ignores the cache and always generates a new story.",
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
@pass_context
def main(
    ctx,
    query,
    prompt_file,
    sample_rate,
    queries_path,
    stories_path,
    models_path,
    sound_model,
    stt_model,
    llm_model,
    temperature,
    max_tokens,
    tts_model,
    tts_voice,
    tts_format,
    language,
    query_guard,
    debug,
    ignore_cache,
    sound_driver,
    trim_first_frame,
):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    ctx.sound_model = sound_model
    ctx.stt_model = stt_model
    ctx.llm_model = llm_model
    ctx.tts_model = tts_model
    ctx.temperature = temperature
    ctx.sample_rate = sample_rate
    ctx.max_tokens = max_tokens
    ctx.tts_voice = tts_voice
    ctx.tts_format = tts_format
    ctx.language = language
    ctx.query_guard = query_guard
    ctx.ignore_cache = ignore_cache
    ctx.debug = debug
    ctx.sound_driver = sound_driver
    ctx.trim_first_frame = trim_first_frame

    ctx.prompt_file = utils.resolve(prompt_file)
    ctx.queries_path = utils.resolve(queries_path)
    ctx.stories_path = utils.resolve(stories_path)
    ctx.models_path = utils.resolve(models_path)

    ctx.sync_client, ctx.async_client = utils.get_openai_clients()
    ctx.recognizer = utils.get_speech_recognizer(ctx.models_path, sound_model)

    asyncio.run(fably.main(ctx, query))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nInterrupted by user")
