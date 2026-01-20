"""
鼠标移动模式 - 支持多边形区域
"""
import random
import math


class MousePattern:
    """鼠标移动模式枚举"""
    GRID = 0
    RANDOM = 1
    SPIRAL = 2


def point_in_polygon(point, polygon):
    """
    判断点是否在多边形内（射线法）
    : param point: (x, y)
    :param polygon: [(x1,y1), (x2,y2), ...]
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        
        j = i
    
    return inside


def get_polygon_bounds(polygon):
    """获取多边形边界矩形"""
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return (min(xs), min(ys), max(xs), max(ys))


class PatternGenerator:
    """移动模式生成器 - 支持多边形"""
    
    def __init__(self, area, step_size, pattern, polygon=None):
        """
        初始化
        :param area: (x, y, width, height) 矩形区域（多边形时为边界矩形）
        : param step_size: 移动步长
        :param pattern:  移动模式
        : param polygon: 多边形顶点列表 [(x,y), ...]，为None时使用矩形
        """
        self.area_x, self.area_y, self.area_w, self. area_h = area
        self.step_size = step_size
        self.pattern = pattern
        self.polygon = polygon
        
        self.reset()
    
    def reset(self):
        """重置生成器"""
        if self.pattern == MousePattern.GRID: 
            self._init_grid()
        elif self.pattern == MousePattern.RANDOM: 
            self._init_random()
        elif self.pattern == MousePattern.SPIRAL:
            self._init_spiral()
    
    def _init_grid(self):
        """初始化网格模式"""
        self. grid_x = 0
        self.grid_y = 0
        self.direction = 1
    
    def _init_random(self):
        """初始化随机模式"""
        pass
    
    def _init_spiral(self):
        """初始化螺旋模式"""
        self.spiral_angle = 0
        self.spiral_radius = 0
        self.center_x = self.area_w // 2
        self.center_y = self.area_h // 2
        self.max_radius = min(self.area_w, self.area_h) // 2
    
    def _is_point_valid(self, x, y):
        """检查点是否在有效区域内"""
        if self.polygon:
            # 多边形模式：检查点是否在多边形内
            return point_in_polygon((x, y), self.polygon)
        else:
            # 矩形模式：检查点是否在矩形内
            return (self.area_x <= x < self.area_x + self. area_w and
                    self.area_y <= y < self.area_y + self.area_h)
    
    def next_point(self):
        """获取下一个点位"""
        if self.pattern == MousePattern.GRID:
            return self._next_grid_point()
        elif self.pattern == MousePattern. RANDOM:
            return self._next_random_point()
        elif self.pattern == MousePattern. SPIRAL:
            return self._next_spiral_point()
    
    def _next_grid_point(self):
        """网格模式下一个点"""
        # 尝试找到下一个有效点
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            x = self.area_x + self.grid_x
            y = self.area_y + self.grid_y
            
            # 更新网格位置
            self.grid_x += self.step_size * self.direction
            
            if self. grid_x >= self.area_w:
                self.grid_x = self.area_w - 1
                self.grid_y += self.step_size
                self.direction = -1
            elif self.grid_x < 0:
                self.grid_x = 0
                self.grid_y += self.step_size
                self.direction = 1
            
            if self.grid_y >= self. area_h:
                self. grid_y = 0
                self.grid_x = 0
                self.direction = 1
            
            # 检查点是否有效
            if self._is_point_valid(x, y):
                return (int(x), int(y))
            
            attempts += 1
        
        # 如果找不到有效点，返回中心点
        return self._get_fallback_point()
    
    def _next_random_point(self):
        """随机模式下一个点"""
        max_attempts = 100
        
        for _ in range(max_attempts):
            x = self.area_x + random.randint(0, self.area_w - 1)
            y = self.area_y + random.randint(0, self. area_h - 1)
            
            if self._is_point_valid(x, y):
                return (int(x), int(y))
        
        return self._get_fallback_point()
    
    def _next_spiral_point(self):
        """螺旋模式下一个点"""
        max_attempts = 100
        
        for _ in range(max_attempts):
            x = self.center_x + int(self.spiral_radius * math.cos(self.spiral_angle))
            y = self.center_y + int(self.spiral_radius * math.sin(self.spiral_angle))
            
            # 转换为绝对坐标
            abs_x = x + self.area_x
            abs_y = y + self.area_y
            
            # 更新螺旋参数
            self.spiral_angle += 0.3
            self.spiral_radius += self.step_size * 0.05
            
            if self.spiral_radius > self.max_radius:
                self.spiral_radius = 0
                self.spiral_angle = 0
            
            if self._is_point_valid(abs_x, abs_y):
                return (int(abs_x), int(abs_y))
        
        return self._get_fallback_point()
    
    def _get_fallback_point(self):
        """获取备用点（多边形中心）"""
        if self.polygon:
            # 计算多边形中心
            cx = sum(p[0] for p in self.polygon) / len(self.polygon)
            cy = sum(p[1] for p in self.polygon) / len(self.polygon)
            return (int(cx), int(cy))
        else:
            return (self.area_x + self.area_w // 2, self.area_y + self. area_h // 2)


class PolygonPatternGenerator(PatternGenerator):
    """专门用于多边形的模式生成器"""
    
    def __init__(self, polygon, step_size, pattern):
        """
        初始化
        :param polygon: 多边形顶点列表 [(x,y), ...]
        :param step_size: 移动步长
        :param pattern: 移动模式
        """
        # 计算边界矩形
        bounds = get_polygon_bounds(polygon)
        min_x, min_y, max_x, max_y = bounds
        area = (min_x, min_y, max_x - min_x, max_y - min_y)
        
        super().__init__(area, step_size, pattern, polygon)
        
        # 预生成有效点列表（用于优化随机模式）
        self._pregenerate_valid_points()
    
    def _pregenerate_valid_points(self):
        """预生成多边形内的有效点"""
        self.valid_points = []
        
        step = max(self.step_size // 2, 5)
        
        for y in range(int(self.area_y), int(self.area_y + self.area_h), step):
            for x in range(int(self.area_x), int(self.area_x + self.area_w), step):
                if point_in_polygon((x, y), self.polygon):
                    self.valid_points.append((x, y))
        
        if not self.valid_points:
            # 如果没有找到有效点，使用多边形中心
            cx = sum(p[0] for p in self.polygon) / len(self.polygon)
            cy = sum(p[1] for p in self.polygon) / len(self.polygon)
            self.valid_points. append((int(cx), int(cy)))
    
    def _next_random_point(self):
        """随机模式 - 从预生成的点中选择"""
        if self.valid_points:
            return random.choice(self.valid_points)
        return self._get_fallback_point()