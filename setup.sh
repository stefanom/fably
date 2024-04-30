#!/bin/bash

# NOTE: this assumes running on a Raspberry Pi OS (64-bit) Lite

# ----------- Phase 1 -------------

# Update the system to the latest packages and reboot because the Linux kernel might have changed
sudo apt update
sudo apt upgrade -y
sudo reboot


# ----------- Phase 2 -------------

# Download the reSpeaker HAT drivers source code
sudo apt install git -y
git config --global init.defaultBranch main
git clone https://github.com/HinTak/seeed-voicecard
cd seeed-voicecard

# Move to the right branch for the current kernel version
uname_r=$(uname -r)
version=$(echo "$uname_r" | sed 's/\([0-9]*\.[0-9]*\).*/\1/')
git checkout v$version

# Compilie the drivers to make sure everything works
make

# If we get no errors, install the drivers then reboot
sudo ./install.sh
sudo reboot

# Test the speaker to make sure everything worked
aplay /usr/share/sounds/alsa/Front_Center.wav


# ----------- Phase 3 -------------

# Install the stuff we need for Fably
sudo apt install --yes \
    libportaudio2 \
    libsndfile1 \
    python3-venv \
    python3-pip \
    python3-scipy \
    python3-numpy \
    python3-soundfile \
    python3-pydub \
    python3-click \
    python3-dotenv \
    python3-yaml \
    python3-pyaudio \
    python3-rpi.gpio


# Create a python user environment
python -m venv --system-site-packages .venv
source .venv/bin/activate

# Clone Fably's source code
git clone https://github.com/stefanom/fably
cd fably

# Install python dependencies
pip install -r requirements.txt

# Make Fably start automatically with the system
chmod +x ./startup/start.sh
sudo cp ./install/rpi/fably.service /etc/systemd/system/fably.service
sudo systemctl enable fably.service

# Personalize the shell startup message
sudo cp ./install/rpi/motd /etc/motd

# Reboot and hear a sound
sudo reboot


# ----------- Phase 4 -------------
