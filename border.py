from pygamehelper import *
from pygame import *

from random import randrange, choice

class Border:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.elevation = None

        self.parts = [(self.start, self.end)]

        self.isRiver = False
        self.riverWidth = 1

    def subDevide(self, offsetSize):
        newParts = []
        for part in self.parts:
            if part[0] != part[1]:
                middle = (part[0] + part[1])/2
                direct = (part[1] - part[0]).perpendicular_normal()
                newLen = randrange(-1 * offsetSize, offsetSize)/10
                if newLen == 0:
                    newLen = choice([-0.1, 0.1])
                direct.length = newLen
                direct.x = int(direct.x)
                direct.y = int(direct.y)
                newMiddle = middle + direct
                newParts.extend([(part[0], newMiddle), (newMiddle, part[1])])
        self.parts = newParts

    def getReversedParts(self):
        reversedParts = []
        for part in reversed(self.parts):
            reversedParts.append((part[1], part[0]))
        return reversedParts

    def draw(self, screen, camera):
        for part in self.parts:
            if camera.point_visible(part[0]) or camera.point_visible(part[1]):
                start = camera.world_to_screen(part[0])
                end = camera.world_to_screen(part[1])
                if camera.viewProps["DrawMode"] == 1:
                    pygame.draw.line(screen, (0, 0, 0), start, end, 4)
                elif self.isRiver:
                    pygame.draw.line(screen, (90, 132, 152), start, end, self.riverWidth+1)
