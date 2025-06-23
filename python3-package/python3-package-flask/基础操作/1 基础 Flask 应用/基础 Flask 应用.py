from flask import Flask, jsonify, render_template, request, redirect, url_for

app = Flask(__name__)


# 首页路由
@app.route('/')
def home():
    return render_template('home.html')


# 关于页面
@app.route('/about')
def about():
    return render_template('about.html', title='关于我们')


# 用户个人资料
@app.route('/user/<username>')
def user_profile(username):
    return render_template('profile.html', username=username)


# API 示例
@app.route('/api/data')
def api_data():
    return jsonify({
        'status': 'success',
        'data': [1, 2, 3, 4, 5],
        'message': 'API 请求成功'
    })


# 表单处理示例
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # 这里可以添加保存到数据库或发送邮件的逻辑
        return redirect(url_for('contact_success', name=name))

    return render_template('contact.html')


@app.route('/contact/success/<name>')
def contact_success(name):
    return render_template('contact_success.html', name=name)


# 错误处理
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=False)