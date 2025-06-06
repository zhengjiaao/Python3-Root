import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QCheckBox, QRadioButton, QGroupBox, QProgressBar,
    QSlider, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit,
    QListWidget, QTabWidget, QFileDialog, QMessageBox,
    QInputDialog, QDialog, QDialogButtonBox, QFormLayout,QListWidgetItem
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont, QPixmap, QIcon, QIntValidator


class AddItemDialog(QDialog):
    """自定义添加项目对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新项目")
        self.setWindowIcon(QIcon(":qt-project.org/qmessagebox/images/information.png"))
        self.setFixedSize(400, 250)

        layout = QVBoxLayout(self)

        # 表单布局
        form_layout = QFormLayout()

        # 项目名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入项目名称")
        form_layout.addRow("项目名称:", self.name_edit)

        # 项目类型
        self.type_combo = QComboBox()
        self.type_combo.addItems(["常规", "重要", "紧急", "已完成"])
        form_layout.addRow("项目类型:", self.type_combo)

        # 优先级
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 5)
        self.priority_spin.setValue(3)
        form_layout.addRow("优先级(1-5):", self.priority_spin)

        # 描述
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(60)
        self.desc_edit.setPlaceholderText("项目描述...")
        form_layout.addRow("项目描述:", self.desc_edit)

        layout.addLayout(form_layout)

        # 按钮组
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def get_item_data(self):
        """获取输入的项目数据"""
        return {
            "name": self.name_edit.text(),
            "type": self.type_combo.currentText(),
            "priority": self.priority_spin.value(),
            "description": self.desc_edit.toPlainText()
        }


class PyQtGUIApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("PyQt5 GUI 示例")
        self.setGeometry(300, 300, 800, 600)

        # 设置应用图标
        self.setWindowIcon(QIcon(":qt-project.org/qmessagebox/images/qtlogo-64.png"))

        # 创建主控件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 创建标签控件
        title_label = QLabel("PyQt5 GUI 应用示例")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            background-color: #3498db;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 10px;
        """)

        # 创建选项卡控件
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabBar::tab {
                background: #f1f2f6;
                padding: 10px 20px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
        """)

        # 第一个选项卡：基本控件
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)

        # 输入控件组
        input_group = QGroupBox("输入控件")
        input_layout = QVBoxLayout(input_group)

        # 文本输入
        text_input_layout = QHBoxLayout()
        text_label = QLabel("文本输入:")
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("请输入文本...")
        text_input_layout.addWidget(text_label)
        text_input_layout.addWidget(self.text_input)
        input_layout.addLayout(text_input_layout)

        # 数字输入
        number_layout = QHBoxLayout()
        spin_label = QLabel("整数输入:")
        self.spin_box = QSpinBox()
        self.spin_box.setRange(0, 100)

        double_label = QLabel("小数输入:")
        self.double_spin = QDoubleSpinBox()
        self.double_spin.setRange(0, 100)
        self.double_spin.setSingleStep(0.5)

        number_layout.addWidget(spin_label)
        number_layout.addWidget(self.spin_box)
        number_layout.addWidget(double_label)
        number_layout.addWidget(self.double_spin)
        input_layout.addLayout(number_layout)

        # 日期时间输入
        datetime_layout = QHBoxLayout()
        date_label = QLabel("日期:")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())

        time_label = QLabel("时间:")
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())

        datetime_layout.addWidget(date_label)
        datetime_layout.addWidget(self.date_edit)
        datetime_layout.addWidget(time_label)
        datetime_layout.addWidget(self.time_edit)
        input_layout.addLayout(datetime_layout)

        # 按钮控件组
        button_group = QGroupBox("按钮控件")
        button_layout = QVBoxLayout(button_group)

        # 普通按钮
        btn_layout = QHBoxLayout()
        self.show_text_btn = QPushButton("显示文本")
        self.show_text_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.exit_btn = QPushButton("退出")
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6; 
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)

        btn_layout.addWidget(self.show_text_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.exit_btn)
        button_layout.addLayout(btn_layout)

        # 单选按钮
        radio_layout = QHBoxLayout()
        radio_label = QLabel("选项:")
        self.radio1 = QRadioButton("选项1")
        self.radio2 = QRadioButton("选项2")
        self.radio3 = QRadioButton("选项3")
        self.radio1.setChecked(True)

        radio_layout.addWidget(radio_label)
        radio_layout.addWidget(self.radio1)
        radio_layout.addWidget(self.radio2)
        radio_layout.addWidget(self.radio3)
        button_layout.addLayout(radio_layout)

        # 复选框
        checkbox_layout = QHBoxLayout()
        self.checkbox1 = QCheckBox("复选框1")
        self.checkbox2 = QCheckBox("复选框2")
        self.checkbox3 = QCheckBox("复选框3")
        self.checkbox1.setChecked(True)

        checkbox_layout.addWidget(self.checkbox1)
        checkbox_layout.addWidget(self.checkbox2)
        checkbox_layout.addWidget(self.checkbox3)
        button_layout.addLayout(checkbox_layout)

        # 下拉列表
        combo_layout = QHBoxLayout()
        combo_label = QLabel("下拉选择:")
        self.combo_box = QComboBox()
        self.combo_box.addItems(["选项 A", "选项 B", "选项 C", "选项 D"])

        combo_layout.addWidget(combo_label)
        combo_layout.addWidget(self.combo_box)
        button_layout.addLayout(combo_layout)

        # 文本显示区域
        text_display_group = QGroupBox("文本显示")
        text_display_layout = QVBoxLayout(text_display_group)
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        text_display_layout.addWidget(self.text_display)

        # 添加到基本选项卡
        basic_layout.addWidget(input_group)
        basic_layout.addWidget(button_group)
        basic_layout.addWidget(text_display_group)

        # 第二个选项卡：高级控件
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)

        # 进度条和滑块
        progress_group = QGroupBox("进度控制")
        progress_layout = QVBoxLayout(progress_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(30)

        # 滑块
        slider_layout = QHBoxLayout()
        slider_label = QLabel("滑块:")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(30)

        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(self.slider)

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addLayout(slider_layout)

        # 列表控件
        list_group = QGroupBox("项目列表")
        list_layout = QVBoxLayout(list_group)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #dee2e6;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        # 添加示例项目
        self.list_widget.addItems(["项目 1 [常规]", "项目 2 [重要]", "项目 3 [紧急]"])
        list_layout.addWidget(self.list_widget)

        list_btn_layout = QHBoxLayout()
        self.add_list_btn = QPushButton("添加项目")
        self.add_list_btn.setIcon(QIcon(":qt-project.org/qmessagebox/images/information.png"))
        self.add_list_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; 
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)

        self.remove_list_btn = QPushButton("删除项目")
        self.remove_list_btn.setIcon(QIcon(":qt-project.org/qmessagebox/images/critical.png"))
        self.remove_list_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; 
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        self.clear_list_btn = QPushButton("清空列表")
        self.clear_list_btn.setIcon(QIcon(":qt-project.org/qmessagebox/images/warning.png"))
        self.clear_list_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12; 
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)

        self.view_item_btn = QPushButton("查看详情")
        self.view_item_btn.setIcon(QIcon(":qt-project.org/qmessagebox/images/question.png"))
        self.view_item_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        list_btn_layout.addWidget(self.add_list_btn)
        list_btn_layout.addWidget(self.remove_list_btn)
        list_btn_layout.addWidget(self.view_item_btn)
        list_btn_layout.addWidget(self.clear_list_btn)
        list_layout.addLayout(list_btn_layout)

        # 添加到高级选项卡
        advanced_layout.addWidget(progress_group)
        advanced_layout.addWidget(list_group)
        advanced_layout.addStretch()

        # 第三个选项卡：关于
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)

        about_label = QLabel("PyQt5 GUI 示例应用\n\n"
                             "本示例展示了PyQt5中常用的GUI控件和功能，包括：\n"
                             "- 文本输入框、按钮、标签等基本控件\n"
                             "- 单选按钮、复选框、下拉列表等选择控件\n"
                             "- 进度条、滑块等进度控件\n"
                             "- 列表控件和操作\n"
                             "- 日期时间选择器\n"
                             "- 消息对话框和文件对话框\n\n"
                             "PyQt5是一个强大的Python GUI框架，可用于创建跨平台的桌面应用程序。")
        about_label.setFont(QFont("Arial", 12))
        about_label.setAlignment(Qt.AlignCenter)

        # 添加图标
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(":qt-project.org/qmessagebox/images/qtlogo-64.png"))
        icon_label.setAlignment(Qt.AlignCenter)

        about_layout.addWidget(icon_label)
        about_layout.addWidget(about_label)

        # 添加选项卡
        tab_widget.addTab(basic_tab, "基本控件")
        tab_widget.addTab(advanced_tab, "高级控件")
        tab_widget.addTab(about_tab, "关于")

        # 添加控件到主布局
        main_layout.addWidget(title_label)
        main_layout.addWidget(tab_widget)

        # 连接信号和槽
        self.connect_signals()

    def connect_signals(self):
        """连接所有信号和槽函数"""
        # 基本控件信号
        self.show_text_btn.clicked.connect(self.display_inputs)
        self.clear_btn.clicked.connect(self.clear_inputs)
        self.exit_btn.clicked.connect(self.close)

        # 滑块和进度条同步
        self.slider.valueChanged.connect(self.progress_bar.setValue)

        # 列表控件信号
        self.add_list_btn.clicked.connect(self.show_add_item_dialog)
        self.remove_list_btn.clicked.connect(self.remove_list_item)
        self.clear_list_btn.clicked.connect(self.confirm_clear_list)
        self.view_item_btn.clicked.connect(self.show_item_details)
        self.list_widget.itemDoubleClicked.connect(self.show_item_details)

    def display_inputs(self):
        """显示所有输入控件的内容"""
        text = "=== 输入内容 ===\n"
        text += f"文本输入: {self.text_input.text()}\n"
        text += f"整数: {self.spin_box.value()}\n"
        text += f"小数: {self.double_spin.value()}\n"
        text += f"日期: {self.date_edit.date().toString('yyyy-MM-dd')}\n"
        text += f"时间: {self.time_edit.time().toString('hh:mm:ss')}\n"

        text += "\n=== 选择内容 ===\n"
        # 获取单选按钮选择
        if self.radio1.isChecked():
            text += "单选选择: 选项1\n"
        elif self.radio2.isChecked():
            text += "单选选择: 选项2\n"
        else:
            text += "单选选择: 选项3\n"

        # 获取复选框选择
        checked_boxes = []
        if self.checkbox1.isChecked():
            checked_boxes.append("复选框1")
        if self.checkbox2.isChecked():
            checked_boxes.append("复选框2")
        if self.checkbox3.isChecked():
            checked_boxes.append("复选框3")
        text += f"复选框选择: {', '.join(checked_boxes)}\n"

        # 获取下拉框选择
        text += f"下拉选择: {self.combo_box.currentText()}\n"

        self.text_display.setText(text)

    def clear_inputs(self):
        """清空所有输入控件"""
        self.text_input.clear()
        self.spin_box.setValue(0)
        self.double_spin.setValue(0.0)
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())
        self.radio1.setChecked(True)
        self.checkbox1.setChecked(True)
        self.checkbox2.setChecked(False)
        self.checkbox3.setChecked(False)
        self.combo_box.setCurrentIndex(0)
        self.text_display.clear()

    def show_add_item_dialog(self):
        """显示添加项目对话框"""
        dialog = AddItemDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            item_data = dialog.get_item_data()
            item_text = f"{item_data['name']} [{item_data['type']}]"

            # 根据类型设置不同的文本颜色
            item = QListWidgetItem(item_text)
            if item_data['type'] == "重要":
                item.setForeground(Qt.darkYellow)
            elif item_data['type'] == "紧急":
                item.setForeground(Qt.red)
            elif item_data['type'] == "已完成":
                item.setForeground(Qt.darkGreen)

            # 存储额外数据
            item.setData(Qt.UserRole, item_data)

            self.list_widget.addItem(item)
            self.list_widget.scrollToItem(item)

    def remove_list_item(self):
        """删除选中的列表项"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            item = self.list_widget.takeItem(current_row)
            QMessageBox.information(
                self,
                "项目删除",
                f"已删除项目: {item.text()}",
                QMessageBox.Ok
            )

    def confirm_clear_list(self):
        """确认清空列表"""
        if self.list_widget.count() == 0:
            return

        reply = QMessageBox.question(
            self, "清空列表",
            "确定要清空整个项目列表吗?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.list_widget.clear()

    def show_item_details(self):
        """显示选中项目的详细信息"""
        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "无选中项目", "请先选择一个项目")
            return

        item_data = current_item.data(Qt.UserRole)
        if not item_data:
            QMessageBox.information(self, "项目详情", f"项目: {current_item.text()}")
            return

        details = f"项目名称: {item_data['name']}\n"
        details += f"类型: {item_data['type']}\n"
        details += f"优先级: {item_data['priority']}\n"
        details += f"描述:\n{item_data['description']}"

        QMessageBox.information(
            self,
            "项目详情",
            details,
            QMessageBox.Ok
        )

    def closeEvent(self, event):
        """重写关闭事件，添加确认对话框"""
        reply = QMessageBox.question(
            self, "退出确认",
            "确定要退出应用吗?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用样式
    app.setStyle("Fusion")

    # 创建并显示主窗口
    window = PyQtGUIApp()
    window.show()

    # 启动应用事件循环
    sys.exit(app.exec_())