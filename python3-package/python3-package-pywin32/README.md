# pywin32 用于操作Excel应用程序

- [菜鸟教程 | Python3 PyQt5](https://www.runoob.com/python3/python-pyqt.html)
- [Python3 PyQt5 各种示例](https://github.com/PyQt5/PyQt)

注意：由于pywin32是操作COM接口，因此代码需要在Windows系统上运行，并且安装了Microsoft Excel。

## 介绍

* 基础操作（启动Excel、打开/创建工作簿、操作工作表、读写单元格、保存和关闭）
* 高级功能（格式设置、公式、图表、宏、事件处理）

pywin32 依赖要求：

1. 仅支持 Windows 系统
2. 需要安装 Microsoft Excel
3. 使用前确保没有 Excel 进程残留

### 替代方案对比

| **库**         | **优点**                         | **缺点**                    |
| :------------- | :------------------------------- | :-------------------------- |
| **`pywin32`**  | 功能全面（支持宏、格式、图片等） | 仅限 Windows，需安装 Office |
| **`openpyxl`** | 跨平台，无需 Excel 环境          | 不支持 VBA 宏               |
| **`xlwings`**  | 封装 `pywin32`，语法更简洁       | 同样依赖 Windows 环境       |

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装依赖库
pip install pywin32

# or
pip install -r requirements.txt
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