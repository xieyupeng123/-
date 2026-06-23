"""
任务21-26：寺庙场景 & 打斗 & 声音 & 游戏结构
- Task 21: 第二个寺庙场景建立和渐入渐出实现
- Task 22: 怪物封装加载
- Task 23: 玩家怪物打斗的设计封装
- Task 24: 玩家与怪物打斗场景设计
- Task 25: 声音和音效
- Task 26: 游戏结构代码实现
"""
import pygame
import os
import sys
import enum
import random
import pytmx
from pytmx.util_pygame import load_pygame

# 初始化Pygame
pygame.init()
pygame.display.set_mode((1, 1))

# 初始化声音模块（Task 25）
pygame.mixer.init()

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("西游记·观音院 - Task 21-26: 寺庙场景 & 打斗")

# 时钟
clock = pygame.time.Clock()
FPS = 60

# ========== Task 26: 游戏状态枚举 ==========
class GameState(enum.IntEnum):
    """游戏状态"""
    Village = 1      # 村庄场景
    Temple = 2       # 寺庙场景
    Battle = 3       # 打斗场景
    GameOver = 4     # 游戏结束
    Victory = 5      # 胜利

class SceneStatus(enum.IntEnum):
    """场景过渡状态"""
    In = 1
    Normal = 2
    Out = 3

