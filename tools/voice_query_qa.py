#!/usr/bin/env python3
"""Interactive agent to test the quality of voice query capture."""

import time
import random
import os

import click

try:
    from gpiozero import Button
except ImportError:
    Button = None


from fably import utils
from fably.cli_utils import pass_context

BUTTON_GPIO_PIN = 17
LONG_PRESS_TIME = 1
HOLD_TIME = 3


def pressed(ctx):
    ctx.press_time = time.time()
    print("Pressed")


def released(ctx):
    release_time = time.time()
    pressed_for = release_time - ctx.press_time
    print(f"  released after {pressed_for:.2f} seconds")

    if pressed_for < ctx.long_press_time:
        print("This is a short press. Playing a random recording...")
        sound_files = [file for file in os.listdir(".") if file.endswith(".wav")]
        if sound_files:
            randomfile = random.choice(sound_files)
            utils.play_audio_file(randomfile, ctx.sound_driver)
        else:
            print("No sound files found. Record one by long pressing.")
    elif pressed_for < ctx.button.hold_time:
        print("This is a long press. Recording a sound...")
        utils.play_sound("what_story", audio_driver=ctx.sound_driver)
        audio_data, sample_rate, _ = utils.record_until_silence(ctx.recognizer)
        audio_file = time.strftime("%d_%m_%Y-%H_%M_%S") + "_voice.wav"
        utils.write_audio_data_to_file(audio_data, audio_file, sample_rate)
        print("Finished recording.")


def held(ctx):
    print("This is a hold press. Erasing all recorded sounds")
    utils.play_sound("delete", audio_driver=ctx.sound_driver)
    os.system("rm *_voice.wav")


@click.command()
@click.option(
    "--sound-driver",
    type=click.Choice(["alsa", "sounddevice"], case_sensitive=False),
    default="alsa",
    help="Which driver to use to emit sound.",
)
@pass_context
def main(ctx, sound_driver):
    if Button is None:
        print("This script requires GPIO buttons to be available.")
        return

    ctx.sound_driver = sound_driver

    sound_model = "vosk-model-small-en-us-0.15"
    ctx.sample_rate = 16000
    ctx.recognizer = utils.get_speech_recognizer(utils.resolve("models"), sound_model)

    try:
        button = Button(BUTTON_GPIO_PIN, hold_time=HOLD_TIME)

        button.when_pressed = lambda: pressed(ctx)
        button.when_released = lambda: released(ctx)
        button.when_held = lambda: held(ctx)
    except Exception:  # pylint: disable=W0703
        print("GPIO pin not found. Can't run this test.")
        return

    ctx.button = button
    ctx.pressed_time = -1
    ctx.long_press_time = LONG_PRESS_TIME

    print(f"Button + audio via {sound_driver} test:")
    print(" - Press shortly to play a random recording")
    print(" - Long press to record a sound")
    print(" - Hold to erase all recorded sounds")
    print("Press ctrl-c to exit")

    try:
        utils.play_sound("hi", audio_driver=ctx.sound_driver)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated.")


if __name__ == "__main__":
    main()
