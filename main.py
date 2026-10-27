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
    
graphRangeX = (-2.5,1)
graphRangeY = (-1,1)

maxTurns = 200

minColor = (1, 38, 97)
maxColor = (255,255,255)

def lerpColor(color1, color2, t):
    return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))
    
def updateGraph():
    pixels = [[(255,255,255)] * WIDTH for _ in range(HEIGHT)] #[y][x]
    for row in range(HEIGHT):
        for col in range(WIDTH):
            rangeX = abs(graphRangeX[0] - graphRangeX[1])
            rangeY = abs(graphRangeY[0] - graphRangeY[1])
            
            graphX = col * (rangeX/WIDTH) - abs(graphRangeX[0])
            graphY = row * (rangeY/HEIGHT) - abs(graphRangeY[0])
            cx, cy = graphX, graphY
            z = (0,0)
            turns = 0
            while turns <= maxTurns:
                turns += 1
                x, y = z
                newX = x * x - y * y + cx
                newY = 2 * x * y + cy
                z = (newX, newY)
                if (x * x + y * y) > 4:
                    break
            if turns >= maxTurns:
                pixels[row][col] = (0,0,0)
            else:
                t = turns/maxTurns
                color = lerpColor(minColor, maxColor, t)
                pixels[row][col] = color
    return pixels
                
    
result = updateGraph()
    
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