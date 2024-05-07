#!/bin/bash

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

python ../tools/tts.py --voice $VOICE "Hi! I'm Fably!" hi_short.wav
python ../tools/tts.py --voice $VOICE "Hi, I'm Fably! I'm your storytelling companion!" hi.wav
python ../tools/tts.py --voice $VOICE "Sorry! I'm afraid I can't do that." sorry.wav
python ../tools/tts.py --voice $VOICE "Hmmm. Something went wrong. Do you want to try again?" wrong.wav
