from ..repositories.project_repository import ProjectRepository
from ..schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from ..utils.exceptions import ValidationException


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def create_project(self, project_data: ProjectCreate) -> ProjectResponse:
        # 业务逻辑验证
        if len(project_data.name) < 3:
            raise ValidationException("Project name must be at least 3 characters")

        project = self.repository.create_project(project_data.dict())
        return ProjectResponse.from_orm(project)

    def get_project(self, project_id: int) -> ProjectResponse:
        project = self.repository.get_project(project_id)
        return ProjectResponse.from_orm(project)

    def get_projects(self, skip: int = 0, limit: int = 100) -> list[ProjectResponse]:
        projects = self.repository.get_projects(skip, limit)
        return [ProjectResponse.from_orm(p) for p in projects]

    def update_project(self, project_id: int, project_data: ProjectUpdate) -> ProjectResponse:
        # 过滤掉未提供的字段
        update_data = {k: v for k, v in project_data.dict().items() if v is not None}

        if not update_data:
            raise ValidationException("No data provided for update")

        project = self.repository.update_project(project_id, update_data)
        return ProjectResponse.from_orm(project)

    def delete_project(self, project_id: int) -> None:
        self.repository.delete_project(project_id)