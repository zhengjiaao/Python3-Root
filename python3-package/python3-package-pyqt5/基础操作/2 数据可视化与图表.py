import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QSlider, QSpinBox,
                             QStatusBar, QFileDialog)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QPixmap
from PyQt5.QtCore import Qt, QPointF


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        """
        初始化图表部件
        支持柱状图、折线图和饼图三种类型
        """
        super().__init__(parent)

        # 设置最小尺寸
        self.setMinimumSize(600, 400)

        # 初始化数据和图表类型
        self.data = []
        self.chart_type = "Bar"  # 默认图表类型为柱状图

        # 定义图表颜色（使用RGB值）
        self.colors = [QColor(255, 99, 132), QColor(54, 162, 235),
                       QColor(255, 206, 86), QColor(75, 192, 192),
                       QColor(153, 102, 255), QColor(255, 159, 64)]

        # 生成示例数据
        self.generate_data()

    def generate_data(self, count=6):
        """
        生成随机示例数据
        :param count: 数据项数量
        """
        self.data = []
        for i in range(count):
            self.data.append({
                'label': f"项目 {i + 1}",
                'value': random.randint(10, 100)  # 随机生成10-100之间的数值
            })

    def set_chart_type(self, chart_type):
        """
        设置当前图表类型
        :param chart_type: 图表类型 ("Bar", "Line", "Pie")
        """
        self.chart_type = chart_type
        self.update()  # 更新界面显示

    def paintEvent(self, event):
        """绘制事件，根据当前设置绘制相应类型的图表"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿

        # 设置背景色
        painter.fillRect(self.rect(), QColor(240, 240, 240))  # 浅灰色背景

        if not self.data:
            return

        # 绘制标题
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(20, 30, f"{self.chart_type} 图表")

        # 根据类型绘制图表
        if self.chart_type == "Bar":
            self.draw_bar_chart(painter)
        elif self.chart_type == "Line":
            self.draw_line_chart(painter)
        elif self.chart_type == "Pie":
            self.draw_pie_chart(painter)

    def draw_bar_chart(self, painter):
        """绘制柱状图"""
        margin = 60  # 边距
        chart_width = self.width() - 2 * margin
        chart_height = self.height() - 2 * margin

        # 计算柱形宽度和间隔
        bar_width = chart_width / (len(self.data) * 1.5)
        gap = bar_width / 2

        # 计算最大值用于比例缩放
        max_value = max(item['value'] for item in self.data)
        scale = chart_height / max_value

        # 绘制坐标轴
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(int(margin), int(self.height() - margin),
                        int(self.width() - margin), int(self.height() - margin))  # X轴
        painter.drawLine(int(margin), int(self.height() - margin), int(margin), int(margin))  # Y轴

        # 绘制Y轴刻度
        for i in range(0, int(max_value) + 10, 10):
            y = self.height() - margin - i * scale
            painter.drawLine(int(margin - 5), int(y), int(margin), int(y))
            painter.drawText(int(margin - 40), int(y + 5), str(i))

        # 绘制柱状图
        for i, item in enumerate(self.data):
            x = margin + gap + i * (bar_width + gap)
            bar_height = item['value'] * scale
            y = self.height() - margin - bar_height

            color = self.colors[i % len(self.colors)]  # 获取对应颜色
            painter.setBrush(color)
            painter.setPen(QPen(color.darker(), 1))  # 设置边框颜色
            painter.drawRect(int(x), int(y), int(bar_width), int(bar_height))  # 绘制矩形

            # 绘制数值标签
            painter.setPen(Qt.black)
            painter.drawText(int(x + bar_width / 2 - 10), int(y - 10), str(item['value']))

            # 绘制X轴标签
            painter.drawText(int(x + bar_width / 2 - 20), int(self.height() - margin + 20), item['label'])

    def draw_line_chart(self, painter):
        """绘制折线图"""
        margin = 60  # 边距
        chart_width = self.width() - 2 * margin
        chart_height = self.height() - 2 * margin

        # 计算最大值用于比例缩放
        max_value = max(item['value'] for item in self.data)
        scale = chart_height / max_value

        # 绘制坐标轴
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(int(margin), int(self.height() - margin),
                         int(self.width() - margin), int(self.height() - margin))  # X轴
        painter.drawLine(int(margin), int(self.height() - margin), int(margin), int(margin))  # Y轴

        # 绘制Y轴刻度
        for i in range(0, int(max_value) + 10, 10):
            y = self.height() - margin - i * scale
            painter.drawLine(int(margin - 5), int(y), int(margin), int(y))
            painter.drawText(int(margin - 40), int(y + 5), str(i))

        # 准备数据点
        points = []
        for i, item in enumerate(self.data):
            # 计算每个点的位置
            x = margin + (i / (len(self.data) - 1)) * chart_width
            y = self.height() - margin - item['value'] * scale
            points.append(QPointF(x, y))

            # 绘制数据点
            color = self.colors[i % len(self.colors)]  # 获取对应颜色
            painter.setBrush(color)
            painter.setPen(QPen(color.darker(), 2))  # 设置边框颜色
            painter.drawEllipse(int(x - 5), int(y - 5), 10, 10)  # 修改这里，使用整数坐标

            # 绘制数据标签
            painter.setPen(Qt.black)
            painter.drawText(int(x - 10), int(self.height() - margin + 20), item['label'])
            painter.drawText(int(x - 10), int(y - 15), str(item['value']))

        # 绘制连线
        if len(points) > 1:
            painter.setPen(QPen(QColor(75, 192, 192), 3))  # 设置线条样式
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])  # 连接各点

    def draw_pie_chart(self, painter):
        """绘制饼图"""
        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = min(self.width(), self.height()) / 3  # 计算半径
        total = sum(item['value'] for item in self.data)  # 总计

        # 绘制饼图
        start_angle = 0  # 起始角度
        for i, item in enumerate(self.data):
            angle = (item['value'] / total) * 360 * 16  # 计算扇形角度

            color = self.colors[i % len(self.colors)]  # 获取对应颜色
            painter.setBrush(color)
            painter.setPen(QPen(color.darker(), 1))  # 设置边框颜色
            # 绘制扇形
            painter.drawPie(int(center_x - radius), int(center_y - radius),
                            int(radius * 2), int(radius * 2),
                            int(start_angle), int(angle))

            # 绘制图例
            legend_x = 50
            legend_y = 50 + i * 30
            painter.drawRect(legend_x, legend_y, 20, 20)  # 图例方块
            painter.setPen(Qt.black)
            # 图例文本：包含名称、数值和百分比
            painter.drawText(legend_x + 30, legend_y + 15,
                           f"{item['label']}: {item['value']} ({item['value'] / total * 100:.1f}%)")

            start_angle += angle  # 更新起始角度

    def save_to_image(self, file_path):
        """
        将图表保存为图像文件
        :param file_path: 文件路径
        """
        pixmap = QPixmap(self.size())
        self.render(pixmap)

        if file_path.lower().endswith('.png'):
            pixmap.save(file_path, 'PNG')
        elif file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
            pixmap.save(file_path, 'JPG')
        else:
            pixmap.save(file_path)


class ChartWindow(QMainWindow):
    def __init__(self):
        """初始化主窗口"""
        super().__init__()

        # 设置窗口属性
        self.setWindowTitle("PyQt5 数据可视化")
        self.setGeometry(100, 100, 800, 600)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 控制面板
        control_layout = QHBoxLayout()

        # 图表类型选择
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Bar", "Line", "Pie"])
        self.chart_type_combo.currentTextChanged.connect(self.update_chart_type)

        # 数据项数选择
        self.data_count_spin = QSpinBox()
        self.data_count_spin.setRange(3, 12)  # 允许选择3到12个数据项
        self.data_count_spin.setValue(6)  # 默认6个数据项
        self.data_count_spin.valueChanged.connect(self.update_data_count)

        # 生成数据按钮
        generate_btn = QPushButton("生成随机数据")
        generate_btn.clicked.connect(self.generate_data)

        # 保存图表按钮
        save_btn = QPushButton("保存图表")
        save_btn.clicked.connect(self.save_chart)

        # 添加控件到控制面板
        control_layout.addWidget(QLabel("图表类型:"))
        control_layout.addWidget(self.chart_type_combo)
        control_layout.addWidget(QLabel("数据项数:"))
        control_layout.addWidget(self.data_count_spin)
        control_layout.addWidget(generate_btn)
        control_layout.addWidget(save_btn)
        control_layout.addStretch()  # 弹性空间

        # 图表部件
        self.chart_widget = ChartWidget()

        # 添加到主布局
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.chart_widget)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪", 3000)

    def update_chart_type(self, chart_type):
        """
        更新图表类型
        :param chart_type: 新的图表类型
        """
        self.chart_widget.set_chart_type(chart_type)

    def update_data_count(self, count):
        """
        更新数据项数
        :param count: 新的数据项数
        """
        self.chart_widget.generate_data(count)
        self.chart_widget.update()

    def generate_data(self):
        """生成新的随机数据并更新图表"""
        self.chart_widget.generate_data(self.data_count_spin.value())
        self.chart_widget.update()
        self.status_bar.showMessage("已生成新的随机数据", 3000)

    def save_chart(self):
        """打开文件对话框，保存图表为图像文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存图表", "", "PNG 图片 (*.png);;JPEG 图片 (*.jpg);;所有文件 (*)"
        )

        if file_path:
            try:
                self.chart_widget.save_to_image(file_path)
                self.status_bar.showMessage(f"图表已成功保存到: {file_path}", 5000)
            except Exception as e:
                self.status_bar.showMessage(f"保存图表时出错: {e}", 5000)

if __name__ == "__main__":
    # 创建 QApplication 实例
    app = QApplication(sys.argv)

    # 设置应用程序样式为 Fusion 以获得更好的视觉效果
    app.setStyle("Fusion")

    # 创建主窗口实例
    window = ChartWindow()

    # 显示主窗口
    window.show()

    # 启动应用程序的事件循环
    sys.exit(app.exec_())
