import os
import sys
import datetime
import win32com.client
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QFileDialog, QTextEdit,
    QProgressBar, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# 安装组件库
# pip install PyQt6 pywin32

class ConversionWorker(QThread):
    progress_signal = pyqtSignal(int, int, str)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)

    def __init__(self, word_files, output_folder, engine):
        super().__init__()
        self.word_files = word_files
        self.output_folder = output_folder
        self.engine = engine
        self.cancel_requested = False

    def run(self):
        total = len(self.word_files)
        success_count = 0
        failure_count = 0

        # 初始化COM应用
        if self.engine == "office":
            app = win32com.client.Dispatch("Word.Application")
            app.DisplayAlerts = False  # 关闭警告提示，避免转换doc失败
            app.AutomationSecurity = 1  # 禁用宏安全警告（仅当信任文件时），避免转换doc失败
        elif self.engine == "wps":
            app = win32com.client.Dispatch("Kwps.Application")
        else:
            self.log_signal.emit("错误：未检测到有效的转换引擎")
            return

        app.Visible = False

        for idx, word_file in enumerate(self.word_files):
            if self.cancel_requested:
                break

            word_file = os.path.normpath(word_file)
            filename = os.path.basename(word_file)
            pdf_name = os.path.splitext(filename)[0] + ".pdf"
            pdf_path = os.path.join(self.output_folder, pdf_name)

            try:
                doc = app.Documents.Open(r'{}'.format(word_file))
                doc.SaveAs(pdf_path, FileFormat=17)
                doc.Close()
                self.log_signal.emit(f"✓ 转换成功: {filename}")
                success_count += 1
            except Exception as e:
                error_detail = f"文件路径: {word_file}\n错误类型: {type(e).__name__}\n详细信息: {str(e)}"
                self.log_signal.emit(f"✗ 转换失败: {filename}\n{error_detail}")
                failure_count += 1

            # 更新进度
            progress = int((idx + 1) / total * 100)
            self.progress_signal.emit(progress, idx + 1, f"{filename} → {pdf_name}")

        # 清理资源
        try:
            app.Quit()
        except:
            self.log_signal.emit("警告：应用退出时发生错误")

        if not self.cancel_requested:
            result = f"转换完成! 成功: {success_count}, 失败: {failure_count}"
            self.finished_signal.emit(result)
        else:
            self.log_signal.emit("用户取消转换操作")

    def cancel(self):
        self.cancel_requested = True


class WordToPDFConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Word转PDF工具")
        self.setGeometry(300, 300, 800, 600)
        self.last_output_folder = None  # 新增初始化

        # 检测可用引擎
        self.engine = self.detect_engine()

        # 创建主部件和布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 引擎显示区域
        engine_layout = QHBoxLayout()
        engine_layout.addWidget(QLabel("当前转换引擎:"))
        self.engine_label = QLabel(self.engine or "未检测到Office/WPS")
        engine_layout.addWidget(self.engine_label)
        engine_layout.addStretch()

        # 文件选择区域
        file_layout = QHBoxLayout()
        self.add_file_btn = QPushButton("添加文件")
        self.add_file_btn.clicked.connect(self.add_files)
        self.add_folder_btn = QPushButton("添加文件夹")
        self.add_folder_btn.clicked.connect(self.add_folder)
        self.clear_list_btn = QPushButton("清空列表")
        self.clear_list_btn.clicked.connect(self.clear_file_list)
        self.remove_btn = QPushButton("移除选中")
        self.remove_btn.clicked.connect(self.remove_selected)

        file_layout.addWidget(self.add_file_btn)
        file_layout.addWidget(self.add_folder_btn)
        file_layout.addWidget(self.clear_list_btn)
        file_layout.addWidget(self.remove_btn)

        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setAcceptDrops(True)

        # 输出选项区域
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出目录:"))
        self.output_path_edit = QTextEdit()
        self.output_path_edit.setMaximumHeight(60)
        self.output_path_edit.setReadOnly(True)
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.select_output_folder)
        self.timestamp_cb = QCheckBox("使用时间戳文件夹")
        self.timestamp_cb.setChecked(True)

        output_layout.addWidget(self.output_path_edit, 3)
        output_layout.addWidget(self.browse_btn)
        output_layout.addWidget(self.timestamp_cb)

        # 进度显示
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_label = QLabel("准备就绪")

        # 控制按钮区域
        control_layout = QHBoxLayout()
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_conversion)

        control_layout.addWidget(self.convert_btn)
        control_layout.addWidget(self.cancel_btn)

        # 日志区域
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("操作日志:"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("font-family: Consolas, 'Courier New', monospace;")

        log_layout.addWidget(self.log_area)

        # 组装主布局
        main_layout.addLayout(engine_layout)
        main_layout.addLayout(file_layout)
        main_layout.addWidget(self.file_list)
        main_layout.addLayout(output_layout)
        main_layout.addWidget(self.progress_label)
        main_layout.addWidget(self.progress_bar)
        main_layout.addLayout(control_layout)
        main_layout.addLayout(log_layout)

        # 初始化工作线程
        self.worker = None

        # 设置默认输出路径
        self.default_output_folder = os.path.dirname(os.path.abspath(__file__))
        self.output_path_edit.setText(self.default_output_folder)

        # 记录日志
        self.log_message(f"应用已启动，检测到转换引擎: {self.engine}")
        self.log_message("请添加Word文件或文件夹")

    def detect_engine(self):
        try:
            word = win32com.client.gencache.EnsureDispatch("Word.Application")
            word.Quit()
            return "office"  # 改为小写，与ConversionWorker匹配
        except:
            try:
                wps = win32com.client.gencache.EnsureDispatch("Kwps.Application")
                wps.Quit()
                return "wps"  # 改为小写
            except:
                return None

    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择Word文件", "",
            "Word文档 (*.doc *.docx);;所有文件 (*.*)"
        )

        if files:
            for file in files:
                file = os.path.normpath(file) # 标准化路径
                if file not in [self.file_list.item(i).text() for i in range(self.file_list.count())]:
                    self.file_list.addItem(file)
            self.log_message(f"添加了 {len(files)} 个文件")

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")

        if folder:
            count = 0
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('.doc', '.docx')):
                        file_path = os.path.join(root, file)
                        if file_path not in [self.file_list.item(i).text() for i in range(self.file_list.count())]:
                            self.file_list.addItem(file_path)
                            count += 1
            self.log_message(f"从文件夹添加了 {count} 个文件")

    def clear_file_list(self):
        self.file_list.clear()
        self.log_message("文件列表已清空")

    def remove_selected(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            self.file_list.takeItem(self.file_list.row(item))
        self.log_message(f"移除了 {len(selected_items)} 个文件")

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if folder:
            self.output_path_edit.setText(folder)
            self.log_message(f"输出目录设置为: {folder}")

    def get_output_folder(self):
        base_folder = self.output_path_edit.toPlainText()
        if not base_folder:
            base_folder = os.path.dirname(os.path.abspath(__file__))

        # 标准化基础路径
        base_folder = os.path.normpath(base_folder)

        if self.timestamp_cb.isChecked():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = os.path.join(base_folder, f"pdf_{timestamp}")
            os.makedirs(output_folder, exist_ok=True)
            return output_folder
        else:
            os.makedirs(base_folder, exist_ok=True)
            return base_folder

    def start_conversion(self):
        if not self.engine:
            QMessageBox.critical(self, "错误", "未检测到Office或WPS，无法转换！")
            return

        if self.file_list.count() == 0:
            QMessageBox.warning(self, "警告", "请先添加要转换的Word文件！")
            return

        # 获取文件列表和输出路径
        word_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        output_folder = self.get_output_folder()
        self.last_output_folder = output_folder

        self.log_message(f"开始转换 {len(word_files)} 个文件...")
        self.log_message(f"输出目录: {output_folder}")

        # 更新UI状态
        self.convert_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("正在初始化转换...")

        # 创建工作线程
        self.worker = ConversionWorker(word_files, output_folder, self.engine)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.log_signal.connect(self.log_message)
        self.worker.finished_signal.connect(self.conversion_finished)
        self.worker.start()

    def cancel_conversion(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.cancel_btn.setEnabled(False)
            self.log_message("正在取消转换，请稍候...")
            # 等待线程安全结束
            self.worker.wait()
            self.worker = None  # 重置worker引用
            self.convert_btn.setEnabled(True)  # 立即启用转换按钮

    def update_progress(self, progress, current, filename):
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"正在转换: {filename} ({current}/{self.file_list.count()})")

    def conversion_finished(self, message):
        self.log_message(message)
        self.progress_label.setText("转换完成!")
        self.convert_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)

        # 询问是否打开输出文件夹
        reply = QMessageBox.question(
            self, "转换完成",
            f"{message}\n\n是否打开输出文件夹?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 安全获取输出文件夹路径
            output_folder = None
            if hasattr(self, 'last_output_folder'):
                output_folder = self.last_output_folder
            elif self.worker is not None:
                output_folder = self.worker.output_folder
            else:
                output_folder = self.get_output_folder()  # 作为最后的选择

            if output_folder and os.path.exists(output_folder):
                os.startfile(output_folder)
            else:
                self.log_message("无法找到输出文件夹路径")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:disabled {
            background-color: #cccccc;
        }
        QListWidget {
            background-color: white;
            border: 1px solid #cccccc;
        }
        QTextEdit {
            background-color: white;
            border: 1px solid #cccccc;
        }
        QProgressBar {
            border: 1px solid #cccccc;
            border-radius: 3px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            width: 10px;
        }
    """)

    window = WordToPDFConverter()
    window.show()
    sys.exit(app.exec())