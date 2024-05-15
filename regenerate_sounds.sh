#!/bin/bash

# Function to check if a command is available in PATH
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if ffmpeg is installed
if ! command_exists ffmpeg; then
    echo "ffmpeg is needed by not installed. Installing..."
    sudo apt update
    sudo apt install -y ffmpeg
    echo "ffmpeg has been installed."
fi

# ------------------ startup --------------

# Download the startup file from the internet
curl -o original_startup.mp3 https://cdn.pixabay.com/audio/2022/01/18/audio_73d436bff1.mp3

# This converts it to wav and cuts to the first 2 seconds
ffmpeg -i original_startup.mp3 -filter:a "afade=t=out:st=1:d=1" -t 2 original_startup.wav
rm original_startup.mp3

# This creates a 1 second fade out at the end
ffmpeg -i original_startup.wav -filter:a "asetrate=24000*2/3,aresample=24000" startup.wav
rm original_startup.wav

# ------------------ voices -------------------

VOICE="nova"
TTS="../../tools/tts.py"
DEST="./fably/sounds"

python $TTS --voice $VOICE "Hi! I'm Fably!" $DEST/hi_short.wav
python $TTS --voice $VOICE "Hi, I'm Fably! I'm your storytelling companion!" $DEST/hi.wav
python $TTT --voice $VOICE "Press the button and tell me what story you'd like me to tell you." $DEST/instructions.wav
python $TTS --voice $VOICE "Sorry! I'm afraid I can't do that." $DEST/sorry.wav
python $TTS --voice $VOICE "I'm deleting all of the saved files." $DEST/delete.wav
python $TTS --voice $VOICE "Hmmm. Something went wrong. Do you want to try again?" $DEST/wrong.wav
python $TTS --voice $VOICE "Bye! Come back soon!" $DEST/bye.wav
