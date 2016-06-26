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
- `python3-gnutls` (`sudo apt-get install python3-gnutls`)

## Installation

### Using fpm binary packages (recommended)

- Clone repo
- Install Ruby (`sudo apt-get install ruby`)
 - `rvm` tool recommended as your Ruby manager if you don't want fpm in global gems`
- Install fpm (`gem install fpm`)
- Build package with `./package.sh deb` or `./package.sh rpm`
- Install package (`sudo dpkg -i ezgpg_*.deb`)

### Using setuputils

- Clone repo
- `sudo setup.py install`

## Running

- Run `ezgpg` from anywhere
- If running from repo:
 - `cd <repo path>`
 - `./ezgpg`
