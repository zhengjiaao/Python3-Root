from sqlalchemy.orm import Session
from ..database.models.project import Project
from ..utils.exceptions import NotFoundException


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, project_data: dict) -> Project:
        project = Project(**project_data)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project(self, project_id: int) -> Project:
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException("Project not found")
        return project

    def get_projects(self, skip: int = 0, limit: int = 100) -> list[Project]:
        return self.db.query(Project).offset(skip).limit(limit).all()

    def update_project(self, project_id: int, project_data: dict) -> Project:
        project = self.get_project(project_id)
        for key, value in project_data.items():
            setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, project_id: int) -> None:
        project = self.get_project(project_id)
        self.db.delete(project)
        self.db.commit()