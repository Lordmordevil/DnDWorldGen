from pygamehelper import *
from pygame import *
from pygame.locals import *
from vec2d import *
from math import e, pi, cos, sin, sqrt
from random import uniform, randrange
from voronoi import *

class Starter(PygameHelper):
    def __init__(self):
        self.w, self.h = 1200, 700
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))
        
        self.delaunay = None
        self.voronoi = None
        self.points = []

        self.showVerts = True;
        self.showTesl = False;
        
        #self.initPoints(20)
        #self.initTriangulation()

        self.hello()

    def hello(self):
        print("Press V to show voronoi edges")
        print("Press T to show triangulation edges")

    def initPoints(self, step):
        for i in range(step, self.w - step, step):
            for j in range(step, self.h - step , step):
                offsetX = randrange(step - 2) - int(step / 2)
                offsetY = randrange(step - 2) - int(step / 2)
                self.points.append(Point(i + offsetX, j + offsetY))

        
    def initTriangulation(self):
        print("set triangulation")
        self.triangulation = Triangulation(self.points)
        print("calc delunary")
        self.delaunay = Delaunay(self.triangulation)
        print("calc voronoi")
        self.voronoi = Voronoi(self.triangulation, (0,0, self.w, self.h))
        print("calc done")
        
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
        self.points.append(Point(pos[0], pos[1]))
        self.initTriangulation()
        
        
    def mouseMotion(self, buttons, pos, rel):
        pass
        
        
    def draw(self):
        self.screen.fill((255, 255, 255))
        
        if self.delaunay is None or self.voronoi is None:
            return
        
        if self.showTesl:
            for trEdge in self.triangulation.edges:
                first = self.points[trEdge.a]
                sec = self.points[trEdge.b]
                pygame.draw.line(self.screen, (0, 0, 0), (int(first.x), int(first.y)), (int(sec.x), int(sec.y)), 1)
    
        if self.showVerts:
            for voEdge in self.voronoi.edges:
                asd = self.voronoi.points[voEdge.a]
                bsd = self.voronoi.points[voEdge.b]
                if ((asd.x > 0 and asd.x < self.w) and (asd.y > 0 and asd.y < self.h) and
                    (bsd.x > 0 and bsd.x < self.w) and (bsd.y > 0 and bsd.y < self.h)):
                    pygame.draw.line(self.screen, (0, 200, 0), (int(asd.x), int(asd.y)), (int(bsd.x), int(bsd.y)), 1)
        
        for point in self.points:
            pygame.draw.circle(self.screen, (200, 0, 0), (int(point.x), int(point.y)), 2, 1)
            

s = Starter()
s.mainLoop(40)
