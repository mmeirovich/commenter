#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

TRUE_VALUES = {"1", "true", "t", "yes", "y", "on"}
FALSE_VALUES = {"0", "false", "f", "no", "n", "off"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload variables from a local .env file to GitHub Actions secrets."
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to the local .env file to read. Defaults to .env.",
    )
    parser.add_argument(
        "--repo",
        help="Optional GitHub repo in OWNER/REPO format. Defaults to the current repo.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the secrets that would be uploaded without changing GitHub.",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Secret name to skip. Repeat the flag to exclude multiple names.",
    )
    return parser.parse_args()


def require_gh_cli() -> None:
    if shutil.which("gh") is None:
        raise SystemExit("GitHub CLI (`gh`) is required but was not found in PATH.")


def require_github_auth() -> None:
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("GitHub CLI is not authenticated. Run `gh auth login` and try again.")


def load_env_vars(env_file: Path, excluded: set[str]) -> dict[str, str]:
    if not env_file.exists():
        raise SystemExit(f"Env file not found: {env_file}")

    raw_values = dotenv_values(env_file)
    env_vars: dict[str, str] = {}

    for key, value in raw_values.items():
        if key in excluded:
            continue
        if value is None:
            raise SystemExit(f"Variable `{key}` in {env_file} is missing a value.")
        env_vars[key] = value

    if not env_vars:
        raise SystemExit(f"No variables found in {env_file}.")

    return env_vars


def validate_known_runtime_vars(env_vars: dict[str, str]) -> None:
    debug_value = env_vars.get("DEBUG")
    if debug_value is not None:
        normalized_debug = debug_value.strip().lower()
        if normalized_debug not in TRUE_VALUES | FALSE_VALUES:
            raise SystemExit(
                "Invalid DEBUG value in the env file. Use true/false, yes/no, on/off, or 1/0."
            )

    port_value = env_vars.get("PORT")
    if port_value is not None:
        try:
            port = int(port_value)
        except ValueError as exc:
            raise SystemExit(
                "Invalid PORT value in the env file. PORT must be an integer."
            ) from exc
        if not 1 <= port <= 65535:
            raise SystemExit(
                "Invalid PORT value in the env file. PORT must be between 1 and 65535."
            )


def upload_secret(name: str, value: str, repo: str | None) -> None:
    command = ["gh", "secret", "set", name, "--body", value]
    if repo:
        command.extend(["--repo", repo])
    subprocess.run(command, check=True)


def main() -> int:
    args = parse_args()
    env_file = Path(args.env_file).expanduser().resolve()
    excluded = set(args.exclude)

    require_gh_cli()
    if not args.dry_run:
        require_github_auth()

    env_vars = load_env_vars(env_file, excluded)
    validate_known_runtime_vars(env_vars)

    if args.dry_run:
        for name in env_vars:
            print(name)
        print(f"\nDry run: {len(env_vars)} secret(s) would be uploaded from {env_file}.")
        return 0

    for name, value in env_vars.items():
        upload_secret(name, value, args.repo)
        print(f"Uploaded {name}")

    print(f"\nUploaded {len(env_vars)} secret(s) from {env_file}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
