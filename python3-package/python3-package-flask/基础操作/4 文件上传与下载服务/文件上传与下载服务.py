from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'  # 设置密钥用于 flash 消息
app.config['UPLOAD_FOLDER'] = 'uploads'  # 文件上传目录
# app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 最大上传文件大小：100MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024  # 最大上传文件大小：5GB
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}  # 允许的文件类型集合

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """
    检查文件扩展名是否允许上传。

    :param filename: 原始文件名
    :return: True 如果是允许的文件类型，否则 False
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# 注册 Jinja2 过滤器：将时间戳格式化为可读时间
@app.template_filter('datetimeformat')
def datetime_format(value):
    """
    将时间戳转换为可读性更好的日期时间格式。

    :param value: 时间戳（float 或 int）
    :return: 格式化后的字符串，如 "2025-06-23 09:30:00"
    """
    dt = datetime.fromtimestamp(value)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    """
    主页视图：列出所有已上传的文件及其信息（名称、大小、修改时间）。
    """
    files = []
    upload_dir = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(upload_dir):
        path = os.path.join(upload_dir, filename)
        if os.path.isfile(path):
            files.append({
                'name': filename,
                'size': os.path.getsize(path),          # 文件大小（字节）
                'modified': os.path.getmtime(path)      # 最后修改时间戳
            })

    return render_template('file_index.html', files=files)


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    处理文件上传请求：
    - 检查是否有文件上传
    - 校验文件名是否为空
    - 校验文件类型是否允许
    - 安全保存文件
    """
    if 'file' not in request.files:
        flash('没有选择文件', 'danger')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('没有选择文件', 'danger')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('文件上传成功', 'success')
    else:
        flash('不允许的文件类型', 'danger')

    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    """
    提供文件下载功能。

    :param filename: 要下载的文件名
    :return: 将文件作为附件返回给客户端
    """
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )


@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """
    删除指定文件。

    :param filename: 要删除的文件名
    """
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            flash('文件已删除', 'success')
        else:
            flash('文件不存在', 'danger')
    except Exception as e:
        flash(f'删除失败: {str(e)}', 'danger')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=False)
