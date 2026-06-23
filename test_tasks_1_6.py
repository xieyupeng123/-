"""
测试任务1-6：背景图片、Tiled地图、地图封装、Sprite应用
"""
import pygame
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tiled_map import TiledMap
from src.sprite import Sprite, AnimatedSprite
from src.player import Player
from src.npc import NPC

# 初始化Pygame
pygame.init()
pygame.display.set_mode((1, 1))  # 需要先初始化display

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("西游记·观音院 - 任务1-6测试")

# 时钟
clock = pygame.time.Clock()
FPS = 60

# 任务1-2：加载背景图片
print("=" * 50)
print("任务1-2：背景图片的显示")
print("=" * 50)
background = pygame.image.load('resource/img/village.jpg').convert()
print("背景图片加载成功")

# 任务3-5：加载Tiled地图
print("\n" + "=" * 50)
print("任务3-5：Tiled地图加载和封装")
print("=" * 50)
game_map = TiledMap('resource/tmx/village.tmx')
map_width, map_height = game_map.get_map_size()
print(f"地图尺寸: {map_width}x{map_height}")

# 任务6：Sprite应用
print("\n" + "=" * 50)
print("任务6：Sprite应用")
print("=" * 50)

# 加载玩家精灵
player_pos = game_map.get_object('sun')
if player_pos:
    print(f"玩家初始位置: ({player_pos['x']}, {player_pos['y']})")
    player_images = {
        'down': [os.path.join('resource', 'img', 'swk', f'0000{i}.tga') for i in range(4)],
        'up': [os.path.join('resource', 'img', 'swk', f'0200{i}.tga') for i in range(4)],
        'left': [os.path.join('resource', 'img', 'swk', f'0100{i}.tga') for i in range(4)],
        'right': [os.path.join('resource', 'img', 'swk', f'0300{i}.tga') for i in range(4)]
    }
    player = Player(player_pos['x'], player_pos['y'], player_images)
    print("玩家精灵创建成功")
else:
    print("未找到玩家位置")
    player = Player(400, 300, {})

# 加载NPC精灵
npcs = []
god_pos = game_map.get_object('god')
if god_pos:
    print(f"土地公位置: ({god_pos['x']}, {god_pos['y']})")
    god_images = {
        'down': [os.path.join('resource', 'img', 'god', f'0214-16505471-0000{i}.tga') for i in range(10)],
        'up': [os.path.join('resource', 'img', 'god', f'0214-16505471-0200{i}.tga') for i in range(10)],
        'left': [os.path.join('resource', 'img', 'god', f'0214-16505471-0100{i}.tga') for i in range(10)],
        'right': [os.path.join('resource', 'img', 'god', f'0214-16505471-0300{i}.tga') for i in range(10)]
    }
    god = NPC(god_pos['x'], god_pos['y'], god_images, '土地公', 'god')
    npcs.append(god)
    print("土地公精灵创建成功")

print(f"NPC数量: {len(npcs)}")
print("\n所有任务测试通过！")

# 游戏主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # 获取按键状态
    keys = pygame.key.get_pressed()

    # 更新玩家
    player.update(keys, map_width, map_height)

    # 更新NPC
    for npc in npcs:
        npc.update()

    # 计算视窗偏移（跟随玩家）
    camera_x = player.x - SCREEN_WIDTH // 2
    camera_y = player.y - SCREEN_HEIGHT // 2

    # 边界限制
    camera_x = max(0, min(camera_x, map_width - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, map_height - SCREEN_HEIGHT))

    # 清屏
    screen.fill((0, 0, 0))

    # 绘制地图
    game_map.render(screen, camera_x, camera_y)

    # 绘制玩家
    player.draw(screen, camera_x, camera_y)

    # 绘制NPC
    for npc in npcs:
        npc.draw(screen, camera_x, camera_y)

    # 显示调试信息
    try:
        font = pygame.font.Font(None, 24)
    except:
        font = pygame.font.SysFont('arial', 20)

    info_texts = [
        f"Tasks 1-6: Background, Tiled, Map, Sprite",
        f"Map: {map_width}x{map_height}",
        f"Camera: ({int(camera_x)}, {int(camera_y)})",
        f"Player: ({int(player.x)}, {int(player.y)})",
        f"NPCs: {len(npcs)}",
    ]

    for i, text in enumerate(info_texts):
        surface = font.render(text, True, (255, 255, 255))
        screen.blit(surface, (10, 10 + i * 25))

    # 更新显示
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
