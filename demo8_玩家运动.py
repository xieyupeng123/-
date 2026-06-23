"""
任务8-12：Sprite对象运动 & 键盘操控 & NPC徘徊
- Task 8: Sprite对象自主运动（位置变化 + 帧动画）
- Task 9: 其他精灵封装
- Task 10: 动画效果类封装（4方向行走动画）
- Task 11: 玩家角色键盘操控（方向键控制）
- Task 12: NPC徘徊运动（记步切换方向）
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
pygame.display.set_caption("西游记·观音院 - Task 8-12: 玩家键盘操控 & NPC徘徊")

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
                'y': obj.y,
                'width': getattr(obj, 'width', 0),
                'height': getattr(obj, 'height', 0)
            })
    return objects

def get_obstacles(tmx_data):
    """获取所有障碍物"""
    obstacles = []
    for obj in tmx_data.objects:
        obj_group = getattr(obj, 'group', '')
        if obj_group == 'obstacle':
            if obj.width > 0 and obj.height > 0:
                obstacles.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        elif obj_group == 'road':
            if hasattr(obj, 'points') and obj.points:
                points = obj.points
                min_x = min(p[0] for p in points) + obj.x
                min_y = min(p[1] for p in points) + obj.y
                max_x = max(p[0] for p in points) + obj.x
                max_y = max(p[1] for p in points) + obj.y
                obstacles.append(pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y))
    return obstacles

# ========== 加载动画帧 ==========
def load_animation_frames(base_path, prefix, count, size=(64, 64)):
    """加载动画帧序列"""
    frames = []
    for i in range(count):
        path = os.path.join(base_path, f"{prefix}{i:05d}.tga")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    return frames if frames else [pygame.Surface(size, pygame.SRCALPHA)]

# ========== 玩家类（Task 11: 键盘操控） ==========
class Player:
    """玩家精灵类 - 支持4方向行走动画和键盘控制"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3
        self.direction = 'down'  # 当前方向
        self.moving = False
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15

        # 加载4方向动画帧
        self.frames = {
            'down': load_animation_frames('resource/img/swk', '0000', 4),
            'up': load_animation_frames('resource/img/swk', '0100', 4),
            'left': load_animation_frames('resource/img/swk', '0200', 4),
            'right': load_animation_frames('resource/img/swk', '0300', 4),
        }
        self.image = self.frames['down'][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, keys, obstacles):
        """更新玩家位置（键盘控制）"""
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
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
                self.image = self.frames[self.direction][self.current_frame]
        else:
            # 站立时显示第0帧
            self.current_frame = 0
            self.image = self.frames[self.direction][0]

    def draw(self, surface, offset_x, offset_y):
        """绘制玩家"""
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        surface.blit(self.image, (screen_x, screen_y))

# ========== NPC类（Task 12: 徘徊运动） ==========
class NPC:
    """NPC精灵类 - 支持徘徊运动（记步切换方向）"""

    def __init__(self, x, y, name="NPC", move_range=100, move_speed=1):
        self.x = x
        self.y = y
        self.name = name
        self.speed = move_speed
        self.start_x = x
        self.start_y = y
        self.move_range = move_range

        # 徘徊运动状态
        self.step_count = 0
        self.max_steps = move_range // move_speed
        self.move_direction_x = 1
        self.move_direction_y = 1
        self.current_axis = 'y'  # 当前移动轴

        # 动画
        self.current_frame = 0
        self.animation_timer = 0
        self.moving = True

        # 加载动画帧（使用长老图像作为占位符）
        self.frames = {
            'down': load_animation_frames('resource/img/elder', 'elder1-000', 4),
        }
        self.image = self.frames['down'][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, *args):
        """更新NPC位置（徘徊运动）"""
        # Task 12: NPC徘徊运动 - 记步切换方向
        dx = 0
        dy = 0

        if self.current_axis == 'x':
            dx = self.speed * self.move_direction_x
        else:
            dy = self.speed * self.move_direction_y

        self.x += dx
        self.y += dy
        self.step_count += 1

        # 边界检测
        self.x = max(0, min(self.x, map_width - self.rect.width))
        self.y = max(0, min(self.y, map_height - self.rect.height))

        # 记步切换方向
        if self.step_count >= self.max_steps:
            self.step_count = 0
            self._change_direction()

        # 更新矩形位置
        self.rect.topleft = (self.x, self.y)

        # 更新动画
        self.animation_timer += 0.15
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames['down'])
            self.image = self.frames['down'][self.current_frame]

    def _change_direction(self):
        """切换移动方向"""
        if self.current_axis == 'y':
            self.current_axis = 'x'
            self.move_direction_x *= -1
        else:
            self.current_axis = 'y'
            self.move_direction_y *= -1

    def draw(self, surface, offset_x, offset_y):
        """绘制NPC"""
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        surface.blit(self.image, (screen_x, screen_y))

