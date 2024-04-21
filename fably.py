#!/usr/bin/env python
"""
Fably uses generative AI cloud APIS to tell stories.
"""

import asyncio
import logging
import os
import re
import wave

from pathlib import Path

import click
import numpy as np
import openai
import sounddevice as sd
import soundfile as sf
import yaml

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

openai.api_key = os.getenv("OPENAI_API_KEY")
openai_sync_client = openai.Client()
openai_async_client = openai.AsyncClient()


def query_to_filename(query):
    """
    Convert a query from a voice assistant into a file name that can be used to save the story.

    This function removes the query guard part and removes any illegal characters from the file name.

    Args:
        query (str): The voice assistant query to convert into a file name.

    Returns:
        str: The file name.
    """
    # Remove the query guard part since it doesn't add any information
    query = query.lower().replace(QUERY_GUARD, "", 1).strip()

    # Replace illegal file name characters with underscores and truncate
    return re.sub(r'[\\/*?:"<>| ]', "_", query)[:MAX_FILE_LENGTH]


def write_to_file(path, text):
    """
    Write the given text to a file at the given path.

    Parameters:
        path (str): The path to the file to write to.
        text (str): The text to write to the file.
    """
    with open(path, "w", encoding="utf8") as f:
        f.write(text)


def read_from_file(path):
    """
    Read the contents of a file at the given path and return the text.

    Parameters:
        path (str): The path to the file to read from.

    Returns:
        str: The contents of the file at the given path.
    """
    return Path(path).read_text(encoding="utf8")


def write_to_yaml(path, data):
    """
    Write data to a YAML file at the given path.

    Parameters:
        path (str): The path to the YAML file to write to.
        data (dict): The data to write to the file.
    """
    with open(path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False)


def rms(data):
    """
    Calculate the root mean square (RMS) of the input data array.

    Parameters:
        data (array): The input array containing the data points.

    Returns:
        float: The root mean square value of the input data.
    """
    return np.sqrt(np.mean(np.square(data)))


def record_until_silence():
    """
    Records audio until silence is detected.

    This function records audio using the default microphone until silence is detected. It uses a callback function to continuously monitor the audio input and detects silence based on a threshold. The recorded audio is stored in a list of frames, which are concatenated and returned as a single numpy array.

    Returns:
        numpy.ndarray: The recorded audio data as a numpy array.

    """
    num_silent_samples = int(SILENCE_DURATION_SEC * SAMPLE_RATE)
    silent_samples_count = 0
    recording_started = False
    query_obtained = False
    recorded_frames = []

    # pylint: disable=unused-argument
    def callback(indata, frames, time, status):
        nonlocal silent_samples_count, recording_started, query_obtained

        current_rms = rms(indata[:, 0])
        # logging.debug(current_rms, silent_samples_count, recording_started)

        if current_rms > SILENCE_THRESHOLD:
            recording_started = True
            silent_samples_count = 0  # Reset counter if loudness is above threshold

        if recording_started:
            recorded_frames.append(indata.copy())

        if recording_started and current_rms <= SILENCE_THRESHOLD:
            silent_samples_count += len(indata)

        if recording_started and silent_samples_count > num_silent_samples:
            query_obtained = True

    # Use a stream with a callback in non-blocking mode
    with sd.InputStream(
        callback=callback, samplerate=SAMPLE_RATE, channels=1
    ) as stream:
        logging.info("Listening... ")
        while True:
            sd.sleep(100)
            if query_obtained:
                stream.stop()
                logging.info("... got it!")
                break

    voice_query = np.concatenate(recorded_frames, axis=0)

    if DEBUG:
        logging.debug("Playing back voice query to check clarity and volume...")
        sd.play(voice_query, SAMPLE_RATE)
        sd.wait()

    return voice_query


def transcribe(audio_data_floats):
    """
    Transcribes the given audio data using the OpenAI API.

    Args:
        audio_data (bytes): The audio data to be transcribed.

    Returns:
        str: The transcription result from the OpenAI API.
    """

    # convert the data from [-1.0,1.0] to [-32768, 32767] for 16 bit PCM
    audio_data = np.int16(audio_data_floats * 32767)

    # pylint: disable=no-member
    with wave.open(QUERY_FILE, "wb") as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(2)  # Sample width in bytes
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_data.tobytes())

    logging.debug("Sending voice query for transcription...")

    with open(QUERY_FILE, "rb") as query:
        response = openai_sync_client.audio.transcriptions.create(
            model=STT_MODEL, language=LANGUAGE, file=query
        )

    os.remove(QUERY_FILE)

    return response.text


