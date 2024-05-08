#!/bin/bash

if ! command -v black &> /dev/null; then
    echo "Black is not installed. Installing Black..."
    pip install black
    if [ $? -ne 0 ]; then
        echo "Failed to install Black. Please check the errors above."
        exit 1
    fi
fi

echo "Formatting Python code..."
black fably tools
