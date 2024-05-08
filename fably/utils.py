"""
Shared utility functions.
"""

import os
import re
import logging
import subprocess
import queue
import json
import time

from pathlib import Path

import yaml
import numpy as np
import openai
import sounddevice as sd
import soundfile as sf

from vosk import Model, KaldiRecognizer


MAX_FILE_LENGTH = 255
SOUNDS_PATH = "sounds"
QUERY_SAMPLE_RATE = 16000


def resolve(path):
    """
    Resolve a path to an absolute path, creating any necessary parent
    directories.

    If the given path is already absolute, it is returned as is. If it is
    relative, it is resolved relative to the directory of the current file.

    If the resolved path points to a directory, it is created if it does not
    exist.
    """
    path = Path(path)
    absolute_path = (
        absolute_path if path.is_absolute() else Path(__file__).resolve().parent / path
    )
    if absolute_path.is_dir():
        absolute_path.mkdir(parents=True, exist_ok=True)
    return absolute_path


def get_speech_recognizer(models_path, model_name):
    """
    Return a speech recognizer instance using the given model.

    The model is downloaded if not already available.
    """
    model_dir = Path(models_path) / Path(model_name)

    if not model_dir.exists():
        zip_path = model_dir.with_suffix(".zip")
        model_url = f"https://alphacephei.com/vosk/models/{model_name}.zip"

        logging.debug("Downloading the model from %s...", model_url)
        subprocess.run(["curl", "-o", str(zip_path), model_url], check=True)

        # Unzip the model
        print("Unzipping the model...")
        subprocess.run(["unzip", "-o", str(zip_path), "-d", str(model_dir)], check=True)

        # Remove the zip file after extraction
        os.remove(zip_path)
        logging.debug("Model %s downloaded and unpacked in %s", model_name, model_dir)

    model = Model(str(model_dir))
    return KaldiRecognizer(
        model, QUERY_SAMPLE_RATE
    )  # The sample rate is fixed in the model


def get_openai_clients():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key is None:
        raise ValueError(
            "OPENAI_API_KEY environment variable not set or .env file not found."
        )
    sync_client = openai.Client(api_key=openai_api_key)
    async_client = openai.AsyncClient(api_key=openai_api_key)
    return sync_client, async_client


def write_audio_data_to_file(audio_data, audio_file, sample_rate):
    """Write audio data to a file with the given sample rate."""
    sf.write(audio_file, audio_data, sample_rate)


def play_sound(sound, audio_driver="alsa"):
    """
    Return the path of the sound file with the given name.
    """
    sound_file = Path(__file__).resolve().parent / SOUNDS_PATH / f"{sound}.wav"
    if not sound_file.exists():
        raise ValueError(f"Sound {sound} not found in path {sound_file}.")
    play_audio_file(sound_file, audio_driver)


def play_audio_file(audio_file, audio_driver="alsa"):
    """
    Play the given audio file using the configured sound driver.
    """
    logging.debug("Playing audio from %s with %s", audio_file, audio_driver)
    if audio_driver == "sounddevice":
        audio_data, sampling_frequency = sf.read(audio_file)
        sd.play(audio_data, sampling_frequency)
        sd.wait()
    elif audio_driver == "alsa":
        os.system(f"aplay {audio_file}")
    else:
        raise ValueError(f"Unsupported audio driver: {audio_driver}")
    logging.debug("Done playing %s with %s", audio_file, audio_driver)


def query_to_filename(query, prefix):
    """
    Convert a query from a voice assistant into a file name that can be used to save the story.

    This function removes the query guard part and removes any illegal characters from the file name.
    """
    # Remove the query guard part since it doesn't add any information
    query = query.lower().replace(prefix, "", 1).strip()

    # Replace illegal file name characters with underscores and truncate
    return re.sub(r'[\\/*?:"<>| ]', "_", query)[:MAX_FILE_LENGTH]


def write_to_file(path, text):
    """
    Write the given text to a file at the given path.
    """
    with open(path, "w", encoding="utf8") as f:
        f.write(text)


def read_from_file(path):
    """
    Read the contents of a file at the given path and return the text.
    """
    return Path(path).read_text(encoding="utf8")


def write_to_yaml(path, data):
    """
    Write data to a YAML file at the given path.
    """
    with open(path, "w", encoding="utf-8") as file:
        yaml.dump(data, file, default_flow_style=False)


def record_until_silence(
    recognizer, trim_first_frame=False, sample_rate=QUERY_SAMPLE_RATE
):
    """
    Records audio until silence is detected.
    This uses a tiny speech recognizer (vosk) to detect silence.

    Returns an nparray of int16 samples.

    NOTE: There are probably less overkill ways to do this but this works well enough for now.
    """
    query = []
    recorded_frames = []
    recognition_queue = queue.Queue()

    def callback(indata, frames, _time, _status):
        """This function is called for each audio block from the microphone"""
        logging.debug("Recorded audio frame with %i samples", frames)
        recognition_queue.put(bytes(indata))
        recorded_frames.append(bytes(indata))

    with sd.RawInputStream(
        samplerate=sample_rate,
        blocksize=sample_rate // 4,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        logging.debug("Recording voice query...")

        while True:
            data = recognition_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if result["text"]:
                    query.append(result["text"])
                    break

        final_result = json.loads(recognizer.FinalResult())
        query.append(final_result["text"])

    npframes = [np.frombuffer(frame, dtype=np.int16) for frame in recorded_frames]

    if trim_first_frame:
        npframes = npframes.pop(0)

    return np.concatenate(npframes, axis=0), sample_rate, " ".join(query)


def transcribe(
    sync_client,
    audio_data,
    stt_model="whisper-1",
    language="en",
    sample_rate=QUERY_SAMPLE_RATE,
    audio_file=None,
):
    """
    Transcribes the given audio data using the OpenAI API.
    """

    if not audio_file:
        audio_file = time.strftime("%d_%m_%Y-%H_%M_%S") + ".wav"
    write_audio_data_to_file(audio_data, audio_file, sample_rate)

    logging.debug("Sending voice query for transcription...")

    with open(audio_file, "rb") as query:
        response = sync_client.audio.transcriptions.create(
            model=stt_model, language=language, file=query
        )

    return response.text, audio_file
