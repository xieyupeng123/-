# -*- coding: utf-8 -*-
"""
精灵基类和动画精灵类
"""
import pygame
from .utils import load_animation_frames


class AnimatedSprite(pygame.sprite.Sprite):
    """动画精灵基类"""

    def __init__(self, x, y, size=(64, 64)):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))

        # 动画相关
        self.frames = {}
        self.current_direction = 'down'
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15

    def load_frames(self, direction, base_path, prefix, count):
        """加载指定方向的动画帧"""
        self.frames[direction] = load_animation_frames(base_path, prefix, count, self.size)

    def update_animation(self):
        """更新动画"""
        if self.current_direction in self.frames:
            frames = self.frames[self.current_direction]
            if frames:
                self.animation_timer += self.animation_speed
                if self.animation_timer >= 1:
                    self.animation_timer = 0
                    self.current_frame = (self.current_frame + 1) % len(frames)
                    self.image = frames[self.current_frame]
                    self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self, surface, offset_x=0, offset_y=0):
        """绘制精灵"""
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        surface.blit(self.image, (screen_x, screen_y))
