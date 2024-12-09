#!/bin/bash

REGISTRY_URL="registry.git.chalmers.se"
REGISTRY_USER=""
REGISTRY_PASSWORD=""

# login to the container registry
echo "Logging in to the container registry..."
echo "$REGISTRY_PASSWORD" | docker login "$REGISTRY_URL" -u "$REGISTRY_USER" --password-stdin
if [ $? -ne 0 ]; then
  echo "Error: Login to container registry failed."
  exit 1
fi

# bring up the containers using docker-compose
echo "Starting services with docker-compose..."
docker-compose up # add -d in deployment
if [ $? -ne 0 ]; then
  echo "Error: Failed to start services with docker-compose."
  exit 1
fi

echo "Services are up and running."
