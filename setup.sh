#!/bin/bash

sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip libportaudio2 libsndfile1 libbluetooth-dev -y

if [ ! -d .python ]; then
    python -m venv .python
fi

.python/bin/pip install -r requirements.txt
.python/bin/pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez
