#!/usr/bin/env python3

import subprocess
import threading
from pathlib import Path

import wave
import pyaudio
import sounddevice as sd
import soundfile as sf
from apa102_pi.colorschemes import colorschemes
from gpiozero import Button

NUM_LED = 3
BRIGHTNESS = 15
GPIO_PIN = 17
SOUND = Path(__file__).resolve().parent / "../sounds/hi.wav"

def play_sound_aplay():
    """Function to play sound using aplay."""
    subprocess.run(['aplay', SOUND])

def play_sound_pyaudio():
    """Function to play sound using pyaudio."""
    wf = wave.open(str(SOUND), 'rb') # Load audio file
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data in chunks
    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()

def play_sound_sounddevice():
    """Function to play sound using sounddevice."""
    data, fs = sf.read(SOUND, dtype='float32')  # Load audio file
    sd.play(data, fs)
    sd.wait()  # Wait until file is completely played

def play_sound():
    play_sound_sounddevice()
    play_sound_pyaudio()
    play_sound_aplay()

def flash_leds():
    """Function to control LED flashing."""
    my_cycle = colorschemes.TheaterChase(
        num_led=NUM_LED,
        pause_value=0.03,
        num_steps_per_cycle=35,
        num_cycles=2,
        order="rgb",
        global_brightness=BRIGHTNESS,
    )
    my_cycle.start()

def button_pressed():
    """Function to handle button press."""
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
        input("Press Enter to terminate the program...\n")
    except KeyboardInterrupt:
        print("Program terminated.")

if __name__ == "__main__":
    main()
