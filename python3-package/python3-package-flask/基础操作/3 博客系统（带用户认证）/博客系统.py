from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PER_PAGE'] = 5  # 每页显示的文章数量

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'  # 设置登录提示消息类别


# 用户模型
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True)

    @property
    def password(self):
        raise AttributeError('密码是不可读属性')

    @password.setter
    def password(self, password):
        """设置密码哈希值"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """验证密码"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# 博客文章模型
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Post {self.title}>'


# 创建数据库表 数据库初始化
# 替换原来的 @app.before_first_request
initialized = False

@app.before_request
def create_tables():
    """创建所有数据库表并初始化默认用户"""
    global initialized
    if not initialized:
        db.create_all()

        # 创建初始用户（如果不存在）
        if not User.query.filter_by(username='admin').first():
            try:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    password='adminpassword'
                )
                db.session.add(admin)
                db.session.commit()
                print("初始用户已创建")
            except Exception as e:
                db.session.rollback()
                print(f"创建初始用户失败: {str(e)}")

        initialized = True


# Flask-Login 加载用户 登录管理器
@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    return User.query.get(int(user_id))

def get_paginated_posts(query, page, per_page):
    """获取分页文章数据"""
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination.items, pagination


# 首页 - 显示所有博客文章
@app.route('/')
def index():
    """首页 - 显示所有博客文章"""
    page = request.args.get('page', 1, type=int)
    per_page = app.config['PER_PAGE']

    try:
        posts_query = Post.query.order_by(Post.created_at.desc())
        posts, pagination = get_paginated_posts(posts_query, page, per_page)

        return render_template('index.html', posts=posts, pagination=pagination)
    except Exception as e:
        app.logger.error(f"获取文章列表失败: {str(e)}")
        flash('加载文章列表时发生错误', 'danger')
        return render_template('index.html', posts=[], pagination=None)


# 查看文章详情
@app.route('/post/<int:post_id>')
def view_post(post_id):
    """查看文章详情"""
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)


# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 表单验证
        if not all([username, email, password, confirm_password]):
            flash('所有字段都是必填项', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('密码长度至少为6个字符', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('用户名已被使用', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'danger')
            return redirect(url_for('register'))

        # 创建新用户
        try:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            flash('注册成功！请登录', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"注册失败: {str(e)}")
            flash('注册过程中发生错误，请稍后再试', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')


# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        remember = bool(request.form.get('remember'))

        # 表单验证
        if not all([username, password]):
            flash('用户名和密码都是必填项', 'danger')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()

        if user and user.verify_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('login.html')



# 用户登出
@app.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('您已成功登出', 'success')
    return redirect(url_for('index'))


# 创建新文章
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    """创建新文章"""
    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content']

        # 表单验证
        if not title or not content:
            flash('标题和内容不能为空', 'danger')
            return redirect(url_for('new_post'))

        if len(title) > 100:
            flash('标题不能超过100个字符', 'danger')
            return redirect(url_for('new_post'))

        # 创建新文章
        try:
            new_post = Post(title=title, content=content, author=current_user)
            db.session.add(new_post)
            db.session.commit()

            flash('文章已发布', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"创建文章失败: {str(e)}")
            flash('发布文章时发生错误', 'danger')
            return redirect(url_for('new_post'))

    return render_template('new_post.html')



# 编辑文章
@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """编辑文章"""
    post = Post.query.get_or_404(post_id)

    # 权限检查
    if post.author != current_user:
        flash('您没有权限编辑此文章', 'danger')
        return redirect(url_for('view_post', post_id=post_id))

    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content']

        # 表单验证
        if not title or not content:
            flash('标题和内容不能为空', 'danger')
            return redirect(url_for('edit_post', post_id=post_id))

        if len(title) > 100:
            flash('标题不能超过100个字符', 'danger')
            return redirect(url_for('edit_post', post_id=post_id))

        # 更新文章
        try:
            post.title = title
            post.content = content
            db.session.commit()

            flash('文章已更新', 'success')
            return redirect(url_for('view_post', post_id=post_id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"更新文章失败: {str(e)}")
            flash('更新文章时发生错误', 'danger')
            return redirect(url_for('edit_post', post_id=post_id))

    return render_template('edit_post.html', post=post)


# 删除文章
@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """删除文章"""
    post = Post.query.get_or_404(post_id)

    # 权限检查
    if post.author != current_user:
        flash('您没有权限删除此文章', 'danger')
        return redirect(url_for('view_post', post_id=post_id))

    # 删除文章
    try:
        db.session.delete(post)
        db.session.commit()

        flash('文章已删除', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"删除文章失败: {str(e)}")
        flash('删除文章时发生错误', 'danger')
        return redirect(url_for('view_post', post_id=post_id))



# 用户个人资料
@app.route('/user/<username>')
def user_profile(username):
    """用户个人资料"""
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = app.config['PER_PAGE']

    try:
        posts_query = Post.query.filter_by(author=user).order_by(Post.created_at.desc())
        posts, pagination = get_paginated_posts(posts_query, page, per_page)

        return render_template('profile.html', user=user, posts=posts, pagination=pagination)
    except Exception as e:
        app.logger.error(f"加载用户资料失败: {str(e)}")
        flash('加载用户资料时发生错误', 'danger')
        return render_template('profile.html', user=user, posts=[], pagination=None)


if __name__ == '__main__':
    app.run(debug=False)