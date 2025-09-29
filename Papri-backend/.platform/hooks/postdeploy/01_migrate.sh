#!/bin/bash

# Activate the virtual environment
source /var/app/venv/staging-LQM1lest/bin/activate

# Change to the app directory
cd /var/app/staging

# Run database migrations
python manage.py migrate --noinput
