# app.py

from flask import Flask, request, session, redirect, url_for, render_template, jsonify
from mongo import MongoDBManager, MongoDBUserManager, MongoDBProductManager, MongoDBOrderManager, object_id_to_str,str_to_object_id
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于 Session 加密

# 初始化数据库连接
db_manager = MongoDBManager()
user_manager = MongoDBUserManager(db_manager)
product_manager = MongoDBProductManager(db_manager)
order_manager = MongoDBOrderManager(db_manager)


# ========================
# 🔐 用户相关路由
# ========================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        success, msg = user_manager.register_user(name, email, password)
        return jsonify({"success": success, "message": msg})
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db_manager.get_collection("users").find_one({"email": email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = str(user['_id'])
            return jsonify({"success": True, "redirect": url_for('index')})
        return jsonify({"success": False, "message": "邮箱或密码错误"})
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ========================
# 🛍️ 商品相关路由
# ========================

@app.route('/')
def index():
    query = request.args.get('query', '')
    category = request.args.get('category', None)
    min_price = float(request.args.get('min_price', 0))
    max_price = float(request.args.get('max_price', 10000))
    page = int(request.args.get('page', 1))

    results = product_manager.search_products(query, category, min_price, max_price, page, per_page=10)
    return render_template('index.html', results=results, query=query, category=category)

# ========================
# 📄 商品详情页
# ========================

@app.route('/product/<product_id>')
def product_detail(product_id):
    # 查询商品
    product = db_manager.get_collection("products").find_one({
        "_id": str_to_object_id(product_id)
    })

    if not product:
        return "商品不存在", 404

    # 转换 _id 为字符串
    product = object_id_to_str(product)

    # 渲染模板
    return render_template('product_detail.html', product=product)


# ========================
# 📦 订单相关路由
# ========================

@app.route('/order/create', methods=['POST'])
def create_order():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "请先登录"})

    items = request.json.get('items', [])
    success, msg = order_manager.create_order(session['user_id'], items)
    return jsonify({"success": success, "message": msg})


# ========================
# 🚀 启动入口
# ========================

if __name__ == '__main__':
    db_manager.create_indexes()
    app.run(debug=False)
