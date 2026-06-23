import pygame
from pygame.constants import QUIT

pygame.init()
background_image = 'resource/img/village.jpg'
screen = pygame.display.set_mode((800, 600), 0, 32)
clock = pygame.time.Clock()
background = pygame.image.load(background_image).convert()
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    screen.blit(background, (0, 0))
    pygame.display.update()
    clock.tick(60)

pygame.quit()