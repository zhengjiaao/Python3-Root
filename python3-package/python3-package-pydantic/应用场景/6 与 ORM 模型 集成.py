import logging
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, event
from sqlalchemy.orm import declarative_base, Session
from typing import Optional

# 初始化日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# SQLAlchemy 模型
Base = declarative_base()

class UserDB(Base):
    """数据库用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True)
    age = Column(Integer)
    hashed_password = Column(String(100))

    def __repr__(self):
        return f"UserDB(id={self.id}, name={self.name}, email={self.email})"

# Pydantic 模型
class UserBase(BaseModel):
    """用户基础模型"""
    name: str
    email: str

class UserCreate(UserBase):
    """用户创建模型"""
    password: str

class UserRead(UserBase):
    """用户读取模型"""
    id: int
    age: Optional[int] = None

    # 配置 ORM 模式
    model_config = ConfigDict(from_attributes=True)

def setup_database():
    """初始化数据库"""
    logger.info("初始化数据库引擎和表结构")
    engine = create_engine("sqlite:///:memory:")
    
    # 添加连接事件日志
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_connection, connection_record):
        logger.debug("数据库连接建立")

    @event.listens_for(engine, "close")
    def receive_close(dbapi_connection, connection_record):
        logger.debug("数据库连接关闭")
    
    Base.metadata.create_all(bind=engine)
    return engine

def create_user(db: Session, user: UserCreate) -> UserDB:
    """创建用户"""
    logger.info(f"创建新用户: {user.name}")
    logger.debug(f"用户详情 - 邮箱: {user.email}")
    
    # 在实际应用中，这里应该进行密码哈希
    db_user = UserDB(
        name=user.name,
        email=user.email,
        age=25,  # 默认年龄
        hashed_password=f"hashed_{user.password}"  # 模拟哈希
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"用户创建成功，ID: {db_user.id}")
        return db_user
    except Exception as e:
        db.rollback()
        logger.error(f"用户创建失败: {str(e)}")
        raise

def main():
    """主函数"""
    try:
        logger.info("开始ORM集成演示")
        
        # 初始化数据库
        engine = setup_database()
        
        with Session(engine) as session:
            # 创建用户
            new_user = UserCreate(
                name="Bob Johnson",
                email="bob@example.com",
                password="secure123"
            )
            
            db_user = create_user(session, new_user)
            
            # 转换为响应模型
            logger.info("将ORM对象转换为Pydantic模型")
            user_response = UserRead.model_validate(db_user)
            logger.info(f"用户响应数据: {user_response.model_dump()}")
            
            # 更新操作
            logger.info("更新用户年龄")
            db_user.age = 30
            session.commit()
            
            # 重新加载
            updated_user = UserRead.model_validate(db_user)
            logger.info(f"更新后的用户数据: {updated_user.model_dump()}")
            
        logger.info("ORM集成演示完成")
    except Exception as e:
        logger.error(f"程序运行失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()
