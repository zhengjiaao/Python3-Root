# app/__init__.py
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 支持打包后的资源路径
def resource_path(relative_path):
    """ 获取打包后资源的正确路径 """
    if getattr(sys, 'frozen', False):  # 是否被打包
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    template_folder = resource_path("app/templates")
    static_folder = resource_path("app/static")
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    # app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # 注册蓝图
    from .main.routes import main_bp
    from .auth.routes import auth_bp
    from .profile.routes import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))
