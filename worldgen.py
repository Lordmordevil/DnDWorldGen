from pygamehelper import *
from pygame import *
from pygame.locals import *
from vec2d import *
from math import e, pi, cos, sin, sqrt
from random import uniform, randrange
from voronoi import *

class Border:
    def __init__(self, start, end):
        self.start = start
        self.end = end

class WorldSait:
    def __init__(self, center):
        self.center = center
        self.neighbours = []
        self.borders = []
        
    @property
    def name(self):
        return "Sait %d:%d" % (self.center.x,self.center.y)

    @property
    def key(self):
        return self.center.key

    def addNeighbour(self, neighbourKey, border):
        self.neighbours.append(neighbourKey)
        self.borders.append(border)

    def draw(self, screen):
        pygame.draw.circle(screen, (200, 0, 0), (int(self.center.x), int(self.center.y)), 2, 1)
        for border in self.borders:
            pygame.draw.line(screen, (0, 200, 0), (int(border.start.x), int(border.start.y)), (int(border.end.x), int(border.end.y)), 1)

class WorldMap:
    def __init__(self, seed, size):
        self.seed = seed
        self.size = size

        self.worldSites = {}

        self.generateFrame()

    def seedFrame(self, points, step):
        for i in range(step, self.size[0] - step, step):
            for j in range(step, self.size[1] - step , step):
                offsetX = randrange(step - 2) - int(step / 2)
                offsetY = randrange(step - 2) - int(step / 2)
                points.append(Point(i + offsetX, j + offsetY))

    def generateFrame(self):
        points = []
        self.seedFrame(points, 20) # step needs to be calced based on world params
        triangulation = Triangulation(points)
        delaunay = Delaunay(triangulation)
        voronoi = Voronoi(triangulation, (0,0, self.size[0], self.size[1]))

        if delaunay is None or voronoi is None:
            print("Error: in generateFrame")
            return
        for trEdge in triangulation.edges:
            centerOne = points[trEdge.a]
            centerTwo = points[trEdge.b]
            if centerOne.key not in self.worldSites:
                newWorldSite = WorldSait(centerOne)
                self.worldSites[centerOne.key] = newWorldSite
            if centerTwo.key not in self.worldSites:
                newWorldSite = WorldSait(centerTwo)
                self.worldSites[centerTwo.key] = newWorldSite
            siteOne = self.worldSites[centerOne.key]
            siteTwo = self.worldSites[centerTwo.key]

            border = None
            if len(trEdge.vEdge) != 0 and len(trEdge.vEdge) != 1:
                print("Error: in generateFrame multiple borders: ", len(trEdge.vEdge))
            elif len(trEdge.vEdge) == 1:
                bordStart = voronoi.points[trEdge.vEdge[0].a]
                bordEnd = voronoi.points[trEdge.vEdge[0].b]
                border = Border(bordStart, bordEnd)
            siteOne.addNeighbour(siteTwo.key, border)
            siteTwo.addNeighbour(siteOne.key, border)
            
    def draw(self, screen):
        for site in self.worldSites.items():
            site[1].draw(screen)



class Starter(PygameHelper):
    def __init__(self):
        self.w, self.h = 1200, 700
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))

        self.showVerts = True;
        self.showTesl = False;

        self.map = WorldMap(123, (self.w, self.h))

        self.hello()

    def hello(self):
        print("Press V to show voronoi edges")
        print("Press T to show triangulation edges")
        
    def update(self):
        pass
        
    def keyUp(self, key):
        if key == 118: #pressed V
            self.showVerts = not self.showVerts
            print("Show voronoi edges: ", self.showVerts)
        if key == 116: #pressed T
            self.showTesl = not self.showTesl
            print("Show triangulation edges: ", self.showTesl)
        
    def mouseUp(self, button, pos):
        pass
        # self.points.append(Point(pos[0], pos[1]))
        # self.initTriangulation()
        
        
    def mouseMotion(self, buttons, pos, rel):
        pass
        
        
    def draw(self):
        self.screen.fill((255, 255, 255))
        
        self.map.draw(self.screen)
            

s = Starter()
s.mainLoop(40)
