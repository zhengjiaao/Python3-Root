# PyQt5 创建图形用户界面（GUI）

- [菜鸟教程 | Python3 PyQt5](https://www.runoob.com/python3/python-pyqt.html)
- [Python3 PyQt5 各种示例](https://github.com/PyQt5/PyQt)

## 介绍

PyQt5 是一个强大的 Python GUI 框架，用于创建功能丰富的桌面应用程序。

#### 核心优势

- **跨平台支持**：Windows、macOS、Linux 兼容
- **丰富组件库**：提供 600+ 类和 6000+ 函数
- **现代 UI 设计**：支持 CSS 样式表美化界面
- **多线程支持**：QThread 实现后台任务处理
- **信号槽机制**：优雅的事件处理方式
- **强大工具集**：包含数据库、网络、多媒体等功能

#### 应用场景

1. **企业桌面应用**：数据管理系统、ERP 系统
2. **科学计算工具**：数据分析、可视化界面
3. **多媒体应用**：音视频播放器、图像处理工具
4. **工业控制界面**：设备监控、数据采集系统
5. **教育软件**：教学工具、实验模拟平台

#### PyQt版本

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
pip install pyqt5-tools

pip install pyqt5==5.15.9
pip install pyqt5-tools==5.15.9.3.3

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

## PyQt5 最佳实践

#### 1.项目结构组织

```text
my_qt_app/
├── main.py                 # 应用入口
├── ui/                     # UI 文件目录
│   ├── main_window.ui
│   └── dialogs/
│       ├── settings_dialog.ui
│       └── about_dialog.ui
├── core/                   # 核心逻辑
│   ├── app_logic.py
│   ├── database.py
│   └── utils.py
├── views/                  # 自定义视图组件
│   ├── custom_widgets.py
│   └── charts.py
├── resources/              # 资源文件
│   ├── icons/
│   │   ├── app_icon.png
│   │   └── ...
│   └── styles/
│       ├── dark_theme.qss
│       └── light_theme.qss
└── requirements.txt
```

#### 2. 样式表使用技巧

```python
# 加载外部样式表
def load_stylesheet(app, theme="light"):
    style_file = f"resources/styles/{theme}_theme.qss"
    try:
        with open(style_file, "r") as f:
            style = f.read()
            app.setStyleSheet(style)
    except FileNotFoundError:
        print(f"样式表文件未找到: {style_file}")

# 常用样式表示例
"""
/* 主窗口样式 */
QMainWindow {
    background-color: #f0f0f0;
    font-family: "Segoe UI", Arial, sans-serif;
}

/* 按钮样式 */
QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #45a049;
}

QPushButton:pressed {
    background-color: #3d8b40;
}

/* 表格样式 */
QTableView {
    gridline-color: #d0d0d0;
    alternate-background-color: #f8f8f8;
}

QHeaderView::section {
    background-color: #e0e0e0;
    padding: 4px;
    border: 1px solid #c0c0c0;
}

/* 标签页样式 */
QTabWidget::pane {
    border: 1px solid #c0c0c0;
    background: white;
}

QTabBar::tab {
    background: #e0e0e0;
    border: 1px solid #c0c0c0;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background: white;
    border-bottom-color: white;
}
"""
```

#### 3. 国际化支持

```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtCore import QTranslator, QLocale

class I18nApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多语言应用")
        self.setGeometry(100, 100, 400, 200)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 布局
        layout = QVBoxLayout(central_widget)
        
        self.welcome_label = QLabel("欢迎使用本应用!")
        layout.addWidget(self.welcome_label)
        
        self.info_label = QLabel("这是一个演示多语言支持的应用")
        layout.addWidget(self.info_label)
        
        # 语言切换按钮
        btn_layout = QHBoxLayout()
        
        english_btn = QPushButton("English")
        english_btn.clicked.connect(lambda: self.change_language('en'))
        
        chinese_btn = QPushButton("中文")
        chinese_btn.clicked.connect(lambda: self.change_language('zh'))
        
        french_btn = QPushButton("Français")
        french_btn.clicked.connect(lambda: self.change_language('fr'))
        
        btn_layout.addWidget(english_btn)
        btn_layout.addWidget(chinese_btn)
        btn_layout.addWidget(french_btn)
        
        layout.addLayout(btn_layout)
        
        # 初始化翻译器
        self.translator = QTranslator()
        
        # 加载默认语言
        self.change_language(QLocale.system().name()[:2])
    
    def change_language(self, lang_code):
        # 移除旧翻译
        QApplication.removeTranslator(self.translator)
        
        # 加载新翻译
        if lang_code == 'zh':
            self.translator.load("translations/app_zh.qm")
        elif lang_code == 'fr':
            self.translator.load("translations/app_fr.qm")
        else:  # 默认英语
            self.translator.load("")  # 空翻译文件恢复为英文
        
        # 应用翻译
        QApplication.installTranslator(self.translator)
        
        # 更新界面文本
        self.retranslateUi()
    
    def retranslateUi(self):
        self.setWindowTitle(QApplication.translate("MainWindow", "多语言应用"))
        self.welcome_label.setText(QApplication.translate("MainWindow", "欢迎使用本应用!"))
        self.info_label.setText(QApplication.translate("MainWindow", "这是一个演示多语言支持的应用"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建翻译器
    translator = QTranslator()
    app.installTranslator(translator)
    
    window = I18nApp()
    window.show()
    
    sys.exit(app.exec_())
```

#### 4. PyQt5 核心组件与功能：

| **组件/功能**           | **描述**     | **关键类/函数**              |
| :---------------------- | :----------- | :--------------------------- |
| `QMainWindow`           | 主窗口框架   | `setCentralWidget()`         |
| `QWidget`               | 基础控件容器 | `QHBoxLayout`, `QVBoxLayout` |
| `QPushButton`           | 按钮控件     | `clicked` 信号               |
| `QLabel`                | 文本标签     | `setText()`, `setPixmap()`   |
| `QLineEdit`             | 单行文本输入 | `text()`, `setText()`        |
| `QTextEdit`             | 多行文本编辑 | `toPlainText()`, `append()`  |
| `QComboBox`             | 下拉选择框   | `addItem()`, `currentText()` |
| `QTableWidget`          | 表格控件     | `setRowCount()`, `setItem()` |
| `QFileDialog`           | 文件对话框   | `getOpenFileName()`          |
| `QMessageBox`           | 消息对话框   | `information()`, `warning()` |
| `QThread`               | 多线程支持   | `start()`, `run()`           |
| `QMediaPlayer`          | 多媒体播放   | `setMedia()`, `play()`       |
| `QPainter`              | 2D 绘图      | `drawLine()`, `drawRect()`   |
| `QSqlDatabase`          | 数据库连接   | `addDatabase()`, `open()`    |
| `QNetworkAccessManager` | 网络访问     | `get()`, `post()`            |

#### 5. 创建一个简单的 PyQt5 应用程序。

安装
```shell
# 安装 PyQt5
pip install pyqt5

# 安装附加工具
pip install pyqt5-tools

```

使用
```python
# 基础示例
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

app = QApplication([])
window = QWidget()
window.setWindowTitle("PyQt5 示例")
label = QLabel("Hello PyQt5!", window)
window.show()
app.exec_()
```