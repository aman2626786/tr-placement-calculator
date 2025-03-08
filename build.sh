#!/usr/bin/env bash
# exit on error
set -o errexit

# Install required system-level dependencies
pip install --upgrade pip

# Install dependencies without build isolation to use pre-built wheels
pip install --no-build-isolation -r requirements.txt