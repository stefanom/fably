#!/bin/bash

# Run check script
echo "Running check script..."
./check.sh
if [ $? -ne 0 ]; then
    echo "Check script failed, aborting."
    exit 1
fi

# Run format script
echo "Running format script..."
./format.sh
if [ $? -ne 0 ]; then
    echo "Format script failed, aborting."
    exit 1
fi

# Commit message handling
commit_message="$1"
if [ -z "$commit_message" ]; then
    read -p "Enter a commit message: " commit_message
    if [ -z "$commit_message" ]; then
        echo "No commit message provided, aborting."
        exit 1
    fi
fi

# # Add all changes to Git
# echo "Adding all changes to Git..."
# git add .
# if [ $? -ne 0 ]; then
#     echo "Failed to add files to Git."
#     exit 1
# fi

# Commit changes
echo "Committing changes..."
git commit -m "$commit_message"
if [ $? -ne 0 ]; then
    echo "Failed to commit. There might be nothing to commit."
    exit 1
fi

# Push changes to the upstream branch
echo "Pushing changes to the upstream..."
git push
if [ $? -ne 0 ]; then
    echo "Failed to push changes to upstream."
    exit 1
fi

echo "Operations completed successfully."
