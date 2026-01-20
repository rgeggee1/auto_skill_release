"""
配置管理
"""
import json
import os


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
    
    def save(self, config):
        """保存配置"""
        try:
            with open(self. config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e: 
            print(f"保存配置失败: {e}")
            return False
    
    def load(self):
        """加载配置"""
        if not os.path.exists(self.config_file):
            return None
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return None