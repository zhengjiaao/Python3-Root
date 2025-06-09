import sys
import os
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFileDialog, QScrollArea, QFrame, QGridLayout,
                             QCheckBox, QGroupBox, QTextEdit, QMessageBox, QSizePolicy, QDialog)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QIcon
from PathUtil import resource_path

class PDFRendererThread(QThread):
    page_rendered = pyqtSignal(int, QPixmap)
    finished = pyqtSignal()

    def __init__(self, pdf_path, zoom=2.0):
        super().__init__()
        self.pdf_path = pdf_path
        self.zoom = zoom
        self.cancelled = False

    def run(self):
        try:
            doc = fitz.open(self.pdf_path)
            total_pages = len(doc)

            for page_num in range(total_pages):
                if self.cancelled:
                    break

                page = doc.load_page(page_num)
                mat = fitz.Matrix(self.zoom, self.zoom)
                pix = page.get_pixmap(matrix=mat)

                # 转换为QPixmap
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(img)

                self.page_rendered.emit(page_num, pixmap)

            doc.close()
            if not self.cancelled:
                self.finished.emit()

        except Exception as e:
            print(f"Error rendering PDF: {str(e)}")

    def cancel(self):
        self.cancelled = True


class PDFExtractorThread(QThread):
    progress_updated = pyqtSignal(int)
    log_message = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, input_path, output_path, page_numbers):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.page_numbers = sorted(page_numbers)
        self.cancelled = False

    def run(self):
        try:
            self.log_message.emit(f"开始提取页面: {', '.join(map(str, self.page_numbers))}")

            # 打开源PDF
            src_doc = fitz.open(self.input_path)

            # 创建新PDF
            dst_doc = fitz.open()

            total_pages = len(self.page_numbers)

            for i, page_num in enumerate(self.page_numbers):
                if self.cancelled:
                    self.log_message.emit("操作已取消!")
                    break

                if page_num < 0 or page_num >= len(src_doc):
                    self.log_message.emit(f"警告: 跳过无效页面 {page_num}")
                    continue

                # 插入选中的页面
                dst_doc.insert_pdf(src_doc, from_page=page_num, to_page=page_num)

                # 更新进度
                progress = int((i + 1) / total_pages * 100)
                self.progress_updated.emit(progress)
                self.log_message.emit(f"已添加页面 {page_num + 1}")

            if not self.cancelled:
                # 保存新PDF
                dst_doc.save(self.output_path)
                dst_doc.close()
                src_doc.close()

                self.log_message.emit(f"PDF提取完成! 保存至: {self.output_path}")
                self.finished.emit(True, f"成功提取{len(self.page_numbers)}页")
            else:
                dst_doc.close()
                src_doc.close()
                if os.path.exists(self.output_path):
                    os.remove(self.output_path)

        except Exception as e:
            self.log_message.emit(f"错误: {str(e)}")
            self.finished.emit(False, str(e))


class PDFExtractorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF页面提取工具-MyZheng")
        self.setWindowIcon(QIcon(resource_path("resources/PDF 提取.ico")))  # 设置程序图标
        # self.setGeometry(100, 100, 1000, 700)

        self.resize_to_screen(scale=0.7)  # 窗口大小为屏幕的70%
        self.center_window()  # 👈 新增这一行，让窗口居中显示

        # 初始化变量
        self.pdf_path = ""
        self.thumbnail_size = QSize(180, 250)
        self.render_thread = None
        self.extract_thread = None
        self.page_checkboxes = []

        # 设置应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f5ff;
            }
            QGroupBox {
                font-size: 20px;
                font-weight: bold;
                border: 1px solid #a0a0a0;
                border-radius: 8px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                font-size: 20px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 30px;
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
            QPushButton#extractBtn {
                background-color: #27ae60;
                font-size: 18px;
                padding: 12px 24px;
                font-size: 30px;
            }
            QPushButton#extractBtn:hover {
                background-color: #219653;
            }
            QPushButton#extractBtn:pressed {
                background-color: #1b7e42;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                font-family: Consolas, monospace;
            }
            QLabel {
                color: #333333;
            }
            QCheckBox {
                color: #444444;
            }
            QScrollArea {
                border: none;
                background-color: #e0e9ff;
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
        title_label = QLabel("PDF页面提取工具")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # 文件选择区域
        file_group = QGroupBox("PDF文件")
        file_layout = QVBoxLayout(file_group)

        file_btn_layout = QHBoxLayout()
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("font-size: 20px; color: #555555;")
        self.browse_btn = QPushButton("选择PDF文件")
        self.browse_btn.clicked.connect(self.browse_pdf)
        file_btn_layout.addWidget(self.file_label, 1)
        file_btn_layout.addWidget(self.browse_btn)
        file_layout.addLayout(file_btn_layout)

        # 文件信息
        info_layout = QHBoxLayout()
        self.page_count_label = QLabel("总页数: -")
        self.page_count_label.setStyleSheet("font-weight: bold;")
        self.selected_count_label = QLabel("已选择: 0 页")
        self.selected_count_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        info_layout.addWidget(self.page_count_label)
        info_layout.addStretch()
        info_layout.addWidget(self.selected_count_label)
        file_layout.addLayout(info_layout)

        main_layout.addWidget(file_group)

        # 页面预览区域
        preview_group = QGroupBox("页面预览 (勾选需要提取的页面)")
        preview_layout = QVBoxLayout(preview_group)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #e0e9ff; border-radius: 6px;")

        # 缩略图容器
        self.thumbnail_container = QWidget()
        self.thumbnail_layout = QGridLayout(self.thumbnail_container)
        self.thumbnail_layout.setSpacing(15)
        self.thumbnail_layout.setContentsMargins(20, 20, 20, 20)
        self.thumbnail_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(self.thumbnail_container)
        preview_layout.addWidget(scroll_area)

        main_layout.addWidget(preview_group, 1)

        # 操作按钮
        btn_layout = QHBoxLayout()

        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all_pages)
        self.select_all_btn.setEnabled(False)

        self.deselect_all_btn = QPushButton("全不选")
        self.deselect_all_btn.clicked.connect(self.deselect_all_pages)
        self.deselect_all_btn.setEnabled(False)

        self.extract_btn = QPushButton("提取选中页面")
        self.extract_btn.setObjectName("extractBtn")
        self.extract_btn.clicked.connect(self.extract_selected_pages)
        self.extract_btn.setEnabled(False)

        btn_layout.addWidget(self.select_all_btn)
        btn_layout.addWidget(self.deselect_all_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.extract_btn)

        main_layout.addLayout(btn_layout)

        # 日志区域
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(100)
        log_layout.addWidget(self.log_text)

        main_layout.addWidget(log_group)

        # 状态栏
        self.statusBar().showMessage("就绪")

        # 添加初始占位符
        self.add_placeholder()

    def add_placeholder(self):
        placeholder = QLabel("请选择PDF文件以预览页面")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setFont(QFont("Arial", 14))
        placeholder.setStyleSheet("color: #777777;")
        self.thumbnail_layout.addWidget(placeholder, 0, 0, 1, 1)

    def browse_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择PDF文件", "", "PDF文件 (*.pdf)"
        )

        if file_path:
            self.pdf_path = file_path
            self.file_label.setText(f"已选择: {os.path.basename(file_path)}")
            self.log_text.append(f"> 已选择PDF文件: {file_path}")

            # 清除现有缩略图
            self.clear_thumbnails()

            # 显示加载提示
            loading = QLabel("正在加载PDF页面...")
            loading.setAlignment(Qt.AlignCenter)
            loading.setFont(QFont("Arial", 12))
            self.thumbnail_layout.addWidget(loading, 0, 0, 1, 1)

            # 启动渲染线程
            self.render_pdf(file_path)

    def render_pdf(self, pdf_path):
        # 获取PDF页数
        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()

            self.page_count_label.setText(f"总页数: {page_count}")
            self.log_text.append(f"> PDF总页数: {page_count}")

            # 创建渲染线程
            self.render_thread = PDFRendererThread(pdf_path, zoom=1.5)
            self.render_thread.page_rendered.connect(self.add_thumbnail)
            self.render_thread.finished.connect(self.on_rendering_finished)
            self.render_thread.start()

            # 启用选择按钮
            self.select_all_btn.setEnabled(True)
            self.deselect_all_btn.setEnabled(True)

        except Exception as e:
            self.log_text.append(f"错误: 无法打开PDF文件 - {str(e)}")
            QMessageBox.critical(self, "错误", f"无法打开PDF文件:\n{str(e)}")

    def clear_thumbnails(self):
        # 移除所有现有缩略图
        for i in reversed(range(self.thumbnail_layout.count())):
            widget = self.thumbnail_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.page_checkboxes = []
        self.selected_count_label.setText("已选择: 0 页")

    def add_thumbnail(self, page_num, pixmap):
        # 移除加载提示（如果存在）
        if self.thumbnail_layout.count() == 1:
            item = self.thumbnail_layout.itemAt(0)
            widget = item.widget() if item else None
            if widget and isinstance(widget, QLabel) and widget.text() == "正在加载PDF页面...":
                self.thumbnail_layout.removeItem(item)
                widget.deleteLater()

        # 创建缩略图框架
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #c0c0c0;
            }
        """)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        frame_layout.setSpacing(8)

        # 页面标签
        page_label = QLabel(f"第 {page_num + 1} 页")
        page_label.setStyleSheet("font-weight: bold;")
        page_label.setAlignment(Qt.AlignCenter)

        # 缩略图
        thumbnail_label = QLabel()
        thumbnail_label.setAlignment(Qt.AlignCenter)
        scaled_pixmap = pixmap.scaled(
            self.thumbnail_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        thumbnail_label.setPixmap(scaled_pixmap)

        # 设置 QLabel 支持点击事件
        thumbnail_label.mousePressEvent = lambda event, p=pixmap: self.show_fullsize_image(p)

        # 选择复选框
        checkbox = QCheckBox(f"选择此页 ({page_num + 1})")
        checkbox.setChecked(False)
        checkbox.stateChanged.connect(self.update_selection_count)
        self.page_checkboxes.append(checkbox)

        frame_layout.addWidget(page_label)
        frame_layout.addWidget(thumbnail_label, 1)
        frame_layout.addWidget(checkbox)

        # 添加到网格布局
        row = page_num // 4
        col = page_num % 4
        self.thumbnail_layout.addWidget(frame, row, col)

    def on_rendering_finished(self):
        self.log_text.append("> PDF页面预览加载完成")
        self.extract_btn.setEnabled(True)
        self.statusBar().showMessage("PDF加载完成，请选择要提取的页面")

    def update_selection_count(self):
        selected_count = sum(1 for cb in self.page_checkboxes if cb.isChecked())
        self.selected_count_label.setText(f"已选择: {selected_count} 页")

    def select_all_pages(self):
        for cb in self.page_checkboxes:
            cb.setChecked(True)
        self.update_selection_count()
        self.log_text.append("> 已选择所有页面")

    def deselect_all_pages(self):
        for cb in self.page_checkboxes:
            cb.setChecked(False)
        self.update_selection_count()
        self.log_text.append("> 已取消选择所有页面")

    def extract_selected_pages(self):
        # 获取选中的页面
        selected_pages = []
        for i, cb in enumerate(self.page_checkboxes):
            if cb.isChecked():
                selected_pages.append(i)

        if not selected_pages:
            self.log_text.append("错误: 请至少选择一个页面进行提取")
            QMessageBox.warning(self, "警告", "请至少选择一个页面进行提取")
            return

        # 选择输出文件路径
        base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        default_name = f"{base_name}_提取页面.pdf"
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存提取的PDF",
            os.path.join(os.path.dirname(self.pdf_path), default_name),
            "PDF文件 (*.pdf)"
        )

        if not output_path:
            return

        # 启动提取线程
        self.log_text.append(f"> 开始提取选中的 {len(selected_pages)} 个页面...")

        self.extract_thread = PDFExtractorThread(
            self.pdf_path,
            output_path,
            selected_pages
        )

        self.extract_thread.log_message.connect(self.log_text.append)
        self.extract_thread.finished.connect(self.on_extraction_finished)

        # 禁用按钮
        self.extract_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.select_all_btn.setEnabled(False)
        self.deselect_all_btn.setEnabled(False)

        # 开始线程
        self.extract_thread.start()

    def show_fullsize_image(self, pixmap):
        dialog = QDialog(self)
        dialog.setWindowTitle("高清预览")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)

        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        scroll_area = QScrollArea()
        scroll_area.setWidget(image_label)
        scroll_area.setWidgetResizable(True)

        layout.addWidget(scroll_area)

        # 获取主屏幕信息并设置窗口大小为屏幕宽度的 80%
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()  # 获取可用屏幕大小（排除任务栏）
        dialog_width = int(screen_size.width() * 0.7)
        dialog_height = int(screen_size.height() * 0.7)

        dialog.resize(dialog_width, dialog_height) # 动态大小

        # dialog.resize(800, 600) #  固定大小
        dialog.exec_()

    def on_extraction_finished(self, success, message):
        # 启用按钮
        self.extract_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.select_all_btn.setEnabled(True)
        self.deselect_all_btn.setEnabled(True)

        if success:
            self.statusBar().showMessage(message)
            self.log_text.append("> 提取操作成功完成!")
            QMessageBox.information(self, "成功", message)
        else:
            self.statusBar().showMessage("提取失败: " + message)
            QMessageBox.critical(self, "错误", f"提取失败:\n{message}")

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

    def closeEvent(self, event):
        # 确保在关闭窗口时停止工作线程
        if self.render_thread and self.render_thread.isRunning():
            self.render_thread.cancel()
            self.render_thread.wait(2000)

        if self.extract_thread and self.extract_thread.isRunning():
            self.extract_thread.cancel()
            self.extract_thread.wait(2000)

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle("Fusion")

    # 设置应用图标
    if hasattr(app, "setWindowIcon"):
        app.setWindowIcon(QIcon(":pdf-icon"))

    window = PDFExtractorApp()
    window.show()
    sys.exit(app.exec_())