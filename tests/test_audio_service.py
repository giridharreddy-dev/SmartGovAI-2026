from unittest.mock import patch, MagicMock

from services.audio_service import voice_text, cleanup_old_audio, get_relative_audio_path


def test_voice_text(sample_telugu_data):
    result = voice_text(sample_telugu_data, "Aarogyasri")

    assert "Aarogyasri" in result
    assert "Eligible citizens" in result


@patch("services.audio_service.gTTS")
def test_generate_audio(mock_gtts, sample_telugu_data):
    from services.audio_service import generate_telugu_audio

    mock_instance = mock_gtts.return_value

    generate_telugu_audio(sample_telugu_data, "Scheme")

    mock_instance.save.assert_called_once()


def test_invalid_audio_path():
    assert get_relative_audio_path(None) is None


@patch("services.audio_service.os.path.getsize")
@patch("services.audio_service.os.path.isfile")
def test_existing_audio(
    mock_isfile,
    mock_size,
):
    mock_isfile.return_value = True
    mock_size.return_value = 100

    result = get_relative_audio_path("static/audio/test.mp3")

    assert result == "audio/test.mp3"


@patch("services.audio_service.gTTS")
def test_audio_generation_failure(
    mock_gtts,
    sample_telugu_data,
):
    mock_gtts.side_effect = RuntimeError()
    from services.audio_service import generate_telugu_audio

    result = generate_telugu_audio(
        sample_telugu_data,
        "Scheme",
    )

    assert result is None


@patch("services.audio_service.os.remove")
@patch("services.audio_service.os.stat")
@patch("services.audio_service.os.path.isfile")
@patch("services.audio_service.os.listdir")
@patch("services.audio_service.os.path.exists")
@patch("services.audio_service.time.time")
def test_cleanup_old_audio(mock_time, mock_exists, mock_listdir, mock_isfile, mock_stat, mock_remove):
    """Verify that old audio files are purged while recent ones are preserved."""
    mock_exists.return_value = True
    mock_time.return_value = 1000000.0  # arbitrary current time
    mock_listdir.return_value = ["old_file.mp3", "new_file.mp3", "keep_me.txt"]
    mock_isfile.return_value = True

    def fake_stat(filepath):
        mock_st = MagicMock()
        if "old_file.mp3" in filepath:
            # 10 days old
            mock_st.st_mtime = 1000000.0 - (10 * 86400)
        else:
            # 1 day old
            mock_st.st_mtime = 1000000.0 - (1 * 86400)
        return mock_st

    mock_stat.side_effect = fake_stat

    cleanup_old_audio(days=7)

    # remove should only be called once, specifically for old_file.mp3
    assert mock_remove.call_count == 1
    args, _ = mock_remove.call_args
    assert "old_file.mp3" in args[0]