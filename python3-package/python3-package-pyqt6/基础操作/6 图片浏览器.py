import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFileDialog, QGraphicsView, QGraphicsScene,
                             QGraphicsPixmapItem, QToolBar, QSlider, QGroupBox, QComboBox)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QIcon, QAction
from PyQt6.QtCore import Qt


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PyQt6 图片浏览器")
        self.setGeometry(100, 100, 1000, 700)
        
        # 当前图片路径和缩放比例
        self.current_image_path = None
        self.zoom_factor = 1.0
        self.rotation_angle = 0
        self.flip_horizontal = False
        self.flip_vertical = False
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 工具栏
        self.create_toolbar()
        
        # 图片显示区域（使用Graphics View）
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.view)
        
        # 控制面板
        control_group = QGroupBox("图片控制")
        control_layout = QHBoxLayout(control_group)
        
        # 缩放滑块
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("缩放:"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 500)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        zoom_layout.addWidget(self.zoom_slider)
        self.zoom_label = QLabel("100%")
        zoom_layout.addWidget(self.zoom_label)
        control_layout.addLayout(zoom_layout)
        
        # 旋转控制
        rotate_layout = QHBoxLayout()
        rotate_layout.addWidget(QLabel("旋转:"))
        self.rotate_combo = QComboBox()
        self.rotate_combo.addItems(["0°", "90°", "180°", "270°"])
        self.rotate_combo.currentIndexChanged.connect(self.on_rotate_changed)
        rotate_layout.addWidget(self.rotate_combo)
        control_layout.addLayout(rotate_layout)
        
        control_layout.addStretch()
        main_layout.addWidget(control_group)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪 - 请打开图片文件", 3000)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("图片工具栏")
        self.addToolBar(toolbar)
        
        # 打开图片
        open_action = QAction("📂 打开图片", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # 放大
        zoom_in_action = QAction("🔍+ 放大", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        # 缩小
        zoom_out_action = QAction("🔍- 缩小", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        # 适应窗口
        fit_action = QAction("⊡ 适应窗口", self)
        fit_action.setShortcut("Ctrl+F")
        fit_action.triggered.connect(self.fit_to_window)
        toolbar.addAction(fit_action)
        
        # 原始大小
        original_action = QAction("1️⃣ 原始大小", self)
        original_action.setShortcut("Ctrl+1")
        original_action.triggered.connect(self.original_size)
        toolbar.addAction(original_action)
        
        toolbar.addSeparator()
        
        # 向左旋转
        rotate_left_action = QAction("↺ 左转90°", self)
        rotate_left_action.triggered.connect(lambda: self.rotate_image(-90))
        toolbar.addAction(rotate_left_action)
        
        # 向右旋转
        rotate_right_action = QAction("↻ 右转90°", self)
        rotate_right_action.triggered.connect(lambda: self.rotate_image(90))
        toolbar.addAction(rotate_right_action)
        
        toolbar.addSeparator()
        
        # 翻转
        flip_h_action = QAction("⇄ 水平翻转", self)
        flip_h_action.triggered.connect(lambda: self.flip_image(True))
        toolbar.addAction(flip_h_action)
        
        flip_v_action = QAction("⇅ 垂直翻转", self)
        flip_v_action.triggered.connect(lambda: self.flip_image(False))
        toolbar.addAction(flip_v_action)
        
        toolbar.addSeparator()
        
        # 保存
        save_action = QAction("💾 保存图片", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_image)
        toolbar.addAction(save_action)
    
    def open_image(self):
        """打开图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开图片", "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*)"
        )
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """加载图片"""
        try:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                raise Exception("无法加载图片")
            
            self.current_image_path = file_path
            self.zoom_factor = 1.0
            self.rotation_angle = 0
            
            # 清空场景并添加新图片
            self.scene.clear()
            self.pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.pixmap_item)
            
            # 更新视图
            self.fit_to_window()
            
            # 更新状态栏
            width = pixmap.width()
            height = pixmap.height()
            self.status_bar.showMessage(
                f"已加载: {file_path} | 尺寸: {width}x{height}", 3000
            )
            
        except Exception as e:
            self.status_bar.showMessage(f"加载图片失败: {e}", 5000)
    
    def zoom_in(self):
        """放大"""
        self.zoom_factor *= 1.2
        self.apply_transform()
        self.update_zoom_slider()
    
    def zoom_out(self):
        """缩小"""
        self.zoom_factor /= 1.2
        self.apply_transform()
        self.update_zoom_slider()
    
    def fit_to_window(self):
        """适应窗口"""
        if not self.scene.items():
            return
        
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.zoom_factor = 1.0
        self.rotation_angle = 0
        self.flip_horizontal = False
        self.flip_vertical = False
        self.update_zoom_slider()
        self.zoom_label.setText("100%")
        self.rotate_combo.setCurrentIndex(0)
    
    def original_size(self):
        """原始大小"""
        self.zoom_factor = 1.0
        self.apply_transform()
        self.update_zoom_slider()
    
    def on_zoom_changed(self, value):
        """缩放滑块改变事件"""
        self.zoom_factor = value / 100.0
        self.zoom_label.setText(f"{value}%")
        self.apply_transform()
    
    def update_zoom_slider(self):
        """更新缩放滑块（不触发信号）"""
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(int(self.zoom_factor * 100))
        self.zoom_slider.blockSignals(False)
    
    def apply_transform(self):
        """应用变换"""
        if not hasattr(self, 'pixmap_item'):
            return
        
        try:
            from PyQt6.QtGui import QTransform
            
            # 创建新的变换矩阵
            transform = QTransform()
            
            # 获取图片中心点
            rect = self.pixmap_item.boundingRect()
            center_x = rect.width() / 2
            center_y = rect.height() / 2
            
            # 平移到中心
            transform.translate(center_x, center_y)
            
            # 应用翻转
            if self.flip_horizontal:
                transform.scale(-1, 1)
            if self.flip_vertical:
                transform.scale(1, -1)
            
            # 应用缩放
            transform.scale(self.zoom_factor, self.zoom_factor)
            
            # 应用旋转
            transform.rotate(self.rotation_angle)
            
            # 平移回原位
            transform.translate(-center_x, -center_y)
            
            # 应用变换
            self.pixmap_item.setTransform(transform)
            
        except Exception as e:
            print(f"变换错误: {e}")
            import traceback
            traceback.print_exc()
    
    def rotate_image(self, angle):
        """旋转图片"""
        self.rotation_angle = (self.rotation_angle + angle) % 360
        self.apply_transform()
    
    def on_rotate_changed(self, index):
        """旋转下拉框改变事件"""
        angles = [0, 90, 180, 270]
        self.rotation_angle = angles[index]
        self.apply_transform()
    
    def flip_image(self, horizontal):
        """翻转图片"""
        try:
            if not hasattr(self, 'pixmap_item'):
                return
            
            if horizontal:
                # 切换水平翻转状态
                self.flip_horizontal = not self.flip_horizontal
                print(f"水平翻转: {self.flip_horizontal}")
            else:
                # 切换垂直翻转状态
                self.flip_vertical = not self.flip_vertical
                print(f"垂直翻转: {self.flip_vertical}")
            
            # 统一应用所有变换
            self.apply_transform()
        except Exception as e:
            print(f"翻转错误: {e}")
            import traceback
            traceback.print_exc()
    
    def save_image(self):
        """保存图片"""
        if not hasattr(self, 'pixmap_item'):
            self.status_bar.showMessage("没有可保存的图片", 3000)
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存图片", "", 
            "PNG 图片 (*.png);;JPEG 图片 (*.jpg);;BMP 图片 (*.bmp)"
        )
        
        if file_path:
            try:
                # 获取当前显示的图像
                pixmap = self.pixmap_item.pixmap()
                
                # 根据格式保存
                if file_path.lower().endswith('.png'):
                    pixmap.save(file_path, 'PNG')
                elif file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                    pixmap.save(file_path, 'JPG')
                elif file_path.lower().endswith('.bmp'):
                    pixmap.save(file_path, 'BMP')
                else:
                    pixmap.save(file_path)
                
                self.status_bar.showMessage(f"图片已保存: {file_path}", 3000)
            except Exception as e:
                self.status_bar.showMessage(f"保存图片失败: {e}", 5000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = ImageViewer()
    window.show()
    
    sys.exit(app.exec())
