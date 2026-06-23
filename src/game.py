# -*- coding: utf-8 -*-
"""
游戏主类 - 整合所有模块
"""
import pygame
import os

from .config import *
from .utils import *
from .player import Player
from .npc import NPC
from .monster import Monster
from .dialogue import DialogueBox
from .battle import BattleScene
from .scene import GameState, SceneStatus, FadeScene
from .menu import MainMenu


class Game:
    """游戏主类"""

    def __init__(self):
        # 初始化Pygame
        pygame.init()
        pygame.display.set_mode((1, 1))
        pygame.mixer.init()

        # 创建窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
        pygame.display.set_caption(GAME_TITLE)

        # 时钟
        self.clock = pygame.time.Clock()

        # 游戏状态
        self.state = GameState.Menu
        self.fade = FadeScene(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.dialogue = DialogueBox(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.battle = BattleScene(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.menu = MainMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.show_obstacles = False

        # 加载地图
        self._load_maps()

        # 创建游戏对象
        self._create_objects()

        print("Game initialized!")

    def _load_maps(self):
        """加载地图"""
        print("Loading maps...")

        # 村庄地图
        self.village_tmx, self.village_width, self.village_height = load_map(VILLAGE_MAP)
        self.village_obstacles = get_obstacles(self.village_tmx)

        # 寺庙地图
        if os.path.exists(TEMPLE_MAP):
            self.temple_tmx, self.temple_width, self.temple_height = load_map(TEMPLE_MAP)
        else:
            self.temple_tmx = self.village_tmx
            self.temple_width = self.village_width
            self.temple_height = self.village_height

    def _create_objects(self):
        """创建游戏对象"""
        # 创建玩家
        player_pos = get_object_position(self.village_tmx, 'sun')
        self.player = Player(player_pos[0], player_pos[1]) if player_pos else Player(400, 300)

        # 创建NPC
        self.npcs = []
        elder_objects = get_objects_by_layer(self.village_tmx, 'elder')
        for elder in elder_objects:
            npc = NPC(elder['x'], elder['y'], elder['name'], NPC_MOVE_RANGE, NPC_SPEED)
            self.npcs.append(npc)

        child_objects = get_objects_by_layer(self.village_tmx, 'child')
        for child in child_objects:
            npc = NPC(child['x'], child['y'], child['name'], 60, NPC_SPEED)
            self.npcs.append(npc)

        # 土地公
        self.god_pos = get_object_position(self.village_tmx, 'god')
        self.god_img = load_sprite_image('resource/img/god/0214-16505471-00000.tga') if self.god_pos else None

        # 怪物
        self.monsters = []
        self._spawn_monsters()

        # 位置标记
        self.temple_entrance = (2800, 800)
        self.village_spawn = (400, 300)

    def _spawn_monsters(self):
        """生成怪物"""
        self.monsters = []
        positions = [(200, 200), (400, 350), (600, 200), (300, 450), (500, 450)]
        for i, (mx, my) in enumerate(positions):
            monster = Monster(mx, my, f"Monster{i+1}", 50 + i*10, 5 + i*2)
            self.monsters.append(monster)

    def _reset_game(self):
        """重置游戏"""
        self.player.reset(self.village_spawn[0], self.village_spawn[1])
        self._spawn_monsters()
        self.state = GameState.Village
        self.fade.set_status(SceneStatus.In)

    def run(self):
        """游戏主循环"""
        running = True

        while running:
            # 事件处理
            running = self._handle_events()

            # 更新游戏状态
            self._update()

            # 绘制
            self._draw()

            # 更新显示
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def _handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.Menu:
                        return False
                    elif self.battle.active:
                        pass
                    elif self.dialogue.active:
                        self.dialogue.hide()
                    else:
                        self.state = GameState.Menu

                elif event.key == pygame.K_F1:
                    self.show_obstacles = not self.show_obstacles

                elif event.key == pygame.K_SPACE:
                    return self._handle_space_key()

                elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    if self.state == GameState.Menu:
                        result = self.menu.handle_input(event.key)
                        if result == "Start Game":
                            self.state = GameState.Village
                            self.fade.set_status(SceneStatus.In)
                        elif result == "Exit":
                            return False

                elif event.key in [pygame.K_UP, pygame.K_DOWN]:
                    if self.state == GameState.Menu:
                        self.menu.handle_input(event.key)

        return True

    def _handle_space_key(self):
        """处理空格键"""
        if self.state == GameState.Menu:
            result = self.menu.handle_input(pygame.K_SPACE)
            if result == "Start Game":
                self.state = GameState.Village
                self.fade.set_status(SceneStatus.In)
            elif result == "Exit":
                return False

        elif self.dialogue.active:
            self.dialogue.hide()

        elif self.battle.active:
            self.battle.player_attack()
            if self.battle.result == 'win':
                pass
            elif self.battle.result == 'lose':
                self._reset_game()

        else:
            # 检测NPC对话
            for npc in self.npcs:
                if self.player.rect.colliderect(npc.rect):
                    self.dialogue.show(npc.name, f"Hello! I am {npc.name}.")
                    break

        return True

    def _update(self):
        """更新游戏状态"""
        if self.state == GameState.Menu:
            pass

        elif self.state == GameState.Village:
            self._update_village()

        elif self.state == GameState.Temple:
            self._update_temple()

        elif self.state == GameState.Battle:
            self.battle.update()
            if not self.battle.active:
                if self.battle.result == 'win':
                    self.state = GameState.Temple
                elif self.battle.result == 'lose':
                    self._reset_game()

        self.fade.update()

    def _update_village(self):
        """更新村庄场景"""
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
                self.player.reset(400, 300)
                self.dialogue.show("System", "Entering temple scene! Prepare for battle!")

    def _update_temple(self):
        """更新寺庙场景"""
        if not self.battle.active and not self.dialogue.active:
            self.player.update(pygame.key.get_pressed(), [])

        for monster in self.monsters:
            if monster.alive:
                monster.update()
                if not self.battle.active and self.player.rect.colliderect(monster.rect):
                    self.battle.start_battle(self.player, monster)
                    self.state = GameState.Battle

    def _draw(self):
        """绘制游戏"""
        self.screen.fill(COLOR_BLACK)

        if self.state == GameState.Menu:
            self.menu.draw(self.screen)
        else:
            self._draw_game_scene()

        # 绘制渐变效果
        self.fade.draw(self.screen)

    def _draw_game_scene(self):
        """绘制游戏场景"""
        # 计算视窗偏移
        camera_x = self.player.x - SCREEN_WIDTH // 2
        camera_y = self.player.y - SCREEN_HEIGHT // 2
        camera_x = max(0, min(camera_x, 3780 - SCREEN_WIDTH))
        camera_y = max(0, min(camera_y, 2395 - SCREEN_HEIGHT))

        # 绘制地图
        if self.state == GameState.Village:
            render_map(self.screen, self.village_tmx, camera_x, camera_y)
        else:
            render_map(self.screen, self.temple_tmx, camera_x, camera_y)

        # 绘制障碍物
        if self.show_obstacles:
            for obs in self.village_obstacles:
                pygame.draw.rect(self.screen, COLOR_RED,
                               (obs.x - camera_x, obs.y - camera_y, obs.width, obs.height), 2)

        # 绘制NPC
        for npc in self.npcs:
            npc.draw(self.screen, camera_x, camera_y)

        # 绘制土地公
        if self.god_img and self.god_pos:
            self.screen.blit(self.god_img, (self.god_pos[0] - camera_x, self.god_pos[1] - camera_y))

        # 绘制怪物
        for monster in self.monsters:
            monster.draw(self.screen, camera_x, camera_y)

        # 绘制玩家
        self.player.draw(self.screen, camera_x, camera_y)

        # 绘制对话框
        self.dialogue.draw(self.screen)

        # 绘制打斗场景
        self.battle.draw(self.screen)

        # 绘制HUD
        self._draw_hud()

    def _draw_hud(self):
        """绘制HUD"""
        font = get_font(24)

        # 玩家血条
        hp_bar_width = 150
        hp_bar_height = 15
        hp_ratio = self.player.hp / self.player.max_hp if self.player.max_hp > 0 else 0

        pygame.draw.rect(self.screen, (100, 100, 100), (10, 10, hp_bar_width, hp_bar_height))
        pygame.draw.rect(self.screen, COLOR_RED, (10, 10, hp_bar_width * hp_ratio, hp_bar_height))

        hp_text = font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, COLOR_WHITE)
        self.screen.blit(hp_text, (170, 10))

        # 状态信息
        state_text = font.render(f"Scene: {self.state.name}", True, COLOR_WHITE)
        self.screen.blit(state_text, (10, 35))

        # 提示信息
        hint = "Arrow: Move | SPACE: Talk/Attack | F1: Obstacles | ESC: Menu"
        self.screen.blit(font.render(hint, True, COLOR_GRAY), (10, SCREEN_HEIGHT - 25))
