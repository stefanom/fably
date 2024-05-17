#!/usr/bin/env python3
"""Test that bottoms, playing sounds and LEDs work together properly and concurrently."""

import threading

try:
    from apa102_pi.colorschemes import colorschemes
except ImportError:
    colorschemes = None

try:
    from gpiozero import Button
except ImportError:
    Button = None

from fably import utils


NUM_LED = 3
GPIO_PIN = 17
CYCLES = 4
BRIGHTNESS = 15


def play_sound():
    utils.play_sound("hi")


def flash_leds():
    if colorschemes:
        my_cycle = colorschemes.TheaterChase(
            num_led=NUM_LED,
            pause_value=0.03,
            num_steps_per_cycle=35,
            num_cycles=CYCLES,
            order="rgb",
            global_brightness=BRIGHTNESS,
        )
        my_cycle.start()


def button_pressed():
    # Start playing sound in a separate thread
    sound_thread = threading.Thread(target=play_sound)
    sound_thread.start()

    # Start flashing LEDs in a separate thread
    led_thread = threading.Thread(target=flash_leds)
    led_thread.start()


def main():
    try:
        button = Button(GPIO_PIN)
        button.when_pressed = button_pressed
    except Exception:  # pylint: disable=W0703
        print("GPIO pin not found. Can't run this test.")
        return

    try:
        print("Press the button on the sound card to play a sound and flash the LEDs.")
        input("Press Enter to terminate the program...\n")
    except KeyboardInterrupt:
        print("Program terminated.")


if __name__ == "__main__":
    main()
