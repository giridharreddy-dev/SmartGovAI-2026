import json
import httpx
import threading
import pytest
from unittest.mock import MagicMock, patch
from google.genai import Client
from services import gemini_service
from services.gemini_service import simplify_document
VALID_RESULT = {lang: {key: "example" for key in ("eligibility", "benefits", "documents", "steps")} for lang in ("simplified", "telugu")}
def _ok_body():
    return {"candidates": [{"content": {"parts": [{"text": json.dumps(VALID_RESULT)}]}}]}
@pytest.fixture(autouse=True)
def isolated_calls(monkeypatch):
    gemini_service._gemini_response_cache.clear()
    gemini_service._gemini_pending.clear()
    monkeypatch.setattr(gemini_service, "GEMINI_RETRY_BASE_DELAY", 0.0)
    monkeypatch.setattr(gemini_service, "GEMINI_RETRY_MAX_DELAY", 0.0)
    yield
    gemini_service._gemini_response_cache.clear()
    gemini_service._gemini_pending.clear()

class ScriptedTransport(httpx.BaseTransport):
    """Returns scripted responses in order; tracks how many requests ran."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def handle_request(self, request):
        self.calls += 1
        return self.responses.pop(0)


def _client_with_transport(transport):
    """Return a real google.genai.Client backed by a scripted httpx transport."""
    return Client(
        api_key="test-key",
        http_options={"httpx_client": httpx.Client(transport=transport)},
    )


# ---------------------------------------------------------------------------
# Retry configuration and application-level retry behavior.
#
# These use a REAL google.genai.Client wired to a scripted httpx transport,
# so the genuine application retry loop runs without network access or
# Gemini calls. Patched get_client supplies the client to simplify_document.
# ---------------------------------------------------------------------------

def _transport_client(responses):
    transport = ScriptedTransport(responses)
    return _client_with_transport(transport), transport


@patch("services.gemini_service.get_client")
def test_timeout_and_single_sdk_attempt(mock_get_client):
    """The application owns retries; SDK attempts must not multiply them."""
    response = MagicMock()
    response.text = json.dumps(VALID_RESULT)
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = response
    mock_get_client.return_value = mock_client

    simplify_document("abc", "scheme")

    config = mock_client.models.generate_content.call_args.kwargs["config"]
    ro = config.http_options.retry_options
    assert ro.attempts == 1
    # SDK default retryable codes remain: 408, 429, 500, 502, 503, 504
    assert ro.http_status_codes is None
    # timeout is untouched at 15000 ms
    assert config.http_options.timeout == 15000


@patch("services.gemini_service.get_client")
def test_503_is_retried_and_eventually_succeeds(mock_get_client):
    """A 503 followed by success is retried and returns the result."""
    client, transport = _transport_client([
        httpx.Response(503, request=httpx.Request("POST", "http://x"), json={"error": {"code": 503, "message": "unavailable"}}),
        httpx.Response(200, request=httpx.Request("POST", "http://x"), json=_ok_body()),
    ])
    mock_get_client.return_value = client

    result = simplify_document("abc", "scheme")

    assert transport.calls == 2
    assert "simplified" in result


@patch("services.gemini_service.get_client")
def test_429_is_retried(mock_get_client):
    """A 429 is retried and can succeed on the next attempt."""
    client, transport = _transport_client([
        httpx.Response(429, request=httpx.Request("POST", "http://x"), json={"error": {"code": 429, "message": "rate limited"}}),
        httpx.Response(200, request=httpx.Request("POST", "http://x"), json=_ok_body()),
    ])
    mock_get_client.return_value = client

    result = simplify_document("abc", "scheme")

    assert transport.calls == 2
    assert "simplified" in result


@patch("services.gemini_service.get_client")
def test_permanent_400_is_not_retried(mock_get_client):
    """A permanent 400 raises immediately and is NOT retried."""
    client, transport = _transport_client([
        httpx.Response(400, request=httpx.Request("POST", "http://x"), json={"error": {"code": 400, "message": "bad request"}}),
    ])
    mock_get_client.return_value = client

    with pytest.raises(Exception):
        simplify_document("abc", "scheme")

    # Only a single attempt: no retry on permanent 4xx
    assert transport.calls == 1


@patch("services.gemini_service.get_client")
def test_timeout_is_retryable(mock_get_client):
    """A transport timeout is retried within the application retry budget."""
    class TimeoutTransport(httpx.BaseTransport):
        def __init__(self):
            self.calls = 0
        def handle_request(self, request):
            self.calls += 1
            if self.calls == 1:
                raise httpx.TimeoutException("timed out", request=request)
            return httpx.Response(200, request=request, json=_ok_body())

    transport = TimeoutTransport()
    client = _client_with_transport(transport)
    mock_get_client.return_value = client

    result = simplify_document("abc", "scheme")

    assert transport.calls == 2
    assert "simplified" in result


@patch("services.gemini_service.get_client")
def test_three_failed_attempts_propagate_failure(mock_get_client):
    """After the configured 3 attempts all fail, the error propagates."""
    client, transport = _transport_client([
        httpx.Response(503, request=httpx.Request("POST", "http://x"), json={"error": {"code": 503, "message": "unavailable"}}),
        httpx.Response(503, request=httpx.Request("POST", "http://x"), json={"error": {"code": 503, "message": "unavailable"}}),
        httpx.Response(503, request=httpx.Request("POST", "http://x"), json={"error": {"code": 503, "message": "unavailable"}}),
        httpx.Response(200, request=httpx.Request("POST", "http://x"), json=_ok_body()),  # would-be 4th, never reached
    ])
    mock_get_client.return_value = client

    with pytest.raises(Exception):
        simplify_document("abc", "scheme")

    # Exactly 3 attempts (3 attempts = original + 2 retries), no silent 4th call
    assert transport.calls == 3


@patch("services.gemini_service.get_client")
def test_cache_stores_result_after_retry(mock_get_client):
    """After a retried success, the result is cached and a duplicate request hits the cache."""
    from services import gemini_service as gs

    client, transport = _transport_client([
        httpx.Response(503, request=httpx.Request("POST", "http://x"), json={"error": {"code": 503, "message": "unavailable"}}),
        httpx.Response(200, request=httpx.Request("POST", "http://x"), json=_ok_body()),
    ])
    mock_get_client.return_value = client

    # Fresh caches for determinism
    gs._gemini_response_cache.clear()
    gs._gemini_pending.clear()

    r1 = simplify_document("identical-text", "scheme")  # first call: 503 -> 200
    r2 = simplify_document("identical-text", "scheme")  # should hit cache

    assert gs._gemini_response_cache
    assert ("simplified" in r1) and ("simplified" in r2)
    # Transport saw 2 requests (1 retry + original); the second simplify_document hit the cache: no new calls
    assert transport.calls == 2


@patch("services.gemini_service.get_client")
def test_coalescing_waiter_times_out_cleanly(mock_get_client, monkeypatch):
    """A waiter whose pending Event never fires exits via timeout, not a hang."""
    from services import gemini_service as gs

    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    # Use a tiny wait so the test doesn't actually block ~60s.
    monkeypatch.setattr(gs, "_GEMINI_COALESCE_WAIT_TIMEOUT", 0.1)

    gs._gemini_response_cache.clear()
    gs._gemini_pending.clear()

    # Build a leader that never finishes: register a pending Event under the
    # exact key simplify_document will compute (same text, scheme, and client),
    # and never set it. The leader is never actually run.
    cache_key = gs._make_gemini_cache_key("text", "scheme") + f":{id(mock_client)}"
    never_set = threading.Event()
    gs._gemini_pending[cache_key] = never_set

    # This call becomes a waiter (pending key already exists). It must hit the
    # timeout and raise instead of hanging. The cache is empty, so it raises.
    with pytest.raises(RuntimeError, match="Timed out waiting"):
        gs.simplify_document("text", "scheme")

    gs._gemini_response_cache.clear()
    gs._gemini_pending.clear()


@patch("services.gemini_service.get_client")
def test_coalescing_normal_waiter_gets_leader_result(mock_get_client, monkeypatch):
    """A waiter whose leader completes normally returns the leader's cache result."""
    from services import gemini_service as gs

    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    monkeypatch.setattr(gs, "_GEMINI_COALESCE_WAIT_TIMEOUT", 5.0)

    gs._gemini_response_cache.clear()
    gs._gemini_pending.clear()

    # Simulate a real leader: pending event exists but cache is empty when the
    # waiter starts. The waiter blocks in wait(); a background thread then
    # completes the "leader" (sets the event + writes the cache), so the waiter
    # should wake, find the cache, and return it.
    cache_key = gs._make_gemini_cache_key("text", "scheme") + f":{id(mock_client)}"
    event = threading.Event()
    gs._gemini_pending[cache_key] = event

    def complete_leader():
        # Give the waiter a moment to enter wait(), then finish as the leader.
        import time
        time.sleep(0.1)
        with gs._gemini_lock:
            gs._gemini_response_cache[cache_key] = {"simplified": {}, "telugu": {}}
        event.set()

    t = threading.Thread(target=complete_leader)
    t.start()
    result = gs.simplify_document("text", "scheme")
    t.join(timeout=5)

    assert result == {"simplified": {}, "telugu": {}}

    gs._gemini_response_cache.clear()
    gs._gemini_pending.clear()