# ez_gpg
Personal take on what a GPG UI should look like

Still missing:
- Multi-file handling
- DnD
- Key management
- <del>PyPI packaging that works</del>
- <del>Debian packaging</del>
- PPA

## Prerequisites

- `python3-setuptools` (`sudo apt-get install python3-setuptools`)
- `python3-gnutls` if you want to run the app without installation (`sudo apt-get install python3-gnutls`)

## Installation

### Using fpm binary packages (recommended)

- Clone repo
- Install Ruby (i.e. `sudo apt-get install ruby`)
 - `rvm` tool recommended as your Ruby manager if you don't want fpm in global gems`
- Install fpm (i.e. `gem install fpm`)
- Build package with `./package.sh deb` or `./package.sh rpm`
- Install package (i.e. `sudo dpkg -i ezgpg_*.deb`)

### Using setuputils

- Clone repo
- `sudo setup.py install`

## Running

- Run `ezgpg` from anywhere
