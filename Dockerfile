# base image for ML with CUDA
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04 as backend

# install python and required tools
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub && \
    apt-key adv --fetch-keys http://archive.ubuntu.com/ubuntu/ubuntu-keyring.gpg && \
    apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    build-essential \
    libgl1 \
    libglib2.0-0 \ 
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy and install python dependencies
COPY requirements.txt ./requirements.txt
RUN python3.11 -m venv venv
RUN . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

# copy django server, machine learning files and db
COPY server/ ./server/
COPY ml/ ./ml/
COPY db_app.sqlite3 ./db_app.sqlite3

# expose port for django
EXPOSE 8000

# Set env variable so python output goes directly to terminal
ENV PYTHONUNBUFFERED=1

# commands to run migrations and start server
CMD . venv/bin/activate && \
    python server/manage.py makemigrations && \
    python server/manage.py migrate && \
    python server/manage.py migrate --database=db_images && \
    echo "n" | python server/manage.py runserver 0.0.0.0:8000