import motor.motor_asyncio
from bson import ObjectId

class AsyncFileManager:
    def __init__(self, mongo_uri, db_name):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(self.db)

    async def upload_file(self, filename, data):
        """上传文件到GridFS，返回文件ID"""
        file_id = await self.fs.upload_from_stream(filename, data)
        return file_id

    async def download_file(self, file_id):
        """从GridFS下载文件，返回文件内容"""
        download_stream = await self.fs.open_download_stream(ObjectId(file_id))
        content = await download_stream.read()
        return content

    async def delete_file(self, file_id):
        """从GridFS删除文件"""
        await self.fs.delete(ObjectId(file_id))

    async def file_exists(self, file_id):
        """检查文件是否存在"""
        try:
            await self.fs.open_download_stream(ObjectId(file_id))
            return True
        except Exception:
            return False

    async def close(self):
        """关闭数据库连接"""
        self.client.close()
