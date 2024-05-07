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
import sounddevice as sd
import soundfile as sf
from vosk import Model, KaldiRecognizer


MAX_FILE_LENGTH = 255


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
    absolute_path = absolute_path if path.is_absolute() else Path(__file__).resolve().parent / path
    if absolute_path.is_dir():
        absolute_path.mkdir(parents=True, exist_ok=True)
    return absolute_path


def get_speech_recognizer(models_path, model_name, samplerate=16000):
    """
    Return a speech recognizer instance using the given model.

    The model is downloaded if not already available.
    """
    model_dir = Path(models_path) / Path(model_name)

    if not model_dir.exists():
        zip_path = model_dir.with_suffix('.zip')
        model_url = f'https://alphacephei.com/vosk/models/{model_name}.zip'

        logging.debug("Downloading the model from %s...", model_url)
        subprocess.run(['curl', '-o', str(zip_path), model_url], check=True)
        
        # Unzip the model
        print("Unzipping the model...")
        subprocess.run(['unzip', '-o', str(zip_path), '-d', str(model_dir)], check=True)
        
        # Remove the zip file after extraction
        os.remove(zip_path)
        logging.debug(f"Model {model_name} downloaded and unpacked in {model_dir}")

    model = Model(model_dir)
    return KaldiRecognizer(model, samplerate)


def play_audio_file(ctx, audio_file):
    """
    Play the given audio file using the configured sound driver.
    """
    logging.debug("Playing audio from %s with %s", audio_file, ctx.driver)
    if ctx.sound_driver == "sounddevice":
        audio_data, sampling_frequency = sf.read(audio_file)
        sd.play(audio_data, sampling_frequency)
        sd.wait()
    elif ctx.sound_driver == "alsa":
        os.system(f"aplay {audio_file}")
    else:
        raise ValueError(f"Unsupported audio driver: {ctx.sound_driver}")
    logging.debug("Done playing %s with %s", audio_file, ctx.driver)


def query_to_filename(ctx, query):
    """
    Convert a query from a voice assistant into a file name that can be used to save the story.

    This function removes the query guard part and removes any illegal characters from the file name.
    """
    # Remove the query guard part since it doesn't add any information
    query = query.lower().replace(ctx.query_guard, "", 1).strip()

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


def record_until_silence(ctx):
    """
    Records audio until silence is detected.
    This uses a tiny speech recognizer to detect silence.

    Returns an nparray of int16 samples.

    NOTE: There are probably much less overkill ways to do this but this works well enough for now.
    """
    query = []
    recorded_frames = []
    recognition_queue = queue.Queue()

    def callback(indata, frames, time, status):
        """ This function is called for each audio block from the microphone """
        recognition_queue.put(bytes(indata))
        recorded_frames.append(bytes(indata))

    """ Listens to the microphone until silence is detected after speech """
    with sd.RawInputStream(samplerate=ctx.sample_rate, blocksize=ctx.sample_rate // 4, dtype='int16', channels=1, callback=callback):
        logging.debug("Recording voice query...")

        while True:
            data = recognition_queue.get()
            if ctx.recognizer.AcceptWaveform(data):
                result = json.loads(ctx.recognizer.Result())
                if result['text']:
                    query.append(result['text'])
                    break

        final_result = json.loads(ctx.recognizer.FinalResult())
        query.append(final_result['text'])

    npframes = [np.frombuffer(frame, dtype=np.int16) for frame in recorded_frames]

    if ctx.remove_first_recorded_frame:
        npframes = npframes.pop(0)

    return np.concatenate(npframes, axis=0), " ".join(query)


def transcribe(ctx, audio_data):
    """
    Transcribes the given audio data using the OpenAI API.
    """

    query_file = time.strftime("%d_%m_%Y-%H_%M_%S") + "_query.wav"
    sf.write(query_file, audio_data, ctx.sample_rate)

    logging.debug("Sending voice query for transcription...")

    with open(query_file, "rb") as query:
        response = ctx.sync_client.audio.transcriptions.create(
            model=ctx.stt_model, language=ctx.language, file=query
        )

    return response.text, query_file
