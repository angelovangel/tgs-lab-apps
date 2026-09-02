#!/bin/bash
set -e

# Build and Push Script for Docker Hub
# Usage: ./build_and_push.sh <dockerhub_username> [tag]
# Example: ./build_and_push.sh angeloas latest

DOCKER_USER="${1}"
TAG="${2:-latest}"

if [ -z "$DOCKER_USER" ]; then
  echo "Error: Docker Hub username required."
  echo "Usage: $0 <dockerhub_username> [tag]"
  echo "Example: $0 angeloas latest"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

APPS=(
  "rapid-barcoding-ont"
  "custom-transfer-opentrons"
  "kinnex-ot2"
  "sanger-opentrons"
  "tracer"
  "minimapper-app"
)

echo "=========================================="
echo " Building & Pushing images for: ${DOCKER_USER}"
echo " Tag: ${TAG}"
echo "=========================================="

i=0
for APP in "${APPS[@]}"; do
  i=$((i+1))
  IMAGE_NAME="${DOCKER_USER}/${APP}:${TAG}"
  APP_DIR="${ROOT_DIR}/${APP}"

  if [ ! -d "$APP_DIR" ]; then
    echo "Warning: Directory $APP_DIR does not exist. Skipping $APP."
    continue
  fi

  echo ""
  echo "------------------------------------------"
  echo " Building ${i} of ${#APPS[@]}: ${IMAGE_NAME}"
  echo " Directory: ${APP_DIR}"
  echo "------------------------------------------"

  docker build --platform linux/amd64 -t "${IMAGE_NAME}" "${APP_DIR}"

  echo " Pushing [ ${IMAGE_NAME} ] to Docker Hub..."
  docker push "${IMAGE_NAME}"

  echo " Successfully pushed ${IMAGE_NAME}"
done

echo ""
echo "=========================================="
echo " All images built and pushed successfully!"
echo "=========================================="
