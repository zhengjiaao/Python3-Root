import unittest
import asyncio
from file_manager import AsyncFileManager
from bson import ObjectId
import os


class TestFileManager(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # 获取MongoDB连接URI，优先使用环境变量
        # self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        # self.db_name = "test_file_manager"

        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://username:pass@127.0.0.0.1:27017/test?authSource=admin")
        self.db_name = "test"

        # 初始化文件管理器
        self.file_manager = AsyncFileManager(self.mongo_uri, self.db_name)

        # 清理测试数据库
        await self.cleanup_database()

        # 测试文件内容
        self.test_content = b"Hello, this is a test file content!"
        self.filename = "test_file.txt"

        # 上传测试文件
        self.file_id = await self.file_manager.upload_file(
            self.filename, self.test_content
        )

    async def asyncTearDown(self):
        # 清理测试数据库
        await self.cleanup_database()
        # 关闭连接
        await self.file_manager.close()

    async def cleanup_database(self):
        """清理测试数据库"""
        db = self.file_manager.client[self.db_name]
        # 删除GridFS相关集合
        await db.fs.files.delete_many({})
        await db.fs.chunks.delete_many({})

    async def test_upload_file(self):
        """测试文件上传功能"""
        # 验证返回的文件ID格式
        self.assertIsInstance(self.file_id, ObjectId)

        # 验证文件是否存在
        exists = await self.file_manager.file_exists(self.file_id)
        self.assertTrue(exists)

    async def test_download_file(self):
        """测试文件下载功能"""
        content = await self.file_manager.download_file(self.file_id)
        self.assertEqual(content, self.test_content)

    async def test_delete_file(self):
        """测试文件删除功能"""
        # 先确认文件存在
        exists = await self.file_manager.file_exists(self.file_id)
        self.assertTrue(exists)

        # 删除文件
        await self.file_manager.delete_file(self.file_id)

        # 验证文件已不存在
        exists = await self.file_manager.file_exists(self.file_id)
        self.assertFalse(exists)

    async def test_download_nonexistent_file(self):
        """测试下载不存在的文件"""
        with self.assertRaises(Exception):  # 预期抛出异常
            fake_id = ObjectId()  # 生成一个不存在的ID
            await self.file_manager.download_file(fake_id)


if __name__ == "__main__":
    unittest.main()