#!/bin/bash

# ensure env arguments are provided
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "❌ Error: Missing required arguments."
  echo "Usage: $0 <SECRET_KEY> <SETUP_PROMPT_1> <SETUP_PROMPT_2>"
  exit 1
fi

# assign args to env variables
SECRET_KEY="$1"
SETUP_PROMPT_1="$2"
SETUP_PROMPT_2="$3"

# define target env file
ENV_FILE="/services/skinscan/.env"

# create or overwrite env file
echo "Writing to $ENV_FILE..."
sudo bash -c "cat > $ENV_FILE" <<EOF
SECRET_KEY=$(echo $SECRET_KEY | base64 -d)
SETUP_PROMPT_1=$SETUP_PROMPT_1
SETUP_PROMPT_2=$SETUP_PROMPT_2
EOF

# set permissions for env file
echo "Setting permissions for $ENV_FILE..."
sudo chmod 600 $ENV_FILE

echo "Environment file created successfully."