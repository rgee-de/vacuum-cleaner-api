#!/bin/bash

# Set default container name if none is provided
containerName=${1:-vacuum-cleaner-api}

# Run the remove script
removeScriptPath="./remove-container.sh"
echo "Running the removal script..."
bash $removeScriptPath $containerName

# Change directory to the root folder where the Dockerfile is located
rootPath=$(dirname "$(pwd)")
cd $rootPath

# Build the new Docker image
echo "Building the new Docker image..."
docker build -t $containerName .

# Run the new container
echo "Running the new container..."
docker run -d -p 8000:8000 --name $containerName $containerName

echo "Deployment completed successfully."

# Change back to the original working directory
cd "$(dirname "$removeScriptPath")"