# ========== 创建精灵对象 ==========
print("\n" + "=" * 50)
print("Task 8-12: 创建精灵对象")
print("=" * 50)

# 1. 创建玩家（孙悟空）
player_pos = get_object_position(tmx_data, 'sun')
if player_pos:
    player = Player(player_pos[0], player_pos[1])
    print(f"[OK] 玩家创建成功: ({player_pos[0]}, {player_pos[1]})")
else:
    player = Player(400, 300)
    print("[WARN] 使用默认位置创建玩家")

# 2. 创建NPC（长老们）
elder_objects = get_objects_by_layer(tmx_data, 'elder')
npcs = []
for elder in elder_objects:
    npc = NPC(elder['x'], elder['y'], elder['name'], move_range=80, move_speed=1)
    npcs.append(npc)
    print(f"[OK] 长老NPC创建: {elder['name']} ({elder['x']}, {elder['y']})")

# 3. 创建NPC（孩子们）
child_objects = get_objects_by_layer(tmx_data, 'child')
for child in child_objects:
    npc = NPC(child['x'], child['y'], child['name'], move_range=60, move_speed=1)
    npcs.append(npc)
    print(f"[OK] 孩子NPC创建: {child['name']} ({child['x']}, {child['y']})")

# 4. 加载土地公（静态）
god_pos = get_object_position(tmx_data, 'god')
god_img = None
if god_pos:
    god_img = load_sprite_image('resource/img/god/0214-16505471-00000.tga')
    print(f"[OK] 土地公位置: ({god_pos[0]}, {god_pos[1]})")

# 5. 加载障碍物
obstacles = get_obstacles(tmx_data)
print(f"[OK] 障碍物数量: {len(obstacles)}")

print(f"\n精灵统计: 玩家1 + NPC{len(npcs)} = {1 + len(npcs)} 个")

# 游戏主循环
running = True
show_obstacles = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_F1:
                show_obstacles = not show_obstacles

    # 获取按键状态
    keys = pygame.key.get_pressed()

    # 更新玩家（键盘控制）
    player.update(keys, obstacles)

    # 更新NPC（徘徊运动）
    for npc in npcs:
        npc.update()

    # 计算视窗偏移
    camera_x = player.x - SCREEN_WIDTH // 2
    camera_y = player.y - SCREEN_HEIGHT // 2
    camera_x = max(0, min(camera_x, map_width - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, map_height - SCREEN_HEIGHT))

    # 清屏
    screen.fill((0, 0, 0))

    # 绘制地图
    render_map(screen, tmx_data, camera_x, camera_y)

    # 绘制障碍物（调试用）
    if show_obstacles:
        for obs in obstacles:
            pygame.draw.rect(screen, (255, 0, 0),
                           (obs.x - camera_x, obs.y - camera_y, obs.width, obs.height), 2)

    # 绘制土地公
    if god_img and god_pos:
        screen.blit(god_img, (god_pos[0] - camera_x, god_pos[1] - camera_y))

    # 绘制NPC
    for npc in npcs:
        npc.draw(screen, camera_x, camera_y)

    # 绘制玩家
    player.draw(screen, camera_x, camera_y)

    # 显示调试信息
    try:
        font = pygame.font.Font(None, 24)
    except:
        font = pygame.font.SysFont('arial', 20)

    info_texts = [
        "Task 8-12: Player Control & NPC Patrol",
        f"Player: ({int(player.x)}, {int(player.y)}) | Dir: {player.direction}",
        f"NPCs: {len(npcs)} | Moving: {player.moving}",
        f"Obstacles: {len(obstacles)} (F1: {'ON' if show_obstacles else 'OFF'})",
        "Arrow Keys: Move | ESC: Quit",
    ]

    for i, text in enumerate(info_texts):
        surface = font.render(text, True, (255, 255, 255))
        screen.blit(surface, (10, 10 + i * 25))

    # 更新显示
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

def load_sprite_image(path, size=(64, 64)):
    """加载精灵图像"""
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    else:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((255, 0, 0, 128))
        return surf
