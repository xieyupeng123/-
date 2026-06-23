# -*- coding: utf-8 -*-
"""
对话框类
"""
import pygame
from .utils import get_font


class DialogueBox:
    """对话框类"""

    def __init__(self, screen_width=800, screen_height=600):
        self.active = False
        self.text = ""
        self.speaker = ""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.box_height = 120
        self.box_y = screen_height - self.box_height - 20

        # 创建对话框表面
        self.box_surface = pygame.Surface((screen_width - 40, self.box_height), pygame.SRCALPHA)
        self.box_surface.fill((0, 0, 0, 200))

        # 字体
        self.font = get_font(28)
        self.name_font = get_font(32)

    def show(self, speaker, text):
        """显示对话框"""
        self.active = True
        self.speaker = speaker
        self.text = text

    def hide(self):
        """隐藏对话框"""
        self.active = False

    def draw(self, surface):
        """绘制对话框"""
        if not self.active:
            return

        # 绘制对话框背景
        surface.blit(self.box_surface, (20, self.box_y))

        # 绘制说话者名称
        name_surface = self.name_font.render(self.speaker, True, (255, 255, 0))
        surface.blit(name_surface, (40, self.box_y + 10))

        # 绘制对话内容（支持自动换行）
        words = self.text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] < self.screen_width - 100:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        # 绘制文本
        for i, line in enumerate(lines[:3]):  # 最多显示3行
            text_surface = self.font.render(line, True, (255, 255, 255))
            surface.blit(text_surface, (40, self.box_y + 45 + i * 25))

        # 绘制提示
        hint_surface = self.font.render("Press SPACE to continue...", True, (200, 200, 200))
        surface.blit(hint_surface, (self.screen_width - 250, self.box_y + self.box_height - 30))
