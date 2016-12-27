# ez_gpg
Personal take on what a usable GPG app should be like

## Releases

[Latest (v0.2.2; deb, rpm, egg, zip)](https://github.com/sgnn7/ez_gpg/releases "Releases")

## Screenshots

![Main Window](/screenshots/main_screen.png?raw=true "Main Window")

![Encryption Window](/screenshots/encrypt.png?raw=true "Encryption Window")

![Signing Window (bad pass)](/screenshots/sign_bad_pw.png?raw=true "Signing Window (bad pass)")

![Decrypytion Window (symetric)](/screenshots/decrypt_symetric.png?raw=true "Decryption Window (symetric)")

![Decrypytion  Window](/screenshots/decrypt.png?raw=true "Decryption  Window")

![Verification Window](/screenshots/verify.png?raw=true "Verification Window")

### In progress:
![Key Management Window](/screenshots/key_management.png?raw=true "Key Management Window")

## Working
- Basic multi-file encryption
 - PKI
 - Symetric
- Basic decryption
 - Can detect if you have the needed decryption key
 - Checks if your password is correct for selected key
- Basic signing
- Basic signature verification (detached signature)
- Key import (armored)
- Key deletion (armored)
- Key export (armored and binary)
- Keyserver fetch of key (with rogue cert checking)
- Python packaging
- Mnemonics (keyboard shortcuts)
- fpm packaging

## Still missing:
- Multi-file handling (sign, verify, decrypt)
- Encryption/signing options
- DnD
- Key management
 - Key creation
 - Push to remote keyserver
 - Key signing
 - Key revocation
 - Key signature update from keyserver
- PPA
- <del>Symetric encryption</del>
- <del>PyPI packaging that works</del>
- <del>Debian packaging</del>

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
