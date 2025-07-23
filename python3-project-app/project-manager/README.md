# 快速开始

## 介绍

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

## 创建虚拟环境

```shell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate     # Windows
source venv/bin/activate  # Linux/Mac
```

## 安装依赖

```shell
# 安装依赖
pip install fastapi uvicorn sqlalchemy pymysql python-dotenv

# or
pip install -r requirements.txt
```

验证：

```shell
pip show fastapi
```

## 运行项目

创建数据库

```shell
CREATE DATABASE project_db;
```

启动

```shell
uvicorn app.main:app --reload
```


