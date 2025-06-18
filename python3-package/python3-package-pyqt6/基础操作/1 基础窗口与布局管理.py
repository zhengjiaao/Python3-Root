import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
                             QCheckBox, QRadioButton, QGroupBox, QTabWidget, QStatusBar)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        """初始化主窗口"""
        super().__init__()

        # 设置窗口属性
        self.setWindowTitle("PyQt6 综合示例")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("app_icon.png"))  # 设置窗口图标

        # 创建中心部件作为所有内容的基础容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局 - 使用垂直布局排列顶部菜单栏和标签页
        main_layout = QVBoxLayout(central_widget)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建并添加标签页
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # 添加三个主要功能标签页
        tab_widget.addTab(self.create_form_tab(), "表单示例")
        tab_widget.addTab(self.create_data_tab(), "数据处理")
        tab_widget.addTab(self.create_settings_tab(), "系统设置")

        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪", 3000)  # 初始消息显示3秒

    def create_menu_bar(self):
        """创建顶部菜单栏"""
        menu_bar = self.menuBar()

        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        new_action = file_menu.addAction("新建")
        open_action = file_menu.addAction("打开")
        save_action = file_menu.addAction("保存")
        file_menu.addSeparator()  # 分隔线
        exit_action = file_menu.addAction("退出")

        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        cut_action = edit_menu.addAction("剪切")
        copy_action = edit_menu.addAction("复制")
        paste_action = edit_menu.addAction("粘贴")

        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        about_action = help_menu.addAction("关于")

        # 连接信号槽
        exit_action.triggered.connect(self.close)  # 退出菜单连接到关闭窗口
        about_action.triggered.connect(self.show_about)  # 关于菜单连接到显示信息函数

    def create_form_tab(self):
        """创建表单示例标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 个人信息组框
        info_group = QGroupBox("个人信息")
        info_layout = QVBoxLayout(info_group)

        # 姓名输入行
        name_layout = QHBoxLayout()
        name_label = QLabel("姓名:")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)

        # 性别选择行
        gender_layout = QHBoxLayout()
        gender_label = QLabel("性别:")
        self.male_radio = QRadioButton("男")
        self.female_radio = QRadioButton("女")
        self.male_radio.setChecked(True)  # 默认选中男性
        gender_layout.addWidget(gender_label)
        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)

        # 职业选择行
        job_layout = QHBoxLayout()
        job_label = QLabel("职业:")
        self.job_combo = QComboBox()
        self.job_combo.addItems(["学生", "工程师", "教师", "医生", "设计师"])
        job_layout.addWidget(job_label)
        job_layout.addWidget(self.job_combo)

        # 兴趣爱好选择行
        hobby_layout = QHBoxLayout()
        hobby_label = QLabel("兴趣爱好:")
        self.reading_check = QCheckBox("阅读")
        self.sports_check = QCheckBox("运动")
        self.music_check = QCheckBox("音乐")
        hobby_layout.addWidget(hobby_label)
        hobby_layout.addWidget(self.reading_check)
        hobby_layout.addWidget(self.sports_check)
        hobby_layout.addWidget(self.music_check)

        # 将上述元素添加到信息组框
        info_layout.addLayout(name_layout)
        info_layout.addLayout(gender_layout)
        info_layout.addLayout(job_layout)
        info_layout.addLayout(hobby_layout)

        # 个人简介文本区域
        bio_group = QGroupBox("个人简介")
        bio_layout = QVBoxLayout(bio_group)
        self.bio_edit = QTextEdit()
        self.bio_edit.setPlaceholderText("请在此输入您的个人简介...")  # 输入提示
        bio_layout.addWidget(self.bio_edit)

        # 按钮区域
        button_layout = QHBoxLayout()
        submit_btn = QPushButton("提交")
        clear_btn = QPushButton("清除")
        button_layout.addStretch()  # 弹性空间，使按钮靠右对齐
        button_layout.addWidget(submit_btn)
        button_layout.addWidget(clear_btn)

        # 连接按钮点击事件
        submit_btn.clicked.connect(self.submit_form)
        clear_btn.clicked.connect(self.clear_form)

        # 将所有组件添加到主布局
        layout.addWidget(info_group)
        layout.addWidget(bio_group)
        layout.addLayout(button_layout)

        return tab

    def create_data_tab(self):
        """创建数据处理标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 数据表格标题
        data_label = QLabel("数据表格")
        data_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))  # 标题加粗
        layout.addWidget(data_label)

        # 表格占位符（实际项目中可用QTableWidget）
        table_placeholder = QLabel("此处将显示数据表格")
        table_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 文本居中
        # 设置样式：背景色、边框、最小高度
        table_placeholder.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; min-height: 200px;")
        layout.addWidget(table_placeholder)

        # 图表标题
        chart_label = QLabel("数据可视化")
        chart_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(chart_label)

        # 图表占位符
        chart_placeholder = QLabel("此处将显示数据图表")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; min-height: 200px;")
        layout.addWidget(chart_placeholder)

        # 操作按钮
        btn_layout = QHBoxLayout()
        load_btn = QPushButton("加载数据")
        export_btn = QPushButton("导出数据")
        analyze_btn = QPushButton("分析数据")

        # 将按钮添加到布局
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(analyze_btn)
        btn_layout.addStretch()  # 弹性空间，使前面的按钮靠左对齐

        layout.addLayout(btn_layout)

        return tab

    def create_settings_tab(self):
        """创建系统设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 主题设置组框
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout(theme_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["默认主题", "深色模式", "蓝色主题", "绿色主题"])
        theme_layout.addWidget(QLabel("选择主题:"))
        theme_layout.addWidget(self.theme_combo)

        # 字体设置组框
        font_group = QGroupBox("字体设置")
        font_layout = QVBoxLayout(font_group)

        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Times New Roman", "Verdana", "微软雅黑"])
        font_layout.addWidget(QLabel("选择字体:"))
        font_layout.addWidget(self.font_combo)

        # 系统设置组框
        sys_group = QGroupBox("系统设置")
        sys_layout = QVBoxLayout(sys_group)

        self.auto_update_check = QCheckBox("自动检查更新")
        self.save_history_check = QCheckBox("保存历史记录")
        self.auto_login_check = QCheckBox("自动登录")

        sys_layout.addWidget(self.auto_update_check)
        sys_layout.addWidget(self.save_history_check)
        sys_layout.addWidget(self.auto_login_check)

        # 应用按钮
        apply_btn = QPushButton("应用设置")
        apply_btn.clicked.connect(self.apply_settings)

        # 将所有组件添加到主布局
        layout.addWidget(theme_group)
        layout.addWidget(font_group)
        layout.addWidget(sys_group)
        layout.addStretch()  # 弹性空间
        layout.addWidget(apply_btn)

        return tab

    def submit_form(self):
        """处理表单提交"""
        # 获取用户输入
        name = self.name_edit.text()
        gender = "男" if self.male_radio.isChecked() else "女"
        job = self.job_combo.currentText()

        # 获取兴趣爱好
        hobbies = []
        if self.reading_check.isChecked(): hobbies.append("阅读")
        if self.sports_check.isChecked(): hobbies.append("运动")
        if self.music_check.isChecked(): hobbies.append("音乐")

        # 获取个人简介
        bio = self.bio_edit.toPlainText()

        # 在实际应用中，这里可以保存数据到数据库或文件
        # 显示状态消息
        self.status_bar.showMessage(f"已提交: {name}, {gender}, {job}, 爱好: {', '.join(hobbies)}", 5000)

    def clear_form(self):
        """清除表单内容"""
        self.name_edit.clear()
        self.male_radio.setChecked(True)  # 默认选中男性
        self.job_combo.setCurrentIndex(0)  # 重置职业选择
        # 清除兴趣爱好勾选
        self.reading_check.setChecked(False)
        self.sports_check.setChecked(False)
        self.music_check.setChecked(False)
        self.bio_edit.clear()  # 清空个人简介

        # 更新状态栏
        self.status_bar.showMessage("表单已清除", 3000)

    def apply_settings(self):
        """应用系统设置"""
        # 获取设置值
        theme = self.theme_combo.currentText()
        font = self.font_combo.currentText()

        auto_update = self.auto_update_check.isChecked()
        save_history = self.save_history_check.isChecked()
        auto_login = self.auto_login_check.isChecked()

        # 在实际应用中，这里会应用设置
        # 更新状态栏
        self.status_bar.showMessage(f"设置已应用: {theme}, 字体: {font}", 5000)

    def show_about(self):
        """显示关于信息"""
        # 实际应用中会显示关于对话框
        self.status_bar.showMessage("PyQt6 示例应用 v1.0 © 2024", 5000)


if __name__ == "__main__":
    """应用程序入口"""
    app = QApplication(sys.argv)

    # 设置应用样式为Fusion以获得更好的视觉效果
    app.setStyle("Fusion")

    # 创建主窗口实例并显示
    window = MainWindow()
    window.show()

    # 启动应用程序事件循环
    sys.exit(app.exec())
