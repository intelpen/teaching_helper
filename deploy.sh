#!/bin/bash

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install -r requirements.txt

# Run the app
streamlit run frontend/main.py --server.port 8501 --server.address 0.0.0.0
