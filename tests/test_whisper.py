import sys
import types
from unittest.mock import MagicMock, patch

import pytest

from scripts.whisper import (
    SUPPORTED_LANGUAGES,
    WhisperError,
    model_for,
    transcribe_local,
)


def test_supported_languages_are_en_and_zh():
    assert set(SUPPORTED_LANGUAGES) == {"en", "zh"}


def test_model_for_english_uses_en_only_checkpoint():
    assert model_for("en") == "base.en"


def test_model_for_chinese_uses_multilingual_checkpoint():
    assert model_for("zh") == "base"


def test_model_for_unsupported_language_raises():
    with pytest.raises(WhisperError):
        model_for("ja")


def _install_fake_whisper_module(monkeypatch, fake_model):
    """Inject a fake `whisper` module into sys.modules so `import whisper` returns it."""
    fake_mod = types.ModuleType("whisper")
    fake_mod.load_model = MagicMock(return_value=fake_model)
    monkeypatch.setitem(sys.modules, "whisper", fake_mod)
    return fake_mod


def test_transcribe_local_loads_en_model_and_passes_language(tmp_path, monkeypatch):
    audio = tmp_path / "a.m4a"
    audio.write_bytes(b"\x00")
    fake_model = MagicMock()
    fake_model.transcribe.return_value = {
        "segments": [{"start": 0.0, "end": 1.5, "text": " hello world "}]
    }
    fake_mod = _install_fake_whisper_module(monkeypatch, fake_model)

    out = transcribe_local(audio, language="en")

    fake_mod.load_model.assert_called_once_with("base.en")
    fake_model.transcribe.assert_called_once()
    kwargs = fake_model.transcribe.call_args.kwargs
    assert kwargs["language"] == "en"
    assert out == [{"t_start": 0.0, "t_end": 1.5, "text": "hello world"}]


def test_transcribe_local_loads_zh_multilingual_model(tmp_path, monkeypatch):
    audio = tmp_path / "a.m4a"
    audio.write_bytes(b"\x00")
    fake_model = MagicMock()
    fake_model.transcribe.return_value = {
        "segments": [{"start": 2.0, "end": 3.0, "text": "你好"}]
    }
    fake_mod = _install_fake_whisper_module(monkeypatch, fake_model)

    out = transcribe_local(audio, language="zh")

    fake_mod.load_model.assert_called_once_with("base")
    assert fake_model.transcribe.call_args.kwargs["language"] == "zh"
    assert out == [{"t_start": 2.0, "t_end": 3.0, "text": "你好"}]


def test_transcribe_local_explicit_model_name_overrides_default(tmp_path, monkeypatch):
    audio = tmp_path / "a.m4a"
    audio.write_bytes(b"\x00")
    fake_model = MagicMock()
    fake_model.transcribe.return_value = {"segments": []}
    fake_mod = _install_fake_whisper_module(monkeypatch, fake_model)

    transcribe_local(audio, language="en", model_name="medium.en")

    fake_mod.load_model.assert_called_once_with("medium.en")


def test_transcribe_local_wraps_missing_package_as_whisper_error(tmp_path, monkeypatch):
    # Ensure `import whisper` raises ImportError inside the function.
    monkeypatch.setitem(sys.modules, "whisper", None)
    with pytest.raises(WhisperError):
        transcribe_local(tmp_path / "x.m4a", language="en")


def test_transcribe_local_wraps_transcribe_failures(tmp_path, monkeypatch):
    audio = tmp_path / "a.m4a"
    audio.write_bytes(b"\x00")
    fake_model = MagicMock()
    fake_model.transcribe.side_effect = RuntimeError("decode boom")
    _install_fake_whisper_module(monkeypatch, fake_model)
    with pytest.raises(WhisperError):
        transcribe_local(audio, language="en")
