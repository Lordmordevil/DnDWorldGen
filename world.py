from pygamehelper import *
from pygame import *

from random import randrange, choice

from border import Border
from worldFrame import WorldFrame
from worldSait import WorldSait

class WorldMap:
    def __init__(self, seed, size):
        self.seed = seed
        self.size = size

        self.worldSites = WorldFrame(seed, size).saveFrame()

        self.rivers = []


    def generateLandmass(self):
        ceedCount = 3 * randrange(5,15)
        mountainRange = 10
        borderSize = 200

        ceedHight = 11

        siteKeys = []
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
                if site[1].markOcean(self.worldSites):
                    haveChanges = True
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
                    border.subDevide(9)
                    if site[0] in neighbour.neighbours:
                        borderMirrorIdx = neighbour.neighbours.index(site[0])
                        if border.start == neighbour.borders[borderMirrorIdx].start:
                            neighbour.borders[borderMirrorIdx].parts = site[1].borders[neighbourIdx].parts
                        else:
                            neighbour.borders[borderMirrorIdx].parts = site[1].borders[neighbourIdx].getReversedParts()
                        neighbour.recalc_border_cache()
                    else:
                        print(neighbour.key)
                neighbourIdx += 1
            site[1].recalc_border_cache()

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


            
    def draw(self, screen, camera):
        for site in self.worldSites.items():
            site[1].draw(screen, camera)
        for site in self.worldSites.items():
            site[1].drawBorders(screen, camera)

