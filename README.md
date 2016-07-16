# ez_gpg
Personal take on what a GPG UI should look like

## Screenshots

![Main Window](/screenshots/main_screen.png?raw=true "Main Window")

![Encryption Window](/screenshots/encrypt.png?raw=true "Encryption Window")

![Signing Window (bad pass)](/screenshots/sign_bad_pw.png?raw=true "Signing Window (bad pass)")

![Decrpytion Window (symetric)](/screenshots/decrypt_symetric.png?raw=true "Decryption Window (symetric)")

![Decrpytion  Window](/screenshots/decrypt.png?raw=true "Decrpytion  Window")

![Verification Window](/screenshots/verify.png?raw=true "Verification Window")

### In progress:
![Key Manag3ement Window](/screenshots/key_management.png?raw=true "Key Management Window")

## Working
- Basic multi-file encryption
- Basic decryption
 - Can detect if you have the needed decryption key
 - Checks if your password is correct for selected key
- Basic signing
- Basic signature verification (detached signature)
- Key import (armoured)
- Key deletion (armoured)
- Python packaging
- fpm packaging

## Still missing:
- Multi-file handling (sign, verify, decrypt)
- Symetric encryption
- Encryption/signing options
- DnD
- Key management
- <del>PyPI packaging that works</del>
- <del>Debian packaging</del>
- PPA

## Prerequisites

- `python3-setuptools` (`sudo apt-get install python3-setuptools`)
- `python3-gnupg` (`sudo apt-get install python3-gnupg`)

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
- `sudo ./setup.py install`

## Running

- Run `ezgpg` from anywhere
- If running from repo:
 - `cd <repo path>`
 - `./ezgpg`
