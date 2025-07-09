import logging
from pydantic import BaseModel, ValidationError, create_model, field_validator, Field
from typing import Any, Dict, Type

# 初始化日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# 动态表单字段定义
form_fields = {
    "username": {
        "type": str,
        "min_length": 3,
        "max_length": 20,
        "description": "Your username"
    },
    "email": {
        "type": str,
        "pattern": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        "description": "Valid email address"
    },
    "age": {
        "type": int,
        "ge": 18,
        "le": 100,
        "default": 25,
        "description": "Age between 18-100"
    },
    "subscribe": {
        "type": bool,
        "default": True,
        "description": "Subscribe to newsletter"
    }
}

def create_form_model(fields: Dict[str, Dict[str, Any]]) -> Type[BaseModel]:
    """动态创建表单模型"""
    field_definitions = {}
    validators = {}

    logger.info("开始创建动态表单模型...")
    logger.debug(f"表单字段定义: {fields}")

    for field_name, params in fields.items():
        field_type = params.pop("type")
        default = params.pop("default", ...)
        description = params.pop("description", None)

        # 创建字段定义
        field_definitions[field_name] = (
            field_type, 
            Field(default=default, description=description, **params)
        )
        logger.debug(f"添加字段: {field_name} - 类型: {field_type}")

        # 为特定字段添加验证器
        if field_name == "username":
            def username_validator(cls, v):
                """用户名验证器"""
                if "admin" in v.lower():
                    logger.warning(f"无效用户名: 包含 'admin' - {v}")
                    raise ValueError("Username cannot contain 'admin'")
                return v

            validators[f"validate_{field_name}"] = field_validator(field_name)(username_validator)
            logger.debug("添加用户名验证器")

    # 创建动态模型
    model = create_model(
        "DynamicForm",
        __base__=BaseModel,
        **field_definitions,
        __validators__=validators
    )
    logger.info("动态表单模型创建成功")
    return model

def validate_form_data(model: Type[BaseModel], data: Dict[str, Any]) -> BaseModel:
    """验证表单数据"""
    logger.info("开始验证表单数据...")
    logger.debug(f"验证数据: {data}")
    
    try:
        form = model(**data)
        logger.info("表单数据验证通过")
        return form
    except ValidationError as e:
        logger.error("表单数据验证失败")
        for error in e.errors():
            logger.error(f"验证错误 - 字段: {error['loc'][0]}, 错误: {error['msg']}")
        raise

def main():
    """主函数"""
    try:
        # 创建表单模型
        FormModel = create_form_model(form_fields)
        
        # 测试无效数据
        invalid_data = {
            "username": "admin_user",  # 无效
            "email": "invalid-email",
            "age": 17
        }
        
        logger.info("\n测试无效数据验证:")
        try:
            validate_form_data(FormModel, invalid_data)
        except ValidationError as e:
            logger.info("无效数据测试完成 (如预期失败)")
        
        # 测试有效数据
        logger.info("\n测试有效数据验证:")
        valid_data = {
            "username": "john_doe",
            "email": "john@example.com",
            "age": 30
        }
        valid_form = validate_form_data(FormModel, valid_data)
        logger.info(f"有效表单数据: {valid_form.model_dump()}")
        
        logger.info("\n动态表单验证测试完成")
        
    except Exception as e:
        logger.error(f"程序运行失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()
