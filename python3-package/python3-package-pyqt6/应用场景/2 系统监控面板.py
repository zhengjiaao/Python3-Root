import sys
import psutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QProgressBar, QGroupBox, QGridLayout, QTextEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


def format_bytes(bytes_val):
    """格式化字节数为可读格式"""
    if bytes_val == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} PB"


class SystemMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PyQt6 系统监控面板")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # CPU监控
        cpu_group = QGroupBox("🖥️ CPU 使用率")
        cpu_layout = QVBoxLayout(cpu_group)
        
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setTextVisible(True)
        self.cpu_progress.setMinimumHeight(30)
        cpu_layout.addWidget(self.cpu_progress)
        
        # CPU详细信息
        cpu_info_layout = QGridLayout()
        self.cpu_cores_label = QLabel("核心数: -")
        self.cpu_freq_label = QLabel("频率: -")
        self.cpu_usage_label = QLabel("使用率: -")
        cpu_info_layout.addWidget(self.cpu_cores_label, 0, 0)
        cpu_info_layout.addWidget(self.cpu_freq_label, 0, 1)
        cpu_info_layout.addWidget(self.cpu_usage_label, 1, 0)
        cpu_layout.addLayout(cpu_info_layout)
        
        main_layout.addWidget(cpu_group)
        
        # 内存监控
        memory_group = QGroupBox("💾 内存使用")
        memory_layout = QVBoxLayout(memory_group)
        
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setTextVisible(True)
        self.memory_progress.setMinimumHeight(30)
        memory_layout.addWidget(self.memory_progress)
        
        # 内存详细信息
        memory_info_layout = QGridLayout()
        self.memory_total_label = QLabel("总计: -")
        self.memory_used_label = QLabel("已用: -")
        self.memory_free_label = QLabel("可用: -")
        self.memory_percent_label = QLabel("使用率: -")
        memory_info_layout.addWidget(self.memory_total_label, 0, 0)
        memory_info_layout.addWidget(self.memory_used_label, 0, 1)
        memory_info_layout.addWidget(self.memory_free_label, 1, 0)
        memory_info_layout.addWidget(self.memory_percent_label, 1, 1)
        memory_layout.addLayout(memory_info_layout)
        
        main_layout.addWidget(memory_group)
        
        # 磁盘监控
        disk_group = QGroupBox("💿 磁盘使用")
        disk_layout = QVBoxLayout(disk_group)
        
        self.disk_table = QTableWidget()
        self.disk_table.setColumnCount(4)
        self.disk_table.setHorizontalHeaderLabels(["分区", "总计", "已用", "可用"])
        self.disk_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        disk_layout.addWidget(self.disk_table)
        
        main_layout.addWidget(disk_group)
        
        # 进程列表
        process_group = QGroupBox("⚙️ 进程列表 (Top 10 by CPU)")
        process_layout = QVBoxLayout(process_group)
        
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(5)
        self.process_table.setHorizontalHeaderLabels(["PID", "名称", "CPU%", "内存%", "状态"])
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        process_layout.addWidget(self.process_table)
        
        main_layout.addWidget(process_group)
        
        # 网络信息
        network_group = QGroupBox("🌐 网络统计")
        network_layout = QHBoxLayout(network_group)
        
        self.net_sent_label = QLabel("发送: -")
        self.net_recv_label = QLabel("接收: -")
        network_layout.addWidget(self.net_sent_label)
        network_layout.addWidget(self.net_recv_label)
        network_layout.addStretch()
        
        main_layout.addWidget(network_group)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪", 3000)
        
        # 定时器用于更新数据
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(2000)  # 每2秒更新一次
        
        # 初始更新
        self.update_stats()
    
    def update_stats(self):
        """更新所有统计信息"""
        try:
            self.update_cpu_stats()
            self.update_memory_stats()
            self.update_disk_stats()
            self.update_process_stats()
            self.update_network_stats()
        except Exception as e:
            self.status_bar.showMessage(f"更新错误: {e}", 5000)
    
    def update_cpu_stats(self):
        """更新CPU统计"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_progress.setValue(int(cpu_percent))
        self.cpu_progress.setFormat(f"{cpu_percent:.1f}%")
        
        # 设置颜色
        if cpu_percent < 50:
            color = "#4CAF50"  # 绿色
        elif cpu_percent < 80:
            color = "#FF9800"  # 橙色
        else:
            color = "#F44336"  # 红色
        
        self.cpu_progress.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        
        # CPU信息
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        self.cpu_cores_label.setText(f"核心数: {cpu_count}")
        self.cpu_freq_label.setText(f"频率: {cpu_freq.current:.2f} MHz" if cpu_freq else "频率: N/A")
        self.cpu_usage_label.setText(f"使用率: {cpu_percent:.1f}%")
    
    def update_memory_stats(self):
        """更新内存统计"""
        memory = psutil.virtual_memory()
        
        self.memory_progress.setValue(int(memory.percent))
        self.memory_progress.setFormat(f"{memory.percent:.1f}%")
        
        # 设置颜色
        if memory.percent < 50:
            color = "#4CAF50"
        elif memory.percent < 80:
            color = "#FF9800"
        else:
            color = "#F44336"
        
        self.memory_progress.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        
        # 内存信息
        self.memory_total_label.setText(f"总计: {format_bytes(memory.total)}")
        self.memory_used_label.setText(f"已用: {format_bytes(memory.used)}")
        self.memory_free_label.setText(f"可用: {format_bytes(memory.available)}")
        self.memory_percent_label.setText(f"使用率: {memory.percent:.1f}%")
    
    def update_disk_stats(self):
        """更新磁盘统计"""
        partitions = psutil.disk_partitions()
        
        self.disk_table.setRowCount(0)
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                row = self.disk_table.rowCount()
                self.disk_table.insertRow(row)
                
                self.disk_table.setItem(row, 0, QTableWidgetItem(partition.mountpoint))
                self.disk_table.setItem(row, 1, QTableWidgetItem(format_bytes(usage.total)))
                self.disk_table.setItem(row, 2, QTableWidgetItem(format_bytes(usage.used)))
                self.disk_table.setItem(row, 3, QTableWidgetItem(format_bytes(usage.free)))
                
            except PermissionError:
                continue
    
    def update_process_stats(self):
        """更新进程统计"""
        # 获取所有进程并按CPU使用率排序
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] is not None and pinfo['memory_percent'] is not None:
                    processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # 按CPU使用率排序，取前10个
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        top_processes = processes[:10]
        
        self.process_table.setRowCount(0)
        
        for proc in top_processes:
            row = self.process_table.rowCount()
            self.process_table.insertRow(row)
            
            self.process_table.setItem(row, 0, QTableWidgetItem(str(proc['pid'])))
            self.process_table.setItem(row, 1, QTableWidgetItem(proc['name'] or 'N/A'))
            self.process_table.setItem(row, 2, QTableWidgetItem(f"{proc['cpu_percent']:.1f}%" if proc['cpu_percent'] else "0.0%"))
            self.process_table.setItem(row, 3, QTableWidgetItem(f"{proc['memory_percent']:.1f}%" if proc['memory_percent'] else "0.0%"))
            self.process_table.setItem(row, 4, QTableWidgetItem(proc['status'] or 'N/A'))
    
    def update_network_stats(self):
        """更新网络统计"""
        try:
            net_io = psutil.net_io_counters()
            
            self.net_sent_label.setText(f"发送: {format_bytes(net_io.bytes_sent)}")
            self.net_recv_label.setText(f"接收: {format_bytes(net_io.bytes_recv)}")
        except Exception as e:
            print(f"网络统计错误: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = SystemMonitor()
    window.show()
    
    sys.exit(app.exec())
