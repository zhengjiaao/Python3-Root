import logging
from pydantic import BaseModel, field_serializer, model_serializer
from datetime import datetime
from enum import Enum
from typing import Any, Self
from pydantic import ConfigDict  # 解决方案1需要

# 或者
# from pydantic import GetCoreSchemaHandler  # 解决方案2需要
# from pydantic_core import core_schema

# 初始化日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


class Role(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class CustomData:
    """自定义数据类"""

    def __init__(self, value: str):
        self.value = value
        logger.debug(f"创建CustomData实例，值: {value}")

    def __repr__(self):
        return f"CustomData({self.value})"


class User(BaseModel):
    """用户模型"""
    model_config = ConfigDict(arbitrary_types_allowed=True)  # 解决方案1

    name: str
    signup_date: datetime
    role: Role
    custom_data: CustomData

    @field_serializer('signup_date')
    def serialize_dt(self, dt: datetime) -> str:
        """将datetime转换为ISO格式字符串"""
        logger.debug(f"序列化日期字段: {dt}")
        return dt.isoformat()

    @field_serializer('custom_data')
    def serialize_custom(self, data: CustomData) -> str:
        """自定义序列化逻辑"""
        logger.debug(f"序列化自定义数据: {data}")
        return f"custom:{data.value}"

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        """控制整个模型的序列化行为"""
        logger.info("开始序列化用户模型")
        data = {
            'name': self.name,
            'signup_date': self.signup_date.isoformat(),
            'role': self.role.value,
            'custom_data': f"custom:{self.custom_data.value}"
        }
        # 添加计算字段
        data['is_admin'] = self.role == Role.ADMIN
        logger.debug(f"添加计算字段 is_admin: {data['is_admin']}")
        return data

    @classmethod
    def model_validate_json(cls, json_data: str) -> Self:
        """自定义JSON反序列化"""
        logger.info("开始反序列化用户数据")
        logger.debug(f"原始JSON数据: {json_data}")

        data = super().model_validate_json(json_data)

        # 后处理自定义数据
        if isinstance(data.custom_data, str) and data.custom_data.startswith("custom:"):
            logger.debug("处理自定义数据反序列化")
            data.custom_data = CustomData(data.custom_data[7:])

        logger.info("反序列化完成")
        return data


def main():
    """主函数"""
    try:
        logger.info("开始数据转换与序列化演示")

        # 创建实例
        logger.info("创建用户实例")
        user = User(
            name="Alice",
            signup_date=datetime.now(),
            role=Role.ADMIN,
            custom_data=CustomData("special")
        )
        logger.debug(f"用户实例创建成功: {user}")

        # 序列化为JSON
        logger.info("序列化用户数据为JSON")
        json_data = user.model_dump_json(indent=2)
        logger.debug(f"序列化结果:\n{json_data}")
        print("序列化结果:", json_data)

        # 从JSON反序列化
        logger.info("从JSON反序列化用户数据")
        new_user = User.model_validate_json(json_data)
        logger.info(f"反序列化成功: {new_user}")
        print("反序列化结果:", new_user)
        print("custom_data类型:", type(new_user.custom_data))

        logger.info("数据转换演示完成")
    except Exception as e:
        logger.error(f"程序运行失败: {str(e)}")
        raise


if __name__ == "__main__":
    main()
