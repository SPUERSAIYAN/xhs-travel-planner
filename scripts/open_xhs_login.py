#!/usr/bin/env python3
"""Open Xiaohongshu in a browser so the user can scan-code login."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote


DEFAULT_URL = "https://www.xiaohongshu.com"
CHROME_PATHS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]


def find_browser() -> Path | None:
    for path in CHROME_PATHS:
        if path.exists():
            return path
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Open Xiaohongshu for user scan-code login.")
    parser.add_argument("--keyword", help="Optional search keyword to open after login, such as '长沙美食 避坑'.")
    parser.add_argument("--profile-dir", type=Path, default=Path(".xhs-browser-profile"))
    parser.add_argument("--debug-port", type=int, default=9222)
    args = parser.parse_args()

    url = DEFAULT_URL
    if args.keyword:
        url = f"https://www.xiaohongshu.com/search_result?keyword={quote(args.keyword)}&type=51"

    browser = find_browser()
    if browser is None:
        print("ERROR: Chrome or Edge was not found. Open Xiaohongshu manually and scan-code login.", file=sys.stderr)
        return 1

    args.profile_dir.mkdir(parents=True, exist_ok=True)
    subprocess.Popen(
        [
            str(browser),
            f"--remote-debugging-port={args.debug_port}",
            f"--user-data-dir={args.profile_dir.resolve()}",
            "--no-first-run",
            "--new-window",
            url,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Opened Xiaohongshu in {browser}")
    print("Ask the user to scan-code login in that browser, then confirm the note list is visible.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
