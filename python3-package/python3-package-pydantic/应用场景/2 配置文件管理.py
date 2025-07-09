import logging
import os
from typing import Literal
from pydantic import BaseModel, Field, field_validator, DirectoryPath, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# 初始化日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

class DatabaseConfig(BaseModel):
    """数据库配置模型"""
    host: str = Field("localhost", description="数据库主机地址")
    port: int = Field(5432, ge=1024, le=65535, description="数据库端口")
    user: str = Field(..., description="数据库用户名")
    password: str = Field(..., description="数据库密码")
    name: str = Field("app_db", description="数据库名称")
    pool_size: int = Field(10, gt=0, description="连接池大小")
    timeout: int = Field(30, gt=0, description="连接超时时间(秒)")

class LoggingConfig(BaseModel):
    """日志配置模型"""
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("INFO", description="日志级别")
    path: str = Field(default="./logs", description="日志文件路径")  # 改为字符串类型
    max_size: int = Field(100, description="日志文件最大大小(MB)")
    backup_count: int = Field(5, description="日志备份数量")

    @field_validator('path')
    def path_must_exist(cls, v: str) -> str:
        """验证日志路径是否存在，不存在则创建"""
        try:
            path = os.path.abspath(os.path.expanduser(v))
            if not os.path.exists(path):
                logger.info(f"创建日志目录: {path}")
                os.makedirs(path, exist_ok=True)
            return path
        except Exception as e:
            logger.error(f"日志目录处理失败: {str(e)}")
            raise ValueError(f"无效的日志路径: {v}")


class AppConfig(BaseSettings):
    """应用配置模型(从环境变量和.env文件加载)"""
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    debug: bool = Field(False, description="调试模式")
    workers: int = Field(4, ge=1, description="工作线程数")
    api_key: str = Field(..., min_length=32, description="API密钥")

    database: DatabaseConfig
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

def load_config() -> AppConfig:
    """加载应用配置"""
    try:
        logger.info("正在加载应用配置...")
        config = AppConfig()
        logger.info("应用配置加载成功")
        logger.debug(f"完整配置信息:\n{config.model_dump_json(indent=2)}")
        return config
    except ValidationError as e:
        logger.error(f"配置验证失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"配置加载失败: {str(e)}")
        raise

def main():
    """主函数"""
    try:
        # 加载配置
        config = load_config()
        
        # 应用配置
        logger.setLevel(config.logging.level)
        
        # 示例使用配置
        logger.info(f"数据库主机: {config.database.host}")
        logger.info(f"日志级别: {config.logging.level}")
        
        # 动态更新配置示例
        config.database.pool_size = 20
        logger.info(f"更新后的连接池大小: {config.database.pool_size}")
        
        # 导出配置到JSON
        config_json = config.model_dump_json(indent=2)
        logger.debug("当前配置JSON:\n" + config_json)
        
        logger.info("应用配置管理完成")
    except Exception as e:
        logger.error(f"应用运行失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()
