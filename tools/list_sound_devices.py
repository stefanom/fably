#!/usr/bin/env python3
"""List the available audio devices from sounddevice."""

import sounddevice as sd


def main():
    default_device_index = sd.default.device[0]

    print("Available audio devices:\n")
    for index, device in enumerate(sd.query_devices()):
        device_type = "input" if device["max_input_channels"] > 0 else "output"
        default = " (default input)" if index == default_device_index else ""
        print(f"{index}: {device['name']} - {device_type}{default}")


if __name__ == "__main__":
    main()
