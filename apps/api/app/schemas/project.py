"""Project Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    title: str = Field(..., min_length=1, max_length=255)
    youtube_url: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""

    title: str | None = Field(None, min_length=1, max_length=255)
    status: str | None = None
    youtube_url: Optional[str] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    status: str
    youtube_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
