import sys
import os
import math
import tempfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog,
                             QGroupBox, QProgressBar, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
import fitz  # PyMuPDF
from PathUtil import resource_path

# 设置临时文件目录（避免权限问题）
tempfile.tempdir = os.path.expanduser("~")


class PDFSplitterThread(QThread):
    progress_updated = pyqtSignal(int)
    log_message = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, input_path, output_dir, split_type, split_value):
        super().__init__()
        self.input_path = input_path
        self.output_dir = output_dir
        self.split_type = split_type
        self.split_value = split_value
        self.cancelled = False

    def run(self):
        print("【DEBUG】线程运行")
        self.log_message.emit("【DEBUG】线程运行")
        try:
            # 打开PDF文件
            self.log_message.emit(f"正在打开PDF文件: {os.path.basename(self.input_path)}")
            doc = fitz.open(self.input_path)
            total_pages = len(doc)

            if total_pages == 0:
                self.log_message.emit("错误: PDF文件没有页面!")
                self.finished.emit(False, "PDF文件没有页面")
                return

            self.log_message.emit(f"PDF总页数: {total_pages}")

            # 根据拆分类型计算拆分点
            if self.split_type == "page":
                per_part = int(self.split_value)
                if per_part <= 0:
                    self.log_message.emit("错误: 每部分页数必须大于0!")
                    self.finished.emit(False, "每部分页数必须大于0")
                    return

                num_parts = math.ceil(total_pages / per_part)
                split_points = [i * per_part for i in range(1, num_parts)]

            elif self.split_type == "chunk":
                num_parts = int(self.split_value)
                if num_parts <= 0 or num_parts > total_pages:
                    self.log_message.emit(f"错误: 块数必须在1到{total_pages}之间!")
                    self.finished.emit(False, "无效的块数")
                    return

                per_part = math.ceil(total_pages / num_parts)
                split_points = [i * per_part for i in range(1, num_parts)]

            elif self.split_type == "size":
                max_size_mb = float(self.split_value)
                if max_size_mb <= 0:
                    self.log_message.emit("错误: 文件大小必须大于0MB!")
                    self.finished.emit(False, "文件大小必须大于0")
                    return

                max_size_bytes = max_size_mb * 1024 * 1024

                # 计算每个部分的大致页数
                doc_size = os.path.getsize(self.input_path)
                avg_page_size = doc_size / total_pages
                pages_per_part = max(1, int(max_size_bytes / avg_page_size))
                num_parts = math.ceil(total_pages / pages_per_part)
                split_points = [i * pages_per_part for i in range(1, num_parts)]

            # 添加最后一个页面作为结束点
            split_points.append(total_pages)
            self.log_message.emit(f"将PDF拆分为 {len(split_points)} 个部分")

            # 执行拆分
            start_page = 0
            base_name = os.path.splitext(os.path.basename(self.input_path))[0]

            for i, end_page in enumerate(split_points):
                if self.cancelled:
                    self.log_message.emit("操作已取消!")
                    break

                # 创建新的PDF文档
                output_doc = fitz.open()
                output_doc.insert_pdf(doc, from_page=start_page, to_page=end_page - 1)

                # 生成输出文件名
                output_filename = f"{base_name}_part{i + 1}.pdf"
                output_path = os.path.join(self.output_dir, output_filename)

                # 保存PDF
                self.log_message.emit(f"正在保存: {output_filename} (页 {start_page + 1}-{end_page})")
                output_doc.save(output_path)
                output_doc.close()

                # 更新进度
                progress = int((i + 1) / len(split_points) * 100)
                self.progress_updated.emit(progress)

                start_page = end_page

            # ✅ 在所有拆分完成后才关闭原始文档
            doc.close()

            if not self.cancelled:
                self.log_message.emit(f"PDF拆分完成! 共生成 {len(split_points)} 个文件")
            self.finished.emit(True, f"共生成 {len(split_points)} 个文件")

        except Exception as e:
            self.log_message.emit(f"错误: {str(e)}")
            self.finished.emit(False, str(e))
        finally:
            print("【DEBUG】线程结束")
            self.log_message.emit("【DEBUG】线程结束")

    def cancel(self):
        self.cancelled = True


class PDFSplitterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF拆分工具-MyZheng")
        self.setWindowIcon(QIcon(resource_path("resources/PDF 拆分.ico")))  # 设置程序图标
        # self.setGeometry(100, 100, 700, 500) # 更小一些
        # self.setGeometry(100, 100, 800, 600) # 设置窗口大小和位置，self.setGeometry(100, 100, 新宽度, 新高度)
        # self.setGeometry(100, 100, 1000, 700) # 更大一些
        self.resize_to_screen(scale=0.7)  # 窗口大小为屏幕的70%
        self.center_window()  # 👈 新增这一行，让窗口居中显示

        # 设置全局字体大小
        # app = QApplication.instance()
        # if app is not None:
        #     font = app.font()
        #     font.setPointSize(12)  # 设置全局字体大小为12
        #     app.setFont(font)

        # 对特定控件加大字体
        # title_label.setFont(QFont("Arial", 20))  # 标题字体更大
        # self.split_type_combo.setFont(QFont("Arial", 14))
        # self.split_value_edit.setFont(QFont("Arial", 14))
        # self.example_label.setFont(QFont("Arial", 14))
        # self.log_text.setFont(QFont("Consolas", 14))

        # 初始化变量
        self.input_path = ""
        self.output_dir = os.path.expanduser("~")
        self.worker_thread = None

        # 设置应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f5ff;
            }
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                border: 1px solid #a0a0a0;
                border-radius: 8px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                font-size: 18px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QPushButton:disabled {
                background-color: #a0a0a0;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                font-family: Consolas, monospace;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
            }
            QProgressBar {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4a86e8;
                width: 10px;
            }
        """)

        self.init_ui()

    def init_ui(self):
        # 创建主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("PDF拆分工具")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        main_layout.addWidget(title_label)

        # 文件选择区域
        file_group = QGroupBox("PDF文件")
        file_layout = QVBoxLayout(file_group)

        file_btn_layout = QHBoxLayout()
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("font-size: 14px; color: #555555;")
        self.browse_btn = QPushButton("选择PDF文件")
        self.browse_btn.clicked.connect(self.browse_file)
        file_btn_layout.addWidget(self.file_label, 1)
        file_btn_layout.addWidget(self.browse_btn)
        file_layout.addLayout(file_btn_layout)

        # 输出目录选择
        output_btn_layout = QHBoxLayout()
        self.output_label = QLabel(f"输出目录: {self.output_dir}")
        self.output_label.setStyleSheet("font-size: 14px; color: #555555;")
        self.output_browse_btn = QPushButton("选择输出目录")
        self.output_browse_btn.clicked.connect(self.browse_output_dir)
        output_btn_layout.addWidget(self.output_label, 1)
        output_btn_layout.addWidget(self.output_browse_btn)
        file_layout.addLayout(output_btn_layout)

        main_layout.addWidget(file_group)

        # 拆分设置区域
        split_group = QGroupBox("拆分设置")
        split_layout = QVBoxLayout(split_group)

        # 拆分类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("拆分方式:"))

        self.split_type_combo = QComboBox()
        self.split_type_combo.addItems(["按页数拆分", "按块数拆分", "按文件大小拆分"])
        self.split_type_combo.currentIndexChanged.connect(self.update_split_ui)
        type_layout.addWidget(self.split_type_combo, 1)

        split_layout.addLayout(type_layout)

        # 拆分值输入
        self.value_layout = QHBoxLayout()
        self.value_layout.addWidget(QLabel("每部分页数:"))

        self.split_value_edit = QLineEdit()
        self.split_value_edit.textChanged.connect(self.update_start_button_state)
        self.split_value_edit.setPlaceholderText("例如: 10")
        self.value_layout.addWidget(self.split_value_edit, 1)

        self.value_unit = QLabel("页")
        self.value_layout.addWidget(self.value_unit)

        split_layout.addLayout(self.value_layout)

        # 示例文本
        self.example_label = QLabel("示例: 每10页拆分为一个文件")
        self.example_label.setStyleSheet("font-size: 12px; color: #666666; font-style: italic;")
        split_layout.addWidget(self.example_label)

        main_layout.addWidget(split_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                height: 25px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # 操作按钮
        btn_layout = QHBoxLayout()
        self.split_btn = QPushButton("开始拆分")
        self.split_btn.setStyleSheet("background-color: #27ae60;")
        self.split_btn.clicked.connect(self.start_split)
        self.split_btn.setEnabled(False)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setStyleSheet("background-color: #e74c3c;")
        self.cancel_btn.clicked.connect(self.cancel_split)
        self.cancel_btn.setEnabled(False)

        self.clear_log_btn = QPushButton("清空日志")
        self.clear_log_btn.setStyleSheet("background-color: #999999;")
        self.clear_log_btn.clicked.connect(self.clear_log)

        btn_layout.addWidget(self.split_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.clear_log_btn)  # 添加到按钮布局中
        main_layout.addLayout(btn_layout)

        # 日志区域
        log_group = QGroupBox("处理日志")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(150)
        log_layout.addWidget(self.log_text)

        main_layout.addWidget(log_group, 1)

        # 状态栏
        self.statusBar().showMessage("就绪")

        # 初始化UI状态
        self.update_split_ui()

    def update_split_ui(self):
        split_type = self.split_type_combo.currentText()

        # 清除之前的布局项
        while self.value_layout.count():
            item = self.value_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 重新创建布局
        if split_type == "按页数拆分":
            self.value_layout.addWidget(QLabel("每部分页数:"))
            self.split_value_edit = QLineEdit()
            self.split_value_edit.setPlaceholderText("例如: 10")
            self.split_value_edit.textChanged.connect(self.update_start_button_state)  # ✅ 新增绑定：在每次新建 QLineEdit 后重新绑定信号
            self.value_layout.addWidget(self.split_value_edit, 1)
            self.value_unit = QLabel("页")
            self.value_layout.addWidget(self.value_unit)
            self.example_label.setText("示例: 每10页拆分为一个文件")
            self.example_label.setStyleSheet("font-size: 14px; color: #555555;")

        elif split_type == "按块数拆分":
            self.value_layout.addWidget(QLabel("拆分为:"))
            self.split_value_edit = QLineEdit()
            self.split_value_edit.setPlaceholderText("例如: 5")
            self.split_value_edit.textChanged.connect(self.update_start_button_state)  # ✅ 新增绑定：在每次新建 QLineEdit 后重新绑定信号
            self.value_layout.addWidget(self.split_value_edit, 1)
            self.value_unit = QLabel("个文件")
            self.value_layout.addWidget(self.value_unit)
            self.example_label.setText("示例: 将PDF拆分为5个文件")
            self.example_label.setStyleSheet("font-size: 14px; color: #555555;")

        elif split_type == "按文件大小拆分":
            self.value_layout.addWidget(QLabel("每部分大小:"))
            self.split_value_edit = QLineEdit()
            self.split_value_edit.setPlaceholderText("例如: 2")
            self.split_value_edit.textChanged.connect(self.update_start_button_state)  # ✅ 新增绑定：在每次新建 QLineEdit 后重新绑定信号
            self.value_layout.addWidget(self.split_value_edit, 1)
            self.value_unit = QLabel("MB")
            self.value_layout.addWidget(self.value_unit)
            self.example_label.setText("示例: 每个文件最大2MB (注意: 按大小拆分是估算值)")
            self.example_label.setStyleSheet("font-size: 14px; color: #555555;")

        # 更新UI
        self.split_value_edit.setFocus()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )

        if file_path:
            self.input_path = file_path
            self.file_label.setText(f"已选择: {os.path.basename(file_path)}")
            self.log_text.append(f"> 已选择PDF文件: {file_path}")
            self.update_start_button_state()

            # 自动设置输出目录为文件所在目录
            self.output_dir = os.path.dirname(file_path)
            self.output_label.setText(f"输出目录: {self.output_dir}")

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择输出目录", self.output_dir
        )

        if dir_path:
            self.output_dir = dir_path
            self.output_label.setText(f"输出目录: {dir_path}")
            self.log_text.append(f"> 输出目录设置为: {dir_path}")

    def update_start_button_state(self):
        enabled = bool(self.input_path) and bool(self.split_value_edit.text())
        self.split_btn.setEnabled(enabled)

    def start_split(self):
        print("【DEBUG】按钮连接状态:", self.split_btn.receivers(self.split_btn.clicked))
        print("【DEBUG】start_split() 被调用")
        self.log_text.append("> 开始拆分PDF...")

        if not self.input_path:
            self.log_text.append("错误: 请先选择PDF文件!")
            return

        if not os.path.exists(self.input_path):
            self.log_text.append(f"错误: 文件不存在 - {self.input_path}")
            return

        split_value = self.split_value_edit.text()
        if not split_value:
            self.log_text.append("错误: 请输入拆分值!")
            return

        # 显示调试信息
        self.log_text.append(f"输入路径: {self.input_path}")
        self.log_text.append(f"拆分类型: {self.split_type_combo.currentText()}")
        self.log_text.append(f"拆分值: {split_value}")

        # 创建worker线程
        self.progress_bar.setValue(0)

        # 验证输入值
        split_type = self.split_type_combo.currentText()

        # 确认输入参数是否符合要求
        self.log_text.append(f"> 开始拆分PDF，文件: {self.input_path}, 类型: {split_type}, 值: {split_value}")

        try:
            if split_type == "按页数拆分" or split_type == "按块数拆分":
                value = int(split_value)
                if value <= 0:
                    self.log_text.append("错误: 拆分值必须大于0!")
                    return
            else:  # 按文件大小拆分
                value = float(split_value)
                if value <= 0:
                    self.log_text.append("错误: 文件大小必须大于0MB!")
                    return
        except ValueError:
            self.log_text.append("错误: 请输入有效的数字!")
            return

        # 创建worker线程
        self.log_text.append("> 开始拆分PDF...")
        self.progress_bar.setValue(0)

        # 映射拆分类型
        type_mapping = {
            "按页数拆分": "page",
            "按块数拆分": "chunk",
            "按文件大小拆分": "size"
        }

        self.worker_thread = PDFSplitterThread(
            self.input_path,
            self.output_dir,
            type_mapping[split_type],
            split_value
        )

        # 连接信号
        self.worker_thread.progress_updated.connect(self.progress_bar.setValue)
        self.worker_thread.log_message.connect(self.log_text.append)
        self.worker_thread.finished.connect(self.on_split_finished)

        # 更新按钮状态
        self.split_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.browse_btn.setEnabled(False)

        # 开始线程
        self.worker_thread.start()

    def cancel_split(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.cancel_btn.setEnabled(False)
            self.log_text.append("> 正在取消操作...")

    def on_split_finished(self, success, message):
        self.split_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.browse_btn.setEnabled(True)

        if success:
            self.statusBar().showMessage("拆分完成! " + message)
            self.log_text.append("> 操作成功完成!")
        else:
            self.statusBar().showMessage("操作失败: " + message)

        self.worker_thread = None

    def closeEvent(self, event):
        # 确保在关闭窗口时停止工作线程
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.worker_thread.wait(2000)  # 等待2秒让线程结束

        event.accept()

    def clear_log(self):
        self.log_text.clear()
        self.log_text.append("> 日志已清空")

    def resize_to_screen(self, scale=0.7):
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * scale)
        height = int(screen.height() * scale)
        self.setGeometry(100, 100, width, height)

    def center_window(self):
        # 获取屏幕的几何尺寸
        screen = QApplication.primaryScreen().geometry()
        # 获取窗口的尺寸
        size = self.geometry()
        # 计算居中位置
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle("Fusion")

    # 设置应用图标
    if hasattr(app, "setWindowIcon"):
        app.setWindowIcon(QIcon(":pdf-icon"))

    window = PDFSplitterApp()
    window.show()
    sys.exit(app.exec_())