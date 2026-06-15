import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QTextEdit, QComboBox, QLabel, 
                             QTabWidget, QSplitter, QTableWidget, QTableWidgetItem,
                             QHeaderView, QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont


class HTTPWorker(QThread):
    """HTTP 请求工作线程"""
    response_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, method, url, headers, body):
        super().__init__()
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body
    
    def run(self):
        try:
            import requests
            
            # 发送请求
            if self.method == "GET":
                response = requests.get(self.url, headers=self.headers, timeout=10)
            elif self.method == "POST":
                response = requests.post(self.url, headers=self.headers, data=self.body, timeout=10)
            elif self.method == "PUT":
                response = requests.put(self.url, headers=self.headers, data=self.body, timeout=10)
            elif self.method == "DELETE":
                response = requests.delete(self.url, headers=self.headers, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {self.method}")
            
            # 解析响应
            result = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'text': response.text,
                'elapsed': response.elapsed.total_seconds()
            }
            
            # 尝试解析JSON
            try:
                result['json'] = response.json()
            except:
                result['json'] = None
            
            self.response_signal.emit(result)
            
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            self.finished_signal.emit()


class HTTPClient(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PyQt6 HTTP 客户端")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 请求区域
        request_group = QGroupBox("请求配置")
        request_layout = QVBoxLayout(request_group)
        
        # URL输入行
        url_layout = QHBoxLayout()
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE"])
        self.method_combo.setCurrentText("GET")
        self.method_combo.currentTextChanged.connect(self.on_method_changed)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入URL地址，例如: https://api.example.com/users")
        self.url_input.returnPressed.connect(self.send_request)
        
        self.send_btn = QPushButton("🚀 发送请求")
        self.send_btn.clicked.connect(self.send_request)
        
        url_layout.addWidget(self.method_combo)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.send_btn)
        
        request_layout.addLayout(url_layout)
        
        # 标签页（Headers和Body）
        tabs = QTabWidget()
        
        # Headers标签
        headers_tab = QWidget()
        headers_layout = QVBoxLayout(headers_tab)
        
        self.headers_table = QTableWidget()
        self.headers_table.setColumnCount(2)
        self.headers_table.setHorizontalHeaderLabels(["Header名称", "Header值"])
        self.headers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # 添加默认headers
        self.add_header_row("Content-Type", "application/json")
        self.add_header_row("User-Agent", "PyQt6-HTTP-Client/1.0")
        
        headers_layout.addWidget(self.headers_table)
        
        add_header_btn = QPushButton("+ 添加Header")
        add_header_btn.clicked.connect(lambda: self.add_header_row("", ""))
        headers_layout.addWidget(add_header_btn)
        
        tabs.addTab(headers_tab, "Headers")
        
        # Body标签
        body_tab = QWidget()
        body_layout = QVBoxLayout(body_tab)
        
        self.body_edit = QTextEdit()
        self.body_edit.setFont(QFont("Consolas", 10))
        self.body_edit.setPlaceholderText('JSON Body (仅POST/PUT):\n{\n  "key": "value"\n}')
        body_layout.addWidget(self.body_edit)
        
        tabs.addTab(body_tab, "Body")
        
        request_layout.addWidget(tabs)
        main_layout.addWidget(request_group)
        
        # 响应区域
        response_group = QGroupBox("响应结果")
        response_layout = QVBoxLayout(response_group)
        
        # 状态信息
        status_layout = QHBoxLayout()
        self.status_label = QLabel("状态: 等待请求...")
        self.time_label = QLabel("耗时: -")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.time_label)
        response_layout.addLayout(status_layout)
        
        # 响应内容标签页
        response_tabs = QTabWidget()
        
        # 原始响应
        raw_tab = QTextEdit()
        raw_tab.setFont(QFont("Consolas", 10))
        raw_tab.setReadOnly(True)
        self.raw_response = raw_tab
        response_tabs.addTab(raw_tab, "原始响应")
        
        # JSON格式化响应
        json_tab = QTextEdit()
        json_tab.setFont(QFont("Consolas", 10))
        json_tab.setReadOnly(True)
        self.json_response = json_tab
        response_tabs.addTab(json_tab, "JSON")
        
        # Headers响应
        headers_response_tab = QTextEdit()
        headers_response_tab.setFont(QFont("Consolas", 10))
        headers_response_tab.setReadOnly(True)
        self.headers_response = headers_response_tab
        response_tabs.addTab(headers_response_tab, "响应Headers")
        
        response_layout.addWidget(response_tabs)
        main_layout.addWidget(response_group)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪", 3000)
        
        # 工作线程
        self.worker = None
    
    def add_header_row(self, key="", value=""):
        """添加header行"""
        row = self.headers_table.rowCount()
        self.headers_table.insertRow(row)
        self.headers_table.setItem(row, 0, QTableWidgetItem(key))
        self.headers_table.setItem(row, 1, QTableWidgetItem(value))
    
    def on_method_changed(self, method):
        """HTTP方法改变事件"""
        if method in ["POST", "PUT"]:
            self.body_edit.setEnabled(True)
        else:
            self.body_edit.setEnabled(False)
    
    def send_request(self):
        """发送HTTP请求"""
        url = self.url_input.text().strip()
        if not url:
            self.status_bar.showMessage("请输入URL地址", 3000)
            return
        
        # 获取headers
        headers = {}
        for row in range(self.headers_table.rowCount()):
            key_item = self.headers_table.item(row, 0)
            value_item = self.headers_table.item(row, 1)
            if key_item and value_item:
                key = key_item.text().strip()
                value = value_item.text().strip()
                if key:
                    headers[key] = value
        
        # 获取body
        body = self.body_edit.toPlainText().strip() if self.method_combo.currentText() in ["POST", "PUT"] else None
        
        # 更新UI状态
        self.send_btn.setEnabled(False)
        self.status_label.setText("状态: 请求中...")
        self.time_label.setText("耗时: -")
        self.status_bar.showMessage("正在发送请求...", 0)
        
        # 创建工作线程
        self.worker = HTTPWorker(self.method_combo.currentText(), url, headers, body)
        self.worker.response_signal.connect(self.handle_response)
        self.worker.error_signal.connect(self.handle_error)
        self.worker.finished_signal.connect(self.request_finished)
        self.worker.start()
    
    def handle_response(self, result):
        """处理响应"""
        status_code = result['status_code']
        elapsed = result['elapsed']
        
        # 更新状态
        color = "green" if 200 <= status_code < 300 else "red"
        self.status_label.setText(f'<span style="color:{color}">状态: {status_code}</span>')
        self.time_label.setText(f"耗时: {elapsed:.3f}s")
        
        # 显示原始响应
        self.raw_response.setText(result['text'])
        
        # 显示JSON响应
        if result['json']:
            formatted_json = json.dumps(result['json'], indent=2, ensure_ascii=False)
            self.json_response.setText(formatted_json)
        else:
            self.json_response.setText("无法解析为JSON格式")
        
        # 显示响应headers
        headers_text = "\n".join([f"{k}: {v}" for k, v in result['headers'].items()])
        self.headers_response.setText(headers_text)
        
        self.status_bar.showMessage(f"请求完成 - 状态码: {status_code}", 3000)
    
    def handle_error(self, error_msg):
        """处理错误"""
        self.status_label.setText('<span style="color:red">状态: 请求失败</span>')
        self.raw_response.setText(f"错误: {error_msg}")
        self.json_response.setText("")
        self.headers_response.setText("")
        self.status_bar.showMessage(f"请求失败: {error_msg}", 5000)
    
    def request_finished(self):
        """请求完成"""
        self.send_btn.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = HTTPClient()
    window.show()
    
    sys.exit(app.exec())
