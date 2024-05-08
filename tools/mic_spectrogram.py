#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""

import math
import shutil

import numpy as np
import sounddevice as sd
import click


# Try to get terminal size or default to 80
try:
    COLUMNS, _ = shutil.get_terminal_size()
except AttributeError:
    COLUMNS = 80


@click.command()
@click.option(
    "-l", "--list-devices", is_flag=True, help="Show list of audio devices and exit"
)
@click.option(
    "-b",
    "--block-duration",
    default=50,
    type=float,
    help="Block size (default 50 milliseconds)",
)
@click.option("-c", "--columns", default=COLUMNS, type=int, help="Width of spectrogram")
@click.option("-d", "--device", type=str, help="Input device (numeric ID or substring)")
@click.option(
    "-g", "--gain", default=10, type=float, help="Initial gain factor (default 10)"
)
@click.option(
    "-r",
    "--frequency-range",
    nargs=2,
    type=float,
    default=[100, 2000],
    help="Frequency range (default 100 2000 Hz)",
)
def main(list_devices, block_duration, columns, device, gain, frequency_range):
    """Main function to handle spectrogram display."""
    if list_devices:
        print(sd.query_devices())
        return

    # ANSI color and character gradients for output
    colors = 30, 34, 35, 91, 93, 97
    chars = " :%#\t#%:"
    gradient = []
    for bg, fg in zip(colors, colors[1:]):
        for char in chars:
            if char == "\t":
                bg, fg = fg, bg
            else:
                gradient.append(f"\x1b[{fg};{bg + 10}m{char}")

    low, high = frequency_range
    if high <= low:
        raise click.BadParameter("HIGH must be greater than LOW")

    samplerate = sd.query_devices(device, "input")["default_samplerate"]
    print(f"Listening to device {device} with {samplerate}...")

    delta_f = (high - low) / (columns - 1)
    fftsize = math.ceil(samplerate / delta_f)
    low_bin = math.floor(low / delta_f)

    def callback(indata, _frames, _time, status):
        if status:
            text = " " + str(status) + " "
            print("\x1b[34;40m", text.center(columns, "#"), "\x1b[0m", sep="")

        if any(indata):
            magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
            magnitude *= gain / fftsize
            line = (
                gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))]
                for x in magnitude[low_bin : low_bin + columns]
            )
            print(*line, sep="", end="\x1b[0m\n")
        else:
            print("no input")

    with sd.InputStream(
        device=device,
        channels=1,
        callback=callback,
        blocksize=int(samplerate * block_duration / 1000),
        samplerate=samplerate,
    ):
        while True:
            response = click.prompt(
                "", prompt_suffix="", show_default=False, default=""
            ).strip()
            if response in ("", "q", "Q"):
                break
            for ch in response:
                if ch == "+":
                    gain *= 2
                elif ch == "-":
                    gain /= 2
                else:
                    print(
                        "\x1b[31;40m",
                        " press <enter> to quit, +<enter> or -<enter> to change scaling ".center(
                            columns, "#"
                        ),
                        "\x1b[0m",
                        sep="",
                    )


if __name__ == "__main__":
    main()
