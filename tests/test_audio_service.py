from unittest.mock import patch

from services.audio_service import voice_text


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


from services.audio_service import audio_url_from_static_path


def test_invalid_audio_path():
    assert audio_url_from_static_path(None) is None


@patch("services.audio_service.url_for")
@patch("services.audio_service.os.path.getsize")
@patch("services.audio_service.os.path.isfile")
def test_existing_audio(
    mock_isfile,
    mock_size,
    mock_url,
):
    mock_isfile.return_value = True
    mock_size.return_value = 100
    mock_url.return_value = "/static/audio/test.mp3"

    result = audio_url_from_static_path("static/audio/test.mp3")

    assert result == "/static/audio/test.mp3"
    mock_url.assert_called_once_with("static", filename="audio/test.mp3")


from services.audio_service import generate_telugu_audio


@patch("services.audio_service.gTTS")
def test_audio_generation_failure(
    mock_gtts,
    sample_telugu_data,
    app,
):
    mock_gtts.side_effect = RuntimeError()

    result = generate_telugu_audio(
        sample_telugu_data,
        "Scheme",
    )

    assert result is None