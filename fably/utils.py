"""
Shared utility functions.
"""

import os
import re
import logging
import json
import time
import colorsys
import zipfile
import queue

from pathlib import Path

import yaml
import numpy as np
import requests
import sounddevice as sd
import soundfile as sf

from vosk import Model, KaldiRecognizer


MAX_FILE_LENGTH = 255
SOUNDS_PATH = "sounds"
QUERY_SAMPLE_RATE = 16000


def rotate_rgb_color(rgb_value, step_size=1):
    """
    Rotate an RGB color by a given step size (in degrees).

    The function takes an RGB value as input (in the format 0xRRGGBB), and
    returns a new RGB value that is a rotation of the original color by the
    given step size.

    The step size is expected to be given in degrees. The function will
    convert the step size to radians and then use it to rotate the color in
    the HSV color space. The resulting RGB color is then converted back to
    the RGB color space.
    """

    # Convert RGB value to normalized RGB components (0.0 to 1.0)
    r = ((rgb_value >> 16) & 0xFF) / 255.0
    g = ((rgb_value >> 8) & 0xFF) / 255.0
    b = (rgb_value & 0xFF) / 255.0

    # Convert RGB to HSV (Hue, Saturation, Value)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Rotate the hue component
    h = (h + (step_size / 360.0)) % 1.0  # Increment hue by step_size (in degrees)

    # Convert HSV back to RGB
    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)

    # Convert RGB components (0.0 to 1.0) back to integer RGB value
    new_rgb_value = int(r_new * 255) << 16 | int(g_new * 255) << 8 | int(b_new * 255)

    return new_rgb_value


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

    if path.is_absolute():
        absolute_path = path
    else:
        # Resolve relative path relative to the directory of the current file
        current_file_path = Path(__file__).resolve().parent
        absolute_path = current_file_path / path

    if not absolute_path.exists():
        try:
            absolute_path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(f"Cannot write to directory: {absolute_path}") from e
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

        # Download the model
        with requests.get(model_url, stream=True, timeout=10) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Unzip the model
        print("Unzipping the model...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(model_dir.parent)

        # Remove the zip file after extraction
        os.remove(zip_path)
        logging.debug("Model %s downloaded and unpacked in %s", model_name, model_dir)

    model = Model(str(model_dir))
    return KaldiRecognizer(
        model, QUERY_SAMPLE_RATE
    )  # The sample rate is fixed in the model


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
        if audio_file.suffix == ".mp3":
            os.system(f"mpg123 {audio_file}")
        else:
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

    # Remove the period at the end if it exists
    if query.endswith("."):
        query = query[:-1]

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


async def transcribe(
    ai,
    audio_data,
    sample_rate=QUERY_SAMPLE_RATE,
    audio_path=None,
):
    """
    Transcribes the given audio data using the OpenAI API.
    """

    file_name = time.strftime("%d_%m_%Y-%H_%M_%S") + ".wav"

    if not audio_path:
        audio_file = Path(file_name)
    else:
        audio_path = audio_path if isinstance(audio_path, Path) else Path(audio_path)
        if audio_path.is_dir():
            audio_file = audio_path / file_name
        else:
            audio_file = audio_path
    write_audio_data_to_file(audio_data, audio_file, sample_rate)

    logging.debug("Sending voice query for transcription...")
    text = await ai.transcriptions(audio_file)
    return text, audio_file
