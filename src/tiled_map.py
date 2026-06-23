"""
任务4-5：Tmx地图封装
将tmx地图封装成一个类
"""
import pygame
import pytmx
from pytmx.util_pygame import load_pygame


class TiledMap:
    """TMX地图类 - 封装地图加载和渲染功能"""

    def __init__(self, filename):
        """
        初始化地图
        :param filename: TMX地图文件路径
        """
        self.filename = filename
        self.tmx_data = None
        self.map_image = None  # 渲染好的地图图像

        # 地图属性
        self.width = 0
        self.height = 0
        self.tile_width = 0
        self.tile_height = 0

        # 加载地图
        self.load()

    def load(self):
        """加载TMX地图"""
        try:
            self.tmx_data = load_pygame(self.filename)

            # 获取地图尺寸
            self.width = self.tmx_data.width * self.tmx_data.tilewidth
            self.height = self.tmx_data.height * self.tmx_data.tileheight
            self.tile_width = self.tmx_data.tilewidth
            self.tile_height = self.tmx_data.tileheight

            # 渲染地图
            self.render_map()

            print(f"地图加载成功: {self.filename}")
            print(f"地图尺寸: {self.width}x{self.height}")
            print(f"瓦片尺寸: {self.tile_width}x{self.tile_height}")

        except Exception as e:
            print(f"地图加载失败: {e}")

    def render_map(self):
        """渲染整个地图到一个surface"""
        if self.tmx_data is None:
            return

        # 创建一个足够大的surface来渲染整个地图
        self.map_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # 渲染所有可见图层
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self._render_tile_layer(self.map_image, layer)
            elif isinstance(layer, pytmx.TiledImageLayer):
                self._render_image_layer(self.map_image, layer)

    def _render_tile_layer(self, surface, layer):
        """渲染瓦片图层"""
        for x, y, gid in layer:
            tile = self.tmx_data.get_tile_image_by_gid(gid)
            if tile:
                surface.blit(tile, (x * self.tile_width, y * self.tile_height))

    def _render_image_layer(self, surface, layer):
        """渲染图像图层"""
        if layer.image:
            surface.blit(layer.image, (0, 0))

    def render(self, surface, offset_x=0, offset_y=0):
        """
        渲染地图到目标surface
        :param surface: 目标surface
        :param offset_x: X偏移量
        :param offset_y: Y偏移量
        """
        if self.map_image:
            # 截取视窗范围内的地图
            rect = pygame.Rect(offset_x, offset_y,
                             surface.get_width(), surface.get_height())
            surface.blit(self.map_image, (0, 0), rect)

    def get_object(self, object_name):
        """
        获取地图对象
        :param object_name: 对象名称
        :return: 对象字典，包含name, x, y等属性
        """
        if self.tmx_data is None:
            return None

        for obj in self.tmx_data.objects:
            if obj.name == object_name:
                return {
                    'name': obj.name,
                    'x': obj.x,
                    'y': obj.y,
                    'width': getattr(obj, 'width', 0),
                    'height': getattr(obj, 'height', 0),
                    'type': getattr(obj, 'type', ''),
                    'properties': dict(obj.properties) if hasattr(obj, 'properties') else {}
                }
        return None

    def get_objects_by_layer(self, layer_name):
        """
        获取指定图层的所有对象
        :param layer_name: 图层名称
        :return: 对象列表
        """
        if self.tmx_data is None:
            return []

        objects = []
        for obj in self.tmx_data.objects:
            # 检查对象是否属于指定图层
            if hasattr(obj, 'group') and obj.group == layer_name:
                objects.append({
                    'name': obj.name,
                    'x': obj.x,
                    'y': obj.y,
                    'width': getattr(obj, 'width', 0),
                    'height': getattr(obj, 'height', 0),
                    'type': getattr(obj, 'type', ''),
                    'properties': dict(obj.properties) if hasattr(obj, 'properties') else {}
                })
        return objects

    def get_obstacles(self):
        """
        获取所有障碍物
        :return: 障碍物矩形列表
        """
        obstacles = []
        for obj in self.tmx_data.objects:
            # 检查对象类型
            obj_type = getattr(obj, 'type', None)
            obj_name = getattr(obj, 'name', None)

            if obj_type == 'obstacle':
                obstacles.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj_name and 'road' in str(obj_name).lower():
                # road图层中的多边形也是障碍物
                if hasattr(obj, 'points'):
                    # 多边形需要转换为矩形
                    points = obj.points
                    if points:
                        min_x = min(p[0] for p in points) + obj.x
                        min_y = min(p[1] for p in points) + obj.y
                        max_x = max(p[0] for p in points) + obj.x
                        max_y = max(p[1] for p in points) + obj.y
                        obstacles.append(pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y))
        return obstacles

    def get_map_size(self):
        """获取地图尺寸"""
        return (self.width, self.height)

    def get_tile_size(self):
        """获取瓦片尺寸"""
        return (self.tile_width, self.tile_height)
