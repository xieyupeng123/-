# -*- coding: utf-8 -*-
"""
打斗场景类
"""
import pygame
import random
from .utils import get_font


class BattleScene:
    """打斗场景类 - 回合制战斗"""

    def __init__(self, screen_width=800, screen_height=600):
        self.active = False
        self.player = None
        self.monster = None
        self.battle_log = []
        self.turn = 'player'  # 'player' or 'monster'
        self.battle_timer = 0
        self.result = None  # 'win' or 'lose'
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 字体
        self.font = get_font(28)
        self.title_font = get_font(48)

    def start_battle(self, player, monster):
        """开始战斗"""
        self.active = True
        self.player = player
        self.monster = monster
        self.battle_log = [f"Encounter {monster.name}! Battle Start!"]
        self.turn = 'player'
        self.battle_timer = 0
        self.result = None

    def player_attack(self):
        """玩家攻击"""
        if self.turn != 'player' or not self.monster.alive:
            return

        # 计算伤害
        damage = self.player.attack_power + random.randint(0, 10)
        self.monster.take_damage(damage)
        self.battle_log.append(f"Sun Wukong attacks {self.monster.name}, dealing {damage} damage!")

        if not self.monster.alive:
            self.battle_log.append(f"{self.monster.name} defeated!")
            self.result = 'win'
        else:
            self.turn = 'monster'
            self.battle_timer = 0

    def monster_attack(self):
        """怪物攻击"""
        if self.turn != 'monster' or not self.monster.alive:
            return

        # 计算伤害
        damage = self.monster.attack + random.randint(0, 5)
        self.player.take_damage(damage)
        self.battle_log.append(f"{self.monster.name} attacks Sun Wukong, dealing {damage} damage!")

        if self.player.hp <= 0:
            self.battle_log.append("Sun Wukong defeated!")
            self.result = 'lose'
        else:
            self.turn = 'player'
            self.battle_timer = 0

    def update(self):
        """更新战斗状态"""
        if not self.active:
            return

        self.battle_timer += 1

        # 怪物自动攻击
        if self.turn == 'monster' and self.battle_timer > 30:
            self.monster_attack()

        # 战斗结束后延迟关闭
        if self.result:
            self.battle_timer += 1
            if self.battle_timer > 90:
                self.active = False

    def draw(self, surface):
        """绘制战斗界面"""
        if not self.active:
            return

        # 绘制战斗背景
        battle_bg = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        battle_bg.fill((0, 0, 0, 200))
        surface.blit(battle_bg, (0, 0))

        # 绘制标题
        title_surface = self.title_font.render("BATTLE!", True, (255, 255, 0))
        surface.blit(title_surface, (self.screen_width // 2 - 80, 50))

        # 绘制玩家信息
        player_text = f"Sun Wukong HP: {self.player.hp}/{self.player.max_hp}"
        surface.blit(self.font.render(player_text, True, (0, 255, 0)), (100, 150))

        # 绘制怪物信息
        if self.monster:
            monster_text = f"{self.monster.name} HP: {self.monster.hp}/{self.monster.max_hp}"
            surface.blit(self.font.render(monster_text, True, (255, 0, 0)), (500, 150))

        # 绘制战斗日志
        for i, log in enumerate(self.battle_log[-5:]):
            surface.blit(self.font.render(log, True, (255, 255, 255)), (100, 250 + i * 35))

        # 绘制提示
        if self.result == 'win':
            hint = "Victory! Press SPACE to continue"
            color = (0, 255, 0)
        elif self.result == 'lose':
            hint = "Defeated! Press SPACE to restart"
            color = (255, 0, 0)
        elif self.turn == 'player':
            hint = "Press SPACE to attack!"
            color = (255, 255, 0)
        else:
            hint = "Enemy turn..."
            color = (200, 200, 200)

        surface.blit(self.font.render(hint, True, color), (250, 500))
