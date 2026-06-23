# -*- coding: utf-8 -*-
"""
工具函数模块
"""
import os
import pygame
import pytmx
from pytmx.util_pygame import load_pygame


def load_animation_frames(base_path, prefix, count, size=(64, 64)):
    """
    加载动画帧序列
    :param base_path: 基础路径
    :param prefix: 文件前缀
    :param count: 帧数量
    :param size: 图像大小
    :return: 帧列表
    """
    frames = []
    for i in range(count):
        path = os.path.join(base_path, f"{prefix}{i:05d}.tga")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    return frames if frames else [pygame.Surface(size, pygame.SRCALPHA)]


def load_sprite_image(path, size=(64, 64)):
    """
    加载精灵图像
    :param path: 图像路径
    :param size: 图像大小
    :return: pygame.Surface
    """
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    else:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((255, 0, 0, 128))
        return surf


def load_map(filename):
    """
    加载TMX地图
    :param filename: 地图文件路径
    :return: (tmx_data, map_width, map_height)
    """
    tmx_data = load_pygame(filename)
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    return tmx_data, map_width, map_height


def render_map(surface, tmx_data, offset_x=0, offset_y=0):
    """
    渲染地图
    :param surface: 目标surface
    :param tmx_data: TMX数据
    :param offset_x: X偏移
    :param offset_y: Y偏移
    """
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
    """
    获取地图对象位置
    :param tmx_data: TMX数据
    :param object_name: 对象名称
    :return: (x, y) 或 None
    """
    for obj in tmx_data.objects:
        if obj.name == object_name:
            return (obj.x, obj.y)
    return None


def get_objects_by_layer(tmx_data, layer_name):
    """
    获取指定图层的所有对象
    :param tmx_data: TMX数据
    :param layer_name: 图层名称
    :return: 对象列表
    """
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
    """
    获取所有障碍物
    :param tmx_data: TMX数据
    :return: 障碍物矩形列表
    """
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


def get_font(size=24):
    """获取字体"""
    try:
        return pygame.font.Font(None, size)
    except:
        return pygame.font.SysFont('arial', size - 4)
