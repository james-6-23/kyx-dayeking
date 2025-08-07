#!/bin/bash
# Push Hajimi King Docker image to GitHub Container Registry

set -e  # Exit on error

# Configuration
GITHUB_USERNAME="${GITHUB_USERNAME:-yourusername}"
IMAGE_NAME="hajimi-king"
REGISTRY="ghcr.io"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check if CR_PAT is set
if [ -z "$CR_PAT" ]; then
    print_error "CR_PAT environment variable is not set!"
    echo "Please set your GitHub Personal Access Token:"
    echo "  export CR_PAT=ghp_xxxxxxxxxxxxxxxxxxxx"
    exit 1
fi

# Get version from git or use timestamp
if git rev-parse --git-dir > /dev/null 2>&1; then
    VERSION=$(git describe --tags --always --dirty)
else
    VERSION=$(date +%Y%m%d-%H%M%S)
fi

print_info "Building and pushing ${IMAGE_NAME} version ${VERSION}"

# Step 1: Build the image
print_info "Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .
print_success "Image built successfully"

# Step 2: Tag the image
print_info "Tagging image..."
docker tag ${IMAGE_NAME}:latest ${REGISTRY}/${GITHUB_USERNAME}/${IMAGE_NAME}:latest
docker tag ${IMAGE_NAME}:latest ${REGISTRY}/${GITHUB_USERNAME}/${IMAGE_NAME}:${VERSION}
print_success "Image tagged"

# Step 3: Login to ghcr.io
print_info "Logging in to ${REGISTRY}..."
echo $CR_PAT | docker login ${REGISTRY} -u ${GITHUB_USERNAME} --password-stdin
print_success "Login successful"

# Step 4: Push the image
print_info "Pushing image to registry..."
docker push ${REGISTRY}/${GITHUB_USERNAME}/${IMAGE_NAME}:latest
docker push ${REGISTRY}/${GITHUB_USERNAME}/${IMAGE_NAME}:${VERSION}
print_success "Image pushed successfully"

# Step 5: Cleanup (optional)
read -p "Do you want to remove local images? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker rmi ${IMAGE_NAME}:latest
    docker rmi ${REGISTRY}/${GITHUB_USERNAME}/${IMAGE_NAME}:latest
    docker rmi ${REGISTRY}/${GITHUB_USERNAME}/${IMAGE_NAME}:${VERSION}
    print_success "Local images removed"
fi

# Summary
echo
print_success "Successfully pushed to:"
echo "  - ${REGISTRY}/${GITHUB_USERNAME}/${IMAGE_NAME}:latest"
echo "  - ${REGISTRY}/${GITHUB_USERNAME}/${IMAGE_NAME}:${VERSION}"
echo
echo "To use this image:"
echo "  docker pull ${REGISTRY}/${GITHUB_USERNAME}/${IMAGE_NAME}:latest"