import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFormLayout, QDialog
)
from PyQt5.QtCore import Qt


class ContactManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("联系人管理系统")
        self.setGeometry(100, 100, 800, 600)

        # 初始化数据库
        self.init_db()

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 按钮区域
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("添加联系人")
        self.add_btn.clicked.connect(self.show_add_dialog)

        self.edit_btn = QPushButton("编辑联系人")
        self.edit_btn.clicked.connect(self.show_edit_dialog)
        self.edit_btn.setEnabled(False)

        self.delete_btn = QPushButton("删除联系人")
        self.delete_btn.clicked.connect(self.delete_contact)
        self.delete_btn.setEnabled(False)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()

        # 搜索区域
        search_layout = QHBoxLayout()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索联系人...")
        self.search_edit.textChanged.connect(self.search_contacts)

        search_layout.addWidget(QLabel("搜索:"))
        search_layout.addWidget(self.search_edit)

        # 联系人表格
        self.contact_table = QTableWidget()
        self.contact_table.setColumnCount(4)
        self.contact_table.setHorizontalHeaderLabels(["ID", "姓名", "电话", "邮箱"])
        self.contact_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.contact_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.contact_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.contact_table.itemSelectionChanged.connect(self.table_selection_changed)

        # 添加到主布局
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.contact_table)

        # 加载联系人
        self.load_contacts()

    def init_db(self):
        self.conn = sqlite3.connect('contacts.db')
        self.cursor = self.conn.cursor()

        # 创建表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT
            )
        ''')
        self.conn.commit()

    def load_contacts(self, search_term=""):
        # 清空表格
        self.contact_table.setRowCount(0)

        # 查询联系人
        if search_term:
            query = "SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?"
            params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
        else:
            query = "SELECT * FROM contacts"
            params = ()

        self.cursor.execute(query, params)
        contacts = self.cursor.fetchall()

        # 填充表格
        for row_idx, contact in enumerate(contacts):
            self.contact_table.insertRow(row_idx)
            for col_idx, value in enumerate(contact):
                item = QTableWidgetItem(str(value))
                self.contact_table.setItem(row_idx, col_idx, item)

    def search_contacts(self):
        search_term = self.search_edit.text()
        self.load_contacts(search_term)

    def table_selection_changed(self):
        selected = self.contact_table.selectionModel().hasSelection()
        self.edit_btn.setEnabled(selected)
        self.delete_btn.setEnabled(selected)

    def get_selected_id(self):
        selected_row = self.contact_table.currentRow()
        if selected_row >= 0:
            return int(self.contact_table.item(selected_row, 0).text())
        return None

    def show_add_dialog(self):
        dialog = ContactDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, phone, email = dialog.get_data()
            self.add_contact(name, phone, email)

    def show_edit_dialog(self):
        contact_id = self.get_selected_id()
        if contact_id is None:
            return

        # 获取当前联系人信息
        self.cursor.execute("SELECT * FROM contacts WHERE id=?", (contact_id,))
        contact = self.cursor.fetchone()

        if contact:
            dialog = ContactDialog(self, contact)
            if dialog.exec_() == QDialog.Accepted:
                name, phone, email = dialog.get_data()
                self.update_contact(contact_id, name, phone, email)

    def add_contact(self, name, phone, email):
        try:
            self.cursor.execute(
                "INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)",
                (name, phone, email)
            )
            self.conn.commit()
            self.load_contacts()
            QMessageBox.information(self, "成功", "联系人已添加")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加联系人失败: {str(e)}")

    def update_contact(self, contact_id, name, phone, email):
        try:
            self.cursor.execute(
                "UPDATE contacts SET name=?, phone=?, email=? WHERE id=?",
                (name, phone, email, contact_id)
            )
            self.conn.commit()
            self.load_contacts()
            QMessageBox.information(self, "成功", "联系人已更新")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新联系人失败: {str(e)}")

    def delete_contact(self):
        contact_id = self.get_selected_id()
        if contact_id is None:
            return

        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除选中的联系人吗?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
                self.conn.commit()
                self.load_contacts()
                QMessageBox.information(self, "成功", "联系人已删除")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除联系人失败: {str(e)}")


class ContactDialog(QDialog):
    def __init__(self, parent=None, contact=None):
        super().__init__(parent)
        self.setWindowTitle("添加联系人" if contact is None else "编辑联系人")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()

        form_layout.addRow("姓名:", self.name_edit)
        form_layout.addRow("电话:", self.phone_edit)
        form_layout.addRow("邮箱:", self.email_edit)

        # 填充现有数据
        if contact:
            self.name_edit.setText(contact[1])
            self.phone_edit.setText(contact[2])
            self.email_edit.setText(contact[3])

        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)

    def get_data(self):
        return (
            self.name_edit.text().strip(),
            self.phone_edit.text().strip(),
            self.email_edit.text().strip()
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ContactManager()
    window.show()
    sys.exit(app.exec_())
