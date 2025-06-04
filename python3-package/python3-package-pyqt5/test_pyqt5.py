import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QCheckBox, QRadioButton, QGroupBox, QProgressBar,
    QSlider, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit,
    QListWidget, QTabWidget, QFileDialog, QMessageBox, QInputDialog
)

# app = QApplication(sys.argv)
# window = QWidget()
# window.setWindowTitle('PyQt5 Test')
# # window.setGeometry(100, 100, 200, 200) # 设置窗口大小和位置
# # window.resize(400, 300) # 设置窗口大小
# # window.move(300, 300) # 设置窗口位置
# window.show()
# sys.exit(app.exec_())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('PyQt5 Test')
    # window.setGeometry(100, 100, 200, 200) # 设置窗口大小和位置
    # window.resize(400, 300) # 设置窗口大小
    # window.move(300, 300) # 设置窗口位置
    window.show()
    sys.exit(app.exec_())

## 运行上述代码，PyQt5 将在屏幕上显示一个窗口，标题为“PyQt5 Test”。