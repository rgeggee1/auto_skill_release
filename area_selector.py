"""
坐标点记录器
"""
from PyQt5.QtWidgets import QDialog, QWidget, QMenu, QAction
from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath


class PointRecorder(QDialog):
    """坐标点记录器 - 点击记录释放技能的位置"""
    
    def __init__(self, window_rect, existing_points=None, parent=None):
        super().__init__(parent)
        self.window_rect = window_rect
        self.points = existing_points. copy() if existing_points else []
        self.hover_point_index = -1
        self. dragging_point_index = -1
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        
        win_x, win_y, win_w, win_h = self.window_rect
        self.setGeometry(win_x, win_y, win_w, win_h)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 半透明背景
        painter. fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        # 提示文字
        painter.setPen(QPen(Qt.white, 1))
        painter.setFont(painter.font())
        
        hints = [
            "🎯 左键点击 = 添加坐标点（技能释放位置）",
            "🖱️ 拖拽已有点 = 调整位置",
            "🗑️ 右键点击坐标点 = 删除",
            "✅ 按 Enter 或 右键空白处 = 完成",
            "❌ 按 ESC = 取消",
            f"📍 已记录 {len(self.points)} 个坐标点"
        ]
        
        y_offset = 25
        for hint in hints:
            painter.drawText(15, y_offset, hint)
            y_offset += 22
        
        # 绘制连接线（显示释放顺序）
        if len(self.points) >= 2:
            painter.setPen(QPen(QColor(255, 255, 255, 100), 1, Qt.DashLine))
            for i in range(len(self.points) - 1):
                p1 = self.points[i]
                p2 = self.points[i + 1]
                painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
        
        # 绘制坐标点
        for i, point in enumerate(self. points):
            x, y = int(point[0]), int(point[1])
            
            # 根据状态选择颜色
            if i == self.dragging_point_index:
                # 拖拽中
                color = QColor(76, 175, 80)  # 绿色
                radius = 14
            elif i == self.hover_point_index:
                # 悬停
                color = QColor(255, 193, 7)  # 黄色
                radius = 12
            else:
                # 普通状态
                color = QColor(79, 195, 247)  # 蓝色
                radius = 10
            
            # 绘制外圈
            painter.setPen(QPen(color, 3))
            painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 100)))
            painter.drawEllipse(QPointF(x, y), radius, radius)
            
            # 绘制序号
            painter.setPen(QPen(Qt.white, 1))
            painter.setBrush(QBrush(color))
            
            # 序号背景圆
            num_radius = 10
            num_x = x + radius
            num_y = y - radius
            painter.drawEllipse(QPointF(num_x, num_y), num_radius, num_radius)
            
            # 序号文字
            painter.setPen(QPen(Qt.white))
            number_str = str(i + 1)
            painter.drawText(
                int(num_x - 4 * len(number_str)), 
                int(num_y + 4), 
                number_str
            )
            
            # 坐标信息
            coord_text = f"({x}, {y})"
            painter. setPen(QPen(QColor(200, 200, 200)))
            painter.drawText(x + 15, y + 5, coord_text)
    
    def mousePressEvent(self, event):
        pos = (event.pos().x(), event.pos().y())
        
        if event.button() == Qt.LeftButton:
            point_index = self._get_point_at(pos)
            
            if point_index >= 0:
                # 开始拖拽现有点
                self.dragging_point_index = point_index
            else:
                # 添加新点
                self.points.append(pos)
            
            self.update()
            
        elif event.button() == Qt.RightButton:
            point_index = self._get_point_at(pos)
            
            if point_index >= 0:
                # 右键点��点 - 删除
                self._delete_point(point_index)
            else:
                # 右键空白处 - 完成
                if len(self.points) >= 1:
                    self.accept()
    
    def mouseMoveEvent(self, event):
        pos = (event.pos().x(), event.pos().y())
        
        if self.dragging_point_index >= 0:
            # 拖拽点
            self.points[self.dragging_point_index] = pos
        else:
            # 更新悬停状态
            self.hover_point_index = self._get_point_at(pos)
        
        self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging_point_index = -1
            self.update()
    
    def mouseDoubleClickEvent(self, event):
        """双击完成"""
        if event.button() == Qt.LeftButton and len(self.points) >= 1:
            self. accept()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt. Key_Enter):
            if len(self.points) >= 1:
                self.accept()
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            # Ctrl+Z 撤销最后一个点
            if self.points:
                self.points.pop()
                self.update()
        elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            # 删除最后一个点
            if self.points:
                self.points.pop()
                self.update()
    
    def _get_point_at(self, pos, threshold=20):
        """获取指定位置的点索引"""
        for i, point in enumerate(self.points):
            dx = pos[0] - point[0]
            dy = pos[1] - point[1]
            if (dx * dx + dy * dy) <= threshold * threshold:
                return i
        return -1
    
    def _delete_point(self, index):
        """删除点"""
        if 0 <= index < len(self.points):
            self.points.pop(index)
            self.hover_point_index = -1
            self.update()
    
    def get_points(self):
        """获取所有坐标点"""
        return self.points. copy() if self.points else None


class PointsPreview(QWidget):
    """坐标点预览窗口"""
    
    def __init__(self, points, window_offset=(0, 0), parent=None):
        super().__init__(parent)
        self.points = points
        self.window_offset = window_offset
        
        self._calculate_bounds()
        self.init_ui()
    
    def _calculate_bounds(self):
        """计算边界"""
        if not self.points:
            self.min_x = self.min_y = 0
            self.max_x = self.max_y = 100
            return
        
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        
        self.min_x = min(xs) - 30
        self.min_y = min(ys) - 30
        self.max_x = max(xs) + 30
        self.max_y = max(ys) + 30
    
    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt. Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        x = self.window_offset[0] + self.min_x
        y = self.window_offset[1] + self.min_y
        w = self.max_x - self.min_x
        h = self.max_y - self.min_y
        
        self.setGeometry(int(x), int(y), int(w), int(h))
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制连接线
        if len(self.points) >= 2:
            painter.setPen(QPen(QColor(79, 195, 247, 150), 2, Qt.DashLine))
            for i in range(len(self.points) - 1):
                p1 = self.points[i]
                p2 = self.points[i + 1]
                x1 = p1[0] - self.min_x
                y1 = p1[1] - self. min_y
                x2 = p2[0] - self.min_x
                y2 = p2[1] - self.min_y
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # 绘制点
        for i, point in enumerate(self.points):
            x = point[0] - self. min_x
            y = point[1] - self.min_y
            
            # 点
            painter.setPen(QPen(QColor(79, 195, 247), 3))
            painter.setBrush(QBrush(QColor(79, 195, 247, 100)))
            painter.drawEllipse(QPointF(x, y), 12, 12)
            
            # 序号
            painter. setPen(QPen(Qt. white))
            painter.drawText(int(x - 4), int(y + 4), str(i + 1))