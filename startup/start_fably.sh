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

# Run Fably in a constant loop (using the default APIs)
fably --loop

# Use this command to talk to a local LLM model served by Ollama instead
# fably --loop --llm-url=http://mygpu.local:11434/v1
