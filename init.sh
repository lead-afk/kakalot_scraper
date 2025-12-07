#!/bin/bash
# Initialization script
echo "Starting initialization..."
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "Initialization complete."