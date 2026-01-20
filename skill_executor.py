"""
技能执行引擎 - 修复窗口焦点问题
"""
import time
import ctypes
from ctypes import wintypes
from PyQt5.QtCore import QThread, pyqtSignal


# Windows API
user32 = ctypes.windll.user32

# 鼠标事件常量
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000

# 键盘事件常量
KEYEVENTF_KEYUP = 0x0002

# 鼠标位置结构
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

# 虚拟键码映射
VK_CODE = {
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
    'f': 0x46, 'g': 0x47, 'h':  0x48, 'i':  0x49, 'j': 0x4A,
    'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
    'p': 0x50, 'q': 0x51, 'r':  0x52, 's':  0x53, 't':  0x54,
    'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59,
    'z':  0x5A,
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    'f1':  0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5':  0x74,
    'f6': 0x75, 'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79,
    'f11': 0x7A, 'f12': 0x7B,
    'space': 0x20, 'enter': 0x0D, 'tab': 0x09, 'shift':  0x10,
    'ctrl': 0x11, 'alt': 0x12, 'esc': 0x1B,
}


class SkillExecutor(QThread):
    """技能执行器"""
    
    # 信号
    status_updated = pyqtSignal(int, tuple, float, int)
    round_updated = pyqtSignal(int, float, bool, float)
    mouse_moved_detected = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config, window_manager):
        super().__init__()
        self.config = config
        self. window_manager = window_manager
        
        self.running = False
        self.is_paused = False
        self. exec_count = 0
        self.current_pos = (0, 0)
        self.start_time = 0
        
        # 坐标点列表
        self.points = config.get('points', [])
        self.points_count = len(self.points)
        
        # 轮次相关
        self.current_round = 0
        self.round_interval = config.get('round_interval', 5.0)
        self.current_point_index = 0
        
        # 防误触
        self.anti_touch = config.get('anti_touch', True)
        self.last_mouse_pos = None
        self.expected_mouse_pos = None
    
    def run(self):
        """执行主循环"""
        if not self.points:
            self.error_occurred.emit("没有设置坐标点！")
            return
        
        self.running = True
        self. exec_count = 0
        self.current_round = 1
        self.current_point_index = 0
        self. start_time = time.time()
        
        # 初始化鼠标位置
        self.last_mouse_pos = self._get_cursor_pos()
        
        try: 
            while self.running:
                # 暂停检查
                if self.is_paused:
                    self.last_mouse_pos = self._get_cursor_pos()
                    time.sleep(0.1)
                    continue
                
                # 防误触检测
                if self.anti_touch and self._check_mouse_manually_moved():
                    self.is_paused = True
                    self.mouse_moved_detected.emit()
                    continue
                
                # 检查窗口有效性
                if not self. window_manager.is_window_valid(self.config['window_handle']):
                    self. error_occurred.emit("目标窗口已关闭！")
                    break
                
                # 获取窗口位置
                rect = self. window_manager.get_window_rect(self.config['window_handle'])
                if not rect: 
                    self.error_occurred. emit("无法获取窗口位置！")
                    break
                
                win_x, win_y, _, _ = rect
                
                # 获取当前坐标点
                point = self.points[self.current_point_index]
                rel_x, rel_y = int(point[0]), int(point[1])
                
                # 转换为屏幕坐标
                screen_x = win_x + rel_x
                screen_y = win_y + rel_y
                
                self.current_pos = (rel_x, rel_y)
                
                # ★ 关键：先激活游戏窗口
                self._activate_window(self.config['window_handle'])
                time.sleep(0.01)
                
                # 移动鼠标
                self._move_mouse(screen_x, screen_y)
                self.expected_mouse_pos = (screen_x, screen_y)
                time.sleep(0.02)
                
                # 释放技能
                self._press_key(self.config['skill_key'])
                
                # 更新鼠标位置记录
                self. last_mouse_pos = self._get_cursor_pos()
                
                self.exec_count += 1
                
                # 计算进度
                progress = ((self.current_point_index + 1) / self.points_count) * 100
                
                # 发送状态更新
                runtime = time. time() - self.start_time
                self.status_updated. emit(
                    self.exec_count, 
                    self.current_pos, 
                    runtime,
                    self. current_point_index + 1
                )
                self.round_updated.emit(self.current_round, progress, False, 0)
                
                # 移动到下一个点
                self.current_point_index += 1
                
                # 检查是否完成一轮
                if self.current_point_index >= self.points_count:
                    self._wait_between_rounds()
                    self. current_round += 1
                    self.current_point_index = 0
                
                # 等待间隔
                time.sleep(self.config['interval'] / 1000.0)
                
        except Exception as e: 
            self.error_occurred. emit(f"执行错误: {str(e)}")
        finally:
            self.running = False
    
    def _activate_window(self, hwnd):
        """激活窗口，使其获得焦点"""
        # 检查窗口是否已经是前台窗口
        if user32.GetForegroundWindow() == hwnd:
            return
        
        # 如果窗口最小化，先恢复
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        
        # 激活窗口
        user32.SetForegroundWindow(hwnd)
    
    def _get_cursor_pos(self):
        """获取当前鼠标位置"""
        point = POINT()
        user32.GetCursorPos(ctypes. byref(point))
        return (point.x, point.y)
    
    def _check_mouse_manually_moved(self):
        """检测鼠标是否被手动移动"""
        if self.last_mouse_pos is None: 
            return False
        
        current_pos = self._get_cursor_pos()
        
        # 如果是程序刚移动完鼠标，跳过检测
        if self.expected_mouse_pos:
            expected_x, expected_y = self.expected_mouse_pos
            if (abs(current_pos[0] - expected_x) <= 5 and 
                abs(current_pos[1] - expected_y) <= 5):
                return False
        
        # 计算移动距离
        dx = abs(current_pos[0] - self.last_mouse_pos[0])
        dy = abs(current_pos[1] - self.last_mouse_pos[1])
        distance = (dx * dx + dy * dy) ** 0.5
        
        return distance > 15
    
    def _wait_between_rounds(self):
        """轮次之间等待"""
        if self.round_interval <= 0:
            return
        
        wait_start = time.time()
        wait_duration = self. round_interval
        
        while self.running and not self.is_paused:
            elapsed = time.time() - wait_start
            remaining = wait_duration - elapsed
            
            if remaining <= 0:
                break
            
            self.round_updated. emit(self.current_round, 100, True, remaining)
            time.sleep(0.1)
            
            while self. is_paused and self.running:
                self.last_mouse_pos = self._get_cursor_pos()
                time.sleep(0.1)
        
        self.last_mouse_pos = self._get_cursor_pos()
    
    def _move_mouse(self, x, y):
        """移动鼠标到指定位置"""
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        abs_x = int(x * 65535 / screen_width)
        abs_y = int(y * 65535 / screen_height)
        
        user32.mouse_event(
            MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
            abs_x, abs_y, 0, 0
        )
    
    def _press_key(self, key):
        """按下并释放键"""
        key = key.lower()
        
        if key in VK_CODE:
            vk = VK_CODE[key]
        else:
            vk = ord(key. upper()) if len(key) == 1 else None
        
        if vk:
            user32.keybd_event(vk, 0, 0, 0)
            time.sleep(0.01)
            user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
    
    def pause(self):
        """暂停执行"""
        self. is_paused = True
    
    def resume(self):
        """继续执行"""
        self.last_mouse_pos = self._get_cursor_pos()
        self.expected_mouse_pos = None
        self. is_paused = False
    
    def stop(self):
        """停止执行"""
        self.running = False
        self.wait()