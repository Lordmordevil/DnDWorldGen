from pygamehelper import *
from pygame import *
from vec2d import *
from math import e, pi, cos, sin, sqrt
from random import uniform, randrange, choice
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

        self.lockedElevation = False
        self.elevation = -10
        
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

    # def getColor(self): #Marti heatmap
    #     color = (120 + self.elevation *10, 10, 120 - self.elevation *10)
    #     return color

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
        ceedCount = 3 * randrange(3,12)
        mountainRange = 10
        borderSize = 200

        siteKeys = []
        #siteKeys = list(self.worldSites.keys())
        for site in self.worldSites.items():
            if (site[1].center.x > borderSize and site[1].center.x < (self.size[0] - borderSize) and 
                site[1].center.y > borderSize and site[1].center.y < (self.size[1] - borderSize) and 
                not site[1].lockedElevation):
                siteKeys.append(site[0])

        for ceed in range(ceedCount):
            rangeMembers = []
            rangeMembers.append(choice(siteKeys))
            self.worldSites[rangeMembers[-1]].elevation = 10
            while len(rangeMembers) < mountainRange:
                curSite = self.worldSites[rangeMembers[-1]]
                added = False
                for neighbour in curSite.neighbours:
                    if neighbour not in rangeMembers and not self.worldSites[neighbour].lockedElevation:
                        self.worldSites[neighbour].elevation = 10
                        rangeMembers.append(neighbour)
                        added = True
                        break
                if not added:
                    print("Problem with generating mountain range")
                    break
        self.blurMap()

    def blurMap(self):
        newElevation = {}
        for site in self.worldSites.items():
            if not site[1].lockedElevation:
                elevationSum = site[1].elevation
                for neighbour in site[1].neighbours:
                    elevationSum += self.worldSites[neighbour].elevation
                newElevation[site[0]] =int(elevationSum/ (len(site[1].neighbours) + 1))
        for values in newElevation.items():
            self.worldSites[values[0]].elevation = values[1]

    def reset(self):
        for site in self.worldSites.items():
            if not site[1].lockedElevation:
                site[1].elevation = -10

            
    def draw(self, screen):
        for site in self.worldSites.items():
            site[1].draw(screen)