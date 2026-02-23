#!/bin/bash -e

if [ -z "$(which fpm)" ]; then
  echo "ERROR! You need to install Ruby and fpm Ruby package first! Exiting..."
  exit 1
fi

package_type="deb"
if [ $# -gt 0 ]; then
  package_type=$1
fi

echo "Package type: $package_type"

# TODO: Use dirname/readlink instead of assuming we build from this dir
echo "Building sdist to validate..."
python -m build --sdist

echo "Removing old package (if needed)..."
rm -f ezgpg_*.$package_type

echo "Building package..."
fpm -s python \
    -t $package_type \
    -d python3 \
    -d python3-tk \
    -n ezgpg \
    -m "Srdjan Grubor <sgnn7@sgnn7.org>" \
    --deb-no-default-config-files \
    --python-package-name-prefix python3 \
    --python-pip pip3 \
    --python-easyinstall easy_install3 \
    --python-bin python3 \
    ./pyproject.toml
