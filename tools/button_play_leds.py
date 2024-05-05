#!/usr/bin/env python3
"""Test that bottoms, playing sounds and LEDs work together properly and concurrently."""

import os
import threading
from pathlib import Path

from apa102_pi.colorschemes import colorschemes
from gpiozero import Button

NUM_LED = 3
GPIO_PIN = 17
CYCLES = 4
BRIGHTNESS = 15

SOUND = Path(__file__).resolve().parent / "../sounds/hi.wav"

def play_sound():
    os.system(f"aplay {SOUND}")

def flash_leds():
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
    button = Button(GPIO_PIN)
    button.when_pressed = button_pressed

    try:
        print("Press the button on the sound card to play a sound and flash the LEDs.")
        input("Press Enter to terminate the program...\n")
    except KeyboardInterrupt:
        print("Program terminated.")

if __name__ == "__main__":
    main()
