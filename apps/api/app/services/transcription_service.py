"""Transcription service skeleton."""

from __future__ import annotations

from app.schemas.transcript import TranscriptionResult, WhisperModelSize


class TranscriptionService:
    """Service responsible for transcribing videos.

    Phase 3.2 deliverable: skeleton only. The public method
    `transcribe` is reserved as the single entry point for the
    transcription layer. Implementation will be completed in
    Phase 3.3 once the faster-whisper runtime contract is
    validated.
    """

    def __init__(self) -> None:
        """Initialize the transcription service."""
        return None

    async def transcribe(
        self,
        video_path: str,
        model_size: WhisperModelSize = WhisperModelSize.BASE,
    ) -> TranscriptionResult:
        """Transcribe a video file and return a TranscriptionResult.

        Phase 3.2 skeleton: this method is not implemented yet.
        """
        raise NotImplementedError("Phase 3.2 skeleton")


__all__ = ["TranscriptionService"]
