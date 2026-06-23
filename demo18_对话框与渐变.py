"""
任务18-20：对话框 & 场景渐入渐出
- Task 18: 对话框的实现（Pygame文字绘制）
- Task 19: 场景切换渐入渐出（RGBA透明度）
- Task 20: 场景渐入渐出封装（状态机设计）
"""
import pygame
import os
import sys
import enum
import pytmx
from pytmx.util_pygame import load_pygame

# 初始化Pygame
pygame.init()
pygame.display.set_mode((1, 1))

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("西游记·观音院 - Task 18-20: 对话框 & 场景渐变")

# 时钟
clock = pygame.time.Clock()
FPS = 60

# ========== Task 20: 场景状态枚举 ==========
class SceneStatus(enum.IntEnum):
    """场景状态"""
    In = 1      # 渐入
    Normal = 2  # 正常显示
    Out = 3     # 渐出

# ========== Task 20: 场景渐入渐出封装 ==========
class FadeScene:
    """场景渐入渐出类 - 有限状态机"""

    def __init__(self, back_image):
        self.back_image = back_image
        self.alpha = 0
        self.status = SceneStatus.In

    def set_status(self, status):
        """设置场景状态"""
        self.status = status
        if status == SceneStatus.In:
            self.alpha = 0
        if status == SceneStatus.Normal:
            self.alpha = 255
        if status == SceneStatus.Out:
            self.alpha = 0

    def get_out(self):
        """检查是否完成渐出"""
        return self.status == SceneStatus.Out and self.alpha == 255

    def get_back_image(self, x, y):
        """获取带渐变效果的背景图像"""
        # 边界限制
        x = max(0, min(x, self.back_image.get_width() - SCREEN_WIDTH))
        y = max(0, min(y, self.back_image.get_height() - SCREEN_HEIGHT))

        # 截取视窗范围
        temp_surface = self.back_image.subsurface((x, y, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.status == SceneStatus.Normal:
            return temp_surface
        elif self.status == SceneStatus.In:
            # 渐入效果
            temp_surface.set_alpha(self.alpha)
            black_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            black_surface.blit(temp_surface, (0, 0))
            self.alpha += 20
            if self.alpha >= 255:
                self.alpha = 0
                self.status = SceneStatus.Normal
            return black_surface
        elif self.status == SceneStatus.Out:
            # 渐出效果
            temp_surface.set_alpha(255 - self.alpha)
            black_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            black_surface.blit(temp_surface, (0, 0))
            self.alpha += 20
            if self.alpha >= 255:
                self.alpha = 255
            return black_surface

# ========== Task 18: 对话框类 ==========
class DialogueBox:
    """对话框类"""

    def __init__(self):
        self.active = False
        self.text = ""
        self.speaker = ""
        self.box_height = 120
        self.box_y = SCREEN_HEIGHT - self.box_height - 20

        # 创建对话框表面
        self.box_surface = pygame.Surface((SCREEN_WIDTH - 40, self.box_height), pygame.SRCALPHA)
        self.box_surface.fill((0, 0, 0, 200))

        # 字体
        try:
            self.font = pygame.font.Font(None, 28)
            self.name_font = pygame.font.Font(None, 32)
        except:
            self.font = pygame.font.SysFont('arial', 24)
            self.name_font = pygame.font.SysFont('arial', 28)

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
            if self.font.size(test_line)[0] < SCREEN_WIDTH - 100:
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
        hint_surface = self.font.render("按空格键继续...", True, (200, 200, 200))
        surface.blit(hint_surface, (SCREEN_WIDTH - 200, self.box_y + self.box_height - 30))

# ========== 加载TMX地图 ==========
map_file = 'resource/tmx/village.tmx'
tmx_data = load_pygame(map_file)

# 地图尺寸
map_width = tmx_data.width * tmx_data.tilewidth
map_height = tmx_data.height * tmx_data.tileheight

# ========== 渲染地图函数 ==========
def render_map(surface, tmx_data, offset_x=0, offset_y=0):
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

def get_object_position(tmx_data, object_name):
    for obj in tmx_data.objects:
        if obj.name == object_name:
            return (obj.x, obj.y)
    return None

def get_objects_by_layer(tmx_data, layer_name):
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

def load_animation_frames(base_path, prefix, count, size=(64, 64)):
    frames = []
    for i in range(count):
        path = os.path.join(base_path, f"{prefix}{i:05d}.tga")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    return frames if frames else [pygame.Surface(size, pygame.SRCALPHA)]

def load_sprite_image(path, size=(64, 64)):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    else:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((255, 0, 0, 128))
        return surf

# ========== 玩家类 ==========
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3
        self.direction = 'down'
        self.moving = False
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15

        self.frames = {
            'down': load_animation_frames('resource/img/swk', '0000', 4),
            'up': load_animation_frames('resource/img/swk', '0100', 4),
            'left': load_animation_frames('resource/img/swk', '0200', 4),
            'right': load_animation_frames('resource/img/swk', '0300', 4),
        }
        self.image = self.frames['down'][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, keys, obstacles):
        dx = 0
        dy = 0
        self.moving = False

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

        new_x = self.x + dx
        new_y = self.y + dy

        new_x = max(0, min(new_x, map_width - self.rect.width))
        new_y = max(0, min(new_y, map_height - self.rect.height))

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

        self.x = new_x
        self.y = new_y
        self.rect.topleft = (self.x, self.y)

        if self.moving:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
                self.image = self.frames[self.direction][self.current_frame]
        else:
            self.current_frame = 0
            self.image = self.frames[self.direction][0]

    def draw(self, surface, offset_x, offset_y):
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        surface.blit(self.image, (screen_x, screen_y))

# ========== NPC类 ==========
class NPC:
    def __init__(self, x, y, name="NPC", move_range=100, move_speed=1):
        self.x = x
        self.y = y
        self.name = name
        self.speed = move_speed
        self.start_x = x
        self.start_y = y
        self.move_range = move_range

        self.step_count = 0
        self.max_steps = move_range // move_speed
        self.move_direction_x = 1
        self.move_direction_y = 1
        self.current_axis = 'y'

        self.current_frame = 0
        self.animation_timer = 0
        self.moving = True

        self.frames = {
            'down': load_animation_frames('resource/img/elder', 'elder1-000', 4),
        }
        self.image = self.frames['down'][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, *args):
        dx = 0
        dy = 0

        if self.current_axis == 'x':
            dx = self.speed * self.move_direction_x
        else:
            dy = self.speed * self.move_direction_y

        self.x += dx
        self.y += dy
        self.step_count += 1

        self.x = max(0, min(self.x, map_width - self.rect.width))
        self.y = max(0, min(self.y, map_height - self.rect.height))

        if self.step_count >= self.max_steps:
            self.step_count = 0
            self._change_direction()

        self.rect.topleft = (self.x, self.y)

        self.animation_timer += 0.15
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames['down'])
            self.image = self.frames['down'][self.current_frame]

    def _change_direction(self):
        if self.current_axis == 'y':
            self.current_axis = 'x'
            self.move_direction_x *= -1
        else:
            self.current_axis = 'y'
            self.move_direction_y *= -1

    def draw(self, surface, offset_x, offset_y):
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        surface.blit(self.image, (screen_x, screen_y))

# ========== 创建对象 ==========
print("\n" + "=" * 50)
print("Task 18-20: 对话框 & 场景渐变")
print("=" * 50)

# 创建玩家
player_pos = get_object_position(tmx_data, 'sun')
player = Player(player_pos[0], player_pos[1]) if player_pos else Player(400, 300)

# 创建NPC
elder_objects = get_objects_by_layer(tmx_data, 'elder')
npcs = []
for elder in elder_objects:
    npc = NPC(elder['x'], elder['y'], elder['name'], move_range=80, move_speed=1)
    npcs.append(npc)

child_objects = get_objects_by_layer(tmx_data, 'child')
for child in child_objects:
    npc = NPC(child['x'], child['y'], child['name'], move_range=60, move_speed=1)
    npcs.append(npc)

# 土地公
god_pos = get_object_position(tmx_data, 'god')
god_img = load_sprite_image('resource/img/god/0214-16505471-00000.tga') if god_pos else None

# 障碍物
obstacles = get_obstacles(tmx_data)

# Task 18: 创建对话框
dialogue = DialogueBox()

# Task 20: 创建场景渐变（这里用黑色背景演示）
fade_scene = FadeScene(screen)
fade_scene.set_status(SceneStatus.In)

print(f"玩家: ({player.x}, {player.y})")
print(f"NPC数量: {len(npcs)}")
print(f"障碍物: {len(obstacles)}")

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
            elif event.key == pygame.K_SPACE:
                if dialogue.active:
                    dialogue.hide()
                else:
                    # 检测是否碰到NPC
                    for npc in npcs:
                        if player.rect.colliderect(npc.rect):
                            dialogue.show(npc.name, f"你好，旅行者！我是{npc.name}。观音院就在前方...")
                            break

    keys = pygame.key.get_pressed()

    # 更新玩家（对话框显示时不能移动）
    if not dialogue.active:
        player.update(keys, obstacles)

    # 更新NPC
    for npc in npcs:
        npc.update()

    # Task 13: 计算视窗偏移
    camera_x = player.x - SCREEN_WIDTH // 2
    camera_y = player.y - SCREEN_HEIGHT // 2
    camera_x = max(0, min(camera_x, map_width - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, map_height - SCREEN_HEIGHT))

    # 清屏
    screen.fill((0, 0, 0))

    # Task 20: 使用渐变效果绘制地图
    if fade_scene.status != SceneStatus.Normal:
        # 渐变状态下使用FadeScene
        map_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        render_map(map_surface, tmx_data, camera_x, camera_y)
        screen.blit(map_surface, (0, 0))
    else:
        render_map(screen, tmx_data, camera_x, camera_y)

    # 绘制障碍物
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

    # Task 18: 绘制对话框
    dialogue.draw(screen)

    # 显示调试信息
    try:
        font = pygame.font.Font(None, 24)
    except:
        font = pygame.font.SysFont('arial', 20)

    info_texts = [
        "Task 18-20: Dialogue & Scene Fade",
        f"Player: ({int(player.x)}, {int(player.y)})",
        f"NPCs: {len(npcs)} | Obstacles: {len(obstacles)}",
        f"Dialogue: {'ON' if dialogue.active else 'OFF'} | Fade: {fade_scene.status.name}",
        "Arrow Keys: Move | SPACE: Talk | F1: Obstacles",
    ]

    for i, text in enumerate(info_texts):
        surface = font.render(text, True, (255, 255, 255))
        screen.blit(surface, (10, 10 + i * 25))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
