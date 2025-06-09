import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout,
    QLabel, QHBoxLayout, QStatusBar, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PathUtil import resource_path


# 假设这两个类分别保存在 PDF拆分工具.py 和 PDF提取工具.py 中
try:
    from PDF拆分工具 import PDFSplitterApp
    from PDF提取工具 import PDFExtractorApp
except ImportError as e:
    QMessageBox.critical(None, "导入错误", f"无法导入模块：{str(e)}")
    raise

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF 工具箱 - MyZheng")
        self.setWindowIcon(QIcon(resource_path("resources/logo.png")))  # 设置程序图标
        self.resize(480, 360)
        self.center_window()

        # 初始化子窗口引用
        self.split_window = None
        self.extract_window = None

        # 主样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f5ff;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
        """)

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("选择要使用的工具")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 按钮容器
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(40, 0, 40, 0)
        btn_layout.setSpacing(30)

        # 拆分按钮
        self.split_btn = QPushButton("📄 PDF 拆分工具")
        self.split_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.split_btn.clicked.connect(self.open_split_tool)
        btn_layout.addWidget(self.split_btn)

        # 提取按钮
        self.extract_btn = QPushButton("✂️ PDF 页面提取工具")
        self.extract_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.extract_btn.clicked.connect(self.open_extract_tool)
        btn_layout.addWidget(self.extract_btn)

        layout.addWidget(btn_container)

        # 版权信息
        copyright_label = QLabel("© 2025 MyZheng - PDF Tools")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: #777; font-size: 12px;")
        layout.addWidget(copyright_label)

        self.setCentralWidget(main_widget)

        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")

    def open_split_tool(self):
        self.statusBar.showMessage("正在打开 PDF 拆分工具...")
        if self.split_window is None or not self.split_window.isVisible():
            self.split_window = PDFSplitterApp()
            self.split_window.setAttribute(Qt.WA_DeleteOnClose)
            self.split_window.destroyed.connect(lambda: setattr(self, 'split_window', None))
            self.split_window.show()
        else:
            self.split_window.raise_()
        self.statusBar.showMessage("就绪")

    def open_extract_tool(self):
        self.statusBar.showMessage("正在打开 PDF 页面提取工具...")
        if self.extract_window is None or not self.extract_window.isVisible():
            self.extract_window = PDFExtractorApp()
            self.extract_window.setAttribute(Qt.WA_DeleteOnClose)
            self.extract_window.destroyed.connect(lambda: setattr(self, 'extract_window', None))
            self.extract_window.show()
        else:
            self.extract_window.raise_()
        self.statusBar.showMessage("就绪")

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 使用更现代的风格
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
