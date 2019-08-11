# (c) 2018 Paul Sokolovsky. MIT license.
from usdl2 import *


RGB888 = 1


class FrameBuffer:

    def __init__(self, buffer, width, height, format, stride=None):
        if stride is None:
            stride = width
        self.win = SDL_CreateWindow(
            "Pycopy FrameBuffer",
            SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
            width, height, 0)
        self.renderer = SDL_CreateRenderer(self.win, -1, 0)

    def _set_color(self, c):
        SDL_SetRenderDrawColor(self.renderer, (c >> 16) & 0xff, (c >> 8) & 0xff, c & 0xff, 255);

    def fill(self, c):
        self._set_color(c)
        SDL_RenderClear(self.renderer)

    def pixel(self, x, y, c):
        self._set_color(c)
        SDL_RenderDrawPoint(self.renderer, x, y)

    def line(self, x1, y1, x2, y2, c):
        self._set_color(c)
        SDL_RenderDrawLine(self.renderer, x1, y1, x2, y2)

    def rect(self, x, y, w, h, c):
        self._set_color(c)
        SDL_RenderDrawRect(self.renderer, SDL_Rect(x, y, w, h))

    def fill_rect(self, x, y, w, h, c):
        self._set_color(c)
        SDL_RenderFillRect(self.renderer, SDL_Rect(x, y, w, h))

    def show(self):
        SDL_RenderPresent(self.renderer)
