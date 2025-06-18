import sys
import os
import random

from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QIcon, QPalette, QColor, QKeySequence
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QFileDialog, QListWidget,
    QStatusBar, QStyle, QMessageBox
)
from PyQt5.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaPlaylist, QMediaContent


class MusicPlayer(QMainWindow):
    def __init__(self):
        """初始化音乐播放器"""
        super().__init__()

        # 初始化播放状态相关变量
        self.playlist_current_index = 0
        self.fullscreen = False
        self.normal_geometry = None
        self.play_mode = "顺序播放"  # 可选: 顺序播放, 单曲循环, 随机播放
        self.play_history = []
        self.user_seek_position = None  # 用于标记是否是用户手动跳转
        self.is_media_buffered = False  # 是否已完成缓冲
        self.pending_seek_position = None  # 待处理的跳转位置

        # 新增用于手动拖拽进度条跳转的防抖定时器
        self.pending_seek_timer = QTimer(self)
        self.pending_seek_timer.setSingleShot(True)
        self.pending_seek_timer.timeout.connect(self.execute_pending_seek)

        # 新增用于快捷键跳转的防抖定时器
        self.shortcut_seek_timer = QTimer(self)
        self.shortcut_seek_timer.setSingleShot(True)
        self.shortcut_seek_timer.timeout.connect(self.perform_shortcut_seeking)
        self.pending_seek_seconds = 0  # 可选：记录待处理的跳转秒数

        # 设置窗口属性
        self.setWindowTitle("Qt5 音乐播放器")
        self.setGeometry(100, 100, 600, 400)

        # 创建媒体播放器并设置最佳参数
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.media_player.setVolume(80)  # 设置初始音量

        # 媒体状态监听
        self.media_player.stateChanged.connect(self.check_media_end)

        # 创建中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 控制面板 - 水平布局
        control_layout = QHBoxLayout()

        # 播放控制按钮
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.clicked.connect(self.play_media)

        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_btn.clicked.connect(self.stop_media)

        # 测试跳转前进/后退 30秒按钮
        test_seek_btn = QPushButton("测试跳转前进30s")
        test_seek_btn.clicked.connect(lambda: self.seek_position(30))  # 跳转30秒
        main_layout.addWidget(test_seek_btn)
        test_seek_back_btn = QPushButton("测试跳转后退30s")
        test_seek_back_btn.clicked.connect(lambda: self.seek_position(-30))  # 跳转-30秒
        main_layout.addWidget(test_seek_back_btn)

        # 音量控制滑块
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)  # 音量范围0-100
        self.volume_slider.setValue(80)       # 默认音量80
        self.volume_slider.setMaximumWidth(120)
        self.volume_slider.valueChanged.connect(self.set_volume)

        # 进度条
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 100)  # 进度条范围0-100%
        self.position_slider.sliderMoved.connect(self.on_slider_moved)
        self.position_slider.sliderReleased.connect(self.on_slider_released)

        # 时间标签
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setMinimumWidth(100)

        # 播放模式按钮
        self.play_mode_btn = QPushButton("顺序播放")
        self.play_mode_btn.clicked.connect(self.change_play_mode)

        # 添加控件到控制面板
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(QLabel("音量:"))
        control_layout.addWidget(self.volume_slider)
        control_layout.addWidget(self.play_mode_btn)
        control_layout.addStretch()
        control_layout.addWidget(self.time_label)

        # 文件操作布局
        file_layout = QHBoxLayout()

        open_btn = QPushButton("打开文件")
        open_btn.clicked.connect(self.open_file)

        open_dir_btn = QPushButton("打开文件夹")
        open_dir_btn.clicked.connect(self.open_directory)

        file_layout.addWidget(open_btn)
        file_layout.addWidget(open_dir_btn)
        file_layout.addStretch()  # 弹性空间

        # 播放列表
        self.playlist = QListWidget()
        self.playlist.itemDoubleClicked.connect(self.play_selected)

        # 添加所有组件到主布局
        main_layout.addLayout(file_layout)
        main_layout.addWidget(self.playlist)
        main_layout.addWidget(self.position_slider)
        main_layout.addLayout(control_layout)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 连接媒体播放器信号
        self.media_player.stateChanged.connect(self.media_state_changed)  # 播放状态变化
        self.media_player.positionChanged.connect(self.position_changed)   # 位置变化
        self.media_player.durationChanged.connect(self.duration_changed)  # 总时长变化
        self.media_player.error.connect(self.handle_error)               # 错误处理

        # 设置初始音量
        self.volume_slider.setValue(80)
        self.set_volume(80)

        # 创建定时器用于更新进度
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # 每秒更新一次
        self.timer.timeout.connect(self.update_slider_position)

        # 添加快捷键
        self.add_shortcuts()

        # 初始化播放列表
        self.playlist.setCurrentRow(0)

    def add_shortcuts(self):
        """添加全局快捷键"""
        # 播放/暂停: 空格
        QShortcut(QKeySequence(Qt.Key_Space), self, self.play_media)

        # 停止: S
        QShortcut(QKeySequence(Qt.Key_S), self, self.stop_media)

        # 音量增加: Up
        QShortcut(QKeySequence(Qt.Key_Up), self, lambda: self.change_volume(5))

        # 音量减少: Down
        QShortcut(QKeySequence(Qt.Key_Down), self, lambda: self.change_volume(-5))

        # 快进: Right
        QShortcut(QKeySequence(Qt.Key_Right), self, lambda: self.prepare_shortcut_seek(10))

        # 快退: Left
        QShortcut(QKeySequence(Qt.Key_Left), self, lambda: self.prepare_shortcut_seek(-10))

    def prepare_shortcut_seek(self, seconds):
        """准备快捷键触发的跳转（带防抖）"""
        self.pending_seek_seconds = seconds
        self.shortcut_seek_timer.start(150)  # 150ms 防抖

    def perform_shortcut_seeking(self):
        """实际执行快捷键触发的跳转"""
        if self.media_player.isMetaDataAvailable():
            try:
                new_pos = max(0, min(
                    self.media_player.duration(),
                    self.media_player.position() + self.pending_seek_seconds * 1000
                ))
                self.media_player.setPosition(new_pos)
            except Exception as e:
                print(f"快捷键跳转失败: {e}")
                self.status_bar.showMessage("快捷键跳转失败，请重试", 5000)

    def change_play_mode(self):
        """改变播放模式"""
        modes = ["顺序播放", "单曲循环", "随机播放"]
        current_index = modes.index(self.play_mode)
        self.play_mode = modes[(current_index + 1) % len(modes)]
        self.play_mode_btn.setText(self.play_mode)

    def check_media_end(self, state):
        """检查媒体播放状态，实现播放列表循环"""
        if state == QMediaPlayer.StoppedState and self.media_player.position() >= self.media_player.duration():
            self.play_next_file()

    def play_next_file(self):
        """播放下一个文件"""
        if self.playlist.count() > 0:
            if self.play_mode == "顺序播放":
                self.playlist_current_index = (self.playlist_current_index + 1) % self.playlist.count()
            elif self.play_mode == "单曲循环":
                pass  # 保持当前索引不变
            elif self.play_mode == "随机播放":
                self.playlist_current_index = random.randint(0, self.playlist.count() - 1)

            item = self.playlist.item(self.playlist_current_index)
            self.play_media_file(item.text())

    def set_volume(self, volume):
        """设置音量"""
        self.media_player.setVolume(volume)

    def seek_position(self, seconds):
        """跳转指定秒数"""
        if self.media_player.mediaStatus() == QMediaPlayer.NoMedia:
            self.status_bar.showMessage("音频尚未加载完成，请稍等...", 3000)
            return

        if self.media_player.duration() > 0:
            new_pos = max(0, min(
                self.media_player.duration(),
                self.media_player.position() + seconds * 1000
            ))
            self.media_player.setPosition(new_pos)
            self.status_bar.showMessage(f"跳转到 {seconds} 秒", 1000)

    def open_file(self):
        """打开单个音频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开音频文件", "",
            "音频文件 (*.mp3 *.wav *.ogg);;所有文件 (*)"
        )

        if file_path:
            self.play_media_file(file_path)
            self.add_to_playlist(file_path)

    def open_directory(self):
        """打开包含音频文件的目录"""
        directory = QFileDialog.getExistingDirectory(self, "选择音频文件夹")

        if directory:
            self.playlist.clear()
            audio_files = []

            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                        audio_files.append(os.path.join(root, file))

            audio_files.sort()
            self.playlist.addItems(audio_files)

            if audio_files:
                self.play_media_file(audio_files[0])

    def add_to_playlist(self, file_path):
        """将文件添加到播放列表（避免重复）"""
        if not self.playlist.findItems(file_path, Qt.MatchExactly):
            self.playlist.addItem(file_path)

    def play_selected(self, item):
        """播放选中的文件"""
        file_path = item.text()
        self.play_media_file(file_path)

    def play_media_file(self, file_path):
        """播放指定音频文件"""
        self.is_media_buffered = False
        self.pending_seek_position = None
        self.status_bar.showMessage("正在加载音频...", 10000)

        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        self.media_player.play()

        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.status_bar.showMessage(f"正在播放: {os.path.basename(file_path)}")
        self.play_history.append(file_path)

    def play_media(self):
        """切换播放/暂停状态"""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def stop_media(self):
        """停止播放"""
        self.media_player.stop()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def update_slider_position(self):
        """更新进度条和时间标签"""
        if self.media_player.duration() > 0:
            position = self.media_player.position()
            duration = self.media_player.duration()

            slider_value = int(position * 100 / duration + 0.5)  # 四舍五入
            self.position_slider.setValue(slider_value)

            current_time = self.format_time(position)
            total_time = self.format_time(duration)
            self.time_label.setText(f"{current_time} / {total_time}")

    def on_slider_moved(self, value):
        """用户正在拖动进度条"""
        self.user_seek_position = value
        self.timer.stop()

        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.was_playing_before_seek = True
            self.media_player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        if self.media_player.duration() > 0:
            duration = self.media_player.duration()
            preview_time = (value * duration) // 100
            current_time = self.format_time(preview_time)
            total_time = self.format_time(duration)
            self.time_label.setText(f"{current_time} / {total_time}")

    def execute_pending_seek(self):
        if self.user_seek_position is None:
            return

        if self.media_player.duration() <= 0:
            self.user_seek_position = None
            return

        duration = self.media_player.duration()
        new_pos = self.user_seek_position * duration // 100
        self.media_player.setPosition(new_pos)

        slider_value = int(new_pos * 100 / duration + 0.5)
        self.position_slider.setValue(slider_value)

        current_time = self.format_time(new_pos)
        total_time = self.format_time(duration)

        # 检查是否需要恢复播放
        if getattr(self, "was_playing_before_seek", False):
            self.media_player.play()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.timer.start()
            self.was_playing_before_seek = False  # 清除标志

        # 清除用户跳转标志
        self.user_seek_position = None

    def on_slider_released(self):
        """进度条释放后执行跳转"""
        if self.user_seek_position is not None:
            self.pending_seek_timer.start(200)  # 防抖处理

    def format_time(self, milliseconds):
        """格式化时间显示为 MM:SS"""
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02d}:{seconds:02d}"

    def media_state_changed(self, state):
        """播放状态变化时更新UI定时器"""
        if state == QMediaPlayer.PlayingState:
            self.timer.start()
        else:
            self.timer.stop()

    def position_changed(self, position):
        """播放位置变化"""
        self.update_slider_position()

    def duration_changed(self, duration):
        """媒体总时长变化"""
        if duration > 0:
            self.position_slider.setRange(0, 100)

    def handle_error(self, error):
        """处理播放错误"""
        error_string = self.media_player.errorString()

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("播放错误")
        msg.setText(f"无法播放此音频文件：\n{error_string}")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.status_bar.showMessage(f"播放错误: {error_string}", 5000)

    def check_audio_devices(self):
        """检查音频输出设备（Qt5 中可选）"""
        pass  # Qt5 的 QAudioOutput 不像 Qt6 提供那么多控制接口

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置深色主题
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(palette)
    app.setStyle("Fusion")

    player = MusicPlayer()
    player.show()

    sys.exit(app.exec_())
