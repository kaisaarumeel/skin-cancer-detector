# base image for ML with CUDA
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04 as backend

ARG SECRET_KEY
ENV SECRET_KEY=${SECRET_KEY}

# install python and required tools
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    build-essential \
    libgl1 \
    libglib2.0-0 \ 
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONPATH="/app:$PYTHONPATH"

# copy and install python dependencies
COPY requirements.txt ./requirements.txt
RUN python3.11 -m venv venv
RUN . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# copy django server, machine learning files, db and migrations script
COPY server/ ./server/
COPY ml/ ./ml/
COPY db_app.sqlite3 ./db_app.sqlite3

# expose port for django
EXPOSE 8000

# Set env variable so python output goes directly to terminal
ENV PYTHONUNBUFFERED=1

# make migrations and start server
CMD sh -c ". venv/bin/activate && \
    cd server \
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py migrate --database=db_images && \
    gunicorn --bind 0.0.0.0:8000 --workers 3 skinscan.wsgi:application"