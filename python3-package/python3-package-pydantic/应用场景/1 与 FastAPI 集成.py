import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List
import uvicorn

# 初始化日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Product API", version="1.0.0")

# 产品创建请求模型
class ProductCreate(BaseModel):
    name: str
    description: str | None = None  # 可选描述
    price: float = Field(gt=0, description="价格必须大于0")  # 验证价格大于0
    categories: List[str] = Field(min_length=1, description="至少需要一个分类")  # 至少一个分类

    @field_validator('name')
    def name_must_contain_space(cls, v):
        """验证名称必须包含空格"""
        if ' ' not in v:
            raise ValueError('名称必须包含空格')
        return v.title()  # 返回标题格式(首字母大写)

# 产品响应模型(继承创建模型)
class ProductResponse(ProductCreate):
    id: int
    created_at: str  # ISO 8601 格式时间字符串

# 模拟内存数据库
products_db = []
next_id = 1

@app.post("/products/", response_model=ProductResponse,
          summary="创建产品", description="创建新产品并返回产品详情")
async def create_product(product: ProductCreate):
    """创建新产品"""
    global next_id
    try:
        logger.info(f"尝试创建新产品: {product.model_dump()}")
        product_data = product.model_dump()
        product_data["id"] = next_id
        product_data["created_at"] = datetime.now().isoformat()
        products_db.append(product_data)
        next_id += 1
        logger.info(f"产品创建成功, ID: {product_data['id']}")
        return product_data
    except Exception as e:
        logger.error(f"产品创建失败: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/products/{product_id}", response_model=ProductResponse,
         summary="获取产品", description="根据ID获取产品详情")
async def get_product(product_id: int):
    """获取单个产品详情"""
    logger.info(f"尝试获取产品, ID: {product_id}")
    for product in products_db:
        if product["id"] == product_id:
            logger.info(f"成功找到产品, ID: {product_id}")
            return product
    logger.warning(f"产品不存在, ID: {product_id}")
    raise HTTPException(status_code=404, detail="产品不存在")

@app.get("/products/", response_model=list[ProductResponse],
         summary="获取所有产品", description="获取产品列表")
async def get_all_products():
    """获取所有产品"""
    logger.info("获取所有产品列表")
    return products_db

def main():
    """启动FastAPI应用"""
    logger.info("正在启动Product API服务...")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()
