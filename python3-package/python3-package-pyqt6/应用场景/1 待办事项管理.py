import sys
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QTextEdit, QListWidget, QLabel,
                             QGroupBox, QMessageBox, QComboBox, QDateEdit, QCheckBox,
                             QSplitter, QStatusBar, QListWidgetItem)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont


class TodoDatabase:
    """待办事项数据库管理类"""
    
    def __init__(self, db_path="todos.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()
    
    def create_table(self):
        """创建数据表"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                due_date TEXT,
                completed INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        self.conn.commit()
    
    def add_todo(self, title, description="", priority="medium", due_date=None):
        """添加待办事项"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO todos (title, description, priority, due_date, completed, created_at, updated_at)
            VALUES (?, ?, ?, ?, 0, ?, ?)
        ''', (title, description, priority, due_date, now, now))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_todos(self, show_completed=False):
        """获取所有待办事项"""
        cursor = self.conn.cursor()
        if show_completed:
            cursor.execute('SELECT * FROM todos ORDER BY created_at DESC')
        else:
            cursor.execute('SELECT * FROM todos WHERE completed = 0 ORDER BY created_at DESC')
        return cursor.fetchall()
    
    def update_todo(self, todo_id, title=None, description=None, priority=None, due_date=None):
        """更新待办事项"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.conn.cursor()
        
        updates = []
        values = []
        
        if title is not None:
            updates.append('title = ?')
            values.append(title)
        if description is not None:
            updates.append('description = ?')
            values.append(description)
        if priority is not None:
            updates.append('priority = ?')
            values.append(priority)
        if due_date is not None:
            updates.append('due_date = ?')
            values.append(due_date)
        
        updates.append('updated_at = ?')
        values.append(now)
        values.append(todo_id)
        
        sql = f"UPDATE todos SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(sql, values)
        self.conn.commit()
    
    def toggle_complete(self, todo_id):
        """切换完成状态"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT completed FROM todos WHERE id = ?', (todo_id,))
        result = cursor.fetchone()
        
        if result:
            new_status = 1 if result[0] == 0 else 0
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('UPDATE todos SET completed = ?, updated_at = ? WHERE id = ?', 
                         (new_status, now, todo_id))
            self.conn.commit()
            return new_status
        return None
    
    def delete_todo(self, todo_id):
        """删除待办事项"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        self.conn.commit()
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()


class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PyQt6 待办事项管理")
        self.setGeometry(100, 100, 1000, 700)
        
        # 初始化数据库
        self.db = TodoDatabase()
        
        # 当前选中的待办ID
        self.current_todo_id = None
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧：待办列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 列表标题
        list_header = QHBoxLayout()
        list_header.addWidget(QLabel("📋 待办列表"))
        
        self.show_completed_check = QCheckBox("显示已完成")
        self.show_completed_check.stateChanged.connect(self.refresh_list)
        list_header.addWidget(self.show_completed_check)
        
        left_layout.addLayout(list_header)
        
        # 待办列表
        self.todo_list = QListWidget()
        self.todo_list.setFont(QFont("Arial", 11))
        self.todo_list.currentItemChanged.connect(self.on_todo_selected)
        left_layout.addWidget(self.todo_list)
        
        # 统计信息
        self.stats_label = QLabel("")
        left_layout.addWidget(self.stats_label)
        
        main_layout.addWidget(left_widget, 2)
        
        # 右侧：详情和编辑
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 添加新待办区域
        add_group = QGroupBox("➕ 添加新待办")
        add_layout = QVBoxLayout(add_group)
        
        # 标题输入
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("标题:"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("输入待办事项标题...")
        title_layout.addWidget(self.title_input)
        add_layout.addLayout(title_layout)
        
        # 优先级选择
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel("优先级:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["低", "中", "高"])
        self.priority_combo.setCurrentIndex(1)
        priority_layout.addWidget(self.priority_combo)
        priority_layout.addStretch()
        add_layout.addLayout(priority_layout)
        
        # 截止日期
        due_layout = QHBoxLayout()
        due_layout.addWidget(QLabel("截止日期:"))
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setDate(QDate.currentDate().addDays(7))
        self.due_date_edit.setCalendarPopup(True)
        due_layout.addWidget(self.due_date_edit)
        due_layout.addStretch()
        add_layout.addLayout(due_layout)
        
        # 描述
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("描述:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        self.desc_edit.setPlaceholderText("输入详细描述（可选）...")
        desc_layout.addWidget(self.desc_edit)
        add_layout.addLayout(desc_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("✅ 添加待办")
        add_btn.clicked.connect(self.add_todo)
        clear_btn = QPushButton("🗑️ 清空表单")
        clear_btn.clicked.connect(self.clear_form)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(clear_btn)
        add_layout.addLayout(btn_layout)
        
        right_layout.addWidget(add_group)
        
        # 编辑选中待办区域
        edit_group = QGroupBox("✏️ 编辑待办")
        edit_layout = QVBoxLayout(edit_group)
        
        # 操作按钮
        action_layout = QHBoxLayout()
        
        self.complete_btn = QPushButton("✔️ 标记完成")
        self.complete_btn.clicked.connect(self.toggle_complete)
        action_layout.addWidget(self.complete_btn)
        
        self.delete_btn = QPushButton("❌ 删除")
        self.delete_btn.clicked.connect(self.delete_todo)
        action_layout.addWidget(self.delete_btn)
        
        edit_layout.addLayout(action_layout)
        
        # 详情显示
        self.detail_label = QLabel("请选择一个待办事项查看详情")
        self.detail_label.setWordWrap(True)
        edit_layout.addWidget(self.detail_label)
        
        right_layout.addWidget(edit_group)
        right_layout.addStretch()
        
        main_layout.addWidget(right_widget, 3)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪", 3000)
        
        # 刷新列表
        self.refresh_list()
    
    def add_todo(self):
        """添加待办事项"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "警告", "请输入待办事项标题")
            return
        
        description = self.desc_edit.toPlainText().strip()
        priority_map = {"低": "low", "中": "medium", "高": "high"}
        priority = priority_map[self.priority_combo.currentText()]
        due_date = self.due_date_edit.date().toString("yyyy-MM-dd")
        
        try:
            self.db.add_todo(title, description, priority, due_date)
            self.log_message(f"已添加: {title}")
            self.clear_form()
            self.refresh_list()
            self.status_bar.showMessage("待办事项已添加", 3000)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加失败: {e}")
    
    def refresh_list(self):
        """刷新待办列表"""
        self.todo_list.clear()
        
        show_completed = self.show_completed_check.isChecked()
        todos = self.db.get_all_todos(show_completed)
        
        for todo in todos:
            todo_id, title, description, priority, due_date, completed, created_at, updated_at = todo
            
            # 优先级图标
            priority_icons = {"low": "🟢", "medium": "🟡", "high": "🔴"}
            priority_icon = priority_icons.get(priority, "⚪")
            
            # 完成状态
            status_icon = "☑️" if completed else "☐"
            
            # 显示文本
            display_text = f"{status_icon} {priority_icon} {title}"
            if due_date and not completed:
                display_text += f" (截止: {due_date})"
            
            # 创建列表项并设置数据
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, todo_id)
            self.todo_list.addItem(item)
        
        # 更新统计
        total = len(todos)
        completed_count = sum(1 for t in todos if t[5])
        self.stats_label.setText(f"总计: {total} | 已完成: {completed_count} | 待完成: {total - completed_count}")
    
    def on_todo_selected(self, current, previous):
        """待办事项选择改变"""
        if current is None:
            self.current_todo_id = None
            self.detail_label.setText("请选择一个待办事项查看详情")
            return
        
        todo_id = current.data(Qt.ItemDataRole.UserRole)
        self.current_todo_id = todo_id
        
        # 获取详细信息
        todos = self.db.get_all_todos(True)
        selected_todo = None
        for todo in todos:
            if todo[0] == todo_id:
                selected_todo = todo
                break
        
        if selected_todo:
            todo_id, title, description, priority, due_date, completed, created_at, updated_at = selected_todo
            
            priority_map = {"low": "低", "medium": "中", "high": "高"}
            priority_text = priority_map.get(priority, priority)
            status_text = "已完成" if completed else "进行中"
            
            detail_text = f"""
<b>标题:</b> {title}<br>
<b>优先级:</b> {priority_text}<br>
<b>状态:</b> {status_text}<br>
<b>截止日期:</b> {due_date or '无'}<br>
<b>创建时间:</b> {created_at}<br>
<b>更新时间:</b> {updated_at}<br>
<br>
<b>描述:</b><br>{description or '无描述'}
            """
            
            self.detail_label.setText(detail_text)
            self.complete_btn.setText("☐ 标记未完成" if completed else "✔️ 标记完成")
    
    def toggle_complete(self):
        """切换完成状态"""
        if not self.current_todo_id:
            QMessageBox.warning(self, "警告", "请先选择一个待办事项")
            return
        
        new_status = self.db.toggle_complete(self.current_todo_id)
        if new_status is not None:
            status_text = "已完成" if new_status else "未完成"
            self.log_message(f"待办事项已标记为: {status_text}")
            self.refresh_list()
            self.status_bar.showMessage(f"已标记为{status_text}", 3000)
    
    def delete_todo(self):
        """删除待办事项"""
        if not self.current_todo_id:
            QMessageBox.warning(self, "警告", "请先选择一个待办事项")
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这个待办事项吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_todo(self.current_todo_id)
            self.log_message("待办事项已删除")
            self.current_todo_id = None
            self.detail_label.setText("请选择一个待办事项查看详情")
            self.refresh_list()
            self.status_bar.showMessage("待办事项已删除", 3000)
    
    def clear_form(self):
        """清空表单"""
        self.title_input.clear()
        self.desc_edit.clear()
        self.priority_combo.setCurrentIndex(1)
        self.due_date_edit.setDate(QDate.currentDate().addDays(7))
    
    def log_message(self, message):
        """记录日志（可以扩展为写入文件）"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    def closeEvent(self, event):
        """关闭窗口时清理资源"""
        self.db.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = TodoApp()
    window.show()
    
    sys.exit(app.exec())
