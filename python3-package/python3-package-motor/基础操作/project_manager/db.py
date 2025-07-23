from motor.motor_asyncio import AsyncIOMotorClient

# 使用内存中的 MongoDB 测试实例 (实际生产替换为真实连接)
# MONGO_URI = "mongodb://localhost:27017"
# DATABASE_NAME = "project_management"
# COLLECTION_NAME = "projects"

MONGO_URI = "mongodb://username:pass@127.0.0.0.1:27017/test?authSource=admin"
DATABASE_NAME = "test"
COLLECTION_NAME = "projects"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
project_collection = db[COLLECTION_NAME]