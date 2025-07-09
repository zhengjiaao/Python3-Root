import logging
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

# 初始化日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

class User(BaseModel):
    """用户数据模型"""
    id: UUID = Field(
        default_factory=uuid4,
        description="用户唯一标识符"
    )
    username: str = Field(
        min_length=3,
        max_length=20,
        description="用户名，3-20个字符"
    )
    email: str = Field(
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="有效的电子邮件地址"
    )
    signup_date: datetime = Field(
        default_factory=datetime.now,
        description="用户注册日期和时间"
    )
    age: int = Field(
        ge=13,
        le=120,
        description="用户年龄，13-120岁之间"
    )
    tags: List[str] = Field(
        default_factory=list,
        max_items=10,
        description="用户标签列表，最多10个标签"
    )
    is_active: bool = Field(
        default=True,
        description="用户是否激活"
    )
    profile: Optional[dict] = Field(
        default=None,
        description="用户额外信息"
    )

def create_user(username: str, email: str, age: int, tags: List[str] = None) -> User:
    """创建并验证用户实例"""
    try:
        logger.info("开始创建用户实例")
        user = User(
            username=username,
            email=email,
            age=age,
            tags=tags or []
        )
        logger.info(f"用户创建成功: {user.username} (ID: {user.id})")
        return user
    except ValidationError as e:
        logger.error("用户创建失败 - 验证错误:")
        for error in e.errors():
            field = error['loc'][0]
            msg = error['msg']
            logger.error(f"- {field}: {msg}")
        raise
    except Exception as e:
        logger.error(f"用户创建失败: {str(e)}")
        raise

def main():
    """主函数"""
    try:
        logger.info("开始用户模型演示")
        
        # 测试有效用户
        valid_user = create_user(
            username="john_doe",
            email="john@example.com",
            age=30,
            tags=["python", "developer"]
        )
        
        # 输出用户数据
        logger.info("用户数据:")
        logger.info(valid_user.model_dump_json(indent=2))
        
        # 测试无效用户
        logger.info("\n测试无效用户数据:")
        try:
            create_user(
                username="ab",  # 太短
                email="invalid-email",  # 格式不正确
                age=10  # 年龄太小
            )
        except ValidationError:
            logger.info("无效用户测试完成 (如预期失败)")
        
        logger.info("用户模型演示完成")
    except Exception as e:
        logger.error(f"程序运行失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()
