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

        self.isOcean = False
        self.isWater = False
        
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
            self.isOcean = True

    def getColor(self):
        color = (236, 240, 241)
        if self.isOcean:
            color = (41, 128, 185)
        elif self.isWater:
            color = (52, 152, 219)
        return color

    def draw(self, screen):
        boundPoints = []
        shouldDrawPoly = True;

        if len(self.borders) < 2:
            shouldDrawPoly = False

        for border in self.borders:
            if shouldDrawPoly:
                if len(boundPoints) == 0:
                    boundPoints.append([int(border.start.x), int(border.start.y)])
                boundPoints.append([int(border.end.x), int(border.end.y)])
            #pygame.draw.line(screen, (0, 200, 0), (int(border.start.x), int(border.start.y)), (int(border.end.x), int(border.end.y)), 1)
        if shouldDrawPoly:
            pygame.draw.polygon(screen, self.getColor(), boundPoints)
        pygame.draw.circle(screen, (200, 0, 0), (int(self.center.x), int(self.center.y)), 2, 1)


class WorldMap:
    def __init__(self, seed, size):
        self.seed = seed
        self.size = size

        self.worldSites = {}

        self.generateFrame()
        self.siteDataCleanup()

    def seedFrame(self, points, step):
        for i in range(step, self.size[0] - step, step):
            for j in range(step, self.size[1] - step , step):
                offsetX = randrange(step - 2) - int(step / 2)
                offsetY = randrange(step - 2) - int(step / 2)
                points.append(Point(i + offsetX, j + offsetY))

    def generateFrame(self):
        points = []

        self.seedFrame(points, 40)
        #self.seedFrame(points, 20) # step needs to be calced based on world params
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
                if ((bordStart.x > 0 and bordStart.x < self.size[0] and
                    bordStart.y > 0 and bordStart.y < self.size[1]) and
                    (bordEnd.x > 0 and bordEnd.x < self.size[0] and
                    bordEnd.y > 0 and bordEnd.y < self.size[1])):
                    border = Border(bordStart, bordEnd)
            siteOne.addNeighbour(siteTwo.key, border)
            siteTwo.addNeighbour(siteOne.key, border)

    def siteDataCleanup(self):
        #Cleanup borders
        for site in self.worldSites.items():
            newBorders = []
            borders = site[1].borders
            for border in borders:
                if border is not None:
                    found = False
                    if len(newBorders) > 0:
                        for newBorder in newBorders:
                            if ((newBorder.start == border.start and 
                               newBorder.end == border.end) or
                               (newBorder.end == border.start and 
                               newBorder.start == border.end)):
                                found = True
                                break
                    if not found:
                        newBorders.append(border)

            if len(newBorders) > 1:
                orderedBorders = []
                orderedBorders.append(newBorders.pop())

                completePoly = True
                while len(newBorders) > 0:
                    change = False
                    for nexBorder in newBorders:
                        if orderedBorders[-1].end == nexBorder.start:
                            orderedBorders.append(nexBorder)
                            newBorders.remove(nexBorder)
                            change = True
                            break
                        elif orderedBorders[-1].end == nexBorder.end:
                            reversedBorder = Border(nexBorder.end, nexBorder.start)
                            orderedBorders.append(reversedBorder)
                            newBorders.remove(nexBorder)
                            change = True
                            break
                    if not change:
                        #print("Error: in siteDataCleanup / hole in poly")
                        completePoly = False
                        break

                if completePoly:
                    site[1].borders = orderedBorders
                else:
                    site[1].borders = newBorders
            else:
                site[1].borders = newBorders




    def generateLandmass(self):
        waterCells = 0
        cellCount = len(self.worldSites)

        tagerRatio = 0.28

        for site in self.worldSites.items():
            if site[1].isOcean:
                waterCells += 1

        curRatio = waterCells / cellCount

        while curRatio < tagerRatio:
            for site in self.worldSites.items():
                curRatio = waterCells / cellCount
                if curRatio > tagerRatio:
                    break
                if site[1].isOcean:
                    neighbourIdx = randrange(len(site[1].neighbours))
                    potOcean = site[1].neighbours[neighbourIdx]
                    if not self.worldSites[potOcean].isOcean:
                        waterCells += 1
                        self.worldSites[potOcean].isOcean = True;

            
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
        self.screen.fill((41, 128, 185))
        
        self.map.draw(self.screen)
            

s = Starter()
s.mainLoop(40)
