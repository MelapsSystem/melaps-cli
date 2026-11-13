# melaps-cli

[![PyPI](https://img.shields.io/pypi/v/melaps-cli)](https://pypi.org/project/melaps-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

Command line interface for [Melaps System](https://melaps.xyz) — submit jobs, watch
GPU telemetry, and manage reservations on our H100 clusters from your terminal.

- Website: <https://melaps.xyz>
- Documentation: <https://docs.melaps.xyz>
- X: <https://x.com/melaps_system>

## Install

```bash
pip install melaps-cli
```

## Quickstart

```bash
melaps auth login --api-key sk_live_...
melaps jobs submit examples/job.yaml
melaps jobs status job-01k4
melaps jobs metrics job-01k4
melaps clusters list
```

## Commands

| Command | What it does |
| --- | --- |
| `melaps auth login` | Save your API key to `~/.config/melaps/config.toml` |
| `melaps jobs submit <spec.yaml>` | Submit a job (idempotent, safe to retry) |
| `melaps jobs status <id>` | Show a job as JSON |
| `melaps jobs list` | List recent jobs |
| `melaps jobs cancel <id>` | Cancel a queued or running job |
| `melaps jobs metrics <id>` | GPU util, memory, power, temperature |
| `melaps clusters list` | Free GPUs per cluster and region |
| `melaps reservations create --gpus 8 --months 6` | Reserve a rack |
| `melaps usage --start 2026-11-01 --end 2026-11-30` | Billed GPU-hours |
| `melaps status` | Platform status |

Jobs are defined in YAML — see [`examples/job.yaml`](examples/job.yaml).
A job can also be submitted with `MELAPS_API_KEY` set instead of logging in.

## Pricing

| Tier | $ / GPU-hour |
| --- | --- |
| On demand | 2.49 |
| Reserved | 1.89 |
| Batch (preemptible) | 1.19 |

Batch jobs receive a 60-second SIGTERM before preemption. Full pricing:
<https://melaps.xyz/#pricing>

## License

MIT — see [LICENSE](LICENSE).

---

**Melaps System** — GPU racks you can hold by the hour.

- Website: <https://melaps.xyz>
- Documentation: <https://docs.melaps.xyz>
- X: <https://x.com/melaps_system>
- Status: <https://melaps.xyz/status>
