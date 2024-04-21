@echo off
echo "Pull from github..."
git pull

echo "Installing requirements..."
pip install -r requirements.txt
