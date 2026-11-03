import pygame
import sys
import time
import threading
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

FConstant = 4.669201609102990
startZoom = FConstant ** 3
startTurns = 500

center = (-1.401155189,0)
viewRange = (3.5, 2)
zoom = startZoom
maxTurns = startTurns

actualZoom = startZoom
renderZoom = startZoom
lastZoom = startZoom

minColor = (1, 38, 97)
maxColor = (201, 178, 0) #(255,255,255)

fpsWindow = 1 #in seconds
fpsLog = []
fpsFont = pygame.font.Font(None, 50)
averageFps = 0

resultLock = threading.Lock()
savedResult = None

def lerpColor(color1, color2, t):
    return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))

def getTurns(zoom):
    return int(startTurns * (zoom / startZoom) ** (np.log(2) / np.log(FConstant)))

palleteSize = 1200
rgbColors = np.zeros((palleteSize, 3), dtype=np.uint8)
def preComputeColors():
    global rgbColors
    turns = np.linspace(0, 1, palleteSize)
    for i, t in enumerate(turns):
        rgbColors[i] = np.array(lerpColor(minColor, maxColor, t))

@njit(parallel=True, nogil=True)
def computeFractal(width, height, graphRangeX, graphRangeY, maxTurns):
    pixels = np.zeros((height, width), dtype=np.uint16)
    
    rangeX = abs(graphRangeX[0] - graphRangeX[1])
    rangeY = abs(graphRangeY[0] - graphRangeY[1])
    
    for row in prange(height):
        for col in range(width):            
            graphX = col * (rangeX/width) + graphRangeX[0]
            graphY = row * (rangeY/height) + graphRangeY[0]
            
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

def zoomSurface(surface, zoom):
    width, height = surface.get_size()
    cropWidth, cropHeight = int(width / zoom), int(height / zoom)
    cropRect = pygame.Rect((width - cropWidth) // 2, (height - cropHeight) // 2, cropWidth, cropHeight)
    return pygame.transform.scale(surface.subsurface(cropRect), (width, height))

colorCurve = 1
def updateFractal(width, height, graphRangeX, graphRangeY, maxTurns):
    result = np.zeros((width, height, 3))
    
    fractal = computeFractal(width, height, graphRangeX, graphRangeY, maxTurns).T
    
    possibleValues = np.arange(maxTurns + 1)
    t = (possibleValues/maxTurns) ** colorCurve
    
    result = rgbColors[(t * (palleteSize - 1)).astype(np.intp)]
    result[maxTurns] = 0
    result = result[fractal]
    return result

def updateRanges(center, viewRange, zoom):
    halfViewX = viewRange[0]/(2 * zoom)
    graphRangeX = (center[0] - halfViewX, center[0] + halfViewX)

    halfViewY = viewRange[1]/(2 * zoom)
    graphRangeY = (center[1] - halfViewY, center[1] + halfViewY)
    return graphRangeX, graphRangeY

def runFractalUpdate():
    global savedResult, actualZoom
    while True:
        startZoom = zoom
        maxTurns = getTurns(startZoom)
            
        rangeX, rangeY = updateRanges(center, viewRange, startZoom)
        result = updateFractal(WIDTH, HEIGHT, rangeX, rangeY, maxTurns)
        with resultLock:
            savedResult = result
            actualZoom = startZoom

savedResult = None
preComputeColors()

rangeX, rangeY = updateRanges(center, viewRange, zoom)
savedResult = updateFractal(WIDTH, HEIGHT, rangeX, rangeY, maxTurns)

thread = threading.Thread(target=runFractalUpdate, daemon=True)
thread.start()

renderSurface = pygame.Surface((WIDTH, HEIGHT))

running = True
while running:
    dt = clock.tick(FPS)/1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    fpsLog.append(dt)
    while sum(fpsLog) > fpsWindow:
        del fpsLog[0]
    if fpsLog:
        averageFps = 1/(sum(fpsLog)/len(fpsLog))
    
    dt = min(dt, 1)
    #center = (center[0] - (0.6 * dt), center[1])
    zoom += (0.5 * zoom) * dt
    
    if zoom >= startZoom * FConstant:
        zoom = startZoom
    
    with resultLock:
        pygame.surfarray.blit_array(renderSurface, savedResult)
        renderZoom = actualZoom
    
    if zoom < renderZoom:
        zoomDelta = ((zoom * FConstant)/renderZoom)
    else:
        zoomDelta = (zoom/renderZoom)
        
    zoomDelta = max(zoomDelta, 1)
    zoomedSurface = zoomSurface(renderSurface, zoomDelta)
                    
    screen.fill(BG_COLOR)
    
    screen.blit(zoomedSurface, (0,0))
    
    fpsText = fpsFont.render(f"FPS: {round(averageFps)}", True, (255,255,255))
    width, height = fpsFont.size(f"FPS: {round(averageFps)}")
    screen.blit(fpsText, (WIDTH/2 - width/2, 10))
    
    pygame.display.flip()
    
    lastZoom = renderZoom

pygame.quit()