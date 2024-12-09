#!/bin/bash

# login to the container registry
echo "Logging in to the container registry..."
docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$REGISTRY_URL"
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
