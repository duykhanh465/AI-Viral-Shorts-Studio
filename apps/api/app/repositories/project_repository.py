"""Project repository for database operations."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    """Handles all database operations for Project entity."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    async def create(self, title: str) -> Project:
        """Create a new project."""
        project = Project(title=title)
        self.session.add(project)
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        """Get a project by ID."""
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Project]:
        """Get all projects ordered by created_at descending."""
        result = await self.session.execute(
            select(Project).order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, project_id: uuid.UUID, title: str | None, status: str | None) -> Project | None:
        """Update a project."""
        project = await self.get_by_id(project_id)
        if not project:
            return None
        if title is not None:
            project.title = title
        if status is not None:
            project.status = status
        await self.session.flush()
        await self.session.refresh(project)
        return project

    async def delete(self, project_id: uuid.UUID) -> bool:
        """Delete a project by ID."""
        project = await self.get_by_id(project_id)
        if not project:
            return False
        await self.session.delete(project)
        await self.session.flush()
        return True
