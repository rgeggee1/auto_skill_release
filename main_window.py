"""
主窗口界面 - 精美布局版 v3.4 (修复搜索功能)
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGroupBox, QLabel, QComboBox, QPushButton, QSpinBox,
    QLineEdit, QMessageBox, QDoubleSpinBox, QCheckBox,
    QListWidget, QListWidgetItem, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from core.window_manager import WindowManager
from core.skill_executor import SkillExecutor
from utils.config import ConfigManager
from utils.hotkey import HotkeyManager
from gui.area_selector import PointRecorder, PointsPreview


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.window_manager = WindowManager()
        self.config_manager = ConfigManager()
        self.skill_executor = None
        self. hotkey_manager = None
        self.selected_window_handle = None
        self.skill_points = []
        self.preview = None
        
        self.init_ui()
        self.load_config()
        self.setup_hotkeys()
        self.setup_status_timer()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("🎮 技能自动释放工具 v3.4")
        self.setFixedSize(500, 680)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        main_layout.addWidget(self. create_window_group())
        main_layout.addWidget(self.create_points_group())
        main_layout.addWidget(self.create_settings_group())
        main_layout.addWidget(self. create_control_group())
        main_layout.addWidget(self. create_status_group())
        
    def create_window_group(self):
        """窗口选择组"""
        group = QGroupBox("🎯 目标窗口")
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(10, 15, 10, 10)
        
        # 第一行：窗口下拉 + 刷新 + 扩展
        row1 = QHBoxLayout()
        row1.setSpacing(6)
        
        self.window_combo = QComboBox()
        self.window_combo.setFixedHeight(28)
        self.window_combo.currentIndexChanged.connect(self.on_window_selected)
        row1.addWidget(self.window_combo, 1)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(32, 28)
        refresh_btn.setToolTip("刷新窗口列表")
        refresh_btn. clicked.connect(self.refresh_windows)
        row1.addWidget(refresh_btn)
        
        extend_btn = QPushButton("🔍")
        extend_btn.setFixedSize(32, 28)
        extend_btn.setStyleSheet("background-color: #6a1b9a;")
        extend_btn.setToolTip("扩展搜索 (显示更多窗口)")
        extend_btn.clicked.connect(self.refresh_windows_extended)
        row1.addWidget(extend_btn)
        
        layout.addLayout(row1)
        
        # 第二行：关键字搜索
        row2 = QHBoxLayout()
        row2.setSpacing(6)
        
        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(28)
        self.search_input.setPlaceholderText("输入窗口标题关键字搜索...")
        self.search_input.returnPressed.connect(self.search_by_title)
        row2.addWidget(self.search_input, 1)
        
        search_btn = QPushButton("搜索")
        search_btn.setFixedSize(50, 28)
        search_btn.clicked.connect(self.search_by_title)
        row2.addWidget(search_btn)
        
        layout.addLayout(row2)
        
        # 窗口信息
        self.window_info_label = QLabel("请选择游戏窗口")
        self.window_info_label. setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.window_info_label)
        
        group.setLayout(layout)
        self.refresh_windows()
        return group
    
    def create_points_group(self):
        """坐标点组"""
        group = QGroupBox("📍 技能释放坐标")
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(10, 15, 10, 10)
        
        # 按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        record_btn = QPushButton("🎯 记录坐标")
        record_btn.setFixedHeight(32)
        record_btn.setStyleSheet("background-color: #1976d2; font-weight: bold;")
        record_btn.clicked.connect(self.record_points)
        btn_row.addWidget(record_btn, 1)
        
        preview_btn = QPushButton("预览")
        preview_btn.setFixedSize(50, 32)
        preview_btn.clicked.connect(self.preview_points)
        btn_row.addWidget(preview_btn)
        
        clear_btn = QPushButton("清除")
        clear_btn.setFixedSize(50, 32)
        clear_btn.setStyleSheet("background-color: #c62828;")
        clear_btn.clicked.connect(self.clear_points)
        btn_row.addWidget(clear_btn)
        
        layout.addLayout(btn_row)
        
        # 坐标列表
        self.points_list = QListWidget()
        self.points_list.setFixedHeight(68)
        self.points_list.setStyleSheet("""
            QListWidget {
                background-color: #383838;
                border: 1px solid #505050;
                border-radius:  4px;
                font-size: 11px;
            }
            QListWidget::item { padding: 3px 8px; }
            QListWidget::item:selected { background-color: #1976d2; }
        """)
        layout.addWidget(self.points_list)
        
        # 底部信息行
        info_row = QHBoxLayout()
        
        self.points_info_label = QLabel("已记录:  0 个点")
        self.points_info_label.setStyleSheet("color: #81c784; font-size: 11px;")
        info_row.addWidget(self.points_info_label)
        
        info_row.addStretch()
        
        del_btn = QPushButton("删除选中")
        del_btn.setFixedHeight(24)
        del_btn.clicked.connect(self.delete_selected_point)
        info_row.addWidget(del_btn)
        
        layout.addLayout(info_row)
        
        group.setLayout(layout)
        return group
    
    def create_settings_group(self):
        """设置组"""
        group = QGroupBox("⚙️ 设置")
        layout = QGridLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 15, 10, 10)
        
        # 第一行：技能按键 + 释放间隔
        layout. addWidget(QLabel("技能按键: "), 0, 0)
        self.skill_key = QLineEdit("q")
        self.skill_key.setFixedSize(50, 26)
        self.skill_key.setAlignment(Qt.AlignCenter)
        self.skill_key.setMaxLength(10)
        layout.addWidget(self.skill_key, 0, 1)
        
        layout.addWidget(QLabel("释放间隔:"), 0, 2)
        self.skill_interval = QSpinBox()
        self.skill_interval.setRange(10, 10000)
        self.skill_interval.setValue(100)
        self.skill_interval.setSuffix(" ms")
        self.skill_interval.setFixedSize(90, 26)
        layout.addWidget(self.skill_interval, 0, 3)
        
        # 第二行：轮次间隔 + 防误触
        layout.addWidget(QLabel("轮次间隔:"), 1, 0)
        self.round_interval = QDoubleSpinBox()
        self.round_interval. setRange(0, 300)
        self.round_interval.setValue(5.0)
        self.round_interval.setSingleStep(0.5)
        self.round_interval.setDecimals(1)
        self.round_interval.setSuffix(" 秒")
        self.round_interval.setFixedSize(80, 26)
        layout.addWidget(self.round_interval, 1, 1)
        
        self.anti_touch_check = QCheckBox("🛡️ 防误触")
        self.anti_touch_check.setChecked(True)
        self.anti_touch_check.setStyleSheet("color: #81c784;")
        self.anti_touch_check.setToolTip("检测到鼠标手动移动时自动暂停")
        layout.addWidget(self.anti_touch_check, 1, 2, 1, 2)
        
        group.setLayout(layout)
        return group
    
    def create_control_group(self):
        """控制按钮组"""
        group = QGroupBox("🎛️ 控制")
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(10, 15, 10, 10)
        
        self.start_btn = QPushButton("▶  开始")
        self.start_btn.setFixedHeight(42)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #388e3c; }
            QPushButton:disabled { background-color: #555; color: #888; }
        """)
        self.start_btn.clicked. connect(self.start_execution)
        layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸  暂停")
        self.pause_btn.setFixedHeight(42)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #f57c00;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton: hover { background-color: #fb8c00; }
            QPushButton:disabled { background-color: #555; color: #888; }
        """)
        self.pause_btn.clicked.connect(self.pause_execution)
        layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹  停止")
        self.stop_btn. setFixedHeight(42)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #c62828;
                font-size:  14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #d32f2f; }
            QPushButton:disabled { background-color: #555; color: #888; }
        """)
        self.stop_btn.clicked.connect(self.stop_execution)
        layout.addWidget(self.stop_btn)
        
        group.setLayout(layout)
        return group
    
    def create_status_group(self):
        """状态显示组"""
        group = QGroupBox("📊 状态")
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(10, 15, 10, 10)
        
        # 状态行
        status_row = QHBoxLayout()
        
        self.status_label = QLabel("● 已停止")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #f44336;")
        status_row.addWidget(self.status_label)
        
        status_row.addStretch()
        
        self.round_wait_label = QLabel("")
        self.round_wait_label.setStyleSheet("color: #ffb74d; font-size: 12px;")
        status_row.addWidget(self.round_wait_label)
        
        layout.addLayout(status_row)
        
        # 数据行
        data_row = QHBoxLayout()
        data_row.setSpacing(20)
        
        self.round_label = QLabel("轮次: 0")
        self.round_label.setStyleSheet("color: #4fc3f7;")
        data_row.addWidget(self.round_label)
        
        self.point_label = QLabel("点:  0/0")
        self.point_label.setStyleSheet("color: #81c784;")
        data_row.addWidget(self.point_label)
        
        self.exec_count_label = QLabel("执行:  0")
        data_row.addWidget(self. exec_count_label)
        
        self.runtime_label = QLabel("时间: 00:00:00")
        data_row.addWidget(self. runtime_label)
        
        data_row.addStretch()
        layout.addLayout(data_row)
        
        # 提示
        self.anti_touch_status = QLabel("")
        self.anti_touch_status.setStyleSheet("color: #ff9800; font-size: 11px;")
        self.anti_touch_status.setWordWrap(True)
        layout.addWidget(self.anti_touch_status)
        
        # 热键提示
        hotkey_hint = QLabel("热键: F6 开始/暂停  |  F7 停止  |  ESC 紧急停止")
        hotkey_hint.setStyleSheet("color: #666; font-size: 10px;")
        hotkey_hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hotkey_hint)
        
        group.setLayout(layout)
        return group

    # ==================== 窗口操作 ====================
    
    def on_window_selected(self, index):
        if index < 0:
            return
        handle = self.window_combo.currentData()
        if handle:
            self.selected_window_handle = handle
            rect = self.window_manager.get_window_rect(handle)
            if rect:
                x, y, w, h = rect
                pid = self.window_manager._get_window_pid(handle)
                process = self.window_manager._get_process_name(pid) or "Unknown"
                self.window_info_label.setText(
                    f"✅ 位置: ({x},{y}) 尺寸:{w}×{h} 进程:{process}"
                )
                self.window_info_label.setStyleSheet("color: #4caf50; font-size: 11px;")
        else:
            self.selected_window_handle = None
            self.window_info_label. setText("请选择游戏窗口")
            self.window_info_label.setStyleSheet("color: #888; font-size: 11px;")
    
    def refresh_windows(self):
        """刷新窗口列表"""
        self.window_combo.clear()
        windows = self.window_manager.get_all_windows()
        for handle, title, _ in windows:
            if title. strip():
                self.window_combo.addItem(title, handle)
        if self.window_combo.count() == 0:
            self.window_combo.addItem("未找到窗口 - 请尝试扩展搜索", None)
    
    def refresh_windows_extended(self):
        """扩展搜索"""
        self.window_combo. clear()
        windows = self. window_manager.get_all_windows_extended()
        for win in windows:
            display = f"{win['display']} ({win['size'][0]}x{win['size'][1]})"
            self.window_combo. addItem(display, win['handle'])
        if self.window_combo.count() == 0:
            self.window_combo. addItem("未找到窗口", None)
        else:
            self.window_info_label.setText(f"🔍 扩展搜索:  找到 {len(windows)} 个窗口")
            self.window_info_label. setStyleSheet("color: #9c27b0; font-size: 11px;")
    
    def search_by_title(self):
        """按标题搜索窗口"""
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入搜索关键字！")
            return
        
        handle = self.window_manager.find_window_by_title(keyword, partial=True)
        if handle:
            title = self.window_manager._get_window_title(handle) or keyword
            
            # 检查是否已在列表中
            found_index = -1
            for i in range(self.window_combo. count()):
                if self. window_combo.itemData(i) == handle:
                    found_index = i
                    break
            
            if found_index >= 0:
                self.window_combo.setCurrentIndex(found_index)
            else:
                self.window_combo.insertItem(0, f"🎯 {title}", handle)
                self.window_combo.setCurrentIndex(0)
            
            self.window_info_label.setText(f"✅ 找到窗口: {title}")
            self.window_info_label. setStyleSheet("color: #4caf50; font-size:  11px;")
        else:
            QMessageBox.warning(
                self, "提示", 
                f"未找到包含 \"{keyword}\" 的窗口！\n\n"
                "请尝试:\n"
                "1. 确保游戏已启动\n"
                "2. 点击扩展搜索按钮🔍"
            )

    # ==================== 坐标点操作 ====================
    
    def record_points(self):
        if not self.selected_window_handle:
            QMessageBox.warning(self, "提示", "请先选择目标窗口！")
            return
        rect = self.window_manager.get_window_rect(self.selected_window_handle)
        if not rect:
            QMessageBox.warning(self, "提示", "无法获取窗口位置！")
            return
        
        self.hide()
        try:
            recorder = PointRecorder(rect, self.skill_points)
            if recorder.exec_():
                points = recorder.get_points()
                if points:
                    self.skill_points = points
                    self.update_points_display()
        finally:
            self.show()
    
    def update_points_display(self):
        self.points_list.clear()
        if self.skill_points:
            self.points_info_label.setText(f"已记录: {len(self. skill_points)} 个点")
            self.points_info_label.setStyleSheet("color: #81c784; font-size: 11px;")
            for i, pt in enumerate(self.skill_points):
                self.points_list.addItem(f" {i+1}. ({int(pt[0])}, {int(pt[1])})")
        else:
            self.points_info_label.setText("已记录: 0 个点")
            self.points_info_label.setStyleSheet("color: #f44336; font-size: 11px;")
    
    def delete_selected_point(self):
        row = self.points_list.currentRow()
        if 0 <= row < len(self.skill_points):
            self.skill_points.pop(row)
            self.update_points_display()
    
    def clear_points(self):
        if self.skill_points:
            if QMessageBox.question(self, "确认", "清除所有坐标点？") == QMessageBox.Yes:
                self.skill_points = []
                self.update_points_display()
    
    def preview_points(self):
        if not self.skill_points:
            QMessageBox.warning(self, "提示", "没有坐标点！")
            return
        if not self.selected_window_handle:
            QMessageBox.warning(self, "提示", "请先选择窗口！")
            return
        rect = self.window_manager.get_window_rect(self.selected_window_handle)
        if rect:
            self.preview = PointsPreview(self.skill_points, (rect[0], rect[1]))
            self.preview.show()
            QTimer.singleShot(3000, self.preview.close)

    # ==================== 执行控制 ====================
    
    def start_execution(self):
        if not self.selected_window_handle:
            QMessageBox.warning(self, "提示", "请先选择目标窗口！")
            return
        if not self.window_manager.is_window_valid(self.selected_window_handle):
            QMessageBox.warning(self, "提示", "窗口已关闭！")
            self.refresh_windows()
            return
        if not self.skill_points:
            QMessageBox.warning(self, "提示", "请先记录坐标点！")
            return
        
        config = {
            'window_handle': self.selected_window_handle,
            'points': self.skill_points,
            'skill_key': self.skill_key.text(),
            'interval': self.skill_interval.value(),
            'round_interval': self.round_interval.value(),
            'anti_touch': self.anti_touch_check.isChecked()
        }
        
        self.skill_executor = SkillExecutor(config, self.window_manager)
        self.skill_executor.status_updated.connect(self.update_status)
        self.skill_executor.round_updated.connect(self.update_round_status)
        self.skill_executor.mouse_moved_detected.connect(self.on_mouse_moved)
        self.skill_executor.error_occurred.connect(self.on_error)
        self.skill_executor.start()
        
        self.start_btn.setEnabled(False)
        self.pause_btn. setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("● 运行中")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4caf50;")
        self.anti_touch_status.setText("")
        self.save_config()
    
    def pause_execution(self):
        if self.skill_executor: 
            if self.skill_executor.is_paused: 
                self.skill_executor. resume()
                self.pause_btn.setText("⏸  暂停")
                self.status_label.setText("● 运行中")
                self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4caf50;")
                self.anti_touch_status. setText("")
            else:
                self. skill_executor.pause()
                self.pause_btn.setText("▶  继续")
                self.status_label.setText("● 已暂停")
                self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ff9800;")
    
    def stop_execution(self):
        if self.skill_executor:
            self.skill_executor.stop()
            self.skill_executor = None
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸  暂停")
        self.stop_btn.setEnabled(False)
        self.status_label.setText("● 已停止")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color:  #f44336;")
        self.round_wait_label.setText("")
        self.anti_touch_status.setText("")
    
    def on_mouse_moved(self):
        self.pause_btn.setText("▶  继续")
        self.status_label.setText("● 已暂停")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ff9800;")
        self.anti_touch_status. setText("🛡️ 检测到鼠标移动，已暂停。按 F6 或点击继续")
    
    def update_status(self, count, pos, runtime, point_idx):
        self.exec_count_label.setText(f"执行: {count}")
        self.point_label.setText(f"点: {point_idx}/{len(self.skill_points)}")
        h, m, s = int(runtime//3600), int(runtime%3600//60), int(runtime%60)
        self.runtime_label.setText(f"时间:  {h:02d}:{m:02d}:{s:02d}")
    
    def update_round_status(self, round_num, progress, waiting, remain):
        self.round_label.setText(f"轮次: {round_num}")
        if waiting:
            self.round_wait_label.setText(f"⏳ 等待: {remain:.1f}s")
            self.status_label.setText("● 等待中")
            self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffb74d;")
        else:
            self.round_wait_label.setText("")
            if self.skill_executor and not self.skill_executor.is_paused:
                self.status_label.setText("● 运行中")
                self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4caf50;")
    
    def on_error(self, msg):
        self.stop_execution()
        QMessageBox.critical(self, "错误", msg)

    # ==================== 热键 ====================
    
    def setup_hotkeys(self):
        self.hotkey_manager = HotkeyManager()
        self.hotkey_manager.register_hotkey('F6', self.toggle_execution)
        self.hotkey_manager.register_hotkey('F7', self.stop_execution)
        self.hotkey_manager.register_hotkey('Escape', self.stop_execution)
        self.hotkey_manager.start()
    
    def toggle_execution(self):
        if self.skill_executor and self.skill_executor.isRunning():
            self.pause_execution()
        else:
            self.start_execution()
    
    def setup_status_timer(self):
        self.status_timer = QTimer()
        self.status_timer.timeout. connect(self.check_window)
        self.status_timer. start(1000)
    
    def check_window(self):
        if self.selected_window_handle:
            if not self.window_manager.is_window_valid(self.selected_window_handle):
                if self.skill_executor and self.skill_executor.isRunning():
                    self. stop_execution()
                    QMessageBox.warning(self, "警告", "窗口已关闭！")

    # ==================== 配置 ====================
    
    def save_config(self):
        self.config_manager.save({
            'skill_points': self.skill_points,
            'skill_key': self.skill_key.text(),
            'interval':  self.skill_interval.value(),
            'round_interval': self.round_interval.value(),
            'anti_touch': self. anti_touch_check.isChecked()
        })
    
    def load_config(self):
        config = self.config_manager.load()
        if config:
            self.skill_points = config. get('skill_points', [])
            self.skill_key. setText(config.get('skill_key', 'q'))
            self.skill_interval.setValue(config.get('interval', 100))
            self.round_interval.setValue(config.get('round_interval', 5.0))
            self.anti_touch_check.setChecked(config.get('anti_touch', True))
            self.update_points_display()
    
    def closeEvent(self, event):
        self.stop_execution()
        if self.hotkey_manager:
            self. hotkey_manager.stop()
        self.save_config()
        event.accept()