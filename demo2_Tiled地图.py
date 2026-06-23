"""
任务3：Tiled的基本使用
使用pytmx加载TMX格式地图并渲染
"""
import pygame
from pygame.constants import QUIT
import pytmx
from pytmx.util_pygame import load_pygame

# 初始化Pygame
pygame.init()
pygame.display.set_mode((1, 1))  # 需要先初始化display

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("西游记·观音院 - 任务3：Tiled地图")

# 时钟
clock = pygame.time.Clock()
FPS = 60

# 加载TMX地图
map_file = 'resource/tmx/village.tmx'
tmx_data = load_pygame(map_file)

# 地图尺寸
map_width = tmx_data.width * tmx_data.tilewidth
map_height = tmx_data.height * tmx_data.tileheight
print(f"地图尺寸: {map_width}x{map_height}")

# 渲染地图函数
def render_map(surface, tmx_data, offset_x=0, offset_y=0):
    """渲染地图"""
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    surface.blit(tile, (x * tmx_data.tilewidth - offset_x,
                                       y * tmx_data.tileheight - offset_y))
        elif isinstance(layer, pytmx.TiledImageLayer):
            if layer.image:
                surface.blit(layer.image, (-offset_x, -offset_y))

# 游戏主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # 清屏
    screen.fill((0, 0, 0))

    # 渲染地图
    render_map(screen, tmx_data)

    # 更新显示
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
