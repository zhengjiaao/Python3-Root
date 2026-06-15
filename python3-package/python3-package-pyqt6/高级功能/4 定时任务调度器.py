import sys
import time
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QTextEdit, QTableWidget,
                             QTableWidgetItem, QHeaderView, QSpinBox, QComboBox,
                             QGroupBox, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer


class TaskWorker(QThread):
    """任务执行工作线程"""
    task_started = pyqtSignal(str)
    task_completed = pyqtSignal(str, str)
    task_error = pyqtSignal(str, str)
    
    def __init__(self, task_id, task_name, interval, command):
        super().__init__()
        self.task_id = task_id
        self.task_name = task_name
        self.interval = interval
        self.command = command
        self.running = True
    
    def run(self):
        """执行定时任务"""
        while self.running:
            try:
                self.task_started.emit(self.task_id)
                
                # 模拟执行命令（实际应用中可以执行系统命令或Python代码）
                result = f"执行命令: {self.command}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                # 模拟耗时操作
                time.sleep(1)
                
                self.task_completed.emit(self.task_id, result)
                
            except Exception as e:
                self.task_error.emit(self.task_id, str(e))
            
            # 等待下一个执行周期
            for _ in range(int(self.interval * 10)):
                if not self.running:
                    break
                time.sleep(0.1)
    
    def stop(self):
        """停止任务"""
        self.running = False


