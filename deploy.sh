#!/bin/bash

# Install required packages
pip install -r requirements.txt

# Run the application with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
