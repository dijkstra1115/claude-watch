"""Local Whisper transcription wrapper (openai-whisper).

The previous version of this module shipped a multipart HTTP client for the
Groq and OpenAI Whisper APIs. That has been removed — transcription now runs
entirely on the user's machine.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional


# `base.en` for English (English-only checkpoint, ~145 MB, faster on CPU).
# `medium`  for Chinese — multilingual `base` mangles zh too often, so we
# trade speed/disk (~1.5 GB) for usable Chinese transcripts.
_DEFAULT_MODEL = {"en": "base.en", "zh": "medium"}

SUPPORTED_LANGUAGES = tuple(_DEFAULT_MODEL.keys())


class WhisperError(Exception):
    pass


def model_for(language: str) -> str:
    """Map a supported language code to the Whisper checkpoint name."""
    if language not in _DEFAULT_MODEL:
        raise WhisperError(
            f"Unsupported language: {language!r} (supported: {', '.join(SUPPORTED_LANGUAGES)})"
        )
    return _DEFAULT_MODEL[language]


def transcribe_local(
    audio: Path,
    *,
    language: str,
    model_name: Optional[str] = None,
) -> list[dict]:
    """Run local openai-whisper.

    Returns: [{"t_start": float, "t_end": float, "text": str}, ...]
    Raises: WhisperError on missing package, model load failure, or decode failure.
    """
    try:
        import whisper as _whisper  # openai-whisper
    except ImportError as e:
        raise WhisperError(
            "openai-whisper not installed. Run: pip install -U openai-whisper"
        ) from e
    name = model_name or model_for(language)
    try:
        model = _whisper.load_model(name)
        result = model.transcribe(str(audio), language=language, verbose=False)
    except Exception as e:
        raise WhisperError(str(e)) from e
    return [
        {
            "t_start": float(s["start"]),
            "t_end": float(s["end"]),
            "text": s["text"].strip(),
        }
        for s in result.get("segments", [])
    ]
