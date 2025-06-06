# Python3 打包成exe

- [pyinstaller.org](https://pyinstaller.org/en/stable/)

## 安装

安装

```shell
pip install pyinstaller
```

## 使用（打包命令）

```shell
# 打包命令
# 基本打包（生成目录）
pyinstaller your_script.py

# 单文件模式 + 添加图标
pyinstaller --onefile --icon=app.ico your_script.py

# 打包命令：单文件模式 + 隐藏控制台窗口 + 添加图标
pyinstaller --onefile --noconsole --icon=app.ico your_script.py

# 打包资源文件（格式：源路径[分隔符]目标路径）
# Windows 用 `;`，Linux/macOS 用 `:`
pyinstaller --add-data "data/*;data" your_script.py  # Windows
pyinstaller --add-data "data/*:data" your_script.py  # Linux/macOS

# 隐藏控制台（GUI 程序）
pyinstaller --noconsole your_script.py

# 加密字节码（需安装 tinyaes）
pyinstaller --onefile --key=123456 your_script.py
```

输出结构：

```text
dist/
   ├── your_script.exe          # 可执行文件（单文件模式仅此文件）
   └── your_script/             # 目录模式
        ├── your_script.exe     # 主程序
        ├── lib/                # 依赖库
        ├── data/               # 资源文件
        └── ...                 # 其他依赖
build/                         # 临时构建文件（可忽略）
your_script.spec              # 配置文件（可修改后重新打包）
```

## 示例


#### 普通脚本打包成exe

创建 python 脚本:`your_script.py`

```python
#!/usr/bin/python3

import time

# 第一个注释
print("Hello, Python!")  # 第二个注释

if True:
    print("True")
else:
    print("False")

time.sleep(10)
```

打包成exe可执行文件

```shell
pyinstaller your_script.py

# or
pyinstaller -F your_script.py
```

- 执行完毕会生成【build】【dist】文件夹和【.spec】结尾的文件。
- exe文件在【dist】文件夹里面。


#### GUI程序打包成exe

安装PyQt5：

```python
pip install PyQt5
pip install PyQt5-stubs
```

创建 python 脚本:`your_gui_program.py`

```python
import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QCheckBox, QRadioButton, QGroupBox, QProgressBar,
    QSlider, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit,
    QListWidget, QTabWidget, QFileDialog, QMessageBox, QInputDialog
)

# app = QApplication(sys.argv)
# window = QWidget()
# window.setWindowTitle('PyQt5 Test')
# # window.setGeometry(100, 100, 200, 200) # 设置窗口大小和位置
# # window.resize(400, 300) # 设置窗口大小
# # window.move(300, 300) # 设置窗口位置
# window.show()
# sys.exit(app.exec_())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('PyQt5 Test')
    # window.setGeometry(100, 100, 200, 200) # 设置窗口大小和位置
    # window.resize(400, 300) # 设置窗口大小
    # window.move(300, 300) # 设置窗口位置
    window.show()
    sys.exit(app.exec_())

## 运行上述代码，PyQt5 将在屏幕上显示一个窗口，标题为“PyQt5 Test”。
```

打包成exe可执行文件

```shell
pyinstaller your_gui_program.py
```

- 执行完毕会生成【build】【dist】文件夹和【.spec】结尾的文件。
- exe文件在【dist】文件夹里面。
- 打包后务必在纯净系统测试功能完整性。

## 注意事项

#### 路径处理技巧

在代码中获取资源路径（兼容开发/打包环境）：

```python
import sys
import os

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # 临时解压目录
else:
    base_path = os.path.dirname(__file__)

resource_path = os.path.join(base_path, "data/file.txt")
```
