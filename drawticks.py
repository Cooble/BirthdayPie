import abc
import graphics
from util import toArray


class Drawable(abc.ABC):
    @abc.abstractmethod
    def draw(self, g):
        # type: (graphics.Graphics) -> None
        pass


class Text(Drawable):
    def __init__(self, x, y, text, centered=0, underline=False):
        self.y = y
        self.x = x
        self.underline = underline
        self.centered = centered
        self.text = text

    def draw(self, g):
        # type: (graphics.Graphics) -> None
        g.drawText(self.x, self.y, self.text, self.centered, self.underline)


class Image(Drawable):
    def __init__(self, x, y, array):
        self.array = array
        self.y = y
        self.x = x

    def draw(self, g):
        # type: (graphics.Graphics) -> None
        g.drawBitmap(self.x, self.y, self.array)


class Rectangle(Drawable):
    def __init__(self, x, y, w, h, clearWithin=True):
        self.clearWithin = clearWithin
        self.w = w
        self.h = h
        self.y = y
        self.x = x

    def draw(self, g):
        # type: (graphics.Graphics) -> None
        g.drawRectangle(self.x, self.y, self.w, self.h, self.clearWithin)


class TextList(Drawable):
    def __init__(self, x, y, textArray, button=False, width=0, height=0, name=""):
        self.name = name
        self.height = height
        self.width = width
        self.bounds = height != 0 and width != 0
        self.button = button
        self.y = y
        self.x = x
        self.textArray = textArray

    def draw(self, g):
        # type: (graphics.Graphics) -> None
        yy = self.y
        if self.bounds:
            if self.name != "":
                yy += 2
                g.drawRectangle(self.x - 1, self.y - 1, self.width + 1, 3)
                g.drawRectangle(self.x - 1, self.y + 1, self.width + 1, self.height + 1)
                g.drawText(self.x, self.y, self.name)

            else:
                g.drawRectangle(self.x - 1, self.y - 1, self.width + 1, self.height + 1)
        elif self.name != "":
            yy += 2
            g.drawText(self.x, self.y, self.name, underline=True)

        for i in range(len(self.textArray)):
            s = self.textArray[i]
            if self.button:
                s = "* " + s
            g.drawText(self.x, yy + i, s)


class TextArea(TextList):
    def __init__(self, x, y, text, width=0, name="", yInverse=False):
        if width == 0:
            width = 10000
        ray = toArray(text, width*2)
        if yInverse:
            y -= len(ray) + 1
        if name!="":
            y -= 2
        super().__init__(x, y, ray, False, width, len(ray) + 1, name)




class Tickable(abc.ABC):
    @abc.abstractmethod
    def tick(self):
        pass


def blank():
    pass


class TickText(Text, Tickable):

    def __init__(self, x, y, text, centered=0, underline=False, methodToRun=blank):
        Text.__init__(self, x, y, text, centered, underline)
        self.speed = -1
        self.innerState = 0
        self.targetText = text
        self.text = ""
        self.methodToRun = methodToRun

    def start(self, speed):
        self.speed = speed

    def reset(self):
        self.speed = 0
        self.innerState = 0
        self.text = ""

    def tick(self):
        if int(self.innerState) != len(self.targetText):
            self.innerState += self.speed
        else:
            self.methodToRun()

        self.text = self.targetText[:int(self.innerState)]
