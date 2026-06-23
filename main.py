"""
西游记·观音院 - 游戏主入口
整合所有功能的完整游戏
"""
import pygame
import os
import sys
import enum
import random
import pytmx
from pytmx.util_pygame import load_pygame

# ========== 初始化 ==========
pygame.init()
pygame.display.set_mode((1, 1))
pygame.mixer.init()

# 窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption("西游记·观音院")

# 时钟
clock = pygame.time.Clock()
FPS = 60

# ========== 游戏状态枚举 ==========
class GameState(enum.IntEnum):
    """游戏状态"""
    Menu = 0         # 主菜单
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

# ========== 场景渐入渐出 ==========
class FadeScene:
    """场景渐入渐出类"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.alpha = 0
        self.status = SceneStatus.In
        self.target_state = None

    def set_status(self, status):
        self.status = status
        if status == SceneStatus.In:
            self.alpha = 0
        elif status == SceneStatus.Normal:
            self.alpha = 255
        elif status == SceneStatus.Out:
            self.alpha = 0

    def get_out(self):
        return self.status == SceneStatus.Out and self.alpha >= 255

    def update(self):
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
        if self.status != SceneStatus.Normal:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 255 - self.alpha))
            surface.blit(overlay, (0, 0))

# ========== 对话框 ==========
class DialogueBox:
    """对话框类"""
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

        self.hp = 100
        self.max_hp = 100
        self.attack_power = 15

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

# ========== NPC类 ==========
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

# ========== 怪物类 ==========
class Monster:
    def __init__(self, x, y, name="Monster", hp=60, attack=8):
        self.x = x
        self.y = y
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.alive = True

        self.current_frame = 0
        self.animation_timer = 0
        self.frames = load_animation_frames('resource/img/elder', 'elder1-000', 4)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.speed = 1
        self.move_timer = 0
        self.move_interval = 60
        self.start_x = x
        self.start_y = y
        self.patrol_range = 100

    def update(self):
        if not self.alive:
            return

        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            dx = random.choice([-1, 0, 1]) * self.speed * 10
            dy = random.choice([-1, 0, 1]) * self.speed * 10
            new_x = self.x + dx
            new_y = self.y + dy

            # 限制移动范围
            if abs(new_x - self.start_x) < self.patrol_range:
                self.x = new_x
            if abs(new_y - self.start_y) < self.patrol_range:
                self.y = new_y

            self.rect.topleft = (self.x, self.y)

        self.animation_timer += 0.15
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def take_damage(self, damage):
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

        bar_width = 50
        bar_height = 5
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (255, 0, 0), (screen_x, screen_y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (screen_x, screen_y - 10, bar_width * hp_ratio, bar_height))

# ========== 打斗场景 ==========
class BattleScene:
    def __init__(self):
        self.active = False
        self.player = None
        self.monster = None
        self.battle_log = []
        self.turn = 'player'
        self.battle_timer = 0
        self.result = None  # 'win' or 'lose'

        try:
            self.font = pygame.font.Font(None, 28)
            self.title_font = pygame.font.Font(None, 48)
        except:
            self.font = pygame.font.SysFont('arial', 24)
            self.title_font = pygame.font.SysFont('arial', 40)

    def start_battle(self, player, monster):
        self.active = True
        self.player = player
        self.monster = monster
        self.battle_log = [f"遭遇 {monster.name}！战斗开始！"]
        self.turn = 'player'
        self.battle_timer = 0
        self.result = None

    def player_attack(self):
        if self.turn != 'player' or not self.monster.alive:
            return

        damage = self.player.attack_power + random.randint(0, 10)
        self.monster.take_damage(damage)
        self.battle_log.append(f"孙悟空攻击 {self.monster.name}，造成 {damage} 点伤害！")

        if not self.monster.alive:
            self.battle_log.append(f"{self.monster.name} 被击败！")
            self.result = 'win'
        else:
            self.turn = 'monster'
            self.battle_timer = 0

    def monster_attack(self):
        if self.turn != 'monster' or not self.monster.alive:
            return

        damage = self.monster.attack + random.randint(0, 5)
        self.player.hp -= damage
        self.battle_log.append(f"{self.monster.name} 攻击孙悟空，造成 {damage} 点伤害！")

        if self.player.hp <= 0:
            self.player.hp = 0
            self.battle_log.append("孙悟空被击败！")
            self.result = 'lose'
        else:
            self.turn = 'player'
            self.battle_timer = 0

    def update(self):
        if not self.active:
            return

        self.battle_timer += 1

        if self.turn == 'monster' and self.battle_timer > 30:
            self.monster_attack()

        if self.result:
            self.battle_timer += 1
            if self.battle_timer > 90:
                self.active = False

    def draw(self, surface):
        if not self.active:
            return

        battle_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        battle_bg.fill((0, 0, 0, 200))
        surface.blit(battle_bg, (0, 0))

        title_surface = self.title_font.render("战斗！", True, (255, 255, 0))
        surface.blit(title_surface, (SCREEN_WIDTH // 2 - 60, 50))

        player_text = f"孙悟空 HP: {self.player.hp}/{self.player.max_hp}"
        surface.blit(self.font.render(player_text, True, (0, 255, 0)), (100, 150))

        if self.monster:
            monster_text = f"{self.monster.name} HP: {self.monster.hp}/{self.monster.max_hp}"
            surface.blit(self.font.render(monster_text, True, (255, 0, 0)), (500, 150))

        for i, log in enumerate(self.battle_log[-5:]):
            surface.blit(self.font.render(log, True, (255, 255, 255)), (100, 250 + i * 35))

        if self.result == 'win':
            hint = "战斗胜利！按空格键继续"
            surface.blit(self.font.render(hint, True, (0, 255, 0)), (250, 500))
        elif self.result == 'lose':
            hint = "战斗失败！按空格键重新开始"
            surface.blit(self.font.render(hint, True, (255, 0, 0)), (230, 500))
        elif self.turn == 'player':
            hint = "按空格键攻击！"
            surface.blit(self.font.render(hint, True, (255, 255, 0)), (300, 500))

# ========== 主菜单 ==========
class MainMenu:
    def __init__(self):
        try:
            self.title_font = pygame.font.Font(None, 72)
            self.menu_font = pygame.font.Font(None, 36)
        except:
            self.title_font = pygame.font.SysFont('arial', 60)
            self.menu_font = pygame.font.SysFont('arial', 30)

        self.selected = 0
        self.options = ["开始游戏", "退出游戏"]

    def draw(self, surface):
        surface.fill((0, 0, 0))

        title = self.title_font.render("西游记·观音院", True, (255, 215, 0))
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        subtitle = self.menu_font.render("祸起观音院", True, (200, 200, 200))
        surface.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 230))

        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.menu_font.render(option, True, color)
            surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 350 + i * 60))

        hint = self.menu_font.render("使用上下方向键选择，回车键确认", True, (150, 150, 150))
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 520))

    def handle_input(self, key):
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.options)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.options)
        elif key == pygame.K_RETURN:
            return self.options[self.selected]
        return None

# ========== 游戏主类 ==========
class Game:
    def __init__(self):
        self.state = GameState.Menu
        self.fade = FadeScene(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.dialogue = DialogueBox()
        self.battle = BattleScene()
        self.menu = MainMenu()

        # 加载地图
        print("加载地图...")
        self.village_tmx, self.village_width, self.village_height = load_map('resource/tmx/village.tmx')
        self.village_obstacles = get_obstacles(self.village_tmx)

        # 尝试加载寺庙地图
        if os.path.exists('resource/tmx/temple.tmx'):
            self.temple_tmx, self.temple_width, self.temple_height = load_map('resource/tmx/temple.tmx')
        else:
            self.temple_tmx = self.village_tmx
            self.temple_width = self.village_width
            self.temple_height = self.village_height

        # 创建玩家
        player_pos = get_object_position(self.village_tmx, 'sun')
        self.player = Player(player_pos[0], player_pos[1]) if player_pos else Player(400, 300)

        # 创建NPC
        self.npcs = []
        elder_objects = get_objects_by_layer(self.village_tmx, 'elder')
        for elder in elder_objects:
            npc = NPC(elder['x'], elder['y'], elder['name'], move_range=80, move_speed=1)
            self.npcs.append(npc)

        child_objects = get_objects_by_layer(self.village_tmx, 'child')
        for child in child_objects:
            npc = NPC(child['x'], child['y'], child['name'], move_range=60, move_speed=1)
            self.npcs.append(npc)

        # 土地公
        self.god_pos = get_object_position(self.village_tmx, 'god')
        self.god_img = load_sprite_image('resource/img/god/0214-16505471-00000.tga') if self.god_pos else None

        # 怪物（寺庙场景）
        self.monsters = []
        self.spawn_monsters()

        # 寺庙入口位置
        self.temple_entrance = (2800, 800)
        self.village_spawn = (400, 300)

        self.show_obstacles = False

        print("游戏初始化完成！")

    def spawn_monsters(self):
        """生成怪物"""
        self.monsters = []
        positions = [(200, 200), (400, 350), (600, 200), (300, 450), (500, 450)]
        for i, (mx, my) in enumerate(positions):
            monster = Monster(mx, my, f"妖怪{i+1}", hp=50 + i*10, attack=5 + i*2)
            self.monsters.append(monster)

    def reset_game(self):
        """重置游戏"""
        self.player.hp = self.player.max_hp
        self.player.x = 400
        self.player.y = 300
        self.player.rect.topleft = (400, 300)
        self.spawn_monsters()
        self.state = GameState.Village
        self.fade.set_status(SceneStatus.In)

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == GameState.Menu:
                            running = False
                        elif self.battle.active:
                            pass
                        elif self.dialogue.active:
                            self.dialogue.hide()
                        else:
                            self.state = GameState.Menu

                    elif event.key == pygame.K_F1:
                        self.show_obstacles = not self.show_obstacles

                    elif event.key == pygame.K_SPACE:
                        if self.state == GameState.Menu:
                            result = self.menu.handle_input(event.key)
                            if result == "开始游戏":
                                self.state = GameState.Village
                                self.fade.set_status(SceneStatus.In)
                            elif result == "退出游戏":
                                running = False

                        elif self.dialogue.active:
                            self.dialogue.hide()

                        elif self.battle.active:
                            self.battle.player_attack()
                            if self.battle.result == 'win':
                                pass
                            elif self.battle.result == 'lose':
                                self.reset_game()

                        else:
                            # 检测NPC对话
                            for npc in self.npcs:
                                if self.player.rect.colliderect(npc.rect):
                                    if npc.name in ['elder1', 'elder2']:
                                        self.dialogue.show(npc.name, "欢迎来到观音院！这里是修行的好地方。")
                                    else:
                                        self.dialogue.show(npc.name, f"你好！我是{npc.name}。")
                                    break

                    elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                        if self.state == GameState.Menu:
                            result = self.menu.handle_input(event.key)
                            if result == "开始游戏":
                                self.state = GameState.Village
                                self.fade.set_status(SceneStatus.In)
                            elif result == "退出游戏":
                                running = False

                    elif event.key in [pygame.K_UP, pygame.K_DOWN]:
                        if self.state == GameState.Menu:
                            self.menu.handle_input(event.key)

            # 更新
            if self.state == GameState.Menu:
                pass

            elif self.state == GameState.Village:
                if not self.dialogue.active:
                    self.player.update(pygame.key.get_pressed(), self.village_obstacles)

                for npc in self.npcs:
                    npc.update()

                # 检测寺庙入口
                if self.god_pos:
                    dist = ((self.player.x - self.temple_entrance[0])**2 +
                           (self.player.y - self.temple_entrance[1])**2)**0.5
                    if dist < 80:
                        self.state = GameState.Temple
                        self.fade.set_status(SceneStatus.Out)
                        self.player.x = 400
                        self.player.y = 300
                        self.player.rect.topleft = (400, 300)
                        self.dialogue.show("系统", "进入寺庙场景！准备战斗！")

            elif self.state == GameState.Temple:
                if not self.battle.active and not self.dialogue.active:
                    self.player.update(pygame.key.get_pressed(), [])

                for monster in self.monsters:
                    if monster.alive:
                        monster.update()
                        if not self.battle.active and self.player.rect.colliderect(monster.rect):
                            self.battle.start_battle(self.player, monster)
                            self.state = GameState.Battle

                # 检测是否所有怪物被击败
                if all(not m.alive for m in self.monsters):
                    self.state = GameState.Victory

            elif self.state == GameState.Battle:
                self.battle.update()
                if not self.battle.active:
                    if self.battle.result == 'win':
                        self.state = GameState.Temple
                    elif self.battle.result == 'lose':
                        self.reset_game()

            self.fade.update()

            # 绘制
            screen.fill((0, 0, 0))

            if self.state == GameState.Menu:
                self.menu.draw(screen)

            else:
                # 计算视窗偏移
                camera_x = self.player.x - SCREEN_WIDTH // 2
                camera_y = self.player.y - SCREEN_HEIGHT // 2
                camera_x = max(0, min(camera_x, 3780 - SCREEN_WIDTH))
                camera_y = max(0, min(camera_y, 2395 - SCREEN_HEIGHT))

                # 绘制地图
                if self.state == GameState.Village:
                    render_map(screen, self.village_tmx, camera_x, camera_y)
                else:
                    render_map(screen, self.temple_tmx, camera_x, camera_y)

                # 绘制障碍物
                if self.show_obstacles:
                    for obs in self.village_obstacles:
                        pygame.draw.rect(screen, (255, 0, 0),
                                       (obs.x - camera_x, obs.y - camera_y, obs.width, obs.height), 2)

                # 绘制NPC
                for npc in self.npcs:
                    npc.draw(screen, camera_x, camera_y)

                # 绘制土地公
                if self.god_img and self.god_pos:
                    screen.blit(self.god_img, (self.god_pos[0] - camera_x, self.god_pos[1] - camera_y))

                # 绘制怪物
                for monster in self.monsters:
                    monster.draw(screen, camera_x, camera_y)

                # 绘制玩家
                self.player.draw(screen, camera_x, camera_y)

                # 绘制对话框
                self.dialogue.draw(screen)

                # 绘制打斗场景
                self.battle.draw(screen)

                # 绘制渐变效果
                self.fade.draw(screen)

                # 绘制HUD
                self.draw_hud(screen)

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def draw_hud(self, surface):
        """绘制HUD（血条等）"""
        try:
            font = pygame.font.Font(None, 24)
        except:
            font = pygame.font.SysFont('arial', 20)

        # 玩家血条
        hp_bar_width = 150
        hp_bar_height = 15
        hp_ratio = self.player.hp / self.player.max_hp

        pygame.draw.rect(surface, (100, 100, 100), (10, 10, hp_bar_width, hp_bar_height))
        pygame.draw.rect(surface, (255, 0, 0), (10, 10, hp_bar_width * hp_ratio, hp_bar_height))

        hp_text = font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, (255, 255, 255))
        surface.blit(hp_text, (170, 10))

        # 状态信息
        state_text = font.render(f"场景: {self.state.name}", True, (255, 255, 255))
        surface.blit(state_text, (10, 35))

        # 提示信息
        hint_texts = [
            "方向键: 移动 | 空格: 对话/攻击 | F1: 障碍物 | ESC: 菜单"
        ]
        for i, text in enumerate(hint_texts):
            surface.blit(font.render(text, True, (200, 200, 200)), (10, SCREEN_HEIGHT - 25))

# ========== 启动游戏 ==========
if __name__ == "__main__":
    game = Game()
    game.run()
