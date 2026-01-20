"""
全局热键管理
"""
import ctypes
from ctypes import wintypes
from PyQt5.QtCore import QThread, pyqtSignal
import time

# Windows API
user32 = ctypes.windll.user32

# 热键修饰符
MOD_NONE = 0x0000
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004

# 虚拟键码
VK_CODE = {
    'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4':  0x73,
    'F5': 0x74, 'F6':  0x75, 'F7': 0x76, 'F8': 0x77,
    'F9': 0x78, 'F10': 0x79, 'F11': 0x7A, 'F12': 0x7B,
    'Escape': 0x1B, 'Space': 0x20, 'Enter': 0x0D,
}


class HotkeyManager(QThread):
    """全局热键管理器"""
    
    def __init__(self):
        super().__init__()
        self.hotkeys = {}  # {id: callback}
        self.running = False
        self.next_id = 1
    
    def register_hotkey(self, key, callback, modifiers=MOD_NONE):
        """
        注册热键
        : param key: 键名 (如 'F6', 'Escape')
        :param callback: 回调函数
        :param modifiers: 修饰符
        """
        if key in VK_CODE:
            vk = VK_CODE[key]
            hotkey_id = self.next_id
            self.next_id += 1
            
            self.hotkeys[hotkey_id] = {
                'vk': vk,
                'modifiers': modifiers,
                'callback': callback,
                'key': key
            }
            return hotkey_id
        return None
    
    def run(self):
        """热键监听主循环"""
        self.running = True
        
        # 注册所有热键
        for hotkey_id, info in self.hotkeys.items():
            result = user32.RegisterHotKey(
                None, hotkey_id, info['modifiers'], info['vk']
            )
            if not result:
                print(f"注册热键失败: {info['key']}")
        
        # 消息循环
        msg = wintypes.MSG()
        while self.running:
            # 使用 PeekMessage 非阻塞检查
            if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                if msg.message == 0x0312:  # WM_HOTKEY
                    hotkey_id = msg.wParam
                    if hotkey_id in self. hotkeys:
                        callback = self.hotkeys[hotkey_id]['callback']
                        if callback:
                            try:
                                callback()
                            except Exception as e: 
                                print(f"热键回调错误: {e}")
            else:
                # 没有消息时短暂休眠
                time.sleep(0.01)
        
        # 注销所有热键
        for hotkey_id in self.hotkeys:
            user32.UnregisterHotKey(None, hotkey_id)
    
    def stop(self):
        """停止热键监听"""
        self.running = False
        self.wait()