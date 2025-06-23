from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


# 定义数据模型
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Todo {self.title}>'


# 创建数据库表
# 标志变量，确保初始化只运行一次
initialized = False

@app.before_request
def create_tables():
    global initialized
    if not initialized:
        db.create_all()
        initialized = True


# 定义序列化模式
class TodoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Todo
        include_fk = True


todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)

# 静态文件路由
@app.route('/')
def index():
    # return app.send_static_file('index.html')  # 或使用 render_template('index.html')
    return render_template('index.html')

@app.route('/edit.html')
def edit_page():
    # return app.send_static_file('edit.html') # 需要放到 静态文件目录 static 下
    return render_template('edit.html') # 使用模板

# API 路由
@app.route('/api/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify(todos_schema.dump(todos))


@app.route('/api/todos/<int:id>', methods=['GET'])
def get_todo(id):
    todo = Todo.query.get_or_404(id)
    return jsonify(todo_schema.dump(todo))


@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()

    # 验证数据
    if 'title' not in data:
        return jsonify({'error': '缺少标题'}), 400

    # 创建待办事项
    new_todo = Todo(
        title=data['title'],
        description=data.get('description', ''),
        completed=data.get('completed', False)
    )

    # 设置截止日期（如果提供）
    if 'due_date' in data:
        try:
            new_todo.due_date = datetime.fromisoformat(data['due_date'])
        except ValueError:
            return jsonify({'error': '无效的日期格式'}), 400

    db.session.add(new_todo)
    db.session.commit()

    return jsonify(todo_schema.dump(new_todo)), 201


@app.route('/api/todos/<int:id>', methods=['PUT'])
def update_todo(id):
    todo = Todo.query.get_or_404(id)
    data = request.get_json()

    # 更新字段
    if 'title' in data:
        todo.title = data['title']
    if 'description' in data:
        todo.description = data['description']
    if 'completed' in data:
        todo.completed = data['completed']
    if 'due_date' in data:
        try:
            todo.due_date = datetime.fromisoformat(data['due_date'])
        except ValueError:
            return jsonify({'error': '无效的日期格式'}), 400

    db.session.commit()
    return jsonify(todo_schema.dump(todo))


@app.route('/api/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': '待办事项已删除'})


if __name__ == '__main__':
    app.run(debug=False)