#!/bin/bash
set -e

# Build and Push Script for Docker Hub
# Usage: ./build_and_push.sh <dockerhub_username> [tag] [app1,app2,...]
# Example: ./build_and_push.sh angeloas latest rapid-barcoding-ont,kinnex-ot2

DOCKER_USER="${1}"
TAG="${2:-latest}"
TARGET_APPS_INPUT="${3}"

if [ -z "$DOCKER_USER" ]; then
  echo "Error: Docker Hub username required."
  echo "Usage: $0 <dockerhub_username> [tag] [app1,app2,...]"
  echo "Example: $0 angeloas latest rapid-barcoding-ont,kinnex-ot2"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

ALL_APPS=(
  "rapid-barcoding-ont"
  "custom-transfer-opentrons"
  "kinnex-ot2"
  "sanger-opentrons"
  "tracer"
  "minimapper-app"
  "nxf-shiny"
  "zinter"
  "faster-app"
)

# Filter APPS array if specific target apps are provided in 3rd argument
if [ -n "$TARGET_APPS_INPUT" ]; then
  IFS=',' read -r -a parsed_apps <<< "$TARGET_APPS_INPUT"
  APPS=()
  for target in "${parsed_apps[@]}"; do
    target=$(echo "$target" | xargs)
    [ -z "$target" ] && continue
    found=0
    for app in "${ALL_APPS[@]}"; do
      if [ "$app" == "$target" ]; then
        APPS+=("$app")
        found=1
        break
      fi
    done
    if [ $found -eq 0 ]; then
      echo "Warning: '$target' is not a recognized app name. Skipping."
    fi
  done

  if [ ${#APPS[@]} -eq 0 ]; then
    echo "Error: No valid apps specified to build."
    echo "Available apps are: ${ALL_APPS[*]}"
    exit 1
  fi
else
  APPS=("${ALL_APPS[@]}")
fi

echo "=========================================="
echo " Building & Pushing images for: ${DOCKER_USER}"
echo " Tag: ${TAG}"
echo " Apps to process: ${APPS[*]}"
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
echo " All specified images built and pushed successfully!"
echo "=========================================="


