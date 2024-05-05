#!/usr/bin/env python3

"""Show the the mic noise floor (in RMS energy) using sounddevice."""

import numpy as np
import sounddevice as sd

CHANNELS = 1              # Number of audio channels (mono)
RATE = 16000              # Sample rate
CHUNK = 8000              # Number of frames per buffer

# device_index = 1
# sd.default.device['input'] = device_index

def main():

    def rms(data):
        return np.sqrt(np.mean(np.square(data)))

    # pylint: disable=unused-argument
    def callback(in_data, frame_count, time_info, status):
        data = in_data[:, 0]
        energy = rms(data)
        print(f"RMS: {energy:.3f}")

    try:
        with sd.InputStream(callback=callback, samplerate=RATE, blocksize=CHUNK, channels=CHANNELS) as stream:
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("Terminated.")


if __name__ == "__main__":
    main()
