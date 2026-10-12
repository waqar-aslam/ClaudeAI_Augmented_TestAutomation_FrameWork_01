"""Digest Allure results into a compact failure table for the failure-analysis agent.

Usage: python -m utils.summarise_allure [results_dir]      (default: allure-results)

* Refuses to run if the results contain credentials or card data (see utils.scan_allure_results).
* Keeps only the newest result per test (results accumulate across runs).
* Prints a markdown table of failed/broken tests plus xfail/skip counts. The "hint" column is a
  deterministic first guess; the agent confirms or overrides it using the evidence.
"""
import json
import re
import sys
from pathlib import Path

from utils.scan_allure_results import _secrets, scan

# (regex on the failure message, category hint, reason) - first match wins.
RULES = [
    (r"XPASS\(strict\)", "Known defect fixed?", "strict xfail passed: the defect may be fixed, remove the xfail after review"),
    (r"PRECONDITION|USER_EMAIL / USER_PASSWORD not set", "Test-data issue", "documented data precondition is not met"),
    (r"API login failed: HTTP 4\d\d", "Test-data issue", "login rejected: check the credentials in .env"),
    (r"HTTP 5\d\d|ECONN|ENOTFOUND|ERR_NAME_NOT_RESOLVED|ERR_CONNECTION|net::ERR|getaddrinfo", "Environment issue",
     "backend/network error"),
    (r"strict mode violation|waiting for locator|Timeout \d+ms exceeded|TimeoutError", "Automation defect",
     "locator/wait problem (check the screenshot for an application change)"),
    (r"AssertionError|assert ", "Application defect (candidate)",
     "assertion on application behaviour failed; compare with the defect register"),
]


def _first_line(message: str, secrets: list[str]) -> str:
    for secret in secrets:
        message = message.replace(secret, "<redacted>")
    line = next((ln.strip() for ln in message.splitlines() if ln.strip()), "")
    return re.sub(r"\s+", " ", line)[:300]


def _hint(message: str, status: str) -> tuple[str, str]:
    if status == "failed" and not message:
        # allure-pytest stores no message for a strict XPASS (a failed test with no exception).
        return "Known defect fixed? (suspected)", "failed with no error message: likely a strict xfail that passed; confirm in the console output"
    for pattern, category, reason in RULES:
        if re.search(pattern, message):
            return category, reason
    return "Unclassified", "no deterministic rule matched; needs manual analysis"


def _nodeid(full_name: str) -> str:
    module, _, test = full_name.partition("#")
    return f"{module.replace('.', '/')}.py::{test}"


def summarise(results_dir: Path) -> str:
    secrets = [v for v in (_secrets().values()) if v]
    latest: dict[str, dict] = {}
    for path in results_dir.glob("*-result.json"):
        data = json.loads(path.read_text(encoding="utf8"))
        key = data.get("historyId", data["uuid"])
        if key not in latest or data["stop"] > latest[key]["stop"]:
            latest[key] = data

    counts: dict[str, int] = {}
    failures = []
    for data in latest.values():
        message = data.get("statusDetails", {}).get("message", "")
        status = "xfail" if data["status"] == "skipped" and message.startswith("XFAIL") else data["status"]
        counts[status] = counts.get(status, 0) + 1
        if data["status"] in ("failed", "broken"):
            failures.append((data, message))

    out = ["## Run summary", ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) or "no results", ""]
    if not failures:
        out.append("No failed or broken tests.")
        return "\n".join(out)

    out += ["## Failed / broken tests", "",
            "| Status | Node id | Message (first line) | Hint | Why | Attachments |", "|---|---|---|---|---|---|"]
    for data, message in sorted(failures, key=lambda f: f[0]["fullName"]):
        category, reason = _hint(message, data["status"])
        attachments = [a["name"] for a in data.get("attachments", [])]
        params = [p["value"] for p in data.get("parameters", []) if p["name"] != "browser_name"]
        node = _nodeid(data["fullName"]) + (f" (params: {params})" if params else "")
        out.append(f"| {data['status']} | `{node}` | {_first_line(message, secrets).replace('|', '/')} "
                   f"| {category} | {reason} | {', '.join(attachments) or '-'} |")
    return "\n".join(out)


if __name__ == "__main__":
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("allure-results")
    leaks = scan([directory])
    if leaks:
        print("REFUSING TO SUMMARISE: credentials or card data found in results:")
        for file, kind in leaks:
            print(f"  {kind} in {file}")
        sys.exit(2)
    print(summarise(directory))
