# https://wiki.libsdl.org/SDL_CreateRenderer
from upysdl2 import *

NULL = None

posX = 100
posY = 100
width = 160
height = 120

win = SDL_CreateWindow("Hello World", posX, posY, width, height, 0);
print(win)

renderer = SDL_CreateRenderer(win, -1, 0);
print(renderer)

if 0:
    bitmapSurface = SDL_LoadBMP("logo_small.bmp")
else:
    import uctypes
    with open("logo_small.bmp", "rb") as f:
        data = f.read()
    bitmapSurface = SDL_LoadBMP_RW(SDL_RWFromMem(uctypes.addressof(data), len(data)), 1)

print(bitmapSurface)

bitmapTex = SDL_CreateTextureFromSurface(renderer, bitmapSurface);
SDL_FreeSurface(bitmapSurface);

SDL_RenderClear(renderer);
SDL_RenderCopy(renderer, bitmapTex, NULL, NULL);
SDL_RenderPresent(renderer);

print("Press Enter to quit")
input()
