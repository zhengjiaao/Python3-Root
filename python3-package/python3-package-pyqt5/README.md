# PyQt5 创建图形用户界面（GUI）

- [菜鸟教程 | Python3 PyQt5](https://www.runoob.com/python3/python-pyqt.html)
- [Python3 PyQt5 各种示例](https://github.com/PyQt5/PyQt)

## 介绍

PyQt 是一个强大的 Python 库，用于创建图形用户界面（GUI），可以用来代替 Python 内置的 Tkinter。

PyQt 是 Qt 框架的 Python 绑定，广泛应用于桌面应用程序开发。

Qt 是一个跨平台的 C++ 应用程序开发框架。

PyQt 允许 Python 开发者利用 Qt 库创建功能强大的 GUI 应用程序。

PyQt 有以下几个主要版本：

* PyQt4：基于 Qt4 的绑定
* PyQt5：基于 Qt5 的绑定
* PyQt6：基于 Qt6 的绑定（最新版本）

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装PyQt5
pip install PyQt5
pip install PyQt5-stubs

# 安装Qt设计师和其他工具（可选）
#pip install PyQt5-tools

# or
pip install -r requirements.txt
```

验证：

```shell
pip show pyqt5
```

## PyQt5 示例

#### 验证 PyQt5 是否正确安装

创建 一个名为 `test_pyqt5.py` 的文件，并运行命令 `python test_pyqt5.py`

```python
import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QCheckBox, QRadioButton, QGroupBox, QProgressBar,
    QSlider, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit,
    QListWidget, QTabWidget, QFileDialog, QMessageBox, QInputDialog
)

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