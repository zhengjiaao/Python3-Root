
##  打包

```shell
# 安装
pip install pyinstaller

# 打包：简单命令
pyinstaller --add-data "config.py;." --add-data "app;app" --clean --name=my_flask_app run.py
# 打包：单文件模式 + 隐藏控制台窗口
pyinstaller --add-data "config.py;." --add-data "app;app" --onefile --noconsole --clean --name=my_flask_app run.py
# 打包：单文件模式 + 添加图标 + 隐藏控制台窗口
pyinstaller --add-data "config.py;." --add-data "app;app" --onefile --noconsole --icon=app.ico --clean --name=my_flask_app run.py
```