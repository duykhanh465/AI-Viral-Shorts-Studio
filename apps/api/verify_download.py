"""Verification script for DownloadService - Phase 2.3.

Run from apps/api/ directory:
    python verify_download.py
"""

from __future__ import annotations

import asyncio
import platform
import sys
from pathlib import Path

import yt_dlp

from app.services.download_service import DownloadService
from app.services.download_exceptions import (
    DownloadFailedError,
    InvalidURLError,
    VideoUnavailableError,
)


YOUTUBE_VALID_URL = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
YOUTUBE_NONEXISTENT_URL = "https://www.youtube.com/watch?v=xxxxxxxxxxx"


def print_header(title: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


async def test_1_success(service: DownloadService) -> DownloadService:
    """Test 1: Download a valid public YouTube video."""
    print_header("TEST 1 - Valid download")
    try:
        result = await service.download(YOUTUBE_VALID_URL)
    except Exception as e:
        print(f"  FAIL - unexpected exception: {type(e).__name__}: {e}")
        raise

    print(f"  filepath    = {result.filepath}")
    print(f"  title       = {result.title!r}")
    print(f"  ext         = {result.ext!r}")
    print(f"  duration    = {result.duration}")
    print(f"  uploader    = {result.uploader!r}")
    print(f"  filesize    = {result.filesize}")

    p = Path(result.filepath)
    assert p.exists(), f"file does not exist: {p}"
    assert p.is_file(), f"not a file: {p}"
    size = p.stat().st_size
    assert size > 0, f"file is empty: {p}"
    assert result.title, "title is empty"
    assert result.ext, "ext is empty"
    assert p.suffix == f".{result.ext}", (
        f"suffix mismatch: {p.suffix} vs .{result.ext}"
    )
    print(f"  PASS - file size = {size} bytes")
    return result


async def test_2_invalid_url(service: DownloadService) -> None:
    """Test 2: Invalid URL must raise InvalidURLError."""
    print_header("TEST 2 - Invalid URL")
    try:
        await service.download("abc")
    except InvalidURLError as e:
        print(f"  PASS - got InvalidURLError: {e}")
        return
    except Exception as e:
        print(f"  FAIL - expected InvalidURLError, got {type(e).__name__}: {e}")
        raise AssertionError(f"Wrong exception type: {type(e).__name__}")
    print("  FAIL - no exception raised")
    raise AssertionError("Expected InvalidURLError")


async def test_3_unavailable_video(service: DownloadService) -> None:
    """Test 3: Non-existent video must raise VideoUnavailableError."""
    print_header("TEST 3 - Non-existent video")
    try:
        await service.download(YOUTUBE_NONEXISTENT_URL)
    except VideoUnavailableError as e:
        print(f"  PASS - got VideoUnavailableError: {e}")
        return
    except DownloadFailedError as e:
        # Acceptable: yt-dlp may map to generic DownloadFailedError
        print(f"  PASS (mapped) - got DownloadFailedError: {e}")
        return
    except Exception as e:
        print(f"  FAIL - unexpected: {type(e).__name__}: {e}")
        raise AssertionError(f"Wrong exception type: {type(e).__name__}")
    print("  FAIL - no exception raised")
    raise AssertionError("Expected VideoUnavailableError or DownloadFailedError")


async def test_4_metadata_consistency(result_filepath: str, ext: str) -> None:
    """Test 4: DownloadResult must be consistent with file on disk."""
    print_header("TEST 4 - DownloadResult <-> file consistency")
    p = Path(result_filepath)
    assert p.exists(), f"file does not exist: {p}"
    size = p.stat().st_size
    assert size > 0, "file is empty"
    assert p.suffix == f".{ext}", f"suffix mismatch: {p.suffix} vs .{ext}"
    print(f"  PASS - suffix={p.suffix} matches ext={ext!r}, size={size} bytes")


async def test_5_duplicate_download(service: DownloadService, first_result) -> None:
    """Test 5: Download same URL twice - observe yt-dlp behavior."""
    print_header("TEST 5 - Duplicate download (observe only)")
    first_path = Path(first_result.filepath)
    first_size_before = first_path.stat().st_size if first_path.exists() else 0

    try:
        second = await service.download(YOUTUBE_VALID_URL)
        print(f"  Downloaded again: filepath={second.filepath}")
        print(f"  Second result ext={second.ext!r} title={second.title!r}")
        second_path = Path(second.filepath)
        second_size = second_path.stat().st_size if second_path.exists() else 0
        if second_path == first_path:
            if second_size == first_size_before:
                print(f"  OBSERVATION: file size unchanged ({second_size}) - likely skipped/kept")
            else:
                print(
                    f"  OBSERVATION: file size changed "
                    f"({first_size_before} -> {second_size}) - likely overwritten"
                )
        else:
            print(f"  OBSERVATION: different file path")
    except Exception as e:
        print(f"  OBSERVATION: second download raised {type(e).__name__}: {e}")


async def main() -> int:
    print_header("ENVIRONMENT")
    print(f"  Python     = {sys.version.split()[0]}")
    print(f"  yt-dlp     = {yt_dlp.version.__version__}")
    print(f"  OS         = {platform.system()} {platform.release()}")

    service = DownloadService()

    try:
        r1 = await test_1_success(service)
    except Exception as e:
        print(f"\nTEST 1 FAILED: {e}")
        return 1

    await test_2_invalid_url(service)

    try:
        await test_3_unavailable_video(service)
    except AssertionError as e:
        print(f"\nTEST 3 FAILED: {e}")
        return 1

    await test_4_metadata_consistency(r1.filepath, r1.ext)

    await test_5_duplicate_download(service, r1)

    print_header("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
