"""
任务1-2：背景图片的显示
实现游戏背景图片的显示
"""
import pygame
from pygame.constants import QUIT

# 初始化Pygame
pygame.init()
pygame.display.set_mode((1, 1))  # 需要先初始化display

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("西游记·观音院 - 任务1：背景图片显示")

# 时钟
clock = pygame.time.Clock()
FPS = 60

# 加载背景图片
background_image = 'resource/img/village.jpg'
background = pygame.image.load(background_image).convert()

# 游戏主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # 绘制背景
    screen.blit(background, (0, 0))

    # 更新显示
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