class TaskScheduler(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PyQt6 定时任务调度器")
        self.setGeometry(100, 100, 1000, 700)
        
        # 任务字典 {task_id: TaskWorker}
        self.tasks = {}
        self.task_counter = 0
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 添加任务区域
        add_group = QGroupBox("添加新任务")
        add_layout = QVBoxLayout(add_group)
        
        # 任务名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("任务名称:"))
        self.task_name_input = QLineEdit()
        self.task_name_input.setPlaceholderText("例如: 数据备份")
        name_layout.addWidget(self.task_name_input)
        add_layout.addLayout(name_layout)
        
        # 执行间隔
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("执行间隔:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 3600)
        self.interval_spin.setValue(60)
        interval_layout.addWidget(self.interval_spin)
        
        self.interval_unit_combo = QComboBox()
        self.interval_unit_combo.addItems(["秒", "分钟", "小时"])
        interval_layout.addWidget(self.interval_unit_combo)
        add_layout.addLayout(interval_layout)
        
        # 执行命令
        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(QLabel("执行命令:"))
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("例如: echo 'Hello World' 或 python script.py")
        cmd_layout.addWidget(self.command_input)
        add_layout.addLayout(cmd_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ 添加任务")
        add_btn.clicked.connect(self.add_task)
        clear_btn = QPushButton("🗑️ 清空表单")
        clear_btn.clicked.connect(self.clear_form)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        add_layout.addLayout(btn_layout)
        
        main_layout.addWidget(add_group)
        
        # 任务列表
        list_group = QGroupBox("任务列表")
        list_layout = QVBoxLayout(list_group)
        
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels(["ID", "任务名称", "间隔", "状态", "最后执行", "操作"])
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        list_layout.addWidget(self.task_table)
        
        main_layout.addWidget(list_group)
        
        # 日志区域
        log_group = QGroupBox("执行日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_area = QTextEdit()
        self.log_area.setFontFamily("Consolas")
        self.log_area.setReadOnly(True)
        log_layout.addWidget(self.log_area)
        
        main_layout.addWidget(log_group)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪", 3000)
        
        # 定时器用于更新UI
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_task_status)
        self.update_timer.start(1000)
    
    def add_task(self):
        """添加新任务"""
        task_name = self.task_name_input.text().strip()
        if not task_name:
            QMessageBox.warning(self, "警告", "请输入任务名称")
            return
        
        command = self.command_input.text().strip()
        if not command:
            QMessageBox.warning(self, "警告", "请输入执行命令")
            return
        
        # 计算间隔（秒）
        interval_value = self.interval_spin.value()
        interval_unit = self.interval_unit_combo.currentText()
        
        if interval_unit == "秒":
            interval = interval_value
        elif interval_unit == "分钟":
            interval = interval_value * 60
        else:  # 小时
            interval = interval_value * 3600
        
        # 创建任务ID
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        
        # 添加到表格
        row = self.task_table.rowCount()
        self.task_table.insertRow(row)
        self.task_table.setItem(row, 0, QTableWidgetItem(task_id))
        self.task_table.setItem(row, 1, QTableWidgetItem(task_name))
        self.task_table.setItem(row, 2, QTableWidgetItem(f"{interval_value} {interval_unit}"))
        self.task_table.setItem(row, 3, QTableWidgetItem("待启动"))
        self.task_table.setItem(row, 4, QTableWidgetItem("-"))
        
        # 操作按钮容器
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        start_btn = QPushButton("▶️ 启动")
        start_btn.clicked.connect(lambda: self.start_task(task_id))
        
        stop_btn = QPushButton("⏹️ 停止")
        stop_btn.clicked.connect(lambda: self.stop_task(task_id))
        stop_btn.setEnabled(False)
        
        delete_btn = QPushButton("❌ 删除")
        delete_btn.clicked.connect(lambda: self.delete_task(task_id))
        
        btn_layout.addWidget(start_btn)
        btn_layout.addWidget(stop_btn)
        btn_layout.addWidget(delete_btn)
        
        self.task_table.setCellWidget(row, 5, btn_widget)
        
        # 创建工作线程（但不立即启动）
        worker = TaskWorker(task_id, task_name, interval, command)
        worker.task_started.connect(self.on_task_started)
        worker.task_completed.connect(self.on_task_completed)
        worker.task_error.connect(self.on_task_error)
        
        self.tasks[task_id] = {
            'worker': worker,
            'row': row,
            'name': task_name,
            'running': False
        }
        
        self.log_message(f"已添加任务: {task_name}")
        self.clear_form()
    
    def start_task(self, task_id):
        """启动任务"""
        if task_id not in self.tasks:
            return
        
        task_info = self.tasks[task_id]
        if task_info['running']:
            return
        
        # 启动工作线程
        worker = task_info['worker']
        worker.start()
        task_info['running'] = True
        
        # 更新UI
        row = task_info['row']
        self.task_table.item(row, 3).setText("运行中")
        
        # 更新按钮状态
        btn_widget = self.task_table.cellWidget(row, 5)
        if btn_widget:
            start_btn = btn_widget.layout().itemAt(0).widget()
            stop_btn = btn_widget.layout().itemAt(1).widget()
            start_btn.setEnabled(False)
            stop_btn.setEnabled(True)
        
        self.log_message(f"任务已启动: {task_info['name']}")
    
    def stop_task(self, task_id):
        """停止任务"""
        if task_id not in self.tasks:
            return
        
        task_info = self.tasks[task_id]
        if not task_info['running']:
            return
        
        # 停止工作线程
        worker = task_info['worker']
        worker.stop()
        worker.wait()
        task_info['running'] = False
        
        # 更新UI
        row = task_info['row']
        self.task_table.item(row, 3).setText("已停止")
        
        # 更新按钮状态
        btn_widget = self.task_table.cellWidget(row, 5)
        if btn_widget:
            start_btn = btn_widget.layout().itemAt(0).widget()
            stop_btn = btn_widget.layout().itemAt(1).widget()
            start_btn.setEnabled(True)
            stop_btn.setEnabled(False)
        
        self.log_message(f"任务已停止: {task_info['name']}")
    
    def delete_task(self, task_id):
        """删除任务"""
        if task_id not in self.tasks:
            return
        
        task_info = self.tasks[task_id]
        
        # 如果任务正在运行，先停止
        if task_info['running']:
            self.stop_task(task_id)
        
        # 从表格中删除
        row = task_info['row']
        self.task_table.removeRow(row)
        
        # 从字典中删除
        del self.tasks[task_id]
        
        self.log_message(f"任务已删除: {task_info['name']}")
    
    def on_task_started(self, task_id):
        """任务开始执行"""
        if task_id in self.tasks:
            task_info = self.tasks[task_id]
            self.log_message(f"[{task_info['name']}] 开始执行...")
    
    def on_task_completed(self, task_id, result):
        """任务执行完成"""
        if task_id in self.tasks:
            task_info = self.tasks[task_id]
            row = task_info['row']
            
            # 更新最后执行时间
            now = datetime.now().strftime('%H:%M:%S')
            self.task_table.item(row, 4).setText(now)
            
            self.log_message(f"[{task_info['name']}] 执行完成")
            self.log_message(f"  {result}")
    
    def on_task_error(self, task_id, error_msg):
        """任务执行出错"""
        if task_id in self.tasks:
            task_info = self.tasks[task_id]
            self.log_message(f"[{task_info['name']}] 执行错误: {error_msg}")
    
    def update_task_status(self):
        """更新任务状态（定时调用）"""
        # 可以在这里添加额外的状态更新逻辑
        pass
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_area.append(f"[{timestamp}] {message}")
    
    def clear_form(self):
        """清空表单"""
        self.task_name_input.clear()
        self.command_input.clear()
        self.interval_spin.setValue(60)
        self.interval_unit_combo.setCurrentIndex(0)
    
    def closeEvent(self, event):
        """关闭窗口时停止所有任务"""
        for task_id, task_info in self.tasks.items():
            if task_info['running']:
                task_info['worker'].stop()
                task_info['worker'].wait()
        
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = TaskScheduler()
    window.show()
    
    sys.exit(app.exec())

