#!/bin/bash

echo "Wait for a microphone to be available"
while ! arecord -l 2>&1 | grep -q 'card [0-9]'; do
    sleep 1
done
echo "Microphone is available"

echo "Activate Python virtual environment..."
source /home/fably/.venv/bin/activate

echo "Run Fably continously..."
cd /home/fably/fably
fably --loop