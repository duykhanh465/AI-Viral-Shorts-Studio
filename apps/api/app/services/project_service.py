"""Project service for business logic."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate


class ProjectService:
    """Handles business logic for Project operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with database session."""
        self.session = session
        self.repository = ProjectRepository(session)

    async def create_project(self, data: ProjectCreate) -> ProjectResponse:
        """Create a new project."""
        project = await self.repository.create(data.title)
        return ProjectResponse.model_validate(project)

    async def get_project(self, project_id: uuid.UUID) -> ProjectResponse | None:
        """Get a project by ID."""
        project = await self.repository.get_by_id(project_id)
        if not project:
            return None
        return ProjectResponse.model_validate(project)

    async def list_projects(self) -> list[ProjectResponse]:
        """List all projects."""
        projects = await self.repository.get_all()
        return [ProjectResponse.model_validate(p) for p in projects]

    async def update_project(self, project_id: uuid.UUID, data: ProjectUpdate) -> ProjectResponse | None:
        """Update a project."""
        project = await self.repository.update(
            project_id,
            title=data.title,
            status=data.status,
        )
        if not project:
            return None
        return ProjectResponse.model_validate(project)

    async def delete_project(self, project_id: uuid.UUID) -> bool:
        """Delete a project."""
        return await self.repository.delete(project_id)
