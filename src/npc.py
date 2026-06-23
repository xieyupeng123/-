"""
任务6：Sprite应用 - NPC类
NPC徘徊运动：在某一区域来回走动
"""
import pygame
import os
from .sprite import AnimatedSprite


class NPC(AnimatedSprite):
    """NPC精灵类 - 支持徘徊运动"""

    def __init__(self, x, y, image_paths, name="NPC", npc_type="normal",
                 move_range=100, move_speed=1):
        """
        初始化NPC
        :param x: x坐标
        :param y: y坐标
        :param image_paths: 图像路径字典
        :param name: NPC名称
        :param npc_type: NPC类型（normal, elder, god等）
        :param move_range: 徘徊范围（像素）
        :param move_speed: 移动速度
        """
        super().__init__(x, y, image_paths)

        # NPC属性
        self.name = name
        self.npc_type = npc_type
        self.speed = move_speed
        self.direction = 'down'
        self.moving = False

        # 徘徊运动参数
        self.start_x = x  # 起始X坐标
        self.start_y = y  # 起始Y坐标
        self.move_range = move_range  # 徘徊范围

        # 步数控制（用于切换方向）
        self.step_count = 0  # 当前步数
        self.max_steps = move_range // move_speed  # 最大步数

        # 移动方向：1表示正方向，-1表示负方向
        self.move_direction_x = 1  # X方向：1向右，-1向左
        self.move_direction_y = 1  # Y方向：1向下，-1向上

        # 当前移动轴：'x'或'y'
        self.current_axis = 'y'  # 默认上下移动

    def update(self, *args):
        """NPC徘徊运动 - 在区域内来回走动"""
        # 移动NPC
        dx = 0
        dy = 0

        if self.current_axis == 'x':
            # 水平移动
            dx = self.speed * self.move_direction_x
        else:
            # 垂直移动
            dy = self.speed * self.move_direction_y

        # 更新位置
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)

        # 更新步数
        self.step_count += 1

        # 检查是否需要切换方向
        if self.step_count >= self.max_steps:
            self.step_count = 0
            self._change_direction()

        # 更新动画
        if dx != 0 or dy != 0:
            self.moving = True
            if dx > 0:
                self.direction = 'right'
            elif dx < 0:
                self.direction = 'left'
            elif dy > 0:
                self.direction = 'down'
            elif dy < 0:
                self.direction = 'up'
            self.update_animation(self.direction)
        else:
            self.moving = False
            # 站立不动时显示第一帧
            self.current_frame = 0
            if self.current_direction in self.animation_frames:
                self.image = self.animation_frames[self.current_direction][0]
                self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def _change_direction(self):
        """切换移动方向（徘徊）"""
        # 交替切换移动轴
        if self.current_axis == 'y':
            self.current_axis = 'x'
            # 切换到X轴时，随机选择左右
            self.move_direction_x *= -1
        else:
            self.current_axis = 'y'
            # 切换到Y轴时，随机选择上下
            self.move_direction_y *= -1

    def draw(self, surface, offset_x=0, offset_y=0):
        """绘制NPC"""
        super().draw(surface, offset_x, offset_y)

    def get_position(self):
        """获取NPC位置"""
        return (self.x, self.y)

    def set_position(self, x, y):
        """设置NPC位置"""
        self.x = x
        self.y = y
        self.rect.topleft = (self.x, self.y)
