"""Transcription exception hierarchy for AI Viral Shorts Studio."""


class TranscriptionError(Exception):
    """Base exception for all transcription errors."""


class ModelLoadError(TranscriptionError):
    """Raised when the transcription model fails to load."""


class TranscriptionFailedError(TranscriptionError):
    """Raised when the transcription process itself fails for any reason."""


class InvalidVideoError(TranscriptionError):
    """Raised when the input video is missing, unreadable, or in an unsupported format."""