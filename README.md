# ez_gpg
Personal take on what a usable GPG app should be like

## Releases

[Latest (v0.2.5; deb, rpm, egg, zip)](https://github.com/sgnn7/ez_gpg/releases "Releases")

## Screenshots

![Main Window](/screenshots/main_screen.png?raw=true "Main Window")

![Encryption Window](/screenshots/encrypt_pki.png?raw=true "Encryption Window (PKI)")

![Encryption Window](/screenshots/encrypt_symmetric.png?raw=true "Encryption Window (Symmetric)")

![Signing Window (bad pass)](/screenshots/sign_bad_pw.png?raw=true "Signing Window (bad pass)")

![Decrypytion Window (symmetric)](/screenshots/decrypt_symmetric.png?raw=true "Decryption Window (symmetric)")

![Decrypytion  Window](/screenshots/decrypt.png?raw=true "Decryption  Window")

![Verification Window](/screenshots/verify.png?raw=true "Verification Window")

### In progress:
![Key Management Window](/screenshots/key_management.png?raw=true "Key Management Window")

## Working
- Basic multi-file encryption
 - PKI
 - Symmetric
- Basic decryption
 - Can detect if you have the needed decryption key
 - Checks if your password is correct for selected key
- Basic signing
- Basic signature verification (detached signature)
- Key creation (RSA/DSA, configurable key length)
- Key import (armored)
- Key deletion (armored)
- Key export (armored and binary)
- Keyserver fetch of key (with rogue cert checking)
- macOS support (Apple Silicon and Intel)
- Python packaging (PyPI via pyproject.toml)
- Mnemonics (keyboard shortcuts)
- fpm packaging

## Still missing:
- Multi-file handling (sign, verify, decrypt)
- Encryption/signing options
- DnD
- Key management
 - Push to remote keyserver
 - Key signing
 - Key revocation
 - Key signature update from keyserver
- PPA
- <del>Key creation</del>
- <del>Symmetric encryption</del>
- <del>PyPI packaging that works</del>
- <del>Debian packaging</del>

## Prerequisites

### Linux (Debian/Ubuntu)

- `python3-setuptools` (`sudo apt-get install python3-setuptools`)
- `python3-gnupg` (`sudo apt-get install python3-gnupg`)

### macOS

Install system dependencies via [Homebrew](https://brew.sh):

```bash
brew install gnupg gtk+3 gobject-introspection pkg-config cairo pygobject3
```

## Installation

### macOS (virtualenv)

```bash
# Clone repo
git clone https://github.com/sgnn7/ez_gpg.git
cd ez_gpg

# Create and activate virtualenv
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run
./ezgpg
```

If `pip install PyGObject` fails, ensure pkg-config can find the required libraries:

```bash
export PKG_CONFIG_PATH="$(brew --prefix)/lib/pkgconfig:$(brew --prefix)/share/pkgconfig:$PKG_CONFIG_PATH"
pip install PyGObject
```

### Linux: Using fpm binary packages (recommended)

- Clone repo
- Install Ruby (`sudo apt-get install ruby`)
 - `rvm` tool recommended as your Ruby manager if you don't want fpm in global gems`
- Install fpm (`gem install fpm`)
- Build package with `./package.sh deb` or `./package.sh rpm`
- Install package (`sudo dpkg -i ezgpg_*.deb`)

### Using pip

- Clone repo
- `pip install .`

## Running

- Run `ezgpg` from anywhere
- If running from repo:
 - `cd <repo path>`
 - `./ezgpg`

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v
```
