#!/usr/bin/env python3
"""List the available audio devices from sounddevice."""

import sounddevice as sd

def list_audio_devices():
    devices = sd.query_devices()
    default_device_index = sd.default.device['input']
    print("Available audio devices:\n")
    for index, device in enumerate(devices):
        device_type = "input" if device['max_input_channels'] > 0 else "output"
        default = " (default input)" if index == default_device_index else ""
        print(f"{index}: {device['name']} - {device_type}{default}")

list_audio_devices()
