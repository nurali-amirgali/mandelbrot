import pygame
import sys

WIDTH = 800
HEIGHT = 600
FPS = 60

BG_COLOR = (30,30,30)

pygame.init()
    
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("mandelbrot renderer")
    
clock = pygame.time.Clock()
    
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
                    
    screen.fill(BG_COLOR)
    pygame.display.flip()

pygame.quit()
sys.exit()