#!/bin/bash

# Check if pylint is installed, if not install it
if ! command -v pylint &> /dev/null ; then
    echo "pylint could not be found, installing..."
    pip install pylint
    if [ $? -ne 0 ]; then
        echo "Failed to install pylint."
        exit 1
    fi
    echo "pylint installed successfully."
fi

echo "Running pylint..."
pylint fably tools/*.py servers/stt_server/*.py servers/tts_server/*.py 
