import numpy as np
from PIL import Image
from numba import njit, prange

WIDTH = 800
HEIGHT = 600
FPS = 30

FConstant = 4.669201609102990
startZoom = FConstant ** 3
startTurns = 5000

center = (-1.401155189,0)
viewRange = (3.5, 2)
zoom = startZoom
maxTurns = startTurns

actualZoom = startZoom
renderZoom = startZoom
lastZoom = startZoom

minColor = (1, 38, 97)
maxColor = (201, 178, 0) #(255,255,255)

def lerpColor(color1, color2, t):
    return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))

def getTurns(zoom):
    return int(startTurns * (zoom / startZoom) ** (np.log(2) / np.log(FConstant)))

palleteSize = 255
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

colorCurve = 1
def updateFractal(width, height, graphRangeX, graphRangeY, maxTurns):
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    fractal = computeFractal(width, height, graphRangeX, graphRangeY, maxTurns)
    
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

preComputeColors()

rangeX, rangeY = updateRanges(center, viewRange, zoom)
savedResult = updateFractal(WIDTH, HEIGHT, rangeX, rangeY, maxTurns)

zoomSpeed = 0.5
timeStep = 1/FPS
duration = np.log(FConstant) / zoomSpeed

numFrames = round(FPS * duration)
frames = []

print("START")
for frame in range(numFrames):
    t = frame / FPS
    zoom = startZoom * FConstant ** (frame / numFrames)
    
    maxTurns = getTurns(zoom)
            
    rangeX, rangeY = updateRanges(center, viewRange, zoom)
    result = updateFractal(WIDTH, HEIGHT, rangeX, rangeY, maxTurns)
    
    frames.append(Image.fromarray(result))
    print(f"frame {frame} complete out of {numFrames} frames")
print("DONE")

frames[0].save(
    "mandelbrot.gif",
    save_all=True,
    append_images=frames[1:],
    duration=1000 // FPS,
    loop=0
)

print("COMPLETE! saved to mandelbrot.gif")