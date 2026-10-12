"""Fail if Allure output contains credentials or card data.  Usage: python -m utils.scan_allure_results [dir ...]

Run after a test run (and before sharing a report). Exits 1 and prints only *which* file and *what kind*
of secret matched, never the secret itself.
"""
import sys
from pathlib import Path

from config.settings import settings
from utils.payment_data import card_values


def _secrets() -> dict[str, str]:
    found = {"password": settings.user_password, "e-mail": settings.user_email, **card_values()}
    return {kind: value for kind, value in found.items() if value}


def scan(directories: list[Path]) -> list[tuple[str, str]]:
    secrets = _secrets()
    hits = []
    for directory in directories:
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            data = path.read_bytes()
            hits += [(str(path), kind) for kind, value in secrets.items() if value.encode() in data]
    return hits


if __name__ == "__main__":
    dirs = [Path(a) for a in sys.argv[1:]] or [Path("allure-results")]
    hits = scan(dirs)
    for file, kind in hits:
        print(f"LEAK: {kind} found in {file}")
    print(f"{len(hits)} leak(s) found" if hits else "no credentials or card data found")
    sys.exit(1 if hits else 0)
