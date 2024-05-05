import os
import json
import queue

import sounddevice as sd
import soundfile as sf
import numpy as np

from vosk import Model, KaldiRecognizer

query_file = "query.wav"
blocksize = 8000
samplerate = 16000


def listen_to_query():
    # Load Vosk model for speech recognition
    model = Model("vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, samplerate)

    # Buffer to hold audio from microphone
    recognition_queue = queue.Queue()

    query = []
    recorded_frames = []

    def callback(indata, frames, time, status):
        """ This function is called for each audio block from the microphone """
        recognition_queue.put(bytes(indata))
        recorded_frames.append(bytes(indata))

    """ Listens to the microphone until silence is detected after speech """
    with sd.RawInputStream(samplerate=samplerate, blocksize=blocksize, dtype='int16', channels=1, callback=callback):
        print("Listening...")

        while True:
            data = recognition_queue.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if result['text']:
                    query.append(result['text'])
                    break

        final_result = json.loads(rec.FinalResult())
        query.append(final_result['text'])

    npframes = [np.frombuffer(frame, dtype=np.int16) for frame in recorded_frames]
    audio_data = np.concatenate(npframes[1:], axis=0)
    sf.write(query_file, audio_data, samplerate)

    data, fs = sf.read(query_file, dtype="float32")
    sd.play(data, fs)
    sd.wait()

    os.system(f"aplay {query_file}")

    return " ".join(query)

# Example usage: invoke listen_to_query function with a timeout or external trigger
print(listen_to_query())
