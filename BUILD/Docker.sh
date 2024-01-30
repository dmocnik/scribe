#!/bin/bash

# Function to parse input arguments
parse_args() {
    for arg in "$@"; do
        case $arg in
            -push)
            PUSH=true
            shift
            ;;
            *)
            # Unknown option
            shift
            ;;
        esac
    done
}

echo "Welcome! Docker image will be compiled shortly."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script needs to be run as root."
    exit
fi

# Print out all arguments
echo "PUSH IMAGE: $PUSH"

# Get the current directory
WORK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Current directory: $WORK_DIR"

echo -n "About to start in 5 seconds. Press Ctrl+C to cancel."
for i in {5..1}; do
    echo -ne "\rAbout to start in $i seconds. Press Ctrl+C to cancel.   "
    sleep 1
done
echo ""

# Enable experimental features
export DOCKER_CLI_EXPERIMENTAL=enabled

# Load environment variables from .env file
dotenv .env

# Set the Docker Hub image name
export DOCKER_IMAGE=${DOCKER_USERNAME}/${DOCKER_REPO}

# Check if DOCKER_USERNAME, DOCKER_PASSWORD and DOCKER_REPO are set
if [ -z "$DOCKER_USERNAME" ] || [ -z "$DOCKER_PASSWORD" ] || [ -z "$DOCKER_REPO" ]; then
    echo "DOCKER_USERNAME, DOCKER_PASSWORD and DOCKER_REPO must be set in .env file, located in BUILD directory. Please check your system configuration."
    exit
fi

# Check if logged in to Docker Hub
if ! docker info | grep -q "Username: ${DOCKER_USERNAME}"; then
    echo "You must be logged in to Docker Hub as ${DOCKER_USERNAME}."
    echo "Run 'docker login' as root to login to Docker Hub."
    exit
fi

# Check if scribe_builder buildx exists
if ! docker buildx ls | grep -q "scribe_builder"; then
    echo "scribe_builder buildx does not exist, creating it."
    docker buildx create --name scribe_builder --use
fi

# Check if scribe_builder buildx is active
if ! docker buildx ls | grep -q "scribe_builder.*active"; then
    echo "scribe_builder buildx is not active, activating it."
    docker buildx use scribe_builder
fi

# [ Build the Image for amd64 and arm64 ]

# Use buildx to build the image for amd64 and arm64
docker buildx inspect --bootstrap
docker buildx build --platform linux/arm64,linux/amd64 -t ${DOCKER_IMAGE} .

# Push the image to Docker Hub if PUSH is set to true
if [ "$PUSH" = true ]; then
    echo "Pushing the image to Docker Hub."
    docker buildx build --platform linux/arm64,linux/amd64 -t ${DOCKER_IMAGE} . --push
fi

# Success message
echo "Docker image has been built and pushed successfully."

# [ Make the Image private? ]
# This is a workaround as images must be pushed before they can be made private

# Get the token for your Docker Hub account
# TOKEN=$(curl -s -H "Content-Type: application/json" -X POST -d '{"username": "'${DOCKER_USERNAME}'", "password": "'${DOCKER_PASSWORD}'"}' https://hub.docker.com/v2/users/login/ | jq -r .token)

# Make the image private
# curl -s -H "Authorization: JWT ${TOKEN}" -X PATCH -d '{"visibility": "private"}' https://hub.docker.com/v2/repositories/${DOCKER_USERNAME}/${DOCKER_REPO}/