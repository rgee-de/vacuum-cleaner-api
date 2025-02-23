#!/bin/bash

# Set default container name if none is provided
containerName=${1:-vacuum-cleaner-api}

# Function to check if a container is running
IsContainerRunning() {
    docker ps -q --filter "name=$containerName"
}

# Function to check if a container exists (running or stopped)
IsContainerExists() {
    docker ps -aq --filter "name=$containerName"
}

# Function to check if an image exists
IsImageExists() {
    docker images -q $containerName
}

# Stop and remove the container if it's running
if [ "$(IsContainerRunning)" ]; then
    echo "Stopping the running container..."
    docker stop $containerName
fi

# Remove the container if it exists
if [ "$(IsContainerExists)" ]; then
    echo "Removing the container..."
    docker rm $containerName
fi

# Remove the Docker image if it exists
if [ "$(IsImageExists)" ]; then
    echo "Removing the Docker image..."
    docker rmi $containerName
fi
