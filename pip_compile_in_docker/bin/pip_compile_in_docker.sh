#!/bin/bash

set -euo pipefail

# It's good to have reproducible builds.
# https://pythonspeed.com/articles/reproducible-docker-builds-python/
#
# We use pinned versions of all our Python dependencies via requirements.txt.
# To generate requirements.txt, we use pip-compile, which reads a high-level
# requirements.in file (doesn't include the transitive dependencies). To ensure
# pip-compile is using the same Python version as the application, we run it in
# Docker with the same python base image.
#
# This script builds the "piptools" Docker image and then runs it to
# update requirements.txt

PIPTOOLS_IMAGE="piptools"
# target in our Dockerfile that installs piptools and runs pip-compile
BUILD_TARGET="generate_requirements"
# directory where the container will read requirements.in and write requirements.txt
CONTAINER_MOUNTPOINT="/reqs"

## Note: doesn't apply in dogsci
# ensure we're at the repo root
# _REPO_ROOT=$(git rev-parse --show-toplevel)
# cd "$_REPO_ROOT"

echo -e "=== building docker image for running pip-compile ===\n"
docker build -t "$PIPTOOLS_IMAGE" --target "$BUILD_TARGET" .

echo -e "\n\n=== running pip-compile to update requirements.txt ===\n"
# mount this repo's requirements/ dir as /reqs
docker run --rm -v "$PWD/requirements:$CONTAINER_MOUNTPOINT" "$PIPTOOLS_IMAGE"
