"""
Invoke style task file for calling tools from poetry
as scripts.
"""

import argparse
import subprocess


def build_cython():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="help")
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args()
    cmd = ["python", "tools/build_cython.py", "build_ext", "--inplace"]
    if args.dry_run:
        cmd.append("dry_run")

    subprocess.run(cmd)
