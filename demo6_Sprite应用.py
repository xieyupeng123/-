"""
任务6：Sprite应用
从TMX地图中读取对象位置，加载并绘制精灵
"""
import pygame
import os
import sys
import pytmx
from pytmx.util_pygame import load_pygame

# 初始化Pygame
pygame.init()
pygame.display.set_mode((1, 1))

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("西游记·观音院 - 任务6：Sprite应用")

# 时钟
clock = pygame.time.Clock()
FPS = 60

# ========== 加载TMX地图 ==========
map_file = 'resource/tmx/village.tmx'
tmx_data = load_pygame(map_file)

# 地图尺寸
map_width = tmx_data.width * tmx_data.tilewidth
map_height = tmx_data.height * tmx_data.tileheight
print(f"地图尺寸: {map_width}x{map_height}")

# ========== 渲染地图函数 ==========
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

# ========== 获取地图对象位置 ==========
def get_object_position(tmx_data, object_name):
    """获取指定名称的对象位置"""
    for obj in tmx_data.objects:
        if obj.name == object_name:
            return (obj.x, obj.y)
    return None

def get_objects_by_layer(tmx_data, layer_name):
    """获取指定图层的所有对象"""
    objects = []
    for obj in tmx_data.objects:
        if hasattr(obj, 'group') and obj.group == layer_name:
            objects.append({
                'name': obj.name,
                'x': obj.x,
                'y': obj.y
            })
    return objects

# ========== 加载精灵图像 ==========
def load_sprite_image(path, size=(64, 64)):
    """加载精灵图像"""
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    else:
        # 创建占位符
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((255, 0, 0, 128))
        return surf

# ========== 从地图加载精灵 ==========
print("\n" + "=" * 50)
print("从TMX地图加载精灵位置")
print("=" * 50)

# 加载玩家精灵（孙悟空）
player_pos = get_object_position(tmx_data, 'sun')
if player_pos:
    print(f"[OK] 玩家（孙悟空）位置: ({player_pos[0]}, {player_pos[1]})")
    player_img = load_sprite_image('resource/img/swk/00000.tga')
else:
    print("[FAIL] 未找到玩家位置")
    player_pos = (400, 300)
    player_img = load_sprite_image('resource/img/swk/00000.tga')

# 加载土地公
god_pos = get_object_position(tmx_data, 'god')
if god_pos:
    print(f"[OK] 土地公位置: ({god_pos[0]}, {god_pos[1]})")
    god_img = load_sprite_image('resource/img/god/0214-16505471-00000.tga')
else:
    print("[FAIL] 未找到土地公位置")
    god_pos = (600, 500)
    god_img = load_sprite_image('resource/img/god/0214-16505471-00000.tga')

# 加载长老NPC
elder_objects = get_objects_by_layer(tmx_data, 'elder')
elder_images = []
for elder in elder_objects:
    print(f"[OK] 长老 {elder['name']} 位置: ({elder['x']}, {elder['y']})")
    elder_img = load_sprite_image('resource/img/elder/elder1-00000.tga')
    elder_images.append({
        'name': elder['name'],
        'x': elder['x'],
        'y': elder['y'],
        'image': elder_img
    })

# 加载孩子NPC
child_objects = get_objects_by_layer(tmx_data, 'child')
child_images = []
for child in child_objects:
    print(f"[OK] 孩子 {child['name']} 位置: ({child['x']}, {child['y']})")
    # 使用长老图像作为占位符
    child_img = load_sprite_image('resource/img/elder/elder1-00000.tga')
    child_images.append({
        'name': child['name'],
        'x': child['x'],
        'y': child['y'],
        'image': child_img
    })

print(f"\n共加载 {1 + 1 + len(elder_images) + len(child_images)} 个精灵")

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

    # 计算视窗偏移（跟随玩家）
    camera_x = player_pos[0] - SCREEN_WIDTH // 2
    camera_y = player_pos[1] - SCREEN_HEIGHT // 2

    # 边界限制
    camera_x = max(0, min(camera_x, map_width - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, map_height - SCREEN_HEIGHT))

    # 清屏
    screen.fill((0, 0, 0))

    # 绘制地图
    render_map(screen, tmx_data, camera_x, camera_y)

    # 绘制玩家（孙悟空）
    screen.blit(player_img, (player_pos[0] - camera_x, player_pos[1] - camera_y))

    # 绘制土地公
    screen.blit(god_img, (god_pos[0] - camera_x, god_pos[1] - camera_y))

    # 绘制长老NPC
    for elder in elder_images:
        screen.blit(elder['image'], (elder['x'] - camera_x, elder['y'] - camera_y))

    # 绘制孩子NPC
    for child in child_images:
        screen.blit(child['image'], (child['x'] - camera_x, child['y'] - camera_y))

    # 显示调试信息
    try:
        font = pygame.font.Font(None, 24)
    except:
        font = pygame.font.SysFont('arial', 20)

    info_texts = [
        "Task 6: Sprite Application",
        f"Map: {map_width}x{map_height}",
        f"Player(sun): ({int(player_pos[0])}, {int(player_pos[1])})",
        f"God: ({int(god_pos[0])}, {int(god_pos[1])})",
        f"Elders: {len(elder_images)}, Children: {len(child_images)}",
    ]

    for i, text in enumerate(info_texts):
        surface = font.render(text, True, (255, 255, 255))
        screen.blit(surface, (10, 10 + i * 25))

    # 更新显示
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
