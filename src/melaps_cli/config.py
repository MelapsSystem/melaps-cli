"""Local CLI configuration (~/.config/melaps/config.toml)."""

import os
import tomllib
from pathlib import Path

from .errors import AuthError

DEFAULT_PATH = Path.home() / ".config" / "melaps" / "config.toml"


def load(path=None):
    """Return the saved config dict, or an empty dict if none exists."""
    path = Path(path) if path else DEFAULT_PATH
    if not path.exists():
        return {}
    with path.open("rb") as f:
        return tomllib.load(f)


def save(api_key, base_url=None, path=None):
    """Persist the API key (0600) to the config file."""
    path = Path(path) if path else DEFAULT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f'api_key = "{api_key}"']
    if base_url:
        lines.append(f'base_url = "{base_url}"')
    path.write_text("\n".join(lines) + "\n")
    os.chmod(path, 0o600)


def api_key(path=None):
    key = os.environ.get("MELAPS_API_KEY") or load(path).get("api_key")
    if not key:
        raise AuthError("no API key set — run `melaps auth login` or set MELAPS_API_KEY")
    return key
