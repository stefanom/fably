#!/usr/bin/env python3
"""Interactive agent to test the quality of voice query capture."""

import time
import random
import os
import json
import queue

import click
import numpy as np
from pathlib import Path
from gpiozero import Button
from signal import pause
import sounddevice as sd
import soundfile as sf

from vosk import Model, KaldiRecognizer

sounds_dir = Path(__file__).resolve().parent / "../sounds"
model_file = Path(__file__).resolve().parent / "../models/vosk-model-small-en-us-0.15"

hello_sound = sounds_dir / "hi.wav"
prompt_sound = sounds_dir / "what_story.wav"
delete_sound = sounds_dir / "delete.wav"

button = Button(17, hold_time=3)

long_press_time = 1
hold_time = 3
press_time = -1

SAMPLERATE = 16000

recognizer = KaldiRecognizer(Model(str(model_file)), SAMPLERATE)

# sd.default.device = 1
# sd.default.latency = ('high', 'high')
# sd.default.blocksize = 1024


def sounddevice_play_sound(sound_file):
    data, fs = sf.read(sound_file, dtype="float32")
    sd.play(data, fs)
    sd.wait()


def alsa_play_sound(sound_file):
    os.system(f"aplay {sound_file}")


def play_sound(driver, sound_file):
    if driver == "sounddevice":
        sounddevice_play_sound(sound_file)
    else:
        alsa_play_sound(sound_file)


def vosk_record_sound(sound_file):
    recognition_queue = queue.Queue()
    recorded_frames = []

    def callback(indata, frames, time, status):
        recognition_queue.put(bytes(indata))
        recorded_frames.append(bytes(indata))

    with sd.RawInputStream(
        samplerate=SAMPLERATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        while True:
            data = recognition_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if result["text"]:
                    break

    npframes = [np.frombuffer(frame, dtype=np.int16) for frame in recorded_frames]
    audio_data = np.concatenate(npframes, axis=0)
    sf.write(sound_file, audio_data, SAMPLERATE)


def record_sound(driver, sound_file):
    vosk_record_sound(sound_file)


def pressed():
    global press_time
    press_time = time.time()
    # print("Pressed");


def released(driver):
    global press_time
    release_time = time.time()
    pressed_for = release_time - press_time
    # print(f"  released after {pressed_for:.2f} seconds")

    if pressed_for < long_press_time:
        print("This is a short press. Playing a random recording...")
        sound_files = [file for file in os.listdir(".") if file.endswith(".wav")]
        if sound_files:
            randomfile = random.choice(sound_files)
            play_sound(driver, randomfile)
        else:
            print("No sound files found. Record one by long pressing.")
    elif pressed_for < button.hold_time:
        print("This is a long press. Recording a sound...")
        play_sound(driver, prompt_sound)
        record_sound(driver, time.strftime("%d_%m_%Y-%H_%M_%S") + "_voice.wav")
        print("Finished recording.")


def held(driver):
    print("This is a hold press. Erasing all recorded sounds")
    play_sound(driver, delete_sound)
    os.system("rm *_voice.wav")


@click.command()
@click.option(
    "--driver", default="alsa", help="Playback audio driver: alsa or sounddevice"
)
def main(driver):
    button.when_pressed = pressed
    button.when_released = lambda: released(driver)
    button.when_held = lambda: held(driver)

    print(f"Button + audio via {driver} test:")
    print(" - Press shortly to play a random recording")
    print(" - Long press to record a sound")
    print(" - Hold to erase all recorded sounds")
    print("Press ctrl-c to exit")
    try:
        play_sound(driver, hello_sound)
        pause()
    except KeyboardInterrupt:
        print("Program terminated.")


if __name__ == "__main__":
    main()
