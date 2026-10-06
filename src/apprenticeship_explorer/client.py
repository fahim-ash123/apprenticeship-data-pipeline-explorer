"""Retrieve data from the Explore Education Statistics API.

Analysis code never makes HTTP calls itself. It asks this client, which knows
the endpoints, sets a timeout on every request and pins a data set version
when asked. The network call sits behind a transport function, so tests can
supply recorded responses and never reach the live API.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

BASE_URL = "https://api.education.gov.uk/statistics/v1"
DEFAULT_TIMEOUT = 30.0
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
    # Deliberately not implemented yet. The tests are written first.
    raise NotImplementedError


class ApiClient:
    """A client for one Explore Education Statistics API.

    Args:
        transport: The function that sends each request. Tests pass a fake.
        timeout: Seconds every request may take before it is abandoned.
        base_url: The API's base URL, without a trailing slash.
    """

    def __init__(
        self,
        transport: Transport = urllib_transport,
        timeout: float = DEFAULT_TIMEOUT,
        base_url: str = BASE_URL,
    ) -> None:
        """Store the settings used for every request."""
        self._transport = transport
        self._timeout = timeout
        self._base_url = base_url

    def summary(self, data_set_id: str) -> dict[str, Any]:
        """Return a data set's summary.

        Args:
            data_set_id: The data set's identifier.

        Returns:
            The decoded summary.
        """
        raise NotImplementedError

    def metadata(self, data_set_id: str, version: str | None = None) -> dict[str, Any]:
        """Return a data set's metadata, for the latest or a pinned version.

        Args:
            data_set_id: The data set's identifier.
            version: The version to pin, such as ``2.0.2``. Omit for the latest.

        Returns:
            The decoded metadata.
        """
        raise NotImplementedError

    def versions(self, data_set_id: str) -> list[dict[str, Any]]:
        """Return every version of a data set, collected across all pages.

        Args:
            data_set_id: The data set's identifier.

        Returns:
            The versions, in the order the API returned them.
        """
        raise NotImplementedError

    def csv(self, data_set_id: str, version: str | None = None) -> str:
        """Return a data set as CSV text, for the latest or a pinned version.

        Args:
            data_set_id: The data set's identifier.
            version: The version to pin, such as ``2.0.2``. Omit for the latest.

        Returns:
            The CSV text, without any byte order mark.
        """
        raise NotImplementedError