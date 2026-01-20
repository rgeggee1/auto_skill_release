"""
游戏技能自动释放工具 - 主程序入口
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from gui.main_window import MainWindow


def main():
    # 启用高DPI支持
    QApplication. setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 设置应用样式
    app.setStyleSheet("""
        QMainWindow {
            background-color:  #2b2b2b;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #3d3d3d;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 10px;
            background-color: #333333;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #4fc3f7;
        }
        QPushButton {
            background-color: #0d47a1;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1565c0;
        }
        QPushButton:pressed {
            background-color: #0a3d91;
        }
        QPushButton:disabled {
            background-color: #555555;
            color: #888888;
        }
        QComboBox, QSpinBox, QLineEdit {
            background-color:  #404040;
            color: white;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 5px;
        }
        QComboBox: hover, QSpinBox:hover, QLineEdit:hover {
            border:  1px solid #4fc3f7;
        }
        QComboBox:: drop-down {
            border: none;
        }
        QLabel {
            color: #e0e0e0;
        }
        QRadioButton {
            color: #e0e0e0;
        }
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()