def generate_story(query, prompt=""):
    """
    Generates a story stream based on a given query and prompt using the OpenAI API.

    Args:
        query (str): The query to generate the story stream from.
        prompt (str, optional): The prompt to use for generating the story stream. Defaults to an empty string.
        model (str, optional): The model to use for generating the story stream. Defaults to "gpt-3.5-turbo".
        max_tokens (int, optional): The maximum number of tokens in the generated story stream. Defaults to 1600.
        temperature (float, optional): The temperature parameter for generating the story stream. Defaults to 1.

    Returns:
        openai.api_resources.completion.Completion: The generated story stream.
    """

    return openai_async_client.chat.completions.create(
        stream=True,
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )


async def synthesize_audio(story_path, index, text=None):
    """
    Fetches TTS audio for a given paragraph of a story and saves it to a file.

    Args:
        story_path (Path): The path to the story directory.
        index (int): The index of the paragraph within the story.
        text (str): The text to synthesize.
    """
    audio_file_path = story_path / f"paragraph_{index}.{TTS_FORMAT}"

    if audio_file_path.exists():
        logging.debug("Paragraph %i audio already exists at %s", index, audio_file_path)
        return index, audio_file_path

    if not text:
        text_file_path = story_path / f"paragraph_{index}.txt"
        if text_file_path.exists():
            text = read_from_file(text_file_path)

    response = await openai_async_client.audio.speech.create(
        input=text, model=TTS_MODEL, voice=TTS_VOICE, response_format=TTS_FORMAT
    )

    logging.debug("Saving audio for paragraph %i...", index)
    response.write_to_file(audio_file_path)
    logging.debug("Paragraph %i audio saved at %s", index, audio_file_path)

    return index, audio_file_path


async def writer(queue, query=None):
    """Creates a story based on a voice query.

    If a textual query is given, it is used. If not, it records sound until silence,
    then transcribes the voice query.

    Then it uses a large generative language model to create a story based on the query,
    and sends each paragraph of the story to a TTS service to have them synthesized
    and saved into audio.

    The story is saved to a directory in the "stories" directory with a different folder
    for each story. If the story already exists, it will be read from disk and the
    audio segments will be played back without regenerating the story.
    """
    if not query:
        voice_query = record_until_silence()
        query = transcribe(voice_query)
        logging.info("Voice query: %s", query)

    logging.debug("Transcription of voice query: %s", query)

    if not query.lower().startswith(QUERY_GUARD):
        print(
            f"Sorry, I can only run queries that start with '{QUERY_GUARD}' and '{query}' does not"
        )
        await queue.put(None)  # Indicate that we're done
        return

    story_path = STORIES_HOME / query_to_filename(query)
    if IGNORE_CACHE or (
        not IGNORE_CACHE and not story_path.exists() and not story_path.is_dir()
    ):
        logging.debug("Creating story folder at %s", story_path)
        story_path.mkdir(parents=True, exist_ok=True)

        logging.debug("Writing model info to disk...")
        info = {
            'query': query,
            'language': LANGUAGE,
            'stt_model': STT_MODEL,
            'llm_model': LLM_MODEL,
            'llm_temperature': TEMPERATURE,
            'llm_max_tokens': MAX_TOKENS,
            'tts_model': TTS_MODEL,
            'tts_voice': TTS_VOICE,
        }
        write_to_yaml(story_path / "info.yaml", info)

        logging.debug("Reading prompt...")
        prompt = Path("prompt.txt").read_text(encoding="utf8")

        logging.debug("Creating story...")
        story_stream = await generate_story(query, prompt)

        index = 0
        paragraph = []

        logging.debug("Iterating over the story stream...")
        async for chunk in story_stream:
            fragment = chunk.choices[0].delta.content

            if fragment is None:
                break

            paragraph.append(fragment)

            if fragment.endswith("\n\n"):
                paragraph_str = "".join(paragraph)
                logging.info("Paragraph %i: %s", index, paragraph_str)
                write_to_file(story_path / f"paragraph_{index}.txt", paragraph_str)
                task = asyncio.create_task(
                    synthesize_audio(story_path, index, paragraph_str)
                )
                await queue.put(task)
                index += 1
                paragraph = []

        logging.debug("Finished processing the story stream.")
    else:
        logging.debug("Reading cached story at %s", story_path)
        for index in range(len(list(story_path.glob("paragraph_*.txt")))):
            logging.debug("Creating reading task for paragraph %i", index)
            task = asyncio.create_task(synthesize_audio(story_path, index))
            await queue.put(task)

    logging.debug("Done processing the story.")
    await queue.put(None)


