"""Download service using yt-dlp.

Currently tested with YouTube URLs.
The implementation uses yt-dlp and may work with other supported providers,
but only YouTube is officially supported in Phase 2.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yt_dlp

from app.services.download_exceptions import (
    DownloadFailedError,
    InvalidURLError,
    VideoUnavailableError,
)


@dataclass(frozen=True)
class DownloadResult:
    """Result of a successful download."""

    filepath: str
    title: str
    duration: int | None
    uploader: str | None
    ext: str
    filesize: int | None


def _find_project_root() -> Path:
    """Find the project root by locating the .git directory.

    Temporary development-only implementation. Will be replaced by
    Settings.download_dir in the deployment/config phase. Downstream
    phases must not depend on this function.
    """
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("Project root (.git) not found")


def _get_download_dir() -> Path:
    """Resolve DOWNLOAD_DIR lazily at runtime.

    Avoids side effect at import time — only triggers when a real
    download is requested.
    """
    return _find_project_root().joinpath("storage", "downloads")


_YDL_OPTS_TEMPLATE: dict[str, Any] = {
    "format": "best[ext=mp4]/best",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
}


def _validate_url(url: str) -> None:
    """Validate URL has scheme and netloc."""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise InvalidURLError(f"Invalid URL: {url!r}")


def _map_download_error(
    e: yt_dlp.utils.DownloadError,
) -> DownloadFailedError | InvalidURLError | VideoUnavailableError:
    """Map yt-dlp DownloadError to domain exception.

    Prefers class-based mapping via exc_info. Falls back to
    DownloadFailedError when exc_info is unavailable, because the
    internal exception layout of yt-dlp may change across versions.
    """
    inner = e.exc_info[1] if e.exc_info else None
    if isinstance(inner, yt_dlp.utils.UnsupportedError):
        return InvalidURLError(str(e))
    if isinstance(inner, (
        yt_dlp.utils.ExtractorError,
        getattr(yt_dlp.utils, "GeoRestrictedError", Exception),
        getattr(yt_dlp.utils, "UnavailableVideoError", Exception),
    )):
        return VideoUnavailableError(str(e))
    return DownloadFailedError(str(e))


def _verify_file(path: Path) -> None:
    """Verify downloaded file exists and is non-empty."""
    if not path.exists() or not path.is_file() or path.stat().st_size == 0:
        raise DownloadFailedError("Downloaded file is missing or empty")


class DownloadService:
    """Service responsible for downloading videos via yt-dlp."""

    async def download(self, url: str) -> DownloadResult:
        """Download video at URL and return metadata.

        Returns:
            DownloadResult with filepath and metadata.

        Raises:
            InvalidURLError: URL missing scheme or netloc.
            VideoUnavailableError: video not accessible.
            DownloadFailedError: any other failure.
        """
        _validate_url(url)

        download_dir = _get_download_dir()
        download_dir.mkdir(parents=True, exist_ok=True)

        ydl_opts = {
            **_YDL_OPTS_TEMPLATE,
            "outtmpl": str(download_dir.joinpath("%(id)s.%(ext)s")),
        }

        try:
            info: dict[str, Any] | None = await asyncio.to_thread(
                _sync_download, url, ydl_opts
            )
        except yt_dlp.utils.DownloadError as e:
            raise _map_download_error(e) from e

        if not isinstance(info, dict):
            raise DownloadFailedError(
                f"yt-dlp returned unexpected type: {type(info).__name__}"
            )

        ext = info.get("ext")
        video_id = info.get("id")
        if not isinstance(ext, str) or not isinstance(video_id, str):
            raise DownloadFailedError("yt-dlp metadata missing ext or id")

        title = info.get("title")
        duration = info.get("duration")
        uploader = info.get("uploader")
        raw_filesize = info.get("filesize") or info.get("filesize_approx")

        file_path = download_dir.joinpath(f"{video_id}.{ext}")
        _verify_file(file_path)

        return DownloadResult(
            filepath=str(file_path),
            title=str(title) if title is not None else "",
            duration=duration if isinstance(duration, int) else None,
            uploader=uploader if isinstance(uploader, str) else None,
            ext=ext,
            filesize=raw_filesize if isinstance(raw_filesize, int) else None,
        )


def _sync_download(url: str, ydl_opts: dict[str, Any]) -> dict[str, Any] | None:
    """Synchronous yt-dlp download, returns info_dict."""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=True)


__all__ = ["DownloadResult", "DownloadService"]
