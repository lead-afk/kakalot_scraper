#!/bin/bash
# Initialization script
echo "Starting initialization..."
python -m venv .venv
source .venv/bin/activate.fish
pip install -r requirements.txt
echo "Initialization complete."