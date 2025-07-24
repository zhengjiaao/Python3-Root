# 快速开始

## 介绍

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装依赖
pip install setuptools

# or
pip install -r requirements.txt
```

验证：

```shell
pip show setuptools
```

## 启动项目

```shell
uvicorn app.main:app --reload --port 8000
# or
python run.py
```

访问方式：

Swagger UI: http://localhost:8000/docs

前端测试页: http://localhost:8000/templates/index.html

