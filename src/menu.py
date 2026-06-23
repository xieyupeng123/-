# -*- coding: utf-8 -*-
"""
主菜单类
"""
import pygame
from .utils import get_font


class MainMenu:
    """主菜单类"""

    def __init__(self, screen_width=800, screen_height=600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.selected = 0
        self.options = ["Start Game", "Exit"]

        # 字体
        self.title_font = get_font(72)
        self.menu_font = get_font(36)

    def draw(self, surface):
        """绘制菜单"""
        surface.fill((0, 0, 0))

        # 标题
        title = self.title_font.render("Journey to the West", True, (255, 215, 0))
        surface.blit(title, (self.screen_width // 2 - title.get_width() // 2, 150))

        subtitle = self.menu_font.render("Guanyin Temple", True, (200, 200, 200))
        surface.blit(subtitle, (self.screen_width // 2 - subtitle.get_width() // 2, 230))

        # 菜单选项
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.menu_font.render(option, True, color)
            surface.blit(text, (self.screen_width // 2 - text.get_width() // 2, 350 + i * 60))

        # 提示
        hint = self.menu_font.render("Use UP/DOWN to select, ENTER to confirm", True, (150, 150, 150))
        surface.blit(hint, (self.screen_width // 2 - hint.get_width() // 2, 520))

    def handle_input(self, key):
        """
        处理输入
        :param key: 按键
        :return: 选中的选项或None
        """
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.options)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.options)
        elif key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
            return self.options[self.selected]
        return None
