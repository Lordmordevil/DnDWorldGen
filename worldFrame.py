from random import randrange

from voronoi import Voronoi
from vec2d import vec2d
from worldSait import WorldSait
from border import Border

import pickle


class WorldFrame:
    def __init__(self, seed, size):
        self.seed = seed
        self.size = size

    def loadFrame(self):
        outfile = open('data.txt', 'rb')
        worldSites = pickle.load(outfile)
        for site in worldSites.items():
            self.siteDataCleanup(site[1])
        return worldSites

    def saveFrame(self):
        worldSites = self.generateFrame()
        outfile = open('data.txt', 'wb')
        pickle.dump(worldSites, outfile)
        for site in worldSites.items():
            self.siteDataCleanup(site[1])
        return worldSites

    def seedFrame(self, points, step):
        for i in range(step, self.size[0] - step, step):
            for j in range(step, self.size[1] - step , step):
                offsetX = randrange(step - 2) - int(step / 2)
                offsetY = randrange(step - 2) - int(step / 2)
                points.append(vec2d(i + offsetX, j + offsetY))

    def generateFrame(self):
        points = []
        worldSites = {}

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
            if centerOne.key not in worldSites:
                newWorldSite = WorldSait(centerOne)
                worldSites[centerOne.key] = newWorldSite
            if centerTwo.key not in worldSites:
                newWorldSite = WorldSait(centerTwo)
                worldSites[centerTwo.key] = newWorldSite
            siteOne = worldSites[centerOne.key]
            siteTwo = worldSites[centerTwo.key]

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
        return worldSites

    def siteDataCleanup(self, site):
        newBorders = []
        newNeghbours = []
        borders = site.borders
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
                    newNeghbours.append(site.neighbours[idx])
            idx += 1
        # For any index the border is between cur cell and neighbour sell with the same idx
        for neighbour in site.neighbours:
            if neighbour not in newNeghbours:
                newNeghbours.append(neighbour)
        # Add neighbours with missing borders (frame sites)

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
                site.borders = orderedBorders
                site.neighbours = orderedNeighbours
            else:
                site.borders = newBorders
                site.neighbours = newNeghbours
        else:
            site.borders = newBorders
            site.neighbours = newNeghbours