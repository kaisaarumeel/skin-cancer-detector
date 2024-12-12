#!/bin/bash

# run database migrations
echo "Running database migrations..."
python server/manage.py makemigrations
python server/manage.py migrate
python server/manage.py migrate --database=db_images

# start server
echo "Starting Gunicorn server..."
exec "$@"