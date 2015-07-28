from pygamehelper import *
from pygame import *
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
        print(" ")
        print("6.  Generating ocean sites")
        print("6.1 Press -V- untill you like it")
        #self.generateLandmass()

    def seedFrame(self, points, step):
        print("1.  Ceeding frame with points")
        for i in range(step, self.size[0] - step, step):
            for j in range(step, self.size[1] - step , step):
                offsetX = randrange(step - 2) - int(step / 2)
                offsetY = randrange(step - 2) - int(step / 2)
                points.append(Point(i + offsetX, j + offsetY))

    def generateFrame(self):
        points = []

        self.seedFrame(points, 15)
        #self.seedFrame(points, 20) # step needs to be calced based on world params
        print("2.  Creating basic triangulation")
        triangulation = Triangulation(points)
        print("2.1 Refine triangulation")
        delaunay = Delaunay(triangulation)
        print(" ")
        print("3.  Calculating voronoi cells")
        voronoi = Voronoi(triangulation, (0,0, self.size[0], self.size[1]))

        if delaunay is None or voronoi is None:
            print("Error: in generateFrame")
            return

        print(" ")
        print("4.  Mapping output to world map")
        edgesDone = 0
        printedProgress = 0
        print("             |_________________________________________________|")
        print("4.  Progress: ", end="")

        for trEdge in triangulation.edges:
            curProgress = int((50/len(triangulation.edges))*edgesDone)
            if printedProgress < curProgress:
                for i in range(curProgress - printedProgress):
                    print("|", end="")
                    printedProgress = curProgress
            edgesDone += 1

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
        print(" ")
        print("5.  Cleanup world site data")

        sitesDone = 0
        printedProgress = 0
        print("             |_________________________________________________|")
        print("5.  Progress: ", end="")

        for site in self.worldSites.items():
            curProgress = int((50/len(self.worldSites.items()))*sitesDone)
            if printedProgress < curProgress:
                for i in range(curProgress - printedProgress):
                    print("|", end="")
                    printedProgress = curProgress
            sitesDone += 1

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
        for site in self.worldSites.items():
            shoud = randrange(20) < 4
            if site[1].isOcean:
                neighbourIdx = randrange(len(site[1].neighbours))
                potOcean = site[1].neighbours[neighbourIdx]
                if not self.worldSites[potOcean].isOcean:
                    self.worldSites[potOcean].isOcean = True;

            
    def draw(self, screen):
        for site in self.worldSites.items():
            site[1].draw(screen)