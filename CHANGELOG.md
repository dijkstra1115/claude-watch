# Changelog

All notable changes to `claude-watch` are documented here.

## [0.1.5] — 2026-05-13

### Changed
- Bump default Chinese Whisper checkpoint from `base` (~140 MB) to `medium` (~1.5 GB). The multilingual `base` model produced unusable transcripts on real lecture audio (mangled CJK, English fragments substituted for Chinese phrases). `medium` is significantly slower on CPU but the only tier that's actually accurate enough to read.

## [0.1.4] — 2026-05-13

### Fixed
- Rename `scripts/whisper.py` to `scripts/local_whisper.py` to avoid a Python import shadow: when running `python scripts/watch.py`, Python adds `scripts/` to `sys.path[0]`, so `import whisper` inside the wrapper was loading our own module instead of the third-party `openai-whisper`, causing `AttributeError: module 'whisper' has no attribute 'load_model'` mid-run.
- Explicit `encoding="utf-8"` on all `read_text` / `write_text` calls in `watch.py` and `library.py`. On Windows, Python defaults to the locale codec (e.g. `cp950` Big5 on zh-TW systems), which can't encode CJK characters in transcripts/manifests and crashed mid-pipeline with `UnicodeEncodeError`.

## [0.1.3] — 2026-05-13

### Changed
- Transcription now runs **locally** via `openai-whisper`. The Groq and OpenAI Whisper HTTP clients have been removed, along with all API-key handling and the `~/.config/claude-watch/.env` scaffold.
- New `--language {en,zh}` flag on `watch.py` selects the spoken language. English uses the `base.en` checkpoint, Chinese uses the multilingual `base` checkpoint.
- `setup.py` preflight now probes for the `whisper` Python package and prints `pip install -U openai-whisper` when missing.
- SKILL.md instructs Claude to ask the user for the language via `AskUserQuestion` when it isn't obvious.

### Removed
- `--whisper groq|openai` flag, `pick_backend`, the multipart HTTP client, and the `.env`-based API-key configuration.

## [0.1.0] — 2026-05-03

### Added
- `/claude-watch <url-or-path> [topic]` slash command that produces structured study notes.
- Scene-aware frame extraction: ffmpeg scene detection (default threshold 0.30) with a coverage floor (synthetic boundaries every 45s across long static gaps) and a budget cap (default 80 frames, drops lowest-scoring detected scenes first; floor boundaries are always preserved).
- Persistent library at `~/claude-watch/library/<slug>/` with cached download, transcript, and scenes — re-runs only regenerate frames + notes.
- Slug rule `YYYY-MM-DD-<title>-<sha1(source+focus)[:4]>` so chronological + collision-safe across focus-range re-watches.
- Native caption pull via yt-dlp (manual + auto-subs) with VTT dedupe.
- Whisper fallback: Groq `whisper-large-v3` (preferred), OpenAI `whisper-1` (alt). Stdlib HTTP clients — no SDKs.
- `--start`/`--end` focused mode with denser coverage floor (15s vs 45s default).
- `setup.py` preflight (`--check` / `--json`) with cross-platform installer (`brew` on macOS auto-runs; `apt`/`dnf`/`winget`/`pip` commands printed elsewhere).
- Three-surface distribution: Claude Code plugin, claude.ai `.skill` bundle (built by `scripts/build-skill.sh`), Codex skill.
- SessionStart hook prints a one-liner only when remediation is needed.
- Strict notes template baked into SKILL.md: TLDR, Key Concepts, per-scene Notes (On screen + Said + Synthesis), Code & Commands, Diagrams Referenced, Open Questions.
