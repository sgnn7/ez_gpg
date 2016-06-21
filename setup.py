#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name = "ezgpg",
    version = "0.1",
    packages = find_packages(),
    zip_safe = True,

    scripts = ['ezgpg'],

    entry_points = {
        'gui_scripts': [
            'ezgpg = ez_gpg.ui.EzGpg:launch',
        ],
        'setuptools.installation': [
            'eggsecutable = ez_gpg.ui.EzGpg:launch',
        ]
    },

    install_requires = ['python-gnupg'],

    package_data = {
        '': ['*.ui', '*.md', '*.css'],
    },

    author = "Srdjan Grubor",
    author_email = "sgnn7@sgnn7.org",
    description = "Simplified GPG UI",
    license = "MIT",
    keywords = "gpg gpg2 ui crypto cryptography pgp",
    url = "https://github.cpom/sgnn7/ez_gpg",
)
