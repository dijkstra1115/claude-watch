import json
from unittest.mock import patch

from scripts import setup as setup_mod


def test_status_for_returns_ready_when_everything_present():
    with patch.object(setup_mod, "_which", side_effect=lambda x: f"/bin/{x}"):
        with patch.object(setup_mod, "_whisper_importable", return_value=True):
            s = setup_mod.status_for()
    assert s["status"] == "ready"
    assert s["missing_binaries"] == []
    assert s["whisper_installed"] is True
    assert s["warnings"] == []


def test_status_for_flags_missing_binaries():
    def fake_which(x):
        return f"/bin/{x}" if x == "ffprobe" else None
    with patch.object(setup_mod, "_which", side_effect=fake_which):
        with patch.object(setup_mod, "_whisper_importable", return_value=True):
            s = setup_mod.status_for()
    assert s["status"] == "needs_install"
    assert "ffmpeg" in s["missing_binaries"]
    assert "yt-dlp" in s["missing_binaries"]


def test_status_for_flags_missing_whisper_package():
    with patch.object(setup_mod, "_which", side_effect=lambda x: f"/bin/{x}"):
        with patch.object(setup_mod, "_whisper_importable", return_value=False):
            s = setup_mod.status_for()
    assert s["status"] == "needs_install"
    assert s["whisper_installed"] is False
    assert s["warnings"] == ["missing_whisper_pkg"]


def test_status_for_needs_install_when_both_missing():
    with patch.object(setup_mod, "_which", return_value=None):
        with patch.object(setup_mod, "_whisper_importable", return_value=False):
            s = setup_mod.status_for()
    assert s["status"] == "needs_install"
    assert s["missing_binaries"] and "missing_whisper_pkg" in s["warnings"]


def test_check_exit_code_maps_status_to_table():
    assert setup_mod.exit_code_for("ready") == 0
    assert setup_mod.exit_code_for("needs_install") == 2


def test_json_output_shape(capsys):
    with patch.object(setup_mod, "_which", side_effect=lambda x: f"/bin/{x}"):
        with patch.object(setup_mod, "_whisper_importable", return_value=True):
            rc = setup_mod.main(["--check", "--json"])
    captured = capsys.readouterr().out
    payload = json.loads(captured)
    assert payload["status"] == "ready"
    assert "platform" in payload
    assert rc == 0


def test_check_silent_on_success(capsys):
    with patch.object(setup_mod, "_which", side_effect=lambda x: f"/bin/{x}"):
        with patch.object(setup_mod, "_whisper_importable", return_value=True):
            rc = setup_mod.main(["--check"])
    out = capsys.readouterr().out
    assert out == "" and rc == 0
