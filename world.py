from pygamehelper import *
from pygame import *
from math import e, pi, cos, sin, sqrt
from random import uniform, randrange, choice
from voronoi import *
from vec2d import vec2d

import pickle

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

    def draw(self, screen, offset, zoom, viewProps):
        for part in self.parts:
            start = (int((part[0].x + offset[0]) * zoom), int((part[0].y+ offset[1]) * zoom))
            end = (int((part[1].x + offset[0]) * zoom), int((part[1].y+ offset[1]) * zoom))
            if viewProps["DrawMode"] == 1:
                pygame.draw.line(screen, (0, 0, 0), start, end, 4)
            elif self.isRiver:
                pygame.draw.line(screen, (90, 132, 152), start, end, self.riverWidth+1)

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

    def draw(self, screen, offset, zoom, viewProps):
        boundPoints = []
        shouldDrawPoly = True;

        if len(self.borders) < 2:
            shouldDrawPoly = False

        if shouldDrawPoly:
            for border in self.borders:
                for part in border.parts:
                    if len(boundPoints) == 0:
                        boundPoints.append([int((part[0].x + offset[0]) * zoom), int((part[0].y + offset[1]) * zoom)])
                    boundPoints.append([int((part[1].x + offset[0]) * zoom), int((part[1].y + offset[1]) * zoom)])
        if shouldDrawPoly:
            pygame.draw.polygon(screen, self.getColor(), boundPoints)
        if viewProps["ShowPoints"]:
            pygame.draw.circle(screen, (200, 0, 0), (int((self.center.x + offset[0]) * zoom), int((self.center.y + offset[1]) * zoom)), 2, 1)

    def drawBorders(self, screen, offset, zoom, viewProps):
        for border in self.borders:
            border.draw(screen, offset, zoom, viewProps)
            



