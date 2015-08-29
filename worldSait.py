from pygamehelper import *
from pygame import *

from border import Border
from vec2d import vec2d


class WorldSait:
    def __init__(self, center):
        self.center = center
        self.neighbours = []
        self.borders = []

        self.lockedElevation = False
        self.elevation = -10

        self.isOcean = False
        
    @property
    def name(self):
        return "Sait %d:%d" % (self.center.x,self.center.y)

    @property
    def key(self):
        return self.center.key

    def addNeighbour(self, neighbourKey, border):
        self.neighbours.append(neighbourKey)
        self.borders.append(border)
        if border is None:
            self.elevation = -10
            self.lockedElevation = True

    def hasNeighbour(self, neighbourID):
        for neighbour in self.neighbours:
            if neighbour == neighbourID:
                return True
        return False

    def getColor(self):
        color = (120, 0, 0)
        elevationColor = {-10: (39, 50, 64),
                          -9 : (48, 59, 75),
                          -8 : (56, 68, 85),
                          -7 : (65, 79, 95),
                          -6 : (69, 84, 101),
                          -5 : (58, 82, 126),
                          -4 : (68, 96, 147),
                          -3 : (69, 101, 116),
                          -2 : (77, 111, 128),
                          -1 : (90, 132, 152),
                          0  : (191, 193, 123),
                          1  : (182, 182, 134),
                          2  : (122, 146, 31),
                          3  : (92, 143, 33),
                          4  : (82, 130, 30),
                          5  : (56, 88, 20),
                          6  : (41, 66, 15),
                          7  : (164, 137, 119),
                          8  : (149, 140, 133),
                          9  : (219, 219, 219),
                          10 : (238, 238, 238)}
        if self.elevation >= -10 and self.elevation <= 10:
            color = elevationColor[self.elevation]
        return color

    def draw(self, screen, camera):
        shouldDrawPoly = True;

        if len(self.borders) < 2 or not camera.point_visible(self.center):
            shouldDrawPoly = False

        if shouldDrawPoly:
            boundPoints = []
            for border in self.borders:
                for part in border.parts:
                    if len(boundPoints) == 0:
                        screen_border_point = camera.world_to_screen(part[0])
                        boundPoints.append([screen_border_point.x, screen_border_point.y])
                    screen_border_point = camera.world_to_screen(part[1])
                    boundPoints.append([screen_border_point.x, screen_border_point.y])
  
            pygame.draw.polygon(screen, self.getColor(), boundPoints)
            if camera.viewProps["ShowPoints"]:
                point_pos = camera.world_to_screen(self.center)
                pygame.draw.circle(screen, (200, 0, 0), point_pos, 2, 1)


    def drawBorders(self, screen, camera):
        if camera.point_visible(self.center):
            for border in self.borders:
                border.draw(screen, camera)