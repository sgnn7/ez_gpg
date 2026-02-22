#!/bin/bash -e

#TODO: Bump minor version

rm -rf *.egg-info/ build/ dist/
python -m build
twine upload --sign --identity "E580373EDE23B6D9" dist/*
