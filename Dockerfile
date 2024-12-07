# base image 
FROM ubuntu:22.04 as backend

# Import missing GPG keys and configure the repository
RUN apt-get install -y gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x871920D1991BC93C | gpg --dearmor -o /etc/apt/keyrings/ubuntu-archive.gpg && \
    chmod 644 /etc/apt/keyrings/ubuntu-archive.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/ubuntu-archive.gpg] http://archive.ubuntu.com/ubuntu jammy main universe restricted multiverse" > /etc/apt/sources.list.d/jammy.list

# install python and required tools
RUN apt-get update && apt-get install -y \
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