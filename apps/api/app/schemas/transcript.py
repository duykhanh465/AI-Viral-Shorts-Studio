"""Transcript Pydantic schemas for AI Viral Shorts Studio."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TranscriptEngine(StrEnum):
    """Transcription engine identifier."""

    FASTER_WHISPER = "faster-whisper"


class WhisperModelSize(StrEnum):
    """Supported Whisper model sizes."""

    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE_V3 = "large-v3"


class Segment(BaseModel):
    """A single transcript segment with timing and optional confidence."""

    start: float = Field(..., ge=0)
    end: float = Field(..., ge=0)
    text: str = Field(..., min_length=1)
    confidence: float | None = None

    model_config = ConfigDict(from_attributes=True)


class Transcript(BaseModel):
    """A complete transcription result for a project.

    Persistence-oriented schema: represents the domain record for a
    completed transcription tied to a specific project. Built by the
    persistence layer (Phase 3.5) from a :class:`TranscriptionResult`
    plus project context (``project_id``), identity (``id``) and the
    insert timestamp (``created_at``).

    The transcription service (Phase 3.3) does NOT produce a
    :class:`Transcript` directly — it produces a
    :class:`TranscriptionResult` (pure transcription output, without
    project context). See DCP-3.3-01.
    """

    id: UUID
    project_id: UUID
    engine: TranscriptEngine
    model_size: WhisperModelSize
    language: str = Field(..., min_length=2, max_length=16)
    text: str = Field(..., min_length=1)
    segments: list[Segment] = Field(default_factory=list)
    duration: float = Field(..., ge=0)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TranscriptionResult(BaseModel):
    """Pure transcription output produced by :class:`TranscriptionService`.

    Service-output schema: holds only the fields the transcription
    service can actually produce at runtime (engine, model, language,
    text, segments, duration). It deliberately does NOT include
    ``project_id`` (service has no project context), ``id`` (DB
    identity, produced by the persistence layer) or ``created_at``
    (insert timestamp, produced by the persistence layer).

    The persistence layer (Phase 3.5) is responsible for mapping a
    :class:`TranscriptionResult` into a :class:`Transcript` by adding
    those three fields. See DCP-3.3-01.
    """

    engine: TranscriptEngine
    model_size: WhisperModelSize
    language: str = Field(..., min_length=2, max_length=16)
    text: str = Field(..., min_length=1)
    segments: list[Segment] = Field(default_factory=list)
    duration: float = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)