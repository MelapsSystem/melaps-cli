# Contributing

1. Fork the repo and create a branch from `main`.
2. `pip install -e ".[dev]"` and run `pytest` before opening a PR.
3. Keep the CLI dependency-free beyond `requests` and `pyyaml`.
4. Never commit API keys — use `MELAPS_API_KEY` or `melaps auth login`.
