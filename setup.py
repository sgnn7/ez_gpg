#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name = "ezgpg",
    version = "0.2.4",
    packages = find_packages(),
    zip_safe = True,

    scripts = ['ezgpg'],

    entry_points = {
        'gui_scripts': [
            'ezgpg = ez_gpg.ui:EzGpg.launch',
        ],
        'setuptools.installation': [
            'eggsecutable = ez_gpg.ui:EzGpg.launch',
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
    url = "https://github.com/sgnn7/ez_gpg",
    keywords = ["gpg", "gpg2", "pgp", "crypto", "cryptography"],
    classifiers = [
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: English",
        "Topic :: Communications :: Email",
        "Topic :: Office/Business",
        "Topic :: Security :: Cryptography",
        "Topic :: Security",
        "Topic :: Utilities",
        ],
)
