# web.py

from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)

# ========================
# 🔧 配置：mock 模式 or 数据库模式
# ========================

# 设置为 True 使用 mock 数据（内存模拟），设置为 False 使用真实数据库
USE_MOCK = False

if not USE_MOCK:
    # 如果使用数据库，导入 SQLAlchemy 和 Migrate
    from flask_sqlalchemy import SQLAlchemy
    from flask_migrate import Migrate

    # 配置 SQLite 数据库 URI 和 SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SECRET_KEY'] = 'your_secret_key'

    # 初始化数据库和迁移工具
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    # 定义 Product 模型类（对应数据库表）
    class Product(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        price = db.Column(db.Float, nullable=False)

        def __repr__(self):
            return f"Product('{self.name}', ${self.price})"
else:
    # Mock 数据类：用于在不连接数据库时模拟数据模型
    class Product:
        def __init__(self, id, name, price):
            self.id = id
            self.name = name
            self.price = price

    # 内存中的产品列表（模拟数据库）
    mock_products = [
        Product(1, "Laptop", 999.99),
        Product(2, "Smartphone", 499.99),
        Product(3, "Tablet", 299.99),
    ]
    product_id_counter = 4  # 自增 ID 计数器


# ========================
# 💡 数据访问封装（兼容两种模式）
# ========================

def get_all_products():
    """
    获取所有产品（兼容 mock 和数据库模式）
    :return: 产品列表
    """
    if USE_MOCK:
        return mock_products
    else:
        return Product.query.all()


def create_product(name, price):
    """
    创建一个新产品（兼容 mock 和数据库模式）
    :param name: 产品名称
    :param price: 产品价格
    :return: 新创建的产品对象
    """
    if USE_MOCK:
        global product_id_counter, mock_products
        new_product = Product(product_id_counter, name, price)
        mock_products.append(new_product)
        product_id_counter += 1
        return new_product
    else:
        new_product = Product(name=name, price=price)
        db.session.add(new_product)
        db.session.commit()
        return new_product


# ========================
# 🌐 API 端点
# ========================

@app.route('/api/products', methods=['GET', 'POST'])
def products_api():
    """
    RESTful API 接口：
    - GET: 返回所有产品列表（JSON 格式）
    - POST: 接收 JSON 数据并创建新商品
    """
    try:
        if request.method == 'GET':
            products = get_all_products()
            return jsonify([{'id': p.id, 'name': p.name, 'price': p.price} for p in products])

        if request.method == 'POST':
            data = request.json
            new_product = create_product(data['name'], data['price'])
            return jsonify({'message': 'Product created', 'id': new_product.id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================
# 🖥️ Web 页面路由
# ========================

@app.route('/')
def home():
    """
    主页视图函数
    显示所有产品信息（从数据库或 mock 数据中获取）
    """
    products = get_all_products()
    return render_template('index.html', products=products)


@app.route('/add_product', methods=['POST'])
def add_product():
    """
    添加产品页面（POST 请求）
    接收 HTML 表单提交的数据，并调用 create_product 方法保存
    """
    try:
        name = request.form['name']
        price = float(request.form['price'])
        create_product(name, price)
        return redirect(url_for('home'))
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ========================
# 🚀 启动入口
# ========================

if __name__ == '__main__':
    try:
        if not USE_MOCK:
            # 如果不是 mock 模式，在启动前初始化数据库
            with app.app_context():
                db.create_all()  # 创建所有未存在的表
                print("✅ 数据库已初始化")
        print("🚀 启动应用...")
        app.run(debug=False)  # 生产环境建议关闭 debug 模式
    except Exception as e:
        print(f"❌ 启动失败: {e}")
