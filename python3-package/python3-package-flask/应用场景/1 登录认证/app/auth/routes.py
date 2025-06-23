# app/auth/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from ..models import User
from .. import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # 检查用户名或邮箱是否已存在
        existing_user = User.query.filter_by(username=username).first() or \
                        User.query.filter_by(email=email).first()

        if existing_user:
            flash('用户名或邮箱已存在', 'danger')
            return redirect(url_for('auth.register'))

        # 创建新用户
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        # 验证用户存在且密码正确
        if user and user.password == password:
            login_user(user)
            flash('登录成功', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('main.index'))
