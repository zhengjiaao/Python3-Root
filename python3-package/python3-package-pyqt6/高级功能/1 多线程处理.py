import sys
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QProgressBar, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal


class WorkerThread(QThread):
    progress_updated = pyqtSignal(int)
    result_ready = pyqtSignal(str)
    finished = pyqtSignal()

    def run(self):
        result = ""
        for i in range(1, 101):
            time.sleep(0.05)  # 模拟耗时操作

            # 处理一些数据
            if i % 10 == 0:
                result += f"已完成步骤 {i}\n"

            # 更新进度
            self.progress_updated.emit(i)

        self.result_ready.emit(result)
        self.finished.emit()


class ThreadedApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 多线程示例")
        self.setGeometry(100, 100, 500, 400)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        layout = QVBoxLayout(central_widget)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)

        # 结果文本框
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        # 按钮
        self.start_btn = QPushButton("开始任务")
        self.start_btn.clicked.connect(self.start_task)

        self.cancel_btn = QPushButton("取消任务")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_task)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 添加到布局
        layout.addWidget(QLabel("任务进度:"))
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("任务结果:"))
        layout.addWidget(self.result_text)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.cancel_btn)
        layout.addWidget(self.status_label)

        # 初始化工作线程
        self.worker_thread = None

    def start_task(self):
        # 禁用开始按钮，启用取消按钮
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status_label.setText("任务运行中...")
        self.result_text.clear()

        # 创建并启动工作线程
        self.worker_thread = WorkerThread()

        # 连接信号
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.result_ready.connect(self.show_result)
        self.worker_thread.finished.connect(self.task_finished)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        # 启动线程
        self.worker_thread.start()

    def cancel_task(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
            self.status_label.setText("任务已取消")
            self.start_btn.setEnabled(True)
            self.cancel_btn.setEnabled(False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def show_result(self, result):
        self.result_text.append(result)

    def task_finished(self):
        self.status_label.setText("任务已完成")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.worker_thread = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ThreadedApp()
    window.show()
    sys.exit(app.exec())
