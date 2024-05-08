#!/usr/bin/env python3
"""Show the the mic noise floor (in RMS energy) using sounddevice."""

import numpy as np
import sounddevice as sd

CHANNELS = 1  # Number of audio channels (mono)
RATE = 16000  # Sample rate
CHUNK = RATE // 4  # Number of frames per buffer


def main():

    def rms(data):
        return np.sqrt(np.mean(np.square(data)))

    def callback(in_data, _frame_count, _time_info, _status):
        data = in_data[:, 0]
        energy = rms(data)
        print(f"RMS: {energy:.3f}")

    try:
        with sd.InputStream(
            callback=callback, samplerate=RATE, blocksize=CHUNK, channels=CHANNELS
        ):
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("Terminated.")


if __name__ == "__main__":
    main()
