#!/usr/bin/env python3
"""Concatenate audio files in a directory into a single audio file."""

import os

import click
from pydub import AudioSegment

FORMAT = "mp3"


@click.command()
@click.option(
    "--folder",
    "-f",
    type=click.Path(exists=True),
    help="Root folder to start searching for MP3 files.",
)
def main(folder):
    # Walk through all directories and subdirectories starting from the root folder
    for root, _, files in os.walk(folder):
        # Prepare the path for the output file
        output_path = os.path.join(root, f"story.{FORMAT}")

        # Skip concatenation if 'story.mp3' already exists
        if os.path.exists(output_path):
            click.echo(f"Skipping concatenation, {output_path} already exists.")
            continue

        # Filter and sort audio files
        audio_files = [f for f in sorted(files) if f.endswith(f".{FORMAT}")]
        if not audio_files:
            continue  # Skip if no MP3 files found in the current directory

        # Create an empty AudioSegment object
        combined = AudioSegment.silent(duration=0)

        # Loop through sorted files and append each to the combined audio
        for filename in audio_files:
            filepath = os.path.join(root, filename)
            audio = AudioSegment.from_mp3(filepath)
            combined += audio
            click.echo(f"Appended {filename} in {root}")

        # Export the combined audio to a new file named 'story.mp3'
        combined.export(output_path, format=FORMAT)
        click.echo(f"Combined audio files saved as {output_path}")


if __name__ == "__main__":
    main()