# ========== Task 20: 场景渐入渐出 ==========
class FadeScene:
    def __init__(self, back_image):
        self.back_image = back_image
        self.alpha = 0
        self.status = SceneStatus.In

    def set_status(self, status):
        self.status = status
        if status == SceneStatus.In:
            self.alpha = 0
        if status == SceneStatus.Normal:
            self.alpha = 255
        if status == SceneStatus.Out:
            self.alpha = 0

    def get_out(self):
        return self.status == SceneStatus.Out and self.alpha == 255

    def get_back_image(self, x, y):
        x = max(0, min(x, self.back_image.get_width() - SCREEN_WIDTH))
        y = max(0, min(y, self.back_image.get_height() - SCREEN_HEIGHT))

        temp_surface = self.back_image.subsurface((x, y, SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.status == SceneStatus.Normal:
            return temp_surface
        elif self.status == SceneStatus.In:
            temp_surface.set_alpha(self.alpha)
            black_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            black_surface.blit(temp_surface, (0, 0))
            self.alpha += 20
            if self.alpha >= 255:
                self.alpha = 0
                self.status = SceneStatus.Normal
            return black_surface
        elif self.status == SceneStatus.Out:
            temp_surface.set_alpha(255 - self.alpha)
            black_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            black_surface.blit(temp_surface, (0, 0))
            self.alpha += 20
            if self.alpha >= 255:
                self.alpha = 255
            return black_surface

# ========== Task 18: 对话框 ==========
class DialogueBox:
    def __init__(self):
        self.active = False
        self.text = ""
        self.speaker = ""
        self.box_height = 120
        self.box_y = SCREEN_HEIGHT - self.box_height - 20

        self.box_surface = pygame.Surface((SCREEN_WIDTH - 40, self.box_height), pygame.SRCALPHA)
        self.box_surface.fill((0, 0, 0, 200))

        try:
            self.font = pygame.font.Font(None, 28)
            self.name_font = pygame.font.Font(None, 32)
        except:
            self.font = pygame.font.SysFont('arial', 24)
            self.name_font = pygame.font.SysFont('arial', 28)

    def show(self, speaker, text):
        self.active = True
        self.speaker = speaker
        self.text = text

    def hide(self):
        self.active = False

    def draw(self, surface):
        if not self.active:
            return

        surface.blit(self.box_surface, (20, self.box_y))

        name_surface = self.name_font.render(self.speaker, True, (255, 255, 0))
        surface.blit(name_surface, (40, self.box_y + 10))

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

        for i, line in enumerate(lines[:3]):
            text_surface = self.font.render(line, True, (255, 255, 255))
            surface.blit(text_surface, (40, self.box_y + 45 + i * 25))

        hint_surface = self.font.render("按空格键继续...", True, (200, 200, 200))
        surface.blit(hint_surface, (SCREEN_WIDTH - 200, self.box_y + self.box_height - 30))

# ========== 辅助函数 ==========
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

def load_map(filename):
    """加载TMX地图"""
    tmx_data = load_pygame(filename)
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    return tmx_data, map_width, map_height

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

# ========== Task 11+15: 玩家类 ==========
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

        # 打斗状态（Task 23）
        self.hp = 100
        self.attack_power = 10
        self.is_attacking = False
        self.attack_timer = 0

    def update(self, keys, obstacles, in_dialogue=False):
        if in_dialogue:
            return

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

        new_x = max(0, min(new_x, 3780 - self.rect.width))
        new_y = max(0, min(new_y, 2395 - self.rect.height))

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

# ========== Task 12: NPC类 ==========
class NPC:
    def __init__(self, x, y, name="NPC", move_range=100, move_speed=1):
        self.x = x
        self.y = y
        self.name = name
        self.speed = move_speed
        self.move_range = move_range

        self.step_count = 0
        self.max_steps = move_range // move_speed
        self.move_direction_x = 1
        self.move_direction_y = 1
        self.current_axis = 'y'

        self.current_frame = 0
        self.animation_timer = 0

        self.frames = {
            'down': load_animation_frames('resource/img/elder', 'elder1-000', 4),
        }
        self.image = self.frames['down'][0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        dx = 0
        dy = 0

        if self.current_axis == 'x':
            dx = self.speed * self.move_direction_x
        else:
            dy = self.speed * self.move_direction_y

        self.x += dx
        self.y += dy
        self.step_count += 1

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

# ========== Task 22: 怪物类 ==========
class Monster:
    """怪物类 - 寺庙场景中的敌人"""

    def __init__(self, x, y, name="Monster", hp=50, attack=5):
        self.x = x
        self.y = y
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.alive = True

        # 动画
        self.current_frame = 0
        self.animation_timer = 0
        self.frames = load_animation_frames('resource/img/elder', 'elder1-000', 4)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        # 移动
        self.speed = 1
        self.move_timer = 0
        self.move_interval = 60

    def update(self):
        if not self.alive:
            return

        # 简单的随机移动
        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            dx = random.choice([-1, 0, 1]) * self.speed * 10
            dy = random.choice([-1, 0, 1]) * self.speed * 10
            self.x = max(0, min(self.x + dx, 800 - self.rect.width))
            self.y = max(0, min(self.y + dy, 600 - self.rect.height))
            self.rect.topleft = (self.x, self.y)

        # 动画
        self.animation_timer += 0.15
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def take_damage(self, damage):
        """受到伤害"""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def draw(self, surface, offset_x=0, offset_y=0):
        if not self.alive:
            return

        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        surface.blit(self.image, (screen_x, screen_y))

        # 绘制血条
        bar_width = 50
        bar_height = 5
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (255, 0, 0), (screen_x, screen_y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (screen_x, screen_y - 10, bar_width * hp_ratio, bar_height))

# ========== Task 23: 打斗场景类 ==========
class BattleScene:
    """打斗场景类"""

    def __init__(self):
        self.active = False
        self.player = None
        self.monster = None
        self.battle_log = []
        self.turn = 'player'  # 'player' or 'monster'
        self.battle_timer = 0

        try:
            self.font = pygame.font.Font(None, 28)
        except:
            self.font = pygame.font.SysFont('arial', 24)

    def start_battle(self, player, monster):
        """开始战斗"""
        self.active = True
        self.player = player
        self.monster = monster
        self.battle_log = [f"遭遇 {monster.name}！战斗开始！"]
        self.turn = 'player'
        self.battle_timer = 0

    def player_attack(self):
        """玩家攻击"""
        if self.turn != 'player' or not self.monster.alive:
            return

        damage = self.player.attack_power + random.randint(0, 5)
        self.monster.take_damage(damage)
        self.battle_log.append(f"孙悟空攻击 {self.monster.name}，造成 {damage} 点伤害！")

        if not self.monster.alive:
            self.battle_log.append(f"{self.monster.name} 被击败！")
            self.active = False
        else:
            self.turn = 'monster'
            self.battle_timer = 0

    def monster_attack(self):
        """怪物攻击"""
        if self.turn != 'monster' or not self.monster.alive:
            return

        damage = self.monster.attack + random.randint(0, 3)
        self.player.hp -= damage
        self.battle_log.append(f"{self.monster.name} 攻击孙悟空，造成 {damage} 点伤害！")

        if self.player.hp <= 0:
            self.player.hp = 0
            self.battle_log.append("孙悟空被击败！游戏结束！")
            self.active = False
        else:
            self.turn = 'player'
            self.battle_timer = 0

    def update(self):
        if not self.active:
            return

        self.battle_timer += 1

        # 怪物自动攻击
        if self.turn == 'monster' and self.battle_timer > 30:
            self.monster_attack()

    def draw(self, surface):
        if not self.active:
            return

        # 绘制战斗背景
        battle_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        battle_bg.fill((0, 0, 0, 180))
        surface.blit(battle_bg, (0, 0))

        # 绘制玩家信息
        player_text = f"孙悟空 HP: {self.player.hp}/100"
        surface.blit(self.font.render(player_text, True, (0, 255, 0)), (50, 200))

        # 绘制怪物信息
        if self.monster:
            monster_text = f"{self.monster.name} HP: {self.monster.hp}/{self.monster.max_hp}"
            surface.blit(self.font.render(monster_text, True, (255, 0, 0)), (550, 200))

        # 绘制战斗日志
        for i, log in enumerate(self.battle_log[-5:]):
            surface.blit(self.font.render(log, True, (255, 255, 255)), (50, 350 + i * 30))

        # 绘制提示
        if self.turn == 'player':
            hint = "按空格键攻击！"
            surface.blit(self.font.render(hint, True, (255, 255, 0)), (300, 500))

# ========== Task 25: 声音管理 ==========
class SoundManager:
    """声音管理类"""

    def __init__(self):
        self.sounds = {}
        self.music_loaded = False

    def load_sound(self, name, path):
        """加载音效"""
        if os.path.exists(path):
            try:
                sound = pygame.mixer.Sound(path)
                self.sounds[name] = sound
            except:
                print(f"无法加载音效: {path}")

    def load_music(self, path):
        """加载背景音乐"""
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                self.music_loaded = True
            except:
                print(f"无法加载音乐: {path}")

    def play_music(self, loops=-1):
        """播放背景音乐"""
        if self.music_loaded:
            pygame.mixer.music.play(loops)

    def play_sound(self, name):
        """播放音效"""
        if name in self.sounds:
            self.sounds[name].play()

# ========== 加载地图 ==========
print("\n" + "=" * 50)
print("Task 21-26: 寺庙场景 & 打斗 & 声音")
print("=" * 50)

# 村庄地图
village_map_file = 'resource/tmx/village.tmx'
village_tmx, village_width, village_height = load_map(village_map_file)
village_obstacles = get_obstacles(village_tmx)

# 寺庙地图（尝试加载，如果不存在则使用村庄地图）
temple_map_file = 'resource/tmx/temple.tmx'
if os.path.exists(temple_map_file):
    temple_tmx, temple_width, temple_height = load_map(temple_map_file)
else:
    print("[INFO] 寺庙地图不存在，使用村庄地图作为替代")
    temple_tmx, temple_width, temple_height = village_tmx, village_width, village_height

# 创建玩家
player_pos = get_object_position(village_tmx, 'sun')
player = Player(player_pos[0], player_pos[1]) if player_pos else Player(400, 300)

# 创建NPC（村庄）
elder_objects = []
for obj in village_tmx.objects:
    if hasattr(obj, 'group') and obj.group == 'elder':
        elder_objects.append({
            'name': obj.name,
            'x': obj.x,
            'y': obj.y
        })

npcs = []
for elder in elder_objects:
    npc = NPC(elder['x'], elder['y'], elder['name'], move_range=80, move_speed=1)
    npcs.append(npc)

# 土地公
god_pos = get_object_position(village_tmx, 'god')
god_img = load_sprite_image('resource/img/god/0214-16505471-00000.tga') if god_pos else None

# Task 22: 创建怪物（寺庙场景）
monsters = []
monster_positions = [(200, 200), (400, 300), (600, 200)]
for i, (mx, my) in enumerate(monster_positions):
    monster = Monster(mx, my, f"妖怪{i+1}", hp=50, attack=5)
    monsters.append(monster)
    print(f"[OK] 怪物创建: {monster.name} ({mx}, {my})")

# Task 18: 对话框
dialogue = DialogueBox()

# Task 23: 打斗场景
battle_scene = BattleScene()

# Task 25: 声音管理
sound_manager = SoundManager()
# sound_manager.load_music('resource/sound/bgm.mp3')  # 如果有背景音乐

# Task 20: 场景渐变
fade_scene = FadeScene(screen)
fade_scene.set_status(SceneStatus.In)

# 游戏状态（Task 26）
game_state = GameState.Village
current_tmx = village_tmx
current_obstacles = village_obstacles

# 场景切换位置
temple_entrance = (2800, 800)  # 寺庙入口位置

print(f"玩家: ({player.x}, {player.y})")
print(f"NPC: {len(npcs)}")
print(f"怪物: {len(monsters)}")
print(f"障碍物: {len(village_obstacles)}")

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
                elif battle_scene.active:
                    battle_scene.player_attack()
                else:
                    # 检测NPC对话
                    for npc in npcs:
                        if player.rect.colliderect(npc.rect):
                            dialogue.show(npc.name, f"你好！观音院就在前方...")
                            break

    keys = pygame.key.get_pressed()

    # 更新游戏逻辑
    if game_state == GameState.Village:
        # 村庄场景
        if not dialogue.active:
            player.update(keys, village_obstacles)

        # 检测是否到达寺庙入口
        if god_pos:
            dist = ((player.x - temple_entrance[0])**2 + (player.y - temple_entrance[1])**2)**0.5
            if dist < 100:
                game_state = GameState.Temple
                fade_scene.set_status(SceneStatus.Out)
                player.x = 400
                player.y = 300
                print("进入寺庙场景！")

    elif game_state == GameState.Temple:
        # 寺庙场景
        if not battle_scene.active:
            player.update(keys, [])

        # 更新怪物
        for monster in monsters:
            if monster.alive:
                monster.update()
                # 检测玩家与怪物碰撞
                if player.rect.colliderect(monster.rect):
                    battle_scene.start_battle(player, monster)
                    game_state = GameState.Battle

    elif game_state == GameState.Battle:
        # 打斗场景
        battle_scene.update()
        if not battle_scene.active:
            if player.hp <= 0:
                game_state = GameState.GameOver
            else:
                game_state = GameState.Temple

    # 更新NPC
    for npc in npcs:
        npc.update()

    # 计算视窗偏移
    camera_x = player.x - SCREEN_WIDTH // 2
    camera_y = player.y - SCREEN_HEIGHT // 2
    camera_x = max(0, min(camera_x, 3780 - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, 2395 - SCREEN_HEIGHT))

    # 清屏
    screen.fill((0, 0, 0))

    # 绘制地图
    if game_state == GameState.Village:
        render_map(screen, village_tmx, camera_x, camera_y)
    else:
        render_map(screen, temple_tmx, camera_x, camera_y)

    # 绘制障碍物
    if show_obstacles:
        for obs in current_obstacles:
            pygame.draw.rect(screen, (255, 0, 0),
                           (obs.x - camera_x, obs.y - camera_y, obs.width, obs.height), 2)

    # 绘制NPC
    for npc in npcs:
        npc.draw(screen, camera_x, camera_y)

    # 绘制土地公
    if god_img and god_pos:
        screen.blit(god_img, (god_pos[0] - camera_x, god_pos[1] - camera_y))

    # 绘制怪物
    for monster in monsters:
        if monster.alive:
            monster.draw(screen, camera_x, camera_y)

    # 绘制玩家
    player.draw(screen, camera_x, camera_y)

    # 绘制对话框
    dialogue.draw(screen)

    # 绘制打斗场景
    battle_scene.draw(screen)

    # 显示调试信息
    try:
        font = pygame.font.Font(None, 24)
    except:
        font = pygame.font.SysFont('arial', 20)

    info_texts = [
        f"Task 21-26 | State: {game_state.name}",
        f"Player: ({int(player.x)}, {int(player.y)}) HP: {player.hp}",
        f"Monsters: {sum(1 for m in monsters if m.alive)}/{len(monsters)}",
        f"NPCs: {len(npcs)} | Obstacles: {len(current_obstacles)}",
        "Arrow: Move | SPACE: Talk/Attack | F1: Obstacles | ESC: Quit",
    ]

    for i, text in enumerate(info_texts):
        surface = font.render(text, True, (255, 255, 255))
        screen.blit(surface, (10, 10 + i * 25))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
