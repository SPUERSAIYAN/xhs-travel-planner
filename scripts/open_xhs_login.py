#!/usr/bin/env python3
"""Open Xiaohongshu in the user's regular browser profile."""

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
    parser = argparse.ArgumentParser(description="Open Xiaohongshu in the user's regular browser profile.")
    parser.add_argument("--keyword", help="Optional search keyword to open after login, such as '长沙美食 避坑'.")
    parser.add_argument("--profile-directory", help='Optional existing Chrome/Edge profile name, such as "Default" or "Profile 1".')
    parser.add_argument("--isolated-profile", action="store_true", help="Use a separate browser profile instead of the regular browser profile.")
    parser.add_argument("--profile-dir", type=Path, default=Path(".xhs-browser-profile"), help="Directory used only with --isolated-profile.")
    parser.add_argument("--debug-port", type=int, help="Optional remote debugging port, used only with --isolated-profile.")
    args = parser.parse_args()

    url = DEFAULT_URL
    if args.keyword:
        url = f"https://www.xiaohongshu.com/search_result?keyword={quote(args.keyword)}&type=51"

    browser = find_browser()
    if browser is None:
        print("ERROR: Chrome or Edge was not found. Open Xiaohongshu manually and scan-code login.", file=sys.stderr)
        return 1

    command = [str(browser), "--no-first-run", "--new-window"]
    if args.isolated_profile:
        args.profile_dir.mkdir(parents=True, exist_ok=True)
        command.append(f"--user-data-dir={args.profile_dir.resolve()}")
        if args.debug_port:
            command.append(f"--remote-debugging-port={args.debug_port}")
    elif args.profile_directory:
        command.append(f"--profile-directory={args.profile_directory}")
    command.append(url)

    subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"Opened Xiaohongshu in {browser}")
    if args.isolated_profile:
        print(f"Using isolated browser profile: {args.profile_dir.resolve()}")
    else:
        profile = args.profile_directory or "the regular/default browser profile"
        print(f"Using {profile}. If already logged in, Xiaohongshu should reuse that session.")
    print("Ask the user to confirm Xiaohongshu is logged in and the note list is visible.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
