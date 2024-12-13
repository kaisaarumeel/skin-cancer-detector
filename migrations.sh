#!/bin/bash

# activate venv 
echo "Activating virtual environment..."
source venv/bin/activate

# run database migrations
echo "Running database migrations..."
python3.11 server/manage.py makemigrations
python3.11 server/manage.py migrate
python3.11 server/manage.py migrate --database=db_images

# start server
echo "Starting Gunicorn server..."
exec "$@"