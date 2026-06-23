"""
任务6：Sprite应用
精灵基类和动画精灵类
"""
import pygame
import os


class Sprite(pygame.sprite.Sprite):
    """精灵基类"""

    def __init__(self, x, y, image_path=None):
        """
        初始化精灵
        :param x: x坐标
        :param y: y坐标
        :param image_path: 图像路径（可选）
        """
        super().__init__()
        self.x = x
        self.y = y
        self.image = None
        self.rect = None

        # 加载图像
        if image_path:
            self.load_image(image_path)

    def load_image(self, image_path):
        """加载图像"""
        if os.path.exists(image_path):
            self.image = pygame.image.load(image_path).convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.topleft = (self.x, self.y)
        else:
            # 创建一个占位符
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.image.fill((255, 0, 0, 128))
            self.rect = self.image.get_rect()
            self.rect.topleft = (self.x, self.y)
            print(f"图像文件不存在: {image_path}")

    def set_position(self, x, y):
        """设置位置"""
        self.x = x
        self.y = y
        self.rect.topleft = (self.x, self.y)

    def update(self, *args):
        """更新精灵状态"""
        pass

    def draw(self, surface, offset_x=0, offset_y=0):
        """
        绘制精灵
        :param surface: 目标surface
        :param offset_x: X偏移量
        :param offset_y: Y偏移量
        """
        if self.image:
            screen_x = self.x - offset_x
            screen_y = self.y - offset_y
            surface.blit(self.image, (screen_x, screen_y))

    def get_rect(self):
        """获取精灵的矩形区域"""
        return pygame.Rect(self.x, self.y,
                          self.rect.width if self.rect else 32,
                          self.rect.height if self.rect else 32)


class AnimatedSprite(Sprite):
    """动画精灵类 - 支持多帧动画"""

    def __init__(self, x, y, image_paths, animation_speed=0.1):
        """
        初始化动画精灵
        :param x: x坐标
        :param y: y坐标
        :param image_paths: 图像路径字典，格式: {'down': [path1, path2, ...], ...}
        :param animation_speed: 动画速度
        """
        # 动画相关属性
        self.animation_frames = {}
        self.current_direction = 'down'
        self.current_frame = 0
        self.animation_speed = animation_speed
        self.frame_timer = 0

        # 加载所有帧
        self._load_animation_frames(image_paths)

        # 初始化基类
        if self.animation_frames.get('down'):
            super().__init__(x, y, image_paths['down'][0])
        else:
            super().__init__(x, y, '')

    def _load_animation_frames(self, image_paths):
        """加载所有动画帧"""
        for direction, paths in image_paths.items():
            self.animation_frames[direction] = []
            for path in paths:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    self.animation_frames[direction].append(img)
                else:
                    print(f"动画帧不存在: {path}")

    def update_animation(self, direction=None, dt=1):
        """
        更新动画帧
        :param direction: 方向
        :param dt: 时间增量
        """
        if direction:
            self.current_direction = direction

        if self.current_direction in self.animation_frames:
            frames = self.animation_frames[self.current_direction]
            if frames:
                self.frame_timer += dt * self.animation_speed
                if self.frame_timer >= 1:
                    self.frame_timer = 0
                    self.current_frame = (self.current_frame + 1) % len(frames)
                    self.image = frames[self.current_frame]
                    self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def set_animation_speed(self, speed):
        """设置动画速度"""
        self.animation_speed = speed

    def get_current_frame_count(self):
        """获取当前方向的帧数"""
        if self.current_direction in self.animation_frames:
            return len(self.animation_frames[self.current_direction])
        return 0
