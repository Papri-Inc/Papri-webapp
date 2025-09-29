#!/bin/bash

# This script runs after the application has been deployed and migrations have been run.
# It starts the Celery worker and beat processes.

# Activate the virtual environment
source /var/app/venv/staging-LQM1lest/bin/activate

# Navigate to the application's directory
cd /var/app/staging

echo "Starting Celery services..."

# Check if a process for the worker is running and kill it before starting a new one
if pgrep -f "celery -A applaude_api worker"; then
    echo "Stopping existing Celery worker."
    pkill -f "celery -A applaude_api worker"
fi

# Check if a process for the beat is running and kill it before starting a new one
if pgrep -f "celery -A applaude_api beat"; then
    echo "Stopping existing Celery beat."
    pkill -f "celery -A applaude_api beat"
fi

# Start Celery worker in the background
# Logs will be written to /var/log/celery_worker.log
nohup celery -A applaude_api worker -l info > /var/log/celery_worker.log 2>&1 &
echo "Celery worker started."

# Start Celery beat in the background for scheduled tasks
# Logs will be written to /var/log/celery_beat.log
nohup celery -A applaude_api beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler > /var/log/celery_beat.log 2>&1 &
echo "Celery beat started."
