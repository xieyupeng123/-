# -*- coding: utf-8 -*-
"""
玩家类
"""
import pygame
from .sprite import AnimatedSprite


class Player(AnimatedSprite):
    """玩家精灵类 - 支持4方向行走动画和键盘控制"""

    def __init__(self, x, y, speed=3, max_hp=100, attack=15):
        super().__init__(x, y)

        # 玩家属性
        self.speed = speed
        self.direction = 'down'
        self.moving = False
        self.hp = max_hp
        self.max_hp = max_hp
        self.attack_power = attack

        # 加载4方向动画帧
        self.load_frames('down', 'resource/img/swk', '0000', 4)
        self.load_frames('up', 'resource/img/swk', '0100', 4)
        self.load_frames('left', 'resource/img/swk', '0200', 4)
        self.load_frames('right', 'resource/img/swk', '0300', 4)

        # 设置初始图像
        if 'down' in self.frames and self.frames['down']:
            self.image = self.frames['down'][0]
            self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, keys, obstacles, map_width=3780, map_height=2395, in_dialogue=False):
        """
        更新玩家位置
        :param keys: 按键状态
        :param obstacles: 障碍物列表
        :param map_width: 地图宽度
        :param map_height: 地图高度
        :param in_dialogue: 是否在对话中
        """
        if in_dialogue:
            return

        dx = 0
        dy = 0
        self.moving = False

        # 方向键控制
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
        new_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)
        for obstacle in obstacles:
            if new_rect.colliderect(obstacle):
                if dx > 0:
                    new_x = obstacle.left - self.rect.width
                elif dx < 0:
                    new_x = obstacle.right
                if dy > 0:
                    new_y = obstacle.top - self.rect.height
                elif dy < 0:
                    new_y = obstacle.bottom

        # 更新位置
        self.x = new_x
        self.y = new_y
        self.rect.topleft = (self.x, self.y)

        # 更新动画
        if self.moving:
            self.update_animation()
        else:
            # 站立时显示第0帧
            self.current_frame = 0
            if self.current_direction in self.frames:
                self.image = self.frames[self.current_direction][0]
                self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def take_damage(self, damage):
        """受到伤害"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def reset(self, x, y):
        """重置玩家位置和状态"""
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)
        self.hp = self.max_hp
