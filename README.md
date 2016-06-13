# ez_gpg
Personal take on what a GPG UI should look like

PS: There's not much here besides a window that can list your GPG keys (for now)

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
