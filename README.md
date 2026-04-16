# envault

> A CLI tool for managing and encrypting project-level environment variables with team sharing support.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install envault
```

---

## Usage

Initialize envault in your project directory:

```bash
envault init
```

Add and encrypt an environment variable:

```bash
envault set API_KEY sk-abc123
```

Load variables into your current shell session:

```bash
eval $(envault load)
```

Share the encrypted vault with your team by committing `.envault.vault` to version control. Team members can decrypt using a shared key:

```bash
envault unlock --key <shared-key>
```

View all stored keys (without revealing values):

```bash
envault list
```

---

## Commands

| Command | Description |
|---|---|
| `init` | Initialize a new vault in the current directory |
| `set <KEY> <VALUE>` | Encrypt and store an environment variable |
| `get <KEY>` | Decrypt and print a single variable |
| `load` | Output all variables as export statements |
| `list` | List all stored keys |
| `unlock` | Decrypt vault using a shared team key |

---

## License

This project is licensed under the [MIT License](LICENSE).