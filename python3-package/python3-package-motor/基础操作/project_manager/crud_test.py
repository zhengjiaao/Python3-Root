import unittest
import asyncio
from bson import ObjectId
from db import project_collection
from crud import create_project, get_project, get_all_projects, update_project, delete_project, search_projects


class TestProjectCRUD(unittest.IsolatedAsyncioTestCase):
    """项目管理CRUD操作单元测试"""

    async def asyncSetUp(self):
        """每个测试前清空集合"""
        await project_collection.delete_many({})

        # 创建测试项目
        self.project_data = {
            "name": "Test Project",
            "description": "Initial description",
            "status": "active",
            "owner": "test@example.com"
        }
        self.created_project = await create_project(self.project_data)
        self.project_id = self.created_project["_id"]

    async def asyncTearDown(self):
        """每个测试后清理数据"""
        await project_collection.delete_many({})

    async def test_create_project(self):
        """测试创建项目"""
        self.assertIsInstance(self.created_project, dict)
        self.assertEqual(self.created_project["name"], "Test Project")
        self.assertEqual(self.created_project["status"], "active")
        self.assertIn("_id", self.created_project)

        # 验证实际存储的数据
        db_project = await project_collection.find_one({"_id": ObjectId(self.project_id)})
        self.assertEqual(db_project["name"], "Test Project")

    async def test_get_project(self):
        """测试获取单个项目"""
        project = await get_project(self.project_id)
        self.assertEqual(project["name"], "Test Project")
        self.assertEqual(project["description"], "Initial description")

    async def test_get_invalid_project(self):
        """测试获取无效ID的项目"""
        project = await get_project("invalid_object_id")
        self.assertIsNone(project)

        project = await get_project(str(ObjectId()))
        self.assertIsNone(project)

    async def test_get_all_projects(self):
        """测试获取所有项目"""
        # 添加第二个项目
        await create_project({
            "name": "Second Project",
            "description": "Another project"
        })

        projects = await get_all_projects()
        self.assertEqual(len(projects), 2)
        names = {p["name"] for p in projects}
        self.assertIn("Test Project", names)
        self.assertIn("Second Project", names)

    async def test_update_project(self):
        """测试更新项目"""
        update_data = {
            "name": "Updated Project",
            "status": "completed",
            "new_field": "added"
        }
        updated = await update_project(self.project_id, update_data)

        self.assertEqual(updated["name"], "Updated Project")
        self.assertEqual(updated["status"], "completed")
        self.assertEqual(updated["new_field"], "added")

        # 验证未修改字段保持不变
        self.assertEqual(updated["description"], "Initial description")

        # 验证无效更新
        invalid_update = await update_project(str(ObjectId()), {"name": "Invalid"})
        self.assertIsNone(invalid_update)

    async def test_delete_project(self):
        """测试删除项目"""
        # 删除项目
        result = await delete_project(self.project_id)
        self.assertTrue(result)

        # 验证项目已删除
        project = await get_project(self.project_id)
        self.assertIsNone(project)

        # 验证无效删除
        result = await delete_project(str(ObjectId()))
        self.assertFalse(result)

    async def test_search_projects(self):
        """测试项目搜索功能"""
        # 添加更多项目
        await create_project({"name": "API Service", "description": "Backend service development"})
        await create_project({"name": "Frontend UI", "description": "User interface implementation"})

        # 测试名称搜索
        results = await search_projects("API")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "API Service")

        # 测试描述搜索
        results = await search_projects("interface")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Frontend UI")

        # 测试不区分大小写
        results = await search_projects("test")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Test Project")

        # 测试无结果
        results = await search_projects("nonexistent")
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()