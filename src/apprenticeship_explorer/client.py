"""Retrieve data from the Explore Education Statistics API.

Analysis code never makes HTTP calls itself. It asks this client, which knows
the endpoints, sets a timeout on every request and pins a data set version
when asked. The network call sits behind a transport function, so tests can
supply recorded responses and never reach the live API.
"""

import json
import time
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

BASE_URL = "https://api.education.gov.uk/statistics/v1"
DEFAULT_TIMEOUT = 30.0
DEFAULT_ATTEMPTS = 3
DEFAULT_BACKOFF = 0.5
VERSIONS_PAGE_SIZE = 20  # The largest page the versions endpoint allows.


class ApiError(Exception):
    """Raised when a request fails, describing what failed and why."""


class TransportError(Exception):
    """Raised by a transport when no response arrives, such as on a timeout."""


@dataclass(frozen=True)
class Response:
    """An HTTP response as the client needs it.

    Attributes:
        status: The HTTP status code.
        body: The raw response body.
    """

    status: int
    body: bytes


Transport = Callable[[str, float], Response]


def urllib_transport(url: str, timeout: float) -> Response:
    """Send a GET request with the standard library.

    Args:
        url: The full URL, including any query string.
        timeout: Seconds to wait before giving up.

    Returns:
        The status and body of the response.
    """
    with urllib.request.urlopen(url, timeout=timeout) as reply:
        return Response(reply.status, reply.read())


class ApiClient:
    """A client for one Explore Education Statistics API.

    Server errors and lost connections are usually temporary, so those requests
    are sent again, waiting longer each time. Client errors mean the request
    itself is wrong, so they are reported at once.

    Args:
        transport: The function that sends each request. Tests pass a fake.
        timeout: Seconds every request may take before it is abandoned.
        attempts: The most times one request is sent, including the first.
        backoff: Seconds to wait before the first retry, doubling each time.
        sleep: The function used to wait. Tests pass one that does not.
        base_url: The API's base URL, without a trailing slash.
    """

    def __init__(
        self,
        transport: Transport = urllib_transport,
        timeout: float = DEFAULT_TIMEOUT,
        attempts: int = DEFAULT_ATTEMPTS,
        backoff: float = DEFAULT_BACKOFF,
        sleep: Callable[[float], None] = time.sleep,
        base_url: str = BASE_URL,
    ) -> None:
        """Store the settings used for every request."""
        self._transport = transport
        self._timeout = timeout
        self._attempts = attempts
        self._backoff = backoff
        self._sleep = sleep
        self._base_url = base_url

    def summary(self, data_set_id: str) -> dict[str, Any]:
        """Return a data set's summary.

        Args:
            data_set_id: The data set's identifier.

        Returns:
            The decoded summary.
        """
        return self._get_json(f"/data-sets/{data_set_id}")

    def metadata(self, data_set_id: str, version: str | None = None) -> dict[str, Any]:
        """Return a data set's metadata, for the latest or a pinned version.

        Args:
            data_set_id: The data set's identifier.
            version: The version to pin, such as ``2.0.2``. Omit for the latest.

        Returns:
            The decoded metadata.
        """
        return self._get_json(f"/data-sets/{data_set_id}/meta", _version_param(version))

    def versions(self, data_set_id: str) -> list[dict[str, Any]]:
        """Return every version of a data set, collected across all pages.

        Args:
            data_set_id: The data set's identifier.

        Returns:
            The versions, in the order the API returned them.
        """
        results, page, total_pages = [], 1, 1
        while page <= total_pages:
            reply = self._get_json(
                f"/data-sets/{data_set_id}/versions",
                {"page": page, "pageSize": VERSIONS_PAGE_SIZE},
            )
            results.extend(reply["results"])
            total_pages = reply["paging"]["totalPages"]
            page += 1
        return results

    def csv(self, data_set_id: str, version: str | None = None) -> str:
        """Return a data set as CSV text, for the latest or a pinned version.

        Args:
            data_set_id: The data set's identifier.
            version: The version to pin, such as ``2.0.2``. Omit for the latest.

        Returns:
            The CSV text, without any byte order mark.
        """
        body = self._get(f"/data-sets/{data_set_id}/csv", _version_param(version))
        return body.decode("utf-8-sig")

    def _get(self, path: str, params: dict[str, Any] | None = None) -> bytes:
        """Send one request and return the response body.

        Args:
            path: The endpoint path after the base URL.
            params: Query parameters to add, if any.

        Returns:
            The raw response body.
        """
        url = self._base_url + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        return self._transport(url, self._timeout).body

    def _get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Send one request and decode the JSON response.

        Args:
            path: The endpoint path after the base URL.
            params: Query parameters to add, if any.

        Returns:
            The decoded JSON.
        """
        return json.loads(self._get(path, params))


def _version_param(version: str | None) -> dict[str, str]:
    """Return the query parameter that pins a version.

    Args:
        version: The version to pin, or ``None`` for the latest.

    Returns:
        ``dataSetVersion`` set to the version, or no parameters for the latest.
    """
    return {"dataSetVersion": version} if version else {}