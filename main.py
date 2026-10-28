import pygame
import sys
import time
import numpy as np
from numba import njit

WIDTH = 800
HEIGHT = 600
FPS = 60

BG_COLOR = (30,30,30)

pygame.init()
    
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("mandelbrot renderer")
    
clock = pygame.time.Clock()
    
graphRangeX = (-2.5,1)
graphRangeY = (-1,1)

maxTurns = 200

minColor = (1, 38, 97)
maxColor = (201, 178, 0) #(255,255,255)

def lerpColor(color1, color2, t):
    return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))

@njit
def computeFractal(width, height, graphRangeX, graphRangeY, maxTurns):
    pixels = np.zeros((height, width), dtype=np.uint8)
    
    rangeX = abs(graphRangeX[0] - graphRangeX[1])
    rangeY = abs(graphRangeY[0] - graphRangeY[1])
    
    for row in range(height):
        for col in range(width):            
            graphX = col * (rangeX/width) - abs(graphRangeX[0])
            graphY = row * (rangeY/height) - abs(graphRangeY[0])
            
            cx, cy = graphX, graphY
            x, y = 0, 0
            turns = 0
            
            while turns <= maxTurns:
                turns += 1
                
                newX = x * x - y * y + cx
                newY = 2 * x * y + cy
                
                x, y = newX, newY
                if x * x + y * y > 4:
                    break
            pixels[row, col] = turns
    return pixels

def updateFractal():
    result = [[(255,255,255)] * WIDTH for _ in range(HEIGHT)]
    fractal = computeFractal(WIDTH, HEIGHT, graphRangeX, graphRangeY, maxTurns)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            turns = fractal[y, x]
            if turns >= maxTurns:
                result[y][x] = (0,0,0)
            else:
                t = turns/maxTurns
                color = lerpColor(minColor, maxColor, t)
                result[y][x] = color
    return result

times = []
for i in range(3):
    startTime = time.perf_counter()
    result = updateFractal()
    endTime = time.perf_counter()
    times.append(endTime - startTime)
    print(f"pass {i} completed")
    
average = sum(times)/3
print(f"took: {round(average, 2)} seconds on average")
print(f"FPS: {round(1/average, 2)}")
    
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
                    
    screen.fill(BG_COLOR)
    
    pixel_array = pygame.PixelArray(screen)

    for pixelY, row in enumerate(result):
        for pixelX, pixel in enumerate(row):
            pixel_array[pixelX, pixelY] = pixel

    pixel_array.close() 
    
    pygame.display.flip()

pygame.quit()
sys.exit()