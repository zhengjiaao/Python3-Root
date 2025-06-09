# main_mongo.py
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError
from pymongo.collection import Collection
from datetime import datetime, timezone
import bcrypt
from typing import Optional, Dict, List, Any, Tuple


# ========================
# 🔧 配置部分
# ========================

# MONGO_URI = "mongodb://localhost:27017/"
MONGO_URI = "mongodb://username:password@localhost:27017/admin" # 带认证
DB_NAME = "test" # 数据库名称


# ========================
# 🛠️ 工具函数
# ========================

def object_id_to_str(doc: Dict[str, Any]) -> Dict[str, Any]:
    """将文档中的 _id 字段转换为字符串"""
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

def str_to_object_id(id_str: str) -> ObjectId:
    """将字符串转换为 ObjectId"""
    return ObjectId(id_str)

def validate_email(email: str) -> bool:
    """简单验证邮箱格式"""
    import re
    pattern = r"[^@]+@[^@]+\.[^@]+"
    return re.match(pattern, email) is not None


# ========================
# 📦 数据库连接管理
# ========================

class MongoDBManager:
    def __init__(self, uri: str = MONGO_URI, db_name: str = DB_NAME):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_collection(self, collection_name: str) -> Collection:
        return self.db[collection_name]

    def create_indexes(self):
        """创建常用索引"""
        self.db.users.create_index([("email", ASCENDING)], unique=True)
        self.db.products.create_index([("name", "text"), ("description", "text")])
        self.db.orders.create_index([("user_id", ASCENDING), ("order_date", DESCENDING)])


# ========================
# 👤 用户管理类
# ========================

class MongoDBUserManager:
    def __init__(self, db_manager: MongoDBManager):
        self.db = db_manager.db

    def register_user(self, name: str, email: str, password: str) -> Tuple[bool, str]:
        """
        注册新用户
        :param name: 用户名
        :param email: 邮箱（唯一）
        :param password: 密码
        :return: (是否成功, 消息)
        """
        try:
            if not validate_email(email):
                return False, "邮箱格式不正确"

            if self.db.users.find_one({"email": email}):
                return False, "该邮箱已被注册"

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            user_data = {
                "name": name,
                "email": email,
                "password": hashed_password,
                "created_at": datetime.now(timezone.utc),
                "roles": ["customer"],
                "profile": {
                    "bio": "",
                    "avatar": None
                }
            }

            result = self.db.users.insert_one(user_data)
            return True, f"用户注册成功，ID: {result.inserted_id}"
        except DuplicateKeyError:
            return False, "该邮箱已被注册"
        except OperationFailure as e:
            return False, f"数据库操作失败: {e}"
        except Exception as e:
            return False, f"未知错误: {e}"


# ========================
# 🛍️ 商品管理类
# ========================

class MongoDBProductManager:
    def __init__(self, db_manager: MongoDBManager):
        self.db = db_manager.db

    def add_product(self, name: str, price: float, category: str,
                     description: str = "", stock: int = 0) -> Any:
        product_data = {
            "name": name,
            "price": float(price),
            "category": category,
            "description": description,
            "stock": int(stock),
            "created_at": datetime.now(timezone.utc),
            "attributes": {},
            "ratings": []
        }
        return self.db.products.insert_one(product_data).inserted_id

    def search_products(self, query: str, category: Optional[str] = None,
                        min_price: float = 0, max_price: float = 10000,
                        page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        search_filter = {
            "$text": {"$search": query},
            "price": {"$gte": min_price, "$lte": max_price}
        }
        if category:
            search_filter["category"] = category

        skip = (page - 1) * per_page
        cursor = self.db.products.find(
            search_filter,
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(per_page)

        products = [object_id_to_str(p) for p in list(cursor)]
        total = self.db.products.count_documents(search_filter)

        return {
            "products": products,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        }


# ========================
# 📦 订单管理类
# ========================

class MongoDBOrderManager:
    def __init__(self, db_manager: MongoDBManager):
        self.db = db_manager.db
        self.client = db_manager.client

    def create_order(self, user_id: Any, items: List[Dict[str, Any]]) -> Tuple[bool, str]:
        total_amount = 0
        for item in items:
            product = self.db.products.find_one({"_id": item["product_id"]})
            if not product:
                return False, f"产品 {item['product_id']} 不存在"
            if product["stock"] < item["quantity"]:
                return False, f"产品 {product['name']} 库存不足"
            total_amount += product["price"] * item["quantity"]

        order_data = {
            "user_id": user_id,
            "items": items,
            "total_amount": total_amount,
            "status": "pending",
            "order_date": datetime.now(timezone.utc),
            "shipping_address": None,
            "payment_info": None
        }

        try:
            # 移除了 with session 启动事务的部分
            order_result = self.db.orders.insert_one(order_data)
            for item in items:
                self.db.products.update_one(
                    {"_id": item["product_id"]},
                    {"$inc": {"stock": -item["quantity"]}}
                )
            return True, f"订单创建成功，ID: {order_result.inserted_id}"
        except PyMongoError as e:
            return False, f"订单创建失败: {str(e)}"
        except Exception as e:
            return False, f"未知错误: {str(e)}"


# ========================
# 🚀 主程序入口
# ========================

if __name__ == "__main__":
    # 初始化数据库连接
    db_manager = MongoDBManager()

    # 创建索引
    db_manager.create_indexes()

    # 初始化各模块
    user_manager = MongoDBUserManager(db_manager)
    product_manager = MongoDBProductManager(db_manager)
    order_manager = MongoDBOrderManager(db_manager)

    # 示例：用户注册
    success, message = user_manager.register_user("李四", "lisi@example.com", "MyPassword123")
    print(message)

    # 示例：添加商品
    product_id = product_manager.add_product("无线耳机", 129.99, "电子产品", "高音质蓝牙耳机", 50)
    print(f"添加产品成功，ID: {product_id}")

    # 示例：搜索商品
    search_results = product_manager.search_products("蓝牙耳机", category="电子产品", min_price=100, max_price=200)
    print("\n搜索结果:")
    for product in search_results["products"]:
        print(f"{product['name']} - ${product['price']}")

    # 示例：创建订单
    user = db_manager.get_collection("users").find_one({"email": "lisi@example.com"})
    if user:
        success, msg = order_manager.create_order(user["_id"], [{"product_id": product_id, "quantity": 2}])
        print(msg)

    # 关闭连接
    db_manager.client.close()