class WorldMap:
    def __init__(self, seed, size):
        self.seed = seed
        self.size = size

        self.worldSites = {}

        self.rivers = []

    def generate(self):

        # outfile = open('data.txt', 'wb')
        # self.generateFrame()
        # pickle.dump(self.worldSites, outfile)

        outfile = open('data.txt', 'rb')
        self.worldSites = pickle.load(outfile)

        self.siteDataCleanup()

    def seedFrame(self, points, step):
        for i in range(step, self.size[0] - step, step):
            for j in range(step, self.size[1] - step , step):
                offsetX = randrange(step - 2) - int(step / 2)
                offsetY = randrange(step - 2) - int(step / 2)
                points.append(vec2d(i + offsetX, j + offsetY))

    def generateFrame(self):
        points = []

        self.seedFrame(points, 15)
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
            newNeghbours = []
            borders = site[1].borders
            idx = 0
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
                        newNeghbours.append(site[1].neighbours[idx])
                idx += 1
            # For any index the border is between cur cell and neighbour sell with the same idx
            for neighbour in site[1].neighbours:
                if neighbour not in newNeghbours:
                    newNeghbours.append(neighbour)

            if len(newBorders) > 1:
                orderedBorders = []
                orderedNeighbours = []
                orderedBorders.append(newBorders.pop(0))
                orderedNeighbours.append(newNeghbours.pop(0))

                completePoly = True
                while len(newBorders) > 0:
                    change = False
                    idx = 0
                    for nexBorder in newBorders:
                        if orderedBorders[-1].end == nexBorder.start:
                            orderedBorders.append(nexBorder)
                            newBorders.remove(nexBorder)
                            orderedNeighbours.append(newNeghbours.pop(idx))
                            change = True
                            break
                        elif orderedBorders[-1].end == nexBorder.end:
                            reversedBorder = Border(nexBorder.end, nexBorder.start)
                            orderedBorders.append(reversedBorder)
                            orderedNeighbours.append(newNeghbours.pop(idx))
                            newBorders.remove(nexBorder)
                            change = True
                            break
                        idx += 1
                    if not change:
                        #print("Error: in siteDataCleanup / hole in poly")
                        completePoly = False
                        break
                for leftNeighbour in newNeghbours:
                    orderedNeighbours.append(leftNeighbour)

                if completePoly:
                    site[1].borders = orderedBorders
                    site[1].neighbours = orderedNeighbours
                else:
                    site[1].borders = newBorders
                    site[1].neighbours = newNeghbours
            else:
                site[1].borders = newBorders
                site[1].neighbours = newNeghbours

    def generateLandmass(self):
        ceedCount = 3 * randrange(5,15)
        mountainRange = 10
        borderSize = 200

        ceedHight = 11

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
            self.worldSites[rangeMembers[-1]].elevation = ceedHight
            while len(rangeMembers) < mountainRange:
                curSite = self.worldSites[rangeMembers[-1]]
                added = False
                for neighbour in curSite.neighbours:
                    if neighbour not in rangeMembers and not self.worldSites[neighbour].lockedElevation:
                        self.worldSites[neighbour].elevation = ceedHight
                        rangeMembers.append(neighbour)
                        added = True
                        break
                if not added:
                    print("Problem with generating mountain range")
                    break
        self.blurMap()

    def calcBorderElevation(self):
        for site in self.worldSites.items():
            if not site[1].lockedElevation:
                for idx in range(len(site[1].borders)):
                    if site[1].borders[idx].elevation == None:
                        site[1].borders[idx].elevation = int((site[1].elevation + self.worldSites[site[1].neighbours[idx]].elevation)/2)

    def markOceans(self):
        while True:
            haveChanges = False
            for site in self.worldSites.items():
                if not site[1].isOcean:
                    if site[1].lockedElevation:
                        site[1].isOcean = True
                        haveChanges = True
                    elif site[1].elevation < 0:
                        for neighbour in site[1].neighbours:
                            if self.worldSites[neighbour].isOcean:
                                site[1].isOcean = True
                                haveChanges = True
                                break
            if not haveChanges:
                break

    def generateRivers(self):
        self.rivers = []
        self.markOceans()
        self.calcBorderElevation()
        for site in self.worldSites.items():
            if site[1].elevation in range(3):
                neighbouringWater = None
                idx = 0
                for neighbour in site[1].neighbours:
                    if self.worldSites[neighbour].elevation < 0 and neighbouringWater == None:
                        neighbouringWater = neighbour
                        break
                if neighbouringWater != None:
                    for neighbour in site[1].neighbours:
                        if self.worldSites[neighbour].hasNeighbour(neighbouringWater) and self.worldSites[neighbour].elevation >= 0:
                            newRiver = []
                            isReversed = False
                            for edge in self.worldSites[neighbouringWater].borders:
                                if edge.start == site[1].borders[idx].end or edge.end == site[1].borders[idx].end:
                                    isReversed = True
                                    break
                            if isReversed:
                                reversedBorder = Border(site[1].borders[idx].end, site[1].borders[idx].start)
                                reversedBorder.elevation = site[1].borders[idx].elevation
                                newRiver.append((site[0], idx, reversedBorder))
                            else:
                                newRiver.append((site[0], idx, site[1].borders[idx]))
                            self.rivers.append(newRiver)
                            self.buildRiver(site[0], neighbour, newRiver, self.rivers)
                            break
                        idx += 1

        filteredRivers = [river for river in self.rivers if len(river) > 9 and abs(river[-1][2].elevation - river[0][2].elevation) > 5]
        self.rivers = []
        for filteredRiver in filteredRivers:
            hasHits = False
            for part in filteredRiver:
                for river in self.rivers:
                    for riverPart in river:
                        if (part[2].start == riverPart[2].start or 
                            part[2].end == riverPart[2].start or 
                            part[2].start == riverPart[2].end or 
                            part[2].end == riverPart[2].end):
                            hasHits = True
                            break
                    if hasHits:
                        break
                if hasHits:
                    break
            if not hasHits:
                self.rivers.append(filteredRiver)

        for river in self.rivers:
            step = int(len(river)/8)
            width = 8
            idx = 0
            for part in river:
                self.worldSites[part[0]].borders[part[1]].isRiver = True
                self.worldSites[part[0]].borders[part[1]].riverWidth = width
                idx += 1
                if idx == step:
                    idx = 0
                    width -= 1
        print("Result:")
        print("Rivers: ", len(self.rivers))
        self.smoothBorders()
        

    def smoothBorders(self):
        for site in self.worldSites.items():
            neighbourIdx = 0
            for border in site[1].borders:
                neighbourId = site[1].neighbours[neighbourIdx]
                neighbour = self.worldSites[neighbourId]
                if site[1].getColor() != neighbour.getColor():
                    border.subDevide(12)
                    if site[0] in neighbour.neighbours:
                        borderMirrorIdx = neighbour.neighbours.index(site[0])
                        if border.start == neighbour.borders[borderMirrorIdx].start:
                            neighbour.borders[borderMirrorIdx].parts = site[1].borders[neighbourIdx].parts
                        else:
                            neighbour.borders[borderMirrorIdx].parts = site[1].borders[neighbourIdx].getReversedParts()
                    else:
                        print(neighbour.key)
                neighbourIdx += 1

    def buildRiver(self, siteOneID, siteTwoID, river, allRivers):
        oldRiverPiece = river[-1][2]
        saiteL = self.worldSites[siteOneID]
        saiteR = self.worldSites[siteTwoID]
        borderLeft = 0
        borderRight = 0
        leftReversed = False
        rightReversed = False

        for bordrderL in saiteL.borders:
            if oldRiverPiece.end == bordrderL.start and oldRiverPiece.start != bordrderL.end:
                break
            elif oldRiverPiece.end == bordrderL.end and oldRiverPiece.start != bordrderL.start:
                leftReversed = True
                break
            borderLeft += 1

        for bordrderR in saiteR.borders:
            if oldRiverPiece.end == bordrderR.start and oldRiverPiece.start != bordrderR.end:
                break
            elif oldRiverPiece.end == bordrderR.end and oldRiverPiece.start != bordrderR.start:
                rightReversed = True
                break
            borderRight += 1

        if (
                borderLeft < len(saiteL.borders) and borderRight < len(saiteR.borders) and 
                saiteL.borders[borderLeft].elevation > saiteR.borders[borderRight].elevation and
                saiteL.borders[borderLeft].elevation >= oldRiverPiece.elevation
            ):
            #generate left
            if leftReversed:
                reversedBorder = Border(saiteL.borders[borderLeft].end, saiteL.borders[borderLeft].start)
                reversedBorder.elevation = saiteL.borders[borderLeft].elevation
                river.append((siteOneID, borderLeft, reversedBorder))
            else:
                river.append((siteOneID, borderLeft, saiteL.borders[borderLeft]))
            self.buildRiver(siteTwoID, saiteL.neighbours[borderLeft], river, allRivers)
        elif borderRight < len(saiteR.borders) and saiteR.borders[borderRight].elevation >= oldRiverPiece.elevation:
            #generate right
            if rightReversed:
                reversedBorder = Border(saiteR.borders[borderRight].end, saiteR.borders[borderRight].start)
                reversedBorder.elevation = saiteR.borders[borderRight].elevation
                river.append((siteTwoID, borderRight, reversedBorder))
            else:
                river.append((siteTwoID, borderRight, saiteR.borders[borderRight]))
            self.buildRiver(siteTwoID, saiteR.neighbours[borderRight], river, allRivers)



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
            site[1].elevation = -10
            self.isOcean = False
            for border in site[1].borders:
                border.elevation = None
                border.isRiver = False
                border.riverWidth = 0


            
    def draw(self, screen, offset, zoom, viewProps):
        for site in self.worldSites.items():
            # if (site[1].center.x in range(offset[0], int(self.size[0]*zoom) + 20) and 
            # site[1].center.y in range(offset[1], int(self.size[1]*zoom) + 20)):
            site[1].draw(screen, offset, zoom, viewProps)
        for site in self.worldSites.items():
            # if (site[1].center.x in range(offset[0], int(self.size[0]*zoom) + 20) and 
            # site[1].center.y in range(offset[1], int(self.size[1]*zoom) + 20)):
            site[1].drawBorders(screen, offset, zoom, viewProps)

    def drawSite(self, screen, viewProps, siteIdx):
        siteKey = list(self.worldSites.keys())[siteIdx]
        curSite = self.worldSites[siteKey]
        zoom = self.size[1] / 100
        offset = [40 - curSite.center.x, 40 - curSite.center.y]
        curSite.draw(screen, offset, zoom, viewProps)
        curSite.drawBorders(screen, offset, zoom, viewProps)
        idx = 0
        for neighbour in curSite.neighbours:
            offsetSite = [0, 0]
            offsetSite[0] = int((self.worldSites[neighbour].center.x - curSite.center.x)*0.5) + offset[0]
            offsetSite[1] = int((self.worldSites[neighbour].center.y - curSite.center.y)*0.5) + offset[1]
            self.worldSites[neighbour].draw(screen, offsetSite, zoom, viewProps)
            siteMarkerPos = (int((self.worldSites[neighbour].center.x + offsetSite[0]) * zoom), int((self.worldSites[neighbour].center.y + offsetSite[1]) * zoom))
            pygame.draw.circle(screen, (24 * idx, 240 - 24 * idx, 3 * idx), siteMarkerPos, 5)
            idx += 1

    def drawRiver(self, screen, offset, zoom, viewProps, siteIdx):
        for site in self.worldSites.items():
            site[1].draw(screen, offset, zoom, viewProps)
        for site in self.worldSites.items():
            site[1].drawBorders(screen, offset, zoom, viewProps)

        curRiver = self.rivers[siteIdx]
        print("Stats: ", len(curRiver), abs(curRiver[-1][2].elevation - curRiver[0][2].elevation))

        for riverPart in curRiver:
            curRiverPart = riverPart[2]
            start = (int((curRiverPart.start.x + offset[0]) * zoom), int((curRiverPart.start.y+ offset[1]) * zoom))
            end = (int((curRiverPart.end.x + offset[0]) * zoom), int((curRiverPart.end.y+ offset[1]) * zoom))
            pygame.draw.line(screen, (125, 0, 0), start, end, 4)
