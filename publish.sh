#!/bin/bash -e

#TODO: Bump minor version

rm -rf *.egg-info/ build/ dist/
./setup.py sdist upload --sign --identity "E580373EDE23B6D9"
