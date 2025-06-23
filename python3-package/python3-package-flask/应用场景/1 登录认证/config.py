# config.py
class Config:
    """
    Flask 应用基础配置类

    可以继承为开发、测试、生产等不同环境配置
    """
    SECRET_KEY = 'your-secret-key'  # 密钥用于 session 安全
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'  # 数据库 URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用修改跟踪，节省资源
