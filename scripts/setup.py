"""Cross-platform preflight + installer for claude-watch.

Exit codes (read by SKILL.md):
    0  ready
    2  needs_install

Transcription runs locally via openai-whisper, so no API keys are required.
The preflight verifies that ffmpeg/ffprobe/yt-dlp are on PATH and that the
`whisper` Python package is importable.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".config" / "claude-watch"
LIBRARY_ROOT = Path.home() / "claude-watch" / "library"
REQUIRED_BINS = ("ffmpeg", "ffprobe", "yt-dlp")


def _which(name: str) -> Optional[str]:
    return shutil.which(name)


def _whisper_importable() -> bool:
    return importlib.util.find_spec("whisper") is not None


def status_for() -> dict:
    missing_bins = [b for b in REQUIRED_BINS if not _which(b)]
    whisper_ok = _whisper_importable()
    warnings: list[str] = []
    if not whisper_ok:
        warnings.append("missing_whisper_pkg")
    status = "needs_install" if (missing_bins or not whisper_ok) else "ready"
    return {
        "status": status,
        "missing_binaries": missing_bins,
        "whisper_installed": whisper_ok,
        "warnings": warnings,
        "platform": platform.system().lower(),
    }


def exit_code_for(status: str) -> int:
    return {"ready": 0, "needs_install": 2}[status]


def _print_install_instructions() -> None:
    sysname = platform.system().lower()
    missing = [b for b in REQUIRED_BINS if not _which(b)]
    whisper_missing = not _whisper_importable()
    if not missing and not whisper_missing:
        return
    if missing:
        if sysname == "darwin":
            if _which("brew"):
                print(f"Run: brew install {' '.join(missing)}", file=sys.stderr)
            else:
                print("Homebrew not found. Install brew, then re-run setup.py.", file=sys.stderr)
        elif sysname == "linux":
            print("Run one of:", file=sys.stderr)
            print(f"  sudo apt-get install -y {' '.join(missing)}", file=sys.stderr)
            print(f"  sudo dnf install -y {' '.join(missing)}", file=sys.stderr)
            print(f"  pipx install yt-dlp  # (if 'yt-dlp' isn't in apt)", file=sys.stderr)
        elif sysname == "windows":
            print("Run:", file=sys.stderr)
            for b in missing:
                if b == "yt-dlp":
                    print(f"  pip install --user yt-dlp", file=sys.stderr)
                else:
                    print(f"  winget install --id Gyan.FFmpeg", file=sys.stderr)
        else:
            print(
                f"Unsupported platform '{sysname}'. Install manually: {', '.join(missing)}",
                file=sys.stderr,
            )
    if whisper_missing:
        print("Run: pip install -U openai-whisper", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true", help="Silent on success; exit code reflects state")
    p.add_argument("--json", action="store_true", help="Emit structured JSON status")
    args = p.parse_args(argv)
    s = status_for()
    if args.json:
        print(json.dumps(s))
        return exit_code_for(s["status"])
    if args.check:
        return exit_code_for(s["status"])
    # Full install / scaffold flow
    LIBRARY_ROOT.mkdir(parents=True, exist_ok=True)
    _print_install_instructions()
    s2 = status_for()
    return exit_code_for(s2["status"])


if __name__ == "__main__":
    raise SystemExit(main())
