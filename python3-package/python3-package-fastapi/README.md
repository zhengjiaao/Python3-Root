# FastAPI Web框架

## 安装FastAPI模块

```shell
pip install fastapi
pip install uvicorn
```

> uvicorn用于运行 Python 的异步 Web 应用程序，与许多流行的 Python 框架（如 FastAPI、Starlette 等）兼容，
> 可以帮助开发者构建高效的异步 Web 服务

## 运行程序

在 PyCharm 的 Terminal 中运行 uvicorn 命令启动 FastAPI 应用程序

```shell
uvicorn main:apps --reload
```

这里的 main 是你的 Python 文件名（不含扩展名main方法的意思），app 是你创建的 FastAPI 应用程序实例。

uvicorn main:app --reload 命令含义如下:

* main：main.py 文件（一个 Python “模块”）。
* app：在 main.py 文件中通过 app = FastAPI() 创建的对象。
* --reload：让服务器在更新代码后重新启动。仅在开发时使用该选项。

## 访问 API文档界面

* API文档界面： http://127.0.0.1:8000/docs

测试：

* http://localhost:8000/
* http://localhost:8000/items/1