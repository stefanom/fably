#!/bin/bash

# NOTE: this assumes running on a Raspberry Pi OS (64-bit) Lite with a 5.xx kernel
# This one is the image we're using as a starting point because it's the last with a 5.xx kernel
# the drivers for the reSpeaker HAT are NOT compatible with the 6.xx kernel series
# https://downloads.raspberrypi.com/raspios_full_arm64/images/raspios_full_arm64-2023-02-22/2023-02-21-raspios-bullseye-arm64-full.img.xz

# With this we freeze the kernel or apt will update it to the 6.xx series
#sudo apt-mark hold raspberrypi-kernel raspberrypi-kernel-headers

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

# If you get no errors, install the drivers then reboot
sudo ./install.sh
sudo reboot

# Test the speaker
aplay /usr/share/sounds/alsa/Front_Center.wav


# ----------- Phase 3 -------------

# Install the stuff we need for Fably
sudo apt install python3 python3-venv python3-pip python3-spidev python3-pyaudio python3-scipy -y
sudo apt install libportaudio2 libsndfile1 -y

# Clone Fably's source code
git clone https://github.com/stefanom/fably

# Create a python environment
if [ ! -d .venv ]; then
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

# Make Fably start automatically with the system
chmod +x .startup/start.sh
mkdir -p /home/fably/.config/systemd/user
sudo cp ./install/rpi/fably.service /home/fably/.config/systemd/user/fably.service
#systemctl --user enable pulseaudio
systemctl --user enable fably.service

# Personalize the startup message
sudo cp ./etc/motd /etc/motd
