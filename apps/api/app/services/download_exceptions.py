"""Download-related exceptions.

These exceptions are the error vocabulary used by the download layer.
They are intentionally defined without dependencies so the download
service can be designed before the underlying downloader is implemented.
"""

from __future__ import annotations


class DownloadError(Exception):
    """Base exception for all download failures.

    Catch this exception to handle any error originating from the
    download layer, regardless of the specific cause.
    """


class InvalidURLError(DownloadError):
    """Raised when the provided URL is not a valid downloadable source.

    This covers structurally invalid URLs as well as URLs that are
    well-formed but pointing to unsupported schemes or hosts.
    """


class VideoUnavailableError(DownloadError):
    """Raised when the target video cannot be retrieved.

    Typical cases include deleted videos, private videos, region
    restrictions, or content removed by the platform.
    """


class DownloadFailedError(DownloadError):
    """Raised when the download process fails after it has been started.

    This covers network errors, I/O errors, timeouts, or any other
    failure that prevents the video from being downloaded successfully.
    """


__all__ = [
    "DownloadError",
    "InvalidURLError",
    "VideoUnavailableError",
    "DownloadFailedError",
]
