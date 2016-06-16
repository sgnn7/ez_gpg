# ez_gpg
Personal take on what a GPG UI should look like

PS: There's not much in the app besides basic encryption and signature verification (for now).

## Prerequisites

python3-gnupg (`sudo apt-get install python3-gnupg`), Gtk 3.0.

## Installation

Clone and run ./ezgpg from the checkout directory.

### Notes

Preliminary workflow (really bad scaling):

Main Window:
```
----------------------------
|     Encrypt | Decrypt    |
|       -------------      |
|       Sign  | Verify     |
|                          |
|         [Key Mgmt]       |
----------------------------
```

Encryption:
```
----------------------------
|   -------------------    |
|   |   Files (DnD)   |    |
|   -------------------    |
|    Receptients:          |
|   -------------------    |
|   |[x] Key 1     ...|    |
|   -------------------    |
|                [Encrypt] |
----------------------------
```

Decryption:
```
----------------------------
|   -------------------    |
|   |   Files (DnD)   |    |
|   -------------------    |
|    Output dir:           |
|   -------------------    |
|   |~/foo         ...|    |
|   -------------------    |
|                [Decrypt] |
----------------------------
```
