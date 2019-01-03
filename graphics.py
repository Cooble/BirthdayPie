from math import fabs


class Graphics:
    RATIO = 2
    rectSymbol = "#"
    underSymbol = "="

    def __init__(self, w, h, ratio=2):
        self.HEIGHT = h
        self.WIDTH = w
        self.RATIO = ratio
        self.RATIO_WIDTH = w * ratio

        self.lines = []
        for i in range(self.HEIGHT):
            line = []
            for j in range(self.RATIO_WIDTH):
                line.append(" ")
            self.lines.append(line)

    def render(s):
        for i in range(s.HEIGHT):
            for j in range(s.RATIO_WIDTH):
                print(s.lines[i][j], end='')
            print()

    def drawBounds(self):
        self.drawRectangle(0, 0, self.WIDTH, self.HEIGHT)

    def clear(s):
        for i in range(s.HEIGHT):
            for j in range(s.RATIO_WIDTH):
                s.lines[i][j] = " "

    def drawRectangle(s, x, y, w, h,clearWithin=True):
        if clearWithin:
            s.drawFullRectangle(x,y,w,h," ")
        x = int(s.RATIO * x)
        w = int(s.RATIO * w)

        for xx in range(w):
            s.pC(x + xx, y, s.rectSymbol)
            s.pC(x + xx, y + h - 1, s.rectSymbol)
        for yy in range(h):
            s.pC(x, y + yy, s.rectSymbol)
            s.pC(x + w - 1, y + yy, s.rectSymbol)

    def drawFullRectangle(s, x, y, w, h,char):
        x = int(s.RATIO * x)
        w = int(s.RATIO * w)
        for xx in range(w):
            xxx=x+xx
            for yy in range(h):
                yyy = y + yy
                s.pC(xxx,yyy, char)

    def pC(self, x, y, char):
        if 0 <= x < self.RATIO_WIDTH and 0 <= y < self.HEIGHT:
            self.lines[y][x] = char

    def drawBitmap(s,x,y,array):
        x = int(s.RATIO * x)
        for yy in range(len(array)):
            line = array[yy]
            for xx in range(len(line)-1):
                s.pC(x + xx, y+yy, line[xx])



    def drawText(s, x, y, text, centered=0, underline=False):  # centered: 0->left, 1->center, 2->right
        if underline:
            string = len(text) * Graphics.underSymbol
            s.drawText(x, y + 1, string, centered)
        x = int(s.RATIO * x)
        if centered == 0:
            for xx in range(len(text)):
                s.pC(x + xx, y, text[xx])
        elif centered == 2:
            for xx in range(len(text)):
                s.pC(x - len(text) + xx, y, text[xx])
        else:
            padding = int(len(text) / 2)
            for xx in range(len(text)):
                s.pC(x - padding + xx, y, text[xx])

    def drawLine(s, x1, y1, x2, y2):
        x1 = int(s.RATIO * x1)
        x2 = int(s.RATIO * x2)
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1

        switchY = y1 > y2
        width = x2 - x1
        height = fabs(y2 - y1)
        for x in range(width):
            mX = int(x / width * width)
            mY = int(((1 - x / width) if switchY else (x / width)) * height)

            s.pC(mX + x1, mY + min(y1, y2), Graphics.rectSymbol)


class Renderer:


    def __init__(self, g):
        self.g = g
        self.listBack = []
        self.list = []

    def render(self):
        self.g.clear()

        for drawable in self.listBack:
            drawable.draw(self.g)
        for drawable in self.list:
            drawable.draw(self.g)
        self.g.render()

    def add(self, drawable):
        self.remove(drawable)
        self.list.append(drawable)

    def addBack(self, drawable):
        self.remove(drawable)
        self.listBack.append(drawable)

    def remove(self, drawable):
        try:
            self.list.remove(drawable)
        except ValueError:
            try:
                self.listBack.remove(drawable)
            except ValueError:
                pass

    def clear(self):
        self.list.clear()
        self.listBack.clear()

