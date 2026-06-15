import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTreeView, QListView, QLabel, QSplitter,
                             QToolBar, QStatusBar, QMessageBox, QLineEdit)
from PyQt6.QtGui import QAction, QIcon, QStandardItemModel, QStandardItem, QFileSystemModel
from PyQt6.QtCore import Qt, QDir


class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PyQt6 文件管理器")
        self.setGeometry(100, 100, 1200, 700)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 工具栏
        self.create_toolbar()
        
        # 地址栏
        address_layout = QHBoxLayout()
        address_layout.addWidget(QLabel("路径:"))
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate_to_path)
        address_layout.addWidget(self.address_bar)
        
        main_layout.addLayout(address_layout)
        
        # 分割器（左侧树形视图，右侧列表视图）
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：目录树
        self.tree_view = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        self.file_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot)
        
        self.tree_view.setModel(self.file_model)
        self.tree_view.setHeaderHidden(True)
        for i in range(1, self.file_model.columnCount()):
            self.tree_view.hideColumn(i)
        
        self.tree_view.clicked.connect(self.on_tree_clicked)
        
        # 右侧：文件列表
        self.list_view = QListView()
        self.list_model = QFileSystemModel()
        self.list_model.setRootPath(QDir.homePath())
        self.list_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)
        
        self.list_view.setModel(self.list_model)
        self.list_view.clicked.connect(self.on_list_clicked)
        
        # 添加到分割器
        splitter.addWidget(self.tree_view)
        splitter.addWidget(self.list_view)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪", 3000)
        
        # 设置初始路径
        home_path = QDir.homePath()
        self.address_bar.setText(home_path)
        self.list_model.setRootPath(home_path)
        self.tree_view.setCurrentIndex(self.file_model.index(home_path))
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)
        
        # 返回上级目录
        up_action = QAction("⬆️ 上级目录", self)
        up_action.setShortcut("Alt+Up")
        up_action.triggered.connect(self.go_up)
        toolbar.addAction(up_action)
        
        # 刷新
        refresh_action = QAction("🔄 刷新", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # 新建文件夹
        new_folder_action = QAction("📁 新建文件夹", self)
        new_folder_action.triggered.connect(self.create_new_folder)
        toolbar.addAction(new_folder_action)
        
        # 删除
        delete_action = QAction("🗑️ 删除", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.delete_selected)
        toolbar.addAction(delete_action)
    
    def on_tree_clicked(self, index):
        """处理树形视图点击事件"""
        path = self.file_model.filePath(index)
        self.address_bar.setText(path)
        self.list_model.setRootPath(path)
    
    def on_list_clicked(self, index):
        """处理列表视图点击事件"""
        path = self.list_model.filePath(index)
        if os.path.isdir(path):
            self.address_bar.setText(path)
            self.list_model.setRootPath(path)
            # 同步树形视图
            tree_index = self.file_model.index(path)
            self.tree_view.setCurrentIndex(tree_index)
            self.tree_view.expand(tree_index)
        else:
            self.status_bar.showMessage(f"选中文件: {os.path.basename(path)}", 3000)
    
    def navigate_to_path(self):
        """导航到指定路径"""
        path = self.address_bar.text()
        if os.path.exists(path) and os.path.isdir(path):
            self.list_model.setRootPath(path)
            tree_index = self.file_model.index(path)
            self.tree_view.setCurrentIndex(tree_index)
            self.tree_view.expand(tree_index)
            self.status_bar.showMessage(f"已导航到: {path}", 3000)
        else:
            QMessageBox.warning(self, "错误", f"路径不存在: {path}")
    
    def go_up(self):
        """返回上级目录"""
        current_path = self.address_bar.text()
        parent_path = os.path.dirname(current_path)
        if parent_path != current_path:  # 防止在根目录时死循环
            self.address_bar.setText(parent_path)
            self.list_model.setRootPath(parent_path)
            tree_index = self.file_model.index(parent_path)
            self.tree_view.setCurrentIndex(tree_index)
    
    def refresh(self):
        """刷新视图"""
        current_path = self.address_bar.text()
        self.list_model.setRootPath("")
        self.list_model.setRootPath(current_path)
        self.status_bar.showMessage("已刷新", 2000)
    
    def create_new_folder(self):
        """创建新文件夹"""
        current_path = self.address_bar.text()
        folder_name = "新建文件夹"
        new_path = os.path.join(current_path, folder_name)
        
        counter = 1
        while os.path.exists(new_path):
            new_path = os.path.join(current_path, f"{folder_name} ({counter})")
            counter += 1
        
        try:
            os.makedirs(new_path)
            self.refresh()
            self.status_bar.showMessage(f"已创建文件夹: {new_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建文件夹失败: {e}")
    
    def delete_selected(self):
        """删除选中的文件或文件夹"""
        indexes = self.list_view.selectedIndexes()
        if not indexes:
            QMessageBox.warning(self, "警告", "请先选择要删除的项目")
            return
        
        paths = set()
        for index in indexes:
            path = self.list_model.filePath(index)
            paths.add(path)
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除以下 {len(paths)} 个项目吗？\n此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success_count = 0
            fail_count = 0
            for path in paths:
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        import shutil
                        shutil.rmtree(path)
                    success_count += 1
                except Exception as e:
                    fail_count += 1
                    print(f"删除失败 {path}: {e}")
            
            self.refresh()
            self.status_bar.showMessage(f"删除完成: 成功 {success_count}, 失败 {fail_count}", 3000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = FileManager()
    window.show()
    
    sys.exit(app.exec())
