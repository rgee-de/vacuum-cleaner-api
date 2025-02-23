param (
    [string]$containerName = "vacuum-cleaner-api"
)

# Path to the remove script
$removeScriptPath = ".\remove-container.ps1"

# Run the remove script
Write-Output "Running the removal script..."
& $removeScriptPath -containerName $containerName

# Change directory to the root folder where the Dockerfile is located
$rootPath = (Get-Item -Path "..\").FullName
Set-Location -Path $rootPath

# Build the new Docker image
Write-Output "Building the new Docker image..."
docker build -t $containerName .

# Run the new container
Write-Output "Running the new container..."
docker run -d -p 8000:8000 --name $containerName $containerName

Write-Output "Deployment completed successfully."

# Change back to the original working directory
Set-Location -Path (Get-Item -Path ".\scripts").FullName
