from bson import ObjectId
from db import project_collection

async def create_project(project_data: dict) -> dict:
    """创建新项目"""
    result = await project_collection.insert_one(project_data)
    return await get_project(str(result.inserted_id))

async def get_project(project_id: str) -> dict:
    """获取单个项目"""
    project = await project_collection.find_one({"_id": ObjectId(project_id)})
    if project:
        project["_id"] = str(project["_id"])
    return project

async def get_all_projects() -> list:
    """获取所有项目"""
    projects = []
    async for project in project_collection.find():
        project["_id"] = str(project["_id"])
        projects.append(project)
    return projects

async def update_project(project_id: str, update_data: dict) -> dict:
    """更新项目信息"""
    result = await project_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": update_data}
    )
    if result.modified_count > 0:
        return await get_project(project_id)
    return None

async def delete_project(project_id: str) -> bool:
    """删除项目"""
    result = await project_collection.delete_one({"_id": ObjectId(project_id)})
    return result.deleted_count > 0

async def search_projects(search_term: str) -> list:
    """搜索项目"""
    projects = []
    async for project in project_collection.find({
        "$or": [
            {"name": {"$regex": search_term, "$options": "i"}},
            {"description": {"$regex": search_term, "$options": "i"}}
        ]
    }):
        project["_id"] = str(project["_id"])
        projects.append(project)
    return projects