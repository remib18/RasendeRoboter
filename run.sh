#!/bin/zsh

# Check if the venv directory exists

if [ ! -d ".venv" ]; then
  echo "The virtual environment does not exist. Please run setup.sh first."
  exit 1
fi

# Activate the virtual environment
source .venv/bin/activate

# Run the Python script
python game.py