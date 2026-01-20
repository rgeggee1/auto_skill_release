"""
窗口管理模块 - 增强版
"""
import ctypes
from ctypes import wintypes

# Windows API
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
dwmapi = ctypes.windll.dwmapi

# 常量
GWL_EXSTYLE = -20
GWL_STYLE = -16
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000
WS_VISIBLE = 0x10000000
WS_CAPTION = 0x00C00000
GW_OWNER = 4
DWMWA_CLOAKED = 14


class WindowManager:
    """窗口管理器 - 增强版"""
    
    def __init__(self):
        self.enum_windows_proc = ctypes.WINFUNCTYPE(
            wintypes.BOOL,
            wintypes. HWND,
            wintypes.LPARAM
        )
    
    def get_all_windows(self, include_all=False):
        """
        获取所有窗口
        : param include_all: 是否包含所有窗口（包括无标题的）
        """
        windows = []
        
        def enum_callback(hwnd, lparam):
            # 基本可见性检查
            if not user32.IsWindowVisible(hwnd):
                return True
            
            # 获取窗口信息
            title = self._get_window_title(hwnd)
            class_name = self._get_window_class(hwnd)
            
            if include_all: 
                # 包含所有可见窗口
                display_name = title if title else f"[{class_name}] (无标题)"
                windows.append((hwnd, display_name, class_name))
            else:
                # 标准过滤
                if self._is_valid_window(hwnd) and title:
                    windows. append((hwnd, title, class_name))
            
            return True
        
        user32.EnumWindows(self.enum_windows_proc(enum_callback), 0)
        return windows
    
    def get_all_windows_extended(self):
        """
        获取所有窗口（扩展模式，包含更多窗口）
        用于找到普通模式下找不到的游戏窗口
        """
        windows = []
        
        def enum_callback(hwnd, lparam):
            # 只检查可见性
            if not user32.IsWindowVisible(hwnd):
                return True
            
            # 检查窗口是否被隐藏 (Windows 10/11 Cloaked)
            if self._is_window_cloaked(hwnd):
                return True
            
            # 获取窗口信息
            title = self._get_window_title(hwnd)
            class_name = self._get_window_class(hwnd)
            
            # 获取进程信息
            pid = self._get_window_pid(hwnd)
            process_name = self._get_process_name(pid) if pid else "Unknown"
            
            # 构建显示名称
            if title:
                display_name = f"{title}"
            else:
                display_name = f"[{class_name}] - {process_name}"
            
            # 获取窗口尺寸，过滤掉太小的窗口
            rect = self. get_window_rect(hwnd)
            if rect:
                _, _, w, h = rect
                if w > 100 and h > 100:  # 至少 100x100 像素
                    windows.append({
                        'handle': hwnd,
                        'title': title,
                        'class': class_name,
                        'process': process_name,
                        'pid': pid,
                        'display':  display_name,
                        'size': (w, h)
                    })
            
            return True
        
        user32.EnumWindows(self.enum_windows_proc(enum_callback), 0)
        
        # 按窗口大小排序（大窗口优先，游戏通常比较大）
        windows.sort(key=lambda x: x['size'][0] * x['size'][1], reverse=True)
        
        return windows
    
    def find_window_by_class(self, class_name):
        """通过窗口类名查找窗口"""
        hwnd = user32.FindWindowW(class_name, None)
        return hwnd if hwnd else None
    
    def find_window_by_title(self, title, partial=True):
        """
        通过标题查找窗口
        :param title:  窗口标题
        :param partial: 是否部分匹配
        """
        if not partial:
            hwnd = user32.FindWindowW(None, title)
            return hwnd if hwnd else None
        
        # 部分匹配
        windows = self.get_all_windows_extended()
        for win in windows:
            if win['title'] and title.lower() in win['title'].lower():
                return win['handle']
        return None
    
    def find_window_by_process(self, process_name):
        """通过进程名查找窗口"""
        windows = self.get_all_windows_extended()
        for win in windows:
            if win['process'] and process_name. lower() in win['process'].lower():
                return win['handle']
        return None
    
    def _is_valid_window(self, hwnd):
        """检查是否是有效的顶层窗口"""
        # 检查窗口样式
        style = user32.GetWindowLongW(hwnd, GWL_STYLE)
        ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        
        # 排除工具窗口
        if ex_style & WS_EX_TOOLWINDOW:
            return False
        
        # 必须没有所有者或者是应用窗口
        owner = user32.GetWindow(hwnd, GW_OWNER)
        if owner and not (ex_style & WS_EX_APPWINDOW):
            return False
        
        # 检查是否被隐藏
        if self._is_window_cloaked(hwnd):
            return False
        
        return True
    
    def _is_window_cloaked(self, hwnd):
        """检查窗口是否被隐藏 (Windows 10/11)"""
        cloaked = ctypes.c_int(0)
        dwmapi.DwmGetWindowAttribute(
            hwnd, 
            DWMWA_CLOAKED, 
            ctypes.byref(cloaked), 
            ctypes.sizeof(cloaked)
        )
        return cloaked.value != 0
    
    def _get_window_title(self, hwnd):
        """获取窗口标题"""
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return None
        
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer. value
    
    def _get_window_class(self, hwnd):
        """获取窗口类名"""
        buffer = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buffer, 256)
        return buffer. value
    
    def _get_window_pid(self, hwnd):
        """获取窗口所属进程ID"""
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return pid.value
    
    def _get_process_name(self, pid):
        """获取进程名称"""
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return None
        
        try:
            buffer = ctypes.create_unicode_buffer(260)
            size = wintypes.DWORD(260)
            
            # 使用 QueryFullProcessImageNameW
            kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size))
            
            # 提取文件名
            full_path = buffer.value
            if full_path: 
                return full_path.split('\\')[-1]
            return None
        finally:
            kernel32.CloseHandle(handle)
    
    def get_window_rect(self, hwnd):
        """获取窗口位置和大小"""
        rect = wintypes.RECT()
        if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            x = rect.left
            y = rect.top
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            return (x, y, w, h)
        return None
    
    def get_client_rect(self, hwnd):
        """获取窗口客户区位置和大小"""
        rect = wintypes.RECT()
        if user32.GetClientRect(hwnd, ctypes.byref(rect)):
            point = wintypes.POINT(0, 0)
            user32.ClientToScreen(hwnd, ctypes.byref(point))
            
            x = point.x
            y = point.y
            w = rect.right
            h = rect.bottom
            return (x, y, w, h)
        return None
    
    def is_window_valid(self, hwnd):
        """检查窗口是否有效"""
        return bool(user32.IsWindow(hwnd) and user32.IsWindowVisible(hwnd))
    
    def is_window_foreground(self, hwnd):
        """检查窗口是否在前台"""
        return user32.GetForegroundWindow() == hwnd
    
    def bring_to_front(self, hwnd):
        """将窗口置于前台"""
        user32.SetForegroundWindow(hwnd)
    
    def client_to_screen(self, hwnd, x, y):
        """将客户区坐标转换为屏幕坐标"""
        point = wintypes.POINT(x, y)
        user32.ClientToScreen(hwnd, ctypes.byref(point))
        return (point.x, point.y)