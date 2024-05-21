"""
Fably's Command line interface.
"""

import logging
import os
import platform
import sys

import click

from dotenv import load_dotenv

from fably import fably
from fably import utils
from fably import leds

from fably.cli_utils import pass_context

OPENAI_URL = "https://api.openai.com/v1"
OLLAMA_URL = "http://127.0.0.1:11434/v1"

PROMPT_FILE = "./prompt.txt"
QUERIES_PATH = "./queries"
STORIES_PATH = "./stories"
MODELS_PATH = "./models"
SOUND_MODEL = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 24000
STT_URL = OPENAI_URL
STT_MODEL = "whisper-1"
LLM_URL = OPENAI_URL
# LLM_URL = OLLAMA_URL
LLM_MODEL = "gpt-4o"
# LLM_MODEL = "gpt-3.5-turbo"
TEMPERATURE = 1.0
MAX_TOKENS = 2000
TTS_URL = OPENAI_URL
TTS_MODEL = "tts-1"
TTS_VOICE = "nova"
TTS_FORMAT = "mp3"
LANGUAGE = "en"
BUTTON_GPIO_PIN = 17
HOLD_TIME = 3
SOUND_DRIVER = "alsa"
QUERY_GUARD = "tell me a story"

# STARTING_COLORS = [0xff0000, 0x00ff00, 0x0000ff]
STARTING_COLORS = [0xFF0000, 0xFF0000, 0xFF0000]

# Load environment variables from .env file, if available
load_dotenv()


@click.command()
@click.argument("query", required=False, default=None, nargs=1)
@click.option(
    "--prompt-file",
    default=PROMPT_FILE,
    help=f'The file to use as the prompt when generating stories. Defaults to "{PROMPT_FILE}".',
)
@click.option(
    "--sample-rate",
    default=SAMPLE_RATE,
    help=f"The sample rate to use when generating stories. Defaults to {SAMPLE_RATE}.",
)
@click.option(
    "--queries-path",
    default=QUERIES_PATH,
    help=f'The directory to store the recorded voice queries in. Defaults to "{QUERIES_PATH}".',
)
@click.option(
    "--stories-path",
    default=STORIES_PATH,
    help=f'The directory to store the generated stories in. Defaults to "{STORIES_PATH}".',
)
@click.option(
    "--models-path",
    default=MODELS_PATH,
    help=f'The directory to store the downloaded models running locally. Defaults to "{MODELS_PATH}".',
)
@click.option(
    "--sound-model",
    default=SOUND_MODEL,
    help=f'The model to use to discriminate speech in voice queries. Defaults to "{SOUND_MODEL}".',
)
@click.option(
    "--stt-url",
    default=LLM_URL,
    help=f'The URL of the cloud endpoint for the STT model. Defaults to "{STT_URL}".',
)
@click.option(
    "--stt-model",
    default=STT_MODEL,
    help=f'The STT model to use when generating stories. Defaults to "{STT_MODEL}".',
)
@click.option(
    "--llm-url",
    default=LLM_URL,
    help=f'The URL of the cloud endpoint for the LLM model. Defaults to "{LLM_URL}".',
)
@click.option(
    "--llm-model",
    default=LLM_MODEL,
    help=f'The LLM model to use when generating stories. Defaults to "{LLM_MODEL}".',
)
@click.option(
    "--temperature",
    type=float,
    default=TEMPERATURE,
    help="The temperature to use when generating stories. Defaults to {TEMPERATURE}.",
)
@click.option(
    "--max-tokens",
    type=int,
    default=MAX_TOKENS,
    help="The maximum number of tokens to use when generating stories. Defaults to {MAX_TOKENS}.",
)
@click.option(
    "--tts-url",
    default=LLM_URL,
    help=f'The URL of the cloud endpoint for the TTS model. Defaults to "{TTS_URL}".',
)
@click.option(
    "--tts-model",
    default=TTS_MODEL,
    help=f'The TTS model to use when generating stories. Defaults to "{TTS_MODEL}".',
)
@click.option(
    "--tts-voice",
    default=TTS_VOICE,
    help=f'The TTS voice to use when generating stories. Defaults to "{TTS_VOICE}".',
)
@click.option(
    "--tts-format",
    default=TTS_FORMAT,
    help=f'The TTS format to use when generating stories. Defaults to "{TTS_FORMAT}".',
)
@click.option(
    "--language",
    default=LANGUAGE,
    help=f'The language to use when generating stories. Defaults to "{LANGUAGE}".',
)
@click.option(
    "--query-guard",
    default=QUERY_GUARD,
    help=f'The text each query has to start with. Defaults to "{QUERY_GUARD}".',
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
    default=SOUND_DRIVER,
    help="Which driver to use to emit sound.",
)
@click.option(
    "--trim-first-frame",
    is_flag=True,
    default=False,
    help="Trim the first frame of recorded audio data. Useful if the mic has a click or hiss at the beginning of each recording.",
)
@click.option(
    "--button-gpio-pin",
    type=int,
    default=BUTTON_GPIO_PIN,
    help=f"The GPIO pin to use for the button. Defaults to {BUTTON_GPIO_PIN}.",
)
@click.option(
    "--hold-time",
    type=float,
    default=HOLD_TIME,
    help="The time to hold the button to erase all recorded sounds. Defaults to {HOLD_TIME} seconds.",
)
@click.option("--loop", is_flag=True, default=False, help="Enables loop operation.")
@pass_context
def cli(
    ctx,
    query,
    prompt_file,
    sample_rate,
    queries_path,
    stories_path,
    models_path,
    sound_model,
    stt_url,
    stt_model,
    llm_url,
    llm_model,
    temperature,
    max_tokens,
    tts_url,
    tts_model,
    tts_voice,
    tts_format,
    language,
    query_guard,
    debug,
    ignore_cache,
    sound_driver,
    trim_first_frame,
    button_gpio_pin,
    hold_time,
    loop,
):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    ctx.sound_model = sound_model
    ctx.stt_url = stt_url
    ctx.stt_model = stt_model
    ctx.llm_url = llm_url
    ctx.llm_model = llm_model
    ctx.tts_url = tts_url
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
    ctx.loop = loop
    ctx.sound_driver = sound_driver
    ctx.trim_first_frame = trim_first_frame
    ctx.button_gpio_pin = button_gpio_pin
    ctx.hold_time = hold_time

    ctx.prompt_file = utils.resolve(prompt_file)
    ctx.queries_path = utils.resolve(queries_path)
    ctx.stories_path = utils.resolve(stories_path)
    ctx.models_path = utils.resolve(models_path)

    ctx.leds = leds.LEDs(STARTING_COLORS)

    ctx.running = True
    ctx.talking = False

    ctx.api_key = os.getenv("OPENAI_API_KEY")
    if ctx.api_key is None:
        raise ValueError(
            "OPENAI_API_KEY environment variable not set or .env file not found."
        )

    # Alsa is only supported on Linux.
    if ctx.sound_driver == "alsa" and platform.system() != "Linux":
        ctx.sound_driver = "sounddevice"

    try:
        fably.main(ctx, query)
    finally:
        ctx.leds.stop()


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        sys.exit("\nInterrupted by user")
