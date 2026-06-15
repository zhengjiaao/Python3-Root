import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QLabel, QFileDialog, QLineEdit,
                             QGroupBox, QMessageBox, QCheckBox, QComboBox, QTextEdit,
                             QProgressBar)
from PyQt6.QtCore import Qt


class BatchRenamer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PyQt6 批量文件重命名工具")
        self.setGeometry(100, 100, 900, 700)
        
        # 文件列表
        self.files = []
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 文件选择区域
        file_group = QGroupBox("📁 文件选择")
        file_layout = QVBoxLayout(file_group)
        
        # 按钮行
        btn_layout = QHBoxLayout()
        
        add_files_btn = QPushButton("➕ 添加文件")
        add_files_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(add_files_btn)
        
        add_folder_btn = QPushButton("📂 添加文件夹")
        add_folder_btn.clicked.connect(self.add_folder)
        btn_layout.addWidget(add_folder_btn)
        
        clear_btn = QPushButton("🗑️ 清空列表")
        clear_btn.clicked.connect(self.clear_list)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        file_layout.addLayout(btn_layout)
        
        # 文件列表
        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)
        
        # 统计信息
        self.file_count_label = QLabel("文件数: 0")
        file_layout.addWidget(self.file_count_label)
        
        main_layout.addWidget(file_group)
        
        # 重命名规则区域
        rule_group = QGroupBox("✏️ 重命名规则")
        rule_layout = QVBoxLayout(rule_group)
        
        # 模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("重命名模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "添加前缀",
            "添加后缀", 
            "替换文本",
            "删除字符",
            "序号重命名",
            "正则表达式"
        ])
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        rule_layout.addLayout(mode_layout)
        
        # 参数输入（根据模式动态显示）
        self.param_layout = QVBoxLayout()
        
        # 前缀输入
        self.prefix_widget = QWidget()
        prefix_layout = QHBoxLayout(self.prefix_widget)
        prefix_layout.addWidget(QLabel("前缀:"))
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("例如: [重要]")
        prefix_layout.addWidget(self.prefix_input)
        self.param_layout.addWidget(self.prefix_widget)
        
        # 后缀输入
        self.suffix_widget = QWidget()
        suffix_layout = QHBoxLayout(self.suffix_widget)
        suffix_layout.addWidget(QLabel("后缀:"))
        self.suffix_input = QLineEdit()
        self.suffix_input.setPlaceholderText("例如: _backup")
        suffix_layout.addWidget(self.suffix_input)
        self.param_layout.addWidget(self.suffix_widget)
        
        # 查找和替换
        self.replace_widget = QWidget()
        replace_layout = QVBoxLayout(self.replace_widget)
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("查找:"))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        replace_layout.addLayout(find_layout)
        
        replace_with_layout = QHBoxLayout()
        replace_with_layout.addWidget(QLabel("替换为:"))
        self.replace_input = QLineEdit()
        replace_with_layout.addWidget(self.replace_input)
        replace_layout.addLayout(replace_with_layout)
        self.param_layout.addWidget(self.replace_widget)
        
        # 删除字符
        self.delete_widget = QWidget()
        delete_layout = QVBoxLayout(self.delete_widget)
        delete_type_layout = QHBoxLayout()
        delete_type_layout.addWidget(QLabel("删除类型:"))
        self.delete_type_combo = QComboBox()
        self.delete_type_combo.addItems(["前N个字符", "后N个字符", "指定位置"])
        delete_layout.addLayout(delete_type_layout)
        
        delete_count_layout = QHBoxLayout()
        delete_count_layout.addWidget(QLabel("数量/位置:"))
        self.delete_count_input = QLineEdit()
        self.delete_count_input.setPlaceholderText("例如: 3")
        delete_count_layout.addWidget(self.delete_count_input)
        delete_layout.addLayout(delete_count_layout)
        self.param_layout.addWidget(self.delete_widget)
        
        # 序号重命名
        self.sequence_widget = QWidget()
        sequence_layout = QVBoxLayout(self.sequence_widget)
        seq_prefix_layout = QHBoxLayout()
        seq_prefix_layout.addWidget(QLabel("文件名前缀:"))
        self.seq_prefix_input = QLineEdit()
        self.seq_prefix_input.setPlaceholderText("例如: 文档")
        seq_prefix_layout.addWidget(self.seq_prefix_input)
        sequence_layout.addLayout(seq_prefix_layout)
        
        seq_start_layout = QHBoxLayout()
        seq_start_layout.addWidget(QLabel("起始序号:"))
        self.seq_start_input = QLineEdit()
        self.seq_start_input.setText("1")
        seq_start_layout.addWidget(self.seq_start_input)
        sequence_layout.addLayout(seq_start_layout)
        
        seq_format_layout = QHBoxLayout()
        seq_format_layout.addWidget(QLabel("序号格式:"))
        self.seq_format_combo = QComboBox()
        self.seq_format_combo.addItems(["001", "0001", "1", "01"])
        seq_format_layout.addWidget(self.seq_format_combo)
        sequence_layout.addLayout(seq_format_layout)
        self.param_layout.addWidget(self.sequence_widget)
        
        # 正则表达式
        self.regex_widget = QWidget()
        regex_layout = QVBoxLayout(self.regex_widget)
        regex_pattern_layout = QHBoxLayout()
        regex_pattern_layout.addWidget(QLabel("正则表达式:"))
        self.regex_pattern_input = QLineEdit()
        self.regex_pattern_input.setPlaceholderText("例如: (.*)\\.txt")
        regex_pattern_layout.addWidget(self.regex_pattern_input)
        regex_layout.addLayout(regex_pattern_layout)
        
        regex_replace_layout = QHBoxLayout()
        regex_replace_layout.addWidget(QLabel("替换为:"))
        self.regex_replace_input = QLineEdit()
        self.regex_replace_input.setPlaceholderText("例如: \\1_new.txt")
        regex_replace_layout.addWidget(self.regex_replace_input)
        regex_layout.addLayout(regex_replace_layout)
        self.param_layout.addWidget(self.regex_widget)
        
        rule_layout.addLayout(self.param_layout)
        
        # 预览按钮
        preview_btn = QPushButton("👁️ 预览结果")
        preview_btn.clicked.connect(self.preview_rename)
        rule_layout.addWidget(preview_btn)
        
        main_layout.addWidget(rule_group)
        
        # 预览区域
        preview_group = QGroupBox("👁️ 预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_area = QTextEdit()
        self.preview_area.setFontFamily("Consolas")
        self.preview_area.setReadOnly(True)
        preview_layout.addWidget(self.preview_area)
        
        main_layout.addWidget(preview_group)
        
        # 执行按钮
        action_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("✅ 执行重命名")
        self.execute_btn.clicked.connect(self.execute_rename)
        action_layout.addWidget(self.execute_btn)
        
        action_layout.addStretch()
        main_layout.addLayout(action_layout)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪 - 请添加文件", 3000)
        
        # 初始化显示
        self.on_mode_changed(0)
    
    def on_mode_changed(self, index):
        """模式改变时显示/隐藏相应参数"""
        # 隐藏所有参数
        self.prefix_widget.setVisible(False)
        self.suffix_widget.setVisible(False)
        self.replace_widget.setVisible(False)
        self.delete_widget.setVisible(False)
        self.sequence_widget.setVisible(False)
        self.regex_widget.setVisible(False)
        
        # 显示当前模式的参数
        if index == 0:  # 添加前缀
            self.prefix_widget.setVisible(True)
        elif index == 1:  # 添加后缀
            self.suffix_widget.setVisible(True)
        elif index == 2:  # 替换文本
            self.replace_widget.setVisible(True)
        elif index == 3:  # 删除字符
            self.delete_widget.setVisible(True)
        elif index == 4:  # 序号重命名
            self.sequence_widget.setVisible(True)
        elif index == 5:  # 正则表达式
            self.regex_widget.setVisible(True)
    
    def add_files(self):
        """添加文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择文件", "", 
            "所有文件 (*)"
        )
        
        if files:
            for file in files:
                if file not in self.files:
                    self.files.append(file)
                    self.file_list.addItem(os.path.basename(file))
            
            self.update_file_count()
            self.status_bar.showMessage(f"已添加 {len(files)} 个文件", 3000)
    
    def add_folder(self):
        """添加文件夹中的所有文件"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        
        if folder:
            count = 0
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in self.files:
                        self.files.append(file_path)
                        self.file_list.addItem(file)
                        count += 1
            
            self.update_file_count()
            self.status_bar.showMessage(f"从文件夹添加了 {count} 个文件", 3000)
    
    def clear_list(self):
        """清空文件列表"""
        self.files.clear()
        self.file_list.clear()
        self.update_file_count()
        self.preview_area.clear()
        self.status_bar.showMessage("列表已清空", 3000)
    
    def update_file_count(self):
        """更新文件计数"""
        self.file_count_label.setText(f"文件数: {len(self.files)}")
    
    def preview_rename(self):
        """预览重命名结果"""
        if not self.files:
            QMessageBox.warning(self, "警告", "请先添加文件")
            return
        
        mode = self.mode_combo.currentIndex()
        preview_text = ""
        
        for i, file_path in enumerate(self.files):
            old_name = os.path.basename(file_path)
            new_name = self.rename_file(old_name, mode, i)
            preview_text += f"{old_name}\n  → {new_name}\n\n"
        
        self.preview_area.setText(preview_text)
        self.status_bar.showMessage("预览已生成", 3000)
    
    def rename_file(self, filename, mode, index):
        """根据模式重命名单个文件"""
        name, ext = os.path.splitext(filename)
        
        if mode == 0:  # 添加前缀
            prefix = self.prefix_input.text()
            return f"{prefix}{name}{ext}"
        
        elif mode == 1:  # 添加后缀
            suffix = self.suffix_input.text()
            return f"{name}{suffix}{ext}"
        
        elif mode == 2:  # 替换文本
            find_text = self.find_input.text()
            replace_text = self.replace_input.text()
            new_name = name.replace(find_text, replace_text)
            return f"{new_name}{ext}"
        
        elif mode == 3:  # 删除字符
            delete_type = self.delete_type_combo.currentIndex()
            try:
                count = int(self.delete_count_input.text())
            except:
                return filename
            
            if delete_type == 0:  # 前N个字符
                new_name = name[count:]
            elif delete_type == 1:  # 后N个字符
                new_name = name[:-count] if count > 0 else name
            else:  # 指定位置
                new_name = name[:count-1] + name[count:]
            
            return f"{new_name}{ext}"
        
        elif mode == 4:  # 序号重命名
            prefix = self.seq_prefix_input.text()
            try:
                start = int(self.seq_start_input.text())
            except:
                start = 1
            
            format_type = self.seq_format_combo.currentIndex()
            if format_type == 0:  # 001
                num_str = f"{start + index:03d}"
            elif format_type == 1:  # 0001
                num_str = f"{start + index:04d}"
            elif format_type == 2:  # 1
                num_str = str(start + index)
            else:  # 01
                num_str = f"{start + index:02d}"
            
            return f"{prefix}_{num_str}{ext}"
        
        elif mode == 5:  # 正则表达式
            pattern = self.regex_pattern_input.text()
            replace = self.regex_replace_input.text()
            try:
                new_name = re.sub(pattern, replace, filename)
                return new_name
            except:
                return filename
        
        return filename
    
    def execute_rename(self):
        """执行重命名"""
        if not self.files:
            QMessageBox.warning(self, "警告", "请先添加文件")
            return
        
        if not self.preview_area.toPlainText():
            reply = QMessageBox.question(
                self, "确认执行",
                "尚未预览，是否直接执行重命名？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        reply = QMessageBox.question(
            self, "确认执行",
            f"确定要重命名 {len(self.files)} 个文件吗？\n此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            mode = self.mode_combo.currentIndex()
            success_count = 0
            fail_count = 0
            
            for i, file_path in enumerate(self.files):
                try:
                    dir_path = os.path.dirname(file_path)
                    old_name = os.path.basename(file_path)
                    new_name = self.rename_file(old_name, mode, i)
                    new_path = os.path.join(dir_path, new_name)
                    
                    if os.path.exists(new_path):
                        print(f"跳过: {new_name} 已存在")
                        fail_count += 1
                        continue
                    
                    os.rename(file_path, new_path)
                    success_count += 1
                    
                    # 更新列表中的路径
                    self.files[i] = new_path
                    
                except Exception as e:
                    print(f"重命名失败 {file_path}: {e}")
                    fail_count += 1
            
            # 刷新列表显示
            self.file_list.clear()
            for file_path in self.files:
                self.file_list.addItem(os.path.basename(file_path))
            
            self.status_bar.showMessage(f"重命名完成: 成功 {success_count}, 失败 {fail_count}", 5000)
            QMessageBox.information(
                self, "完成",
                f"重命名完成!\n成功: {success_count}\n失败: {fail_count}"
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = BatchRenamer()
    window.show()
    
    sys.exit(app.exec())
