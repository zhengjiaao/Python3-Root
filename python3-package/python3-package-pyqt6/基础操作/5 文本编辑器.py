import sys
import warnings

# 忽略 libpng 警告
warnings.filterwarnings("ignore", message=".*iCCP.*")

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QToolBar, QStatusBar, QLabel, QFileDialog,
                             QMessageBox, QFontComboBox, QSpinBox, QColorDialog)
from PyQt6.QtGui import QAction, QTextCharFormat, QColor, QFont, QIcon
from PyQt6.QtCore import Qt


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PyQt6 文本编辑器")
        self.setGeometry(100, 100, 1000, 700)
        
        # 当前文件路径
        self.current_file = None
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 文本编辑区（先创建）
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Consolas", 12))
        self.text_edit.setPlaceholderText("在此开始输入文本...")
        main_layout.addWidget(self.text_edit)
        
        # 工具栏（后创建，因为需要引用 text_edit）
        self.create_toolbar()
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪", 3000)
        
        # 连接信号
        self.text_edit.cursorPositionChanged.connect(self.update_cursor_position)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("编辑工具栏")
        self.addToolBar(toolbar)
        
        # 文件操作
        new_action = QAction("📄 新建", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction("📂 打开", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction("💾 保存", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 撤销和重做
        undo_action = QAction("↩️ 撤销", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.text_edit.undo)
        toolbar.addAction(undo_action)
        
        redo_action = QAction("↪️ 重做", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.text_edit.redo)
        toolbar.addAction(redo_action)
        
        toolbar.addSeparator()
        
        # 剪切、复制、粘贴
        cut_action = QAction("✂️ 剪切", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.text_edit.cut)
        toolbar.addAction(cut_action)
        
        copy_action = QAction("📋 复制", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.text_edit.copy)
        toolbar.addAction(copy_action)
        
        paste_action = QAction("📌 粘贴", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.text_edit.paste)
        toolbar.addAction(paste_action)
        
        toolbar.addSeparator()
        
        # 字体选择
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont("Consolas"))
        self.font_combo.currentFontChanged.connect(self.change_font)
        toolbar.addWidget(QLabel("字体:"))
        toolbar.addWidget(self.font_combo)
        
        # 字号选择
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(12)
        self.size_spin.valueChanged.connect(self.change_font_size)
        toolbar.addWidget(QLabel("字号:"))
        toolbar.addWidget(self.size_spin)
        
        toolbar.addSeparator()
        
        # 加粗、斜体、下划线
        bold_action = QAction("𝗕 加粗", self)
        bold_action.setShortcut("Ctrl+B")
        bold_action.setCheckable(True)
        bold_action.triggered.connect(self.toggle_bold)
        toolbar.addAction(bold_action)
        
        italic_action = QAction("𝘐 斜体", self)
        italic_action.setShortcut("Ctrl+I")
        italic_action.setCheckable(True)
        italic_action.triggered.connect(self.toggle_italic)
        toolbar.addAction(italic_action)
        
        underline_action = QAction("U̲ 下划线", self)
        underline_action.setShortcut("Ctrl+U")
        underline_action.setCheckable(True)
        underline_action.triggered.connect(self.toggle_underline)
        toolbar.addAction(underline_action)
        
        toolbar.addSeparator()
        
        # 文字颜色
        color_action = QAction("🎨 文字颜色", self)
        color_action.triggered.connect(self.change_text_color)
        toolbar.addAction(color_action)
        
        # 背景颜色
        bg_color_action = QAction("🖼️ 背景颜色", self)
        bg_color_action.triggered.connect(self.change_bg_color)
        toolbar.addAction(bg_color_action)
        
        toolbar.addSeparator()
        
        # 全选
        select_all_action = QAction("☑️ 全选", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.text_edit.selectAll)
        toolbar.addAction(select_all_action)
    
    def update_cursor_position(self):
        """更新光标位置显示"""
        cursor = self.text_edit.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.positionInBlock() + 1
        self.status_bar.showMessage(f"行: {line}, 列: {col}", 0)
    
    def new_file(self):
        """新建文件"""
        if self.maybe_save():
            self.text_edit.clear()
            self.current_file = None
            self.setWindowTitle("PyQt6 文本编辑器 - 未命名")
            self.status_bar.showMessage("已创建新文件", 3000)
    
    def open_file(self):
        """打开文件"""
        if not self.maybe_save():
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "", 
            "文本文件 (*.txt);;Python 文件 (*.py);;所有文件 (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_edit.setText(content)
                self.current_file = file_path
                self.setWindowTitle(f"PyQt6 文本编辑器 - {file_path}")
                self.status_bar.showMessage(f"已打开: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开文件失败: {e}")
    
    def save_file(self):
        """保存文件"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_as()
    
    def save_as(self):
        """另存为"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "另存为", "", 
            "文本文件 (*.txt);;Python 文件 (*.py);;所有文件 (*)"
        )
        
        if file_path:
            self._save_to_file(file_path)
            self.current_file = file_path
            self.setWindowTitle(f"PyQt6 文本编辑器 - {file_path}")
    
    def _save_to_file(self, file_path):
        """保存到指定文件"""
        try:
            content = self.text_edit.toPlainText()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.status_bar.showMessage(f"已保存: {file_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存文件失败: {e}")
    
    def maybe_save(self):
        """检查是否需要保存"""
        if self.text_edit.document().isModified():
            reply = QMessageBox.question(
                self, "确认保存",
                "文档已修改，是否保存？",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
                return True
            elif reply == QMessageBox.StandardButton.Cancel:
                return False
        
        return True
    
    def change_font(self, font):
        """更改字体"""
        current_format = self.text_edit.currentCharFormat()
        current_format.setFontFamily(font.family())
        self.text_edit.mergeCurrentCharFormat(current_format)
    
    def change_font_size(self, size):
        """更改字号"""
        current_format = self.text_edit.currentCharFormat()
        current_format.setFontPointSize(size)
        self.text_edit.mergeCurrentCharFormat(current_format)
    
    def toggle_bold(self, checked):
        """切换加粗"""
        current_format = self.text_edit.currentCharFormat()
        current_format.setFontWeight(QFont.Weight.Bold if checked else QFont.Weight.Normal)
        self.text_edit.mergeCurrentCharFormat(current_format)
    
    def toggle_italic(self, checked):
        """切换斜体"""
        current_format = self.text_edit.currentCharFormat()
        current_format.setFontItalic(checked)
        self.text_edit.mergeCurrentCharFormat(current_format)
    
    def toggle_underline(self, checked):
        """切换下划线"""
        current_format = self.text_edit.currentCharFormat()
        current_format.setFontUnderline(checked)
        self.text_edit.mergeCurrentCharFormat(current_format)
    
    def change_text_color(self):
        """更改文字颜色"""
        color = QColor.fromRgb(0, 0, 0)  # 默认黑色
        color_dialog = QColorDialog(self)
        color_dialog.setCurrentColor(color)
        
        if color_dialog.exec():
            selected_color = color_dialog.selectedColor()
            current_format = self.text_edit.currentCharFormat()
            current_format.setForeground(selected_color)
            self.text_edit.mergeCurrentCharFormat(current_format)
    
    def change_bg_color(self):
        """更改背景颜色"""
        color_dialog = QColorDialog(self)
        
        if color_dialog.exec():
            selected_color = color_dialog.selectedColor()
            current_format = self.text_edit.currentCharFormat()
            current_format.setBackground(selected_color)
            self.text_edit.mergeCurrentCharFormat(current_format)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = TextEditor()
    window.show()
    
    sys.exit(app.exec())
