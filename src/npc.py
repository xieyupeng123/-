# -*- coding: utf-8 -*-
"""
NPC类 - 支持徘徊运动
"""
import pygame
from .sprite import AnimatedSprite


class NPC(AnimatedSprite):
    """NPC精灵类 - 支持徘徊运动（记步切换方向）"""

    def __init__(self, x, y, name="NPC", move_range=100, move_speed=1):
        super().__init__(x, y)

        self.name = name
        self.speed = move_speed
        self.move_range = move_range

        # 徘徊运动状态
        self.step_count = 0
        self.max_steps = move_range // move_speed if move_speed > 0 else 100
        self.move_direction_x = 1
        self.move_direction_y = 1
        self.current_axis = 'y'  # 当前移动轴

        # 加载动画帧（使用长老图像）
        self.load_frames('down', 'resource/img/elder', 'elder1-00', 4)

        # 设置初始图像
        if 'down' in self.frames and self.frames['down']:
            self.image = self.frames['down'][0]
            self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, *args):
        """更新NPC位置（徘徊运动）"""
        dx = 0
        dy = 0

        if self.current_axis == 'x':
            dx = self.speed * self.move_direction_x
        else:
            dy = self.speed * self.move_direction_y

        self.x += dx
        self.y += dy
        self.step_count += 1

        # 记步切换方向
        if self.step_count >= self.max_steps:
            self.step_count = 0
            self._change_direction()

        # 更新矩形位置
        self.rect.topleft = (self.x, self.y)

        # 更新动画
        self.update_animation()

    def _change_direction(self):
        """切换移动方向"""
        if self.current_axis == 'y':
            self.current_axis = 'x'
            self.move_direction_x *= -1
        else:
            self.current_axis = 'y'
            self.move_direction_y *= -1