async def reader(queue):
    """Reads audio segments from a queue and plays them back."""
    while True:
        task = await queue.get()
        if task is None:
            logging.debug("Got a none task, done reading the story.")
            break
        logging.debug("Obtained task %s", task)
        index, audio_file = await task

        logging.debug("Playing paragraph %i audio from %s", index, audio_file)
        audio_data, sampling_frequency = sf.read(audio_file)
        sd.play(audio_data, sampling_frequency)
        sd.wait()
        logging.debug("Done playing paragraph %i audio", index)


async def async_main(query):
    queue = asyncio.Queue()
    producer = asyncio.create_task(writer(queue, query))
    consumer = asyncio.create_task(reader(queue))
    await asyncio.gather(producer, consumer)


@click.command()
@click.option("--query", default=None, help="The story to tell.")
@click.option(
    "--silence-threshold",
    default=0.01,
    help="The silence threshold to use when generating stories. Defaults to 0.01.",
)
@click.option(
    "--silence-duration-sec",
    default=1,
    help="The silence duration to use when generating stories. Defaults to 1.",
)
@click.option(
    "--sample-rate",
    default=22050,
    help="The sample rate to use when generating stories. Defaults to 22050.",
)
@click.option(
    "--query-file",
    default="query.wav",
    help='The name of the file to write the query audio to. Defaults to "query.wav".',
)
@click.option(
    "--stories-home",
    default="./stories",
    help='The directory to store the generated stories in. Defaults to "./stories".',
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
    help='The temperature to use when generating stories. Defaults to 1.0.',
)
@click.option(
    "--max-tokens",
    type=int,
    default=1600,
    help='The maximum number of tokens to use when generating stories. Defaults to 1600.',
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
    "--max-file-length",
    default=255,
    help="The maximum length of a generated story file. Defaults to 255.",
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
# pylint: disable=too-many-arguments
def main(
    query,
    silence_threshold,
    silence_duration_sec,
    sample_rate,
    query_file,
    stories_home,
    stt_model,
    llm_model,
    temperature,
    max_tokens,
    tts_model,
    tts_voice,
    tts_format,
    language,
    max_file_length,
    query_guard,
    debug,
    ignore_cache,
):
    # pylint: disable=global-variable-undefined
    global SILENCE_THRESHOLD, SILENCE_DURATION_SEC, SAMPLE_RATE, QUERY_FILE, STORIES_HOME, STT_MODEL, LLM_MODEL, TEMPERATURE, MAX_TOKENS, TTS_MODEL, TTS_VOICE, TTS_FORMAT, LANGUAGE, MAX_FILE_LENGTH, QUERY_GUARD, IGNORE_CACHE, DEBUG

    SILENCE_THRESHOLD = silence_threshold
    SILENCE_DURATION_SEC = silence_duration_sec
    SAMPLE_RATE = sample_rate
    QUERY_FILE = query_file
    STT_MODEL = stt_model
    LLM_MODEL = llm_model
    TTS_MODEL = tts_model
    TEMPERATURE = temperature
    MAX_TOKENS = max_tokens
    TTS_VOICE = tts_voice
    TTS_FORMAT = tts_format
    LANGUAGE = language
    MAX_FILE_LENGTH = max_file_length
    QUERY_GUARD = query_guard
    IGNORE_CACHE = ignore_cache
    DEBUG = debug
    STORIES_HOME = Path(__file__).resolve().parent / stories_home

    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    asyncio.run(async_main(query))


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
