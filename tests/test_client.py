"""Tests for the API client.

No test reaches the live API. Each one gives the client a fake transport that
returns either a recorded response from ``tests/fixtures`` or a response built
in the test, and records the requests the client makes.
"""

import json
from pathlib import Path
from unittest import mock

from apprenticeship_explorer.client import (
    BASE_URL,
    DEFAULT_TIMEOUT,
    ApiClient,
    Response,
    urllib_transport,
)

DATA_SET_ID = "1d419801-a90e-f970-9335-a13623faccbe"
FIXTURES = Path(__file__).parent / "fixtures"


class FakeTransport:
    """Stand in for the network, returning queued responses and recording each call.

    Args:
        responses: What to return for each request, in order. An exception in
            the queue is raised instead of returned.
    """

    def __init__(self, *responses):
        """Queue the responses."""
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url, timeout):
        """Record the request and return or raise the next queued response."""
        self.calls.append((url, timeout))
        reply = self.responses.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


def ok(body):
    """Return a 200 response with the given body as bytes."""
    return Response(200, body if isinstance(body, bytes) else body.encode())


def recorded(name):
    """Return a 200 response whose body is a recorded fixture file."""
    return ok((FIXTURES / name).read_bytes())


def test_summary_requests_the_data_set_endpoint():
    """The summary comes from ``/data-sets/{id}`` and is decoded from JSON."""
    transport = FakeTransport(ok('{"id": "abc"}'))
    assert ApiClient(transport).summary("abc") == {"id": "abc"}
    assert transport.calls[0][0] == f"{BASE_URL}/data-sets/abc"


def test_metadata_without_a_version_asks_for_the_latest():
    """With no version given, no version parameter is sent."""
    transport = FakeTransport(ok("{}"))
    ApiClient(transport).metadata("abc")
    assert transport.calls[0][0] == f"{BASE_URL}/data-sets/abc/meta"


def test_metadata_can_be_pinned_to_a_version():
    """A pinned version is sent as ``dataSetVersion``."""
    transport = FakeTransport(ok("{}"))
    ApiClient(transport).metadata("abc", version="2.0.2")
    assert transport.calls[0][0] == f"{BASE_URL}/data-sets/abc/meta?dataSetVersion=2.0.2"


def test_csv_can_be_pinned_to_a_version():
    """The CSV is fetched for the pinned version and returned as text."""
    transport = FakeTransport(ok("time_period\n202122\n"))
    text = ApiClient(transport).csv("abc", version="2.0.2")
    assert transport.calls[0][0] == f"{BASE_URL}/data-sets/abc/csv?dataSetVersion=2.0.2"
    assert text == "time_period\n202122\n"


def test_csv_byte_order_mark_is_removed():
    """A byte order mark would otherwise become part of the first column's name."""
    transport = FakeTransport(ok(b"\xef\xbb\xbftime_period\n202122\n"))
    assert ApiClient(transport).csv("abc").startswith("time_period")


def test_versions_are_collected_from_every_page():
    """The versions endpoint is paginated, so every page is requested in turn."""
    page_one = '{"paging": {"totalPages": 2}, "results": [{"version": "2.0"}]}'
    page_two = '{"paging": {"totalPages": 2}, "results": [{"version": "1.0"}]}'
    transport = FakeTransport(ok(page_one), ok(page_two))
    versions = ApiClient(transport).versions("abc")
    assert [v["version"] for v in versions] == ["2.0", "1.0"]
    assert [url for url, _ in transport.calls] == [
        f"{BASE_URL}/data-sets/abc/versions?page=1&pageSize=20",
        f"{BASE_URL}/data-sets/abc/versions?page=2&pageSize=20",
    ]


def test_every_request_sets_the_timeout():
    """Each endpoint passes the client's timeout to the transport."""
    one_page = '{"paging": {"totalPages": 1}, "results": []}'
    transport = FakeTransport(ok("{}"), ok("{}"), ok(one_page), ok("a\n"))
    client = ApiClient(transport, timeout=12.5)
    client.summary("abc")
    client.metadata("abc")
    client.versions("abc")
    client.csv("abc")
    assert [timeout for _, timeout in transport.calls] == [12.5] * 4


def test_a_timeout_is_set_by_default():
    """Without a chosen timeout, requests still have one."""
    transport = FakeTransport(ok("{}"))
    ApiClient(transport).summary("abc")
    assert transport.calls[0][1] == DEFAULT_TIMEOUT > 0


def test_recorded_summary_is_for_the_apprenticeships_data_set():
    """The recorded summary response decodes to the data set it was recorded for."""
    summary = ApiClient(FakeTransport(recorded("summary.json"))).summary(DATA_SET_ID)
    assert summary["id"] == DATA_SET_ID


def test_recorded_versions_are_all_returned():
    """Every version in the recorded response comes back, each with a version number."""
    body = (FIXTURES / "versions.json").read_bytes()
    versions = ApiClient(FakeTransport(ok(body))).versions(DATA_SET_ID)
    assert len(versions) == json.loads(body)["paging"]["totalResults"]
    assert all("version" in v for v in versions)


def test_recorded_csv_has_the_expected_columns():
    """The recorded CSV starts with the published header row."""
    text = ApiClient(FakeTransport(recorded("data-set-head.csv"))).csv(DATA_SET_ID, "2.0.2")
    header = text.splitlines()[0].split(",")
    assert "time_period" in header
    assert "start_count" in header


def test_urllib_transport_passes_the_timeout_and_returns_the_body():
    """The real transport hands the timeout to ``urlopen``, which is mocked here."""
    reply = mock.MagicMock(status=200)
    reply.read.return_value = b"{}"
    with mock.patch("urllib.request.urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value = reply
        response = urllib_transport("https://example.test/x", 7.0)
    urlopen.assert_called_once_with("https://example.test/x", timeout=7.0)
    assert response == Response(200, b"{}")