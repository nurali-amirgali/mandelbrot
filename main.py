import pygame
import sys
import time
import numpy as np
from numba import njit, prange

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

rgbColors = np.zeros((maxTurns + 1, 3), dtype=np.uint8)
def preComputeColors():
    global rgbColors
    turns = np.linspace(0, 1, maxTurns)
    for i, t in enumerate(turns):
        rgbColors[i] = np.array(lerpColor(minColor, maxColor, t))
    rgbColors[-1] = np.array((0,0,0))

@njit(parallel=True)
def computeFractal(width, height, graphRangeX, graphRangeY, maxTurns):
    pixels = np.zeros((height, width), dtype=np.uint16)
    
    rangeX = abs(graphRangeX[0] - graphRangeX[1])
    rangeY = abs(graphRangeY[0] - graphRangeY[1])
    
    for row in prange(height):
        for col in range(width):            
            graphX = col * (rangeX/width) - abs(graphRangeX[0])
            graphY = row * (rangeY/height) - abs(graphRangeY[0])
            
            cx, cy = graphX, graphY
            x, y = 0, 0
            turns = 0
            
            while turns < maxTurns:
                turns += 1
                
                newX = x * x - y * y + cx
                newY = 2 * x * y + cy
                
                x, y = newX, newY
                if x * x + y * y > 4:
                    break
            pixels[row, col] = turns
    return pixels

def updateFractal(width, height, graphRangeX, graphRangeY, maxTurns):
    result = np.zeros((width, height, 3))
    
    startTime = time.perf_counter()
    fractal = computeFractal(width, height, graphRangeX, graphRangeY, maxTurns)
    fractal = fractal.T
    endTime = time.perf_counter()
    
    result = rgbColors[fractal]
    computeTime = endTime - startTime
    return result, computeTime

preComputeColors()

times = []
pygameTimes = []
updateFractal(WIDTH, HEIGHT, graphRangeX, graphRangeY, maxTurns)
for i in range(3):
    startTime = time.perf_counter()
    result, timeTaken = updateFractal(WIDTH, HEIGHT, graphRangeX, graphRangeY, maxTurns)
    endTime = time.perf_counter()
    pygameTimes.append(endTime - startTime)
    times.append(timeTaken)
    print(f"pass {i+1} completed")

average = sum(times)/3
pygameAverage = sum(pygameTimes)/3
print(f"took: {round(average, 2)} seconds on average")
print(f"pygame took: {round(pygameAverage, 2)} seconds on average")
print(f"FPS: {round(1/average, 2)}")
    
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
                    
    screen.fill(BG_COLOR)
    
    pygame.surfarray.blit_array(screen, result)
    
    pygame.display.flip()

pygame.quit()