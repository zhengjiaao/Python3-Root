from fastapi import APIRouter, Depends, Query
from ..dependencies.database import get_db_session
from ..repositories.project_repository import ProjectRepository
from ..services.project_service import ProjectService
from ..schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from ..schemas.response import PaginatedResponse, MessageResponse

router = APIRouter(prefix="/projects", tags=["projects"])

def get_project_service(db=Depends(get_db_session)):
    repository = ProjectRepository(db)
    return ProjectService(repository)

@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    project: ProjectCreate,
    service: ProjectService = Depends(get_project_service)
):
    return service.create_project(project)

@router.get("/", response_model=PaginatedResponse[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    service: ProjectService = Depends(get_project_service)
):
    projects = service.get_projects(skip, limit)
    # 实际应用中应添加总计数和分页逻辑
    return {
        "total": len(projects),
        "page": skip // limit + 1,
        "per_page": limit,
        "items": projects
    }

@router.get("/{project_id}", response_model=ProjectResponse)
def read_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service)
):
    return service.get_project(project_id)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project: ProjectUpdate,
    service: ProjectService = Depends(get_project_service)
):
    return service.update_project(project_id, project)

@router.delete("/{project_id}", response_model=MessageResponse)
def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service)
):
    service.delete_project(project_id)
    return {"message": "Project deleted successfully"}