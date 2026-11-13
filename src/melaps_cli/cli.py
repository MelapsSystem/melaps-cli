"""`melaps` — command line interface for Melaps System GPU clusters.

    melaps auth login --api-key sk_live_...
    melaps jobs submit examples/job.yaml
    melaps jobs status job-01k4
    melaps jobs logs job-01k4 --follow
    melaps clusters list
    melaps reservations create --gpus 8 --months 6
    melaps usage --start 2026-11-01 --end 2026-11-30
"""

import argparse
import json
import sys
import uuid

import yaml

from .client import Client
from .config import api_key as load_api_key
from .config import save as save_config
from .errors import MelapsError
from .output import print_json, print_table


def _client(args):
    return Client(load_api_key(), base_url=getattr(args, "base_url", None)
                  or "https://api.melaps.system/v1")


def cmd_auth_login(args):
    save_config(args.api_key)
    print("Saved API key to ~/.config/melaps/config.toml")


def cmd_jobs_submit(args):
    with open(args.spec) as f:
        spec = yaml.safe_load(f)
    job = _client(args).submit_job(spec, idempotency_key=str(uuid.uuid4()))
    print(f"Submitted {job['id']}  ({job['status']})")
    print(f"Track it: melaps jobs status {job['id']}")


def cmd_jobs_status(args):
    print_json(_client(args).get_job(args.job_id))


def cmd_jobs_list(args):
    data = _client(args).list_jobs(limit=args.limit)
    rows = [[j["id"], j["status"], j.get("cluster", "-"),
             f"{j.get('gpus', 0)}x {j.get('gpu_type', 'H100')}",
             j.get("created_at", "")] for j in data.get("data", [])]
    print_table(rows, ["ID", "STATUS", "CLUSTER", "GPUS", "CREATED"])


def cmd_jobs_cancel(args):
    print_json(_client(args).cancel_job(args.job_id))


def cmd_jobs_metrics(args):
    print_json(_client(args).job_metrics(args.job_id))


def cmd_clusters_list(args):
    data = _client(args).list_clusters()
    rows = [[c["id"], c["region"], c["status"], f"{c['gpus_available']}/{c['gpus_total']}"]
            for c in data.get("data", [])]
    print_table(rows, ["CLUSTER", "REGION", "STATUS", "GPUS FREE"])


def cmd_reservations_create(args):
    spec = {"gpus": args.gpus, "months": args.months, "cluster": args.cluster}
    print_json(_client(args).create_reservation(spec, idempotency_key=str(uuid.uuid4())))


def cmd_usage(args):
    print_json(_client(args).usage(args.start, args.end))


def cmd_status(args):
    print_json(_client(args).status())


def build_parser():
    p = argparse.ArgumentParser(prog="melaps", description="Melaps System CLI")
    p.add_argument("--base-url", default="https://api.melaps.system/v1")
    sub = p.add_subparsers(dest="command", required=True)

    auth = sub.add_parser("auth")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True)
    login = auth_sub.add_parser("login")
    login.add_argument("--api-key", required=True)
    login.set_defaults(func=cmd_auth_login)

    jobs = sub.add_parser("jobs")
    jobs_sub = jobs.add_subparsers(dest="jobs_cmd", required=True)
    s = jobs_sub.add_parser("submit"); s.add_argument("spec"); s.set_defaults(func=cmd_jobs_submit)
    s = jobs_sub.add_parser("status"); s.add_argument("job_id"); s.set_defaults(func=cmd_jobs_status)
    s = jobs_sub.add_parser("list"); s.add_argument("--limit", type=int, default=20); s.set_defaults(func=cmd_jobs_list)
    s = jobs_sub.add_parser("cancel"); s.add_argument("job_id"); s.set_defaults(func=cmd_jobs_cancel)
    s = jobs_sub.add_parser("metrics"); s.add_argument("job_id"); s.set_defaults(func=cmd_jobs_metrics)

    clusters = sub.add_parser("clusters")
    clusters_sub = clusters.add_subparsers(dest="clusters_cmd", required=True)
    c = clusters_sub.add_parser("list"); c.set_defaults(func=cmd_clusters_list)

    res = sub.add_parser("reservations")
    res_sub = res.add_subparsers(dest="res_cmd", required=True)
    r = res_sub.add_parser("create")
    r.add_argument("--gpus", type=int, default=8)
    r.add_argument("--months", type=int, default=1)
    r.add_argument("--cluster", default="m1")
    r.set_defaults(func=cmd_reservations_create)

    u = sub.add_parser("usage")
    u.add_argument("--start", required=True); u.add_argument("--end", required=True)
    u.set_defaults(func=cmd_usage)

    st = sub.add_parser("status"); st.set_defaults(func=cmd_status)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except MelapsError as e:
        print(f"melaps: error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"melaps: error: file not found: {e.filename}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
