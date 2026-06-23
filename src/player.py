"""
任务6：Sprite应用 - 玩家类
"""
import pygame
import os
from .sprite import AnimatedSprite


class Player(AnimatedSprite):
    """玩家精灵类"""

    def __init__(self, x, y, image_paths):
        """
        初始化玩家
        :param x: x坐标
        :param y: y坐标
        :param image_paths: 图像路径字典，格式: {'down': [path1, ...], 'up': [...], ...}
        """
        super().__init__(x, y, image_paths)

        # 玩家属性
        self.speed = 3
        self.direction = 'down'
        self.moving = False

        # 碰撞检测用的矩形（比图像小一些）
        self.collision_rect = pygame.Rect(0, 0, 24, 24)
        self.collision_rect.center = self.rect.center

    def update(self, keys, map_width, map_height, obstacles=None):
        """
        更新玩家位置
        :param keys: 按键状态
        :param map_width: 地图宽度
        :param map_height: 地图高度
        :param obstacles: 障碍物列表
        """
        dx = 0
        dy = 0
        self.moving = False

        # 根据按键设置移动方向
        if keys[pygame.K_UP]:
            dy = -self.speed
            self.direction = 'up'
            self.moving = True
        elif keys[pygame.K_DOWN]:
            dy = self.speed
            self.direction = 'down'
            self.moving = True

        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.direction = 'left'
            self.moving = True
        elif keys[pygame.K_RIGHT]:
            dx = self.speed
            self.direction = 'right'
            self.moving = True

        # 计算新位置
        new_x = self.x + dx
        new_y = self.y + dy

        # 边界检测
        new_x = max(0, min(new_x, map_width - self.rect.width))
        new_y = max(0, min(new_y, map_height - self.rect.height))

        # 障碍物碰撞检测
        if obstacles:
            new_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)
            for obstacle in obstacles:
                if new_rect.colliderect(obstacle):
                    # 碰撞检测，阻止移动
                    if dx > 0:  # 向右移动
                        new_x = obstacle.left - self.rect.width
                    elif dx < 0:  # 向左移动
                        new_x = obstacle.right
                    if dy > 0:  # 向下移动
                        new_y = obstacle.top - self.rect.height
                    elif dy < 0:  # 向上移动
                        new_y = obstacle.bottom

        # 更新位置
        self.x = new_x
        self.y = new_y
        self.rect.topleft = (self.x, self.y)
        self.collision_rect.center = self.rect.center

        # 更新动画
        if self.moving:
            self.update_animation(self.direction)
        else:
            # 站立不动时显示第一帧
            self.current_frame = 0
            if self.current_direction in self.animation_frames:
                self.image = self.animation_frames[self.current_direction][0]
                self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self, surface, offset_x=0, offset_y=0):
        """绘制玩家"""
        super().draw(surface, offset_x, offset_y)

    def get_position(self):
        """获取玩家位置"""
        return (self.x, self.y)

    def set_position(self, x, y):
        """设置玩家位置"""
        self.x = x
        self.y = y
        self.rect.topleft = (self.x, self.y)
        self.collision_rect.center = self.rect.center
