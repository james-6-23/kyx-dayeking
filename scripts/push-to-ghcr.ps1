# Push Hajimi King Docker image to GitHub Container Registry
# PowerShell script for Windows

param(
    [string]$GitHubUsername = "yourusername",
    [switch]$CleanupLocal = $false
)

# Configuration
$ImageName = "hajimi-king"
$Registry = "ghcr.io"

# Colors
function Write-Success {
    Write-Host "✓ $args" -ForegroundColor Green
}

function Write-Error {
    Write-Host "✗ $args" -ForegroundColor Red
}

function Write-Info {
    Write-Host "→ $args" -ForegroundColor Yellow
}

# Check if CR_PAT is set
if (-not $env:CR_PAT) {
    Write-Error "CR_PAT environment variable is not set!"
    Write-Host "Please set your GitHub Personal Access Token:"
    Write-Host '  $env:CR_PAT = "ghp_xxxxxxxxxxxxxxxxxxxx"'
    exit 1
}

# Get version
try {
    $Version = git describe --tags --always --dirty 2>$null
    if (-not $Version) {
        throw "Git command failed"
    }
} catch {
    $Version = Get-Date -Format "yyyyMMdd-HHmmss"
}

Write-Info "Building and pushing $ImageName version $Version"

# Step 1: Build the image
Write-Info "Building Docker image..."
docker build -t ${ImageName}:latest .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to build image"
    exit 1
}
Write-Success "Image built successfully"

# Step 2: Tag the image
Write-Info "Tagging image..."
docker tag ${ImageName}:latest ${Registry}/${GitHubUsername}/${ImageName}:latest
docker tag ${ImageName}:latest ${Registry}/${GitHubUsername}/${ImageName}:${Version}
Write-Success "Image tagged"

# Step 3: Login to ghcr.io
Write-Info "Logging in to $Registry..."
$env:CR_PAT | docker login $Registry -u $GitHubUsername --password-stdin
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to login"
    exit 1
}
Write-Success "Login successful"

# Step 4: Push the image
Write-Info "Pushing image to registry..."
docker push ${Registry}/${GitHubUsername}/${ImageName}:latest
docker push ${Registry}/${GitHubUsername}/${ImageName}:${Version}
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to push image"
    exit 1
}
Write-Success "Image pushed successfully"

# Step 5: Cleanup (optional)
if ($CleanupLocal) {
    Write-Info "Removing local images..."
    docker rmi ${ImageName}:latest
    docker rmi ${Registry}/${GitHubUsername}/${ImageName}:latest
    docker rmi ${Registry}/${GitHubUsername}/${ImageName}:${Version}
    Write-Success "Local images removed"
}

# Summary
Write-Host ""
Write-Success "Successfully pushed to:"
Write-Host "  - ${Registry}/${GitHubUsername}/${ImageName}:latest"
Write-Host "  - ${Registry}/${GitHubUsername}/${ImageName}:${Version}"
Write-Host ""
Write-Host "To use this image:"
Write-Host "  docker pull ${Registry}/${GitHubUsername}/${ImageName}:latest"