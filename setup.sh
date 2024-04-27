#!/bin/bash

sudo apt update
sudo apt upgrade -y
sudo apt install python3-venv python3-pip libportaudio2 libsndfile1 libbluetooth-dev alsa-utils bluez bluez-tools ffmpeg espeak -y

if [ ! -d .python ]; then
    python -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt
