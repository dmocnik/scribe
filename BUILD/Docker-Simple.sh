#!/bin/bash

# [ This is a placeholder for now ]

# Prune unused builders
sudo docker builder prune

# Prune unused images
sudo docker image prune -a

# If the container is already deployed, stop it
sudo docker-compose down

# Build the image
sudo docker-compose build --no-cache

# Run the image in the background
sudo docker-compose up -d
