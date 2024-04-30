#!/bin/bash

echo "Wait for SSH service to be fully up and running"
while ! systemctl is-active --quiet ssh; do
    sleep 1
done
echo "SSH service is running"

echo "Wait for the sound card to be available"
while ! aplay -l 2>&1 | grep -q 'card [0-9]'; do
    sleep 1
done
echo "Sound card is available"

echo "Play the startup sounds..."
aplay /home/fably/fably/sounds/startup.wav

#echo "Show the flashing LEDs..."
#python /home/fably/bin/start_leds.py

#source /home/fably/fably/.venv/bin/activate
#python /home/fably/fably/fably.py
