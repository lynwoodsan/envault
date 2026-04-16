import os
from typing import Dict


def export_dotenv(vault: Dict, output_path: str) -> None:
    """Write vault variables to a .env file."""
    with open(output_path, "w") as f:
        for key, value in vault.items():
            escaped = value.replace('"', '\\"')
            f.write(f'{key}="{escaped}"\n')


def import_dotenv(vault: Dict, input_path: str) -> int:
    """Read a .env file and merge variables into vault. Returns count imported."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f".env file not found: {input_path}")

    count = 0
    with open(input_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, raw_value = line.partition("=")
            key = key.strip()
            value = raw_value.strip().strip('"').strip("'")
            if key:
                vault[key] = value
                count += 1
    return count
