import sys
import csv
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QLabel, 
                             QFileDialog, QGroupBox, QMessageBox, QProgressBar,
                             QTextEdit, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class DataImportExport(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PyQt6 数据导入导出工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 当前文件路径
        self.current_file = None
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 工具栏区域
        toolbar_group = QGroupBox("文件操作")
        toolbar_layout = QHBoxLayout(toolbar_group)
        
        # 导入按钮
        import_btn = QPushButton("📥 导入数据")
        import_btn.clicked.connect(self.import_data)
        toolbar_layout.addWidget(import_btn)
        
        # 导出按钮
        export_btn = QPushButton("📤 导出数据")
        export_btn.clicked.connect(self.export_data)
        toolbar_layout.addWidget(export_btn)
        
        toolbar_layout.addStretch()
        
        # 添加分隔线
        separator = QLabel("|")
        separator.setStyleSheet("color: gray; font-weight: bold;")
        toolbar_layout.addWidget(separator)
        
        # 清空表格
        clear_btn = QPushButton("🗑️ 清空表格")
        clear_btn.clicked.connect(self.clear_table)
        toolbar_layout.addWidget(clear_btn)
        
        # 添加行
        add_row_btn = QPushButton("➕ 添加行")
        add_row_btn.clicked.connect(self.add_row)
        toolbar_layout.addWidget(add_row_btn)
        
        # 删除行
        del_row_btn = QPushButton("➖ 删除选中行")
        del_row_btn.clicked.connect(self.delete_selected_rows)
        toolbar_layout.addWidget(del_row_btn)
        
        toolbar_layout.addStretch()
        main_layout.addWidget(toolbar_group)
        
        # 数据统计
        stats_group = QGroupBox("数据统计")
        stats_layout = QHBoxLayout(stats_group)
        
        self.rows_label = QLabel("行数: 0")
        self.cols_label = QLabel("列数: 0")
        stats_layout.addWidget(self.rows_label)
        stats_layout.addWidget(self.cols_label)
        stats_layout.addStretch()
        
        main_layout.addWidget(stats_group)
        
        # 数据表格
        table_group = QGroupBox("数据表格")
        table_layout = QVBoxLayout(table_group)
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(["列1", "列2", "列3", "列4", "列5"])
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # 连接信号
        self.data_table.itemChanged.connect(self.on_item_changed)
        
        table_layout.addWidget(self.data_table)
        main_layout.addWidget(table_group)
        
        # 日志区域
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_area = QTextEdit()
        self.log_area.setFont(QFont("Consolas", 9))
        self.log_area.setMaximumHeight(150)
        self.log_area.setReadOnly(True)
        log_layout.addWidget(self.log_area)
        
        main_layout.addWidget(log_group)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪", 3000)
        
        # 初始化统计信息
        self.update_stats()
    
    def import_data(self):
        """导入数据"""
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self, "导入数据", "", 
            "CSV 文件 (*.csv);;Excel 文件 (*.xlsx *.xls);;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.lower().endswith('.csv'):
                self.import_csv(file_path)
            elif file_path.lower().endswith(('.xlsx', '.xls')):
                self.import_excel(file_path)
            else:
                QMessageBox.warning(self, "警告", "不支持的文件格式")
                return
            
            self.current_file = file_path
            self.log_message(f"成功导入: {file_path}")
            self.status_bar.showMessage(f"已导入: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败: {e}")
            self.log_message(f"导入失败: {e}")
    
    def import_csv(self, file_path):
        """导入CSV文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # 读取表头
            headers = next(reader)
            self.data_table.setColumnCount(len(headers))
            self.data_table.setHorizontalHeaderLabels(headers)
            
            # 清空现有数据
            self.data_table.setRowCount(0)
            
            # 读取数据
            for row_data in reader:
                row = self.data_table.rowCount()
                self.data_table.insertRow(row)
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(value)
                    self.data_table.setItem(row, col, item)
            
            self.update_stats()
    
    def import_excel(self, file_path):
        """导入Excel文件"""
        try:
            import pandas as pd
            
            # 读取Excel
            df = pd.read_excel(file_path)
            
            # 设置列数和表头
            self.data_table.setColumnCount(len(df.columns))
            self.data_table.setHorizontalHeaderLabels([str(col) for col in df.columns])
            
            # 清空现有数据
            self.data_table.setRowCount(0)
            
            # 填充数据
            for _, row in df.iterrows():
                row_idx = self.data_table.rowCount()
                self.data_table.insertRow(row_idx)
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value) if pd.notna(value) else "")
                    self.data_table.setItem(row_idx, col_idx, item)
            
            self.update_stats()
            
        except ImportError:
            QMessageBox.warning(self, "警告", "需要安装pandas和openpyxl库来读取Excel文件\n请运行: pip install pandas openpyxl")
        except Exception as e:
            raise Exception(f"读取Excel文件失败: {e}")
    
    def export_data(self):
        """导出数据"""
        if self.data_table.rowCount() == 0:
            QMessageBox.warning(self, "警告", "没有数据可导出")
            return
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "导出数据", "", 
            "CSV 文件 (*.csv);;Excel 文件 (*.xlsx);;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.lower().endswith('.csv'):
                self.export_csv(file_path)
            elif file_path.lower().endswith('.xlsx'):
                self.export_excel(file_path)
            else:
                # 默认导出为CSV
                if not file_path.endswith('.csv'):
                    file_path += '.csv'
                self.export_csv(file_path)
            
            self.log_message(f"成功导出: {file_path}")
            self.status_bar.showMessage(f"已导出: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")
            self.log_message(f"导出失败: {e}")
    
    def export_csv(self, file_path):
        """导出为CSV文件"""
        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            
            # 写入表头
            headers = []
            for col in range(self.data_table.columnCount()):
                header_item = self.data_table.horizontalHeaderItem(col)
                headers.append(header_item.text() if header_item else f"列{col+1}")
            writer.writerow(headers)
            
            # 写入数据
            for row in range(self.data_table.rowCount()):
                row_data = []
                for col in range(self.data_table.columnCount()):
                    item = self.data_table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)
    
    def export_excel(self, file_path):
        """导出为Excel文件"""
        try:
            import pandas as pd
            
            # 收集数据
            data = []
            headers = []
            
            for col in range(self.data_table.columnCount()):
                header_item = self.data_table.horizontalHeaderItem(col)
                headers.append(header_item.text() if header_item else f"列{col+1}")
            
            for row in range(self.data_table.rowCount()):
                row_data = {}
                for col in range(self.data_table.columnCount()):
                    item = self.data_table.item(row, col)
                    row_data[headers[col]] = item.text() if item else ""
                data.append(row_data)
            
            # 创建DataFrame并保存
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False, engine='openpyxl')
            
        except ImportError:
            QMessageBox.warning(self, "警告", "需要安装pandas和openpyxl库来导出Excel文件\n请运行: pip install pandas openpyxl")
        except Exception as e:
            raise Exception(f"导出Excel文件失败: {e}")
    
    def clear_table(self):
        """清空表格"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空所有数据吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.data_table.setRowCount(0)
            self.update_stats()
            self.log_message("表格已清空")
    
    def add_row(self):
        """添加新行"""
        row = self.data_table.rowCount()
        self.data_table.insertRow(row)
        
        # 填充空单元格
        for col in range(self.data_table.columnCount()):
            item = QTableWidgetItem("")
            self.data_table.setItem(row, col, item)
        
        self.update_stats()
        self.log_message(f"已添加第 {row + 1} 行")
    
    def delete_selected_rows(self):
        """删除选中的行"""
        selected_rows = set()
        for item in self.data_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的行")
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的 {len(selected_rows)} 行吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 从后往前删除，避免索引变化
            for row in sorted(selected_rows, reverse=True):
                self.data_table.removeRow(row)
            
            self.update_stats()
            self.log_message(f"已删除 {len(selected_rows)} 行")
    
    def on_item_changed(self, item):
        """单元格内容改变事件"""
        pass  # 可以在这里添加自动保存等功能
    
    def update_stats(self):
        """更新统计信息"""
        rows = self.data_table.rowCount()
        cols = self.data_table.columnCount()
        self.rows_label.setText(f"行数: {rows}")
        self.cols_label.setText(f"列数: {cols}")
    
    def log_message(self, message):
        """添加日志消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_area.append(f"[{timestamp}] {message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = DataImportExport()
    window.show()
    
    sys.exit(app.exec())
