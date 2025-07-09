import logging
import re
from pydantic import BaseModel, ValidationError, ValidationInfo, field_validator
from pydantic.functional_validators import AfterValidator
from typing import Annotated

# 初始化日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

def validate_password(value: str) -> str:
    """密码验证函数"""
    logger.debug(f"开始验证密码: {value[:1]}...")  # 只记录第一个字符避免泄露密码
    
    if len(value) < 8:
        logger.error("密码长度不足8个字符")
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", value):
        logger.error("密码缺少大写字母")
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", value):
        logger.error("密码缺少小写字母")
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", value):
        logger.error("密码缺少数字")
        raise ValueError("Password must contain at least one digit")
    if not re.search(r"[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]", value):
        logger.error("密码缺少特殊字符")
        raise ValueError("Password must contain at least one special character")
    
    logger.debug("密码验证通过")
    return value

SecurePassword = Annotated[str, AfterValidator(validate_password)]

class UserRegistration(BaseModel):
    """用户注册模型"""
    username: str
    password: SecurePassword
    confirm_password: str

    @field_validator('confirm_password')
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        """验证两次密码是否匹配"""
        logger.debug("验证密码匹配")
        if 'password' in info.data and v != info.data['password']:
            logger.error("两次输入的密码不匹配")
            raise ValueError("Passwords do not match")
        return v

    @field_validator('username', mode='after')
    def normalize_username(cls, v: str) -> str:
        """用户名标准化处理"""
        normalized = v.strip().lower()
        logger.debug(f"用户名标准化: {v} -> {normalized}")
        return normalized

    @field_validator('username')
    def validate_username_length(cls, v: str) -> str:
        """验证用户名长度"""
        logger.debug(f"验证用户名长度: {v}")
        if len(v) < 3:
            logger.error("用户名太短")
            raise ValueError("Username must be at least 3 characters long")
        return v

    @field_validator('username')
    def validate_username_chars(cls, v: str) -> str:
        """验证用户名字符"""
        logger.debug(f"验证用户名字符: {v}")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            logger.error("用户名包含非法字符")
            raise ValueError("Username can only contain letters, numbers and underscores")
        return v

def validate_user_registration(data: dict) -> UserRegistration:
    """验证用户注册数据"""
    try:
        logger.info("开始验证用户注册数据")
        user = UserRegistration(**data)
        logger.info("用户注册数据验证成功")
        return user
    except ValidationError as e:
        logger.error("用户注册数据验证失败")
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error['loc'])
            logger.error(f"{field}: {error['msg']}")
        raise

def main():
    """主函数"""
    try:
        # 测试无效数据
        logger.info("\n测试无效用户注册数据:")
        try:
            validate_user_registration({
                "username": "alice!",
                "password": "weak",
                "confirm_password": "wrong"
            })
        except ValidationError:
            logger.info("无效数据测试完成 (如预期失败)")
        
        # 测试有效数据
        logger.info("\n测试有效用户注册数据:")
        valid_user = validate_user_registration({
            "username": "alice_smith",
            "password": "StrongP@ss123",
            "confirm_password": "StrongP@ss123"
        })
        logger.info(f"有效用户数据: {valid_user}")
        
        logger.info("\n用户注册验证测试完成")
    except Exception as e:
        logger.error(f"程序运行失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()
