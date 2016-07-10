#!/bin/bash -e

#TODO: Bump minor version

rm -rf *.egg-info/ build/ dist/
./setup.py sdist upload
