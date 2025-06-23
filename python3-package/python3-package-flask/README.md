# 快速开始

## 介绍

Flask - 轻量级微框架

应用场景：API服务、小型应用、快速原型开发

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装依赖
# Flask生态
pip install flask 

# 可选的，数据库、表单、认证等
pip install flask-sqlalchemy flask-migrate flask-cors

# 可选的，序列化与反序列化
pip install flask-marshmallow marshmallow-sqlalchemy

# or
pip install -r requirements.txt
```

验证：

```shell
pip show flask
```

启动命令：

```shell
flask --app web.py run
```

## 示例

