# -*- coding: utf-8 -*-
"""
场景管理类
"""
import pygame
import enum


class GameState(enum.IntEnum):
    """游戏状态"""
    Menu = 0
    Village = 1
    Temple = 2
    Battle = 3
    GameOver = 4
    Victory = 5


class SceneStatus(enum.IntEnum):
    """场景过渡状态"""
    In = 1
    Normal = 2
    Out = 3


class FadeScene:
    """场景渐入渐出类"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.alpha = 0
        self.status = SceneStatus.In

    def set_status(self, status):
        """设置场景状态"""
        self.status = status
        if status == SceneStatus.In:
            self.alpha = 0
        elif status == SceneStatus.Normal:
            self.alpha = 255
        elif status == SceneStatus.Out:
            self.alpha = 0

    def get_out(self):
        """检查是否完成渐出"""
        return self.status == SceneStatus.Out and self.alpha >= 255

    def update(self):
        """更新渐变状态"""
        if self.status == SceneStatus.In:
            self.alpha += 10
            if self.alpha >= 255:
                self.alpha = 255
                self.status = SceneStatus.Normal
        elif self.status == SceneStatus.Out:
            self.alpha += 10
            if self.alpha >= 255:
                self.alpha = 255

    def draw(self, surface):
        """绘制渐变效果"""
        if self.status != SceneStatus.Normal:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 255 - self.alpha))
            surface.blit(overlay, (0, 0))
