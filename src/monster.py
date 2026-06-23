# -*- coding: utf-8 -*-
"""
怪物类
"""
import pygame
import random
from .sprite import AnimatedSprite


class Monster(AnimatedSprite):
    """怪物类 - 寺庙场景中的敌人"""

    def __init__(self, x, y, name="Monster", hp=60, attack=8, move_range=100):
        super().__init__(x, y)

        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.alive = True

        # 移动设置
        self.speed = 1
        self.move_timer = 0
        self.move_interval = 60
        self.start_x = x
        self.start_y = y
        self.patrol_range = move_range

        # 加载动画帧
        self.load_frames('down', 'resource/img/elder', 'elder1-00', 4)

        # 设置初始图像
        if 'down' in self.frames and self.frames['down']:
            self.image = self.frames['down'][0]
            self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        """更新怪物位置"""
        if not self.alive:
            return

        # 简单的随机移动
        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            dx = random.choice([-1, 0, 1]) * self.speed * 10
            dy = random.choice([-1, 0, 1]) * self.speed * 10
            new_x = self.x + dx
            new_y = self.y + dy

            # 限制移动范围
            if abs(new_x - self.start_x) < self.patrol_range:
                self.x = new_x
            if abs(new_y - self.start_y) < self.patrol_range:
                self.y = new_y

            self.rect.topleft = (self.x, self.y)

        # 更新动画
        self.update_animation()

    def take_damage(self, damage):
        """受到伤害"""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def draw(self, surface, offset_x=0, offset_y=0):
        """绘制怪物（带血条）"""
        if not self.alive:
            return

        # 绘制怪物
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        surface.blit(self.image, (screen_x, screen_y))

        # 绘制血条
        bar_width = 50
        bar_height = 5
        hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 0
        pygame.draw.rect(surface, (255, 0, 0), (screen_x, screen_y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (screen_x, screen_y - 10, bar_width * hp_ratio, bar_height))
