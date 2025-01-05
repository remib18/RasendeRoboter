#!/bin/zsh

# Check if Homebrew is installed
if test ! $(which brew); then
  echo "Homebrew is not installed. Please install Homebrew first."
  exit 1
fi

# Update Homebrew
brew update

# Install Homebrew packages
brew install virtualenv

# Create a virtual environment
virtualenv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install Python packages
pip install -r requirements.txt