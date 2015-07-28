from pygamehelper import *
from pygame import *
from pygame.locals import *
from vec2d import *
from math import e, pi, cos, sin, sqrt
from random import uniform, randrange


class Starter(PygameHelper):
    def __init__(self):
        self.w, self.h = 600, 350
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))
        
        self.nx = []
        self.ny = []
        self.nr = []
        self.ng = []
        self.nb = []

        self.num_cells = 10

        for i in range(self.num_cells):
                self.nx.append(randrange(self.w))
                self.ny.append(randrange(self.h))
                self.nr.append(randrange(256))
                self.ng.append(randrange(256))
                self.nb.append(randrange(256))

        self.changed = True

        
    def update(self):
        pass
        
    def keyUp(self, key):
        pass

        
    def mouseUp(self, button, pos):
        self.nx.append(pos[0])
        self.ny.append(pos[1])
        self.nr.append(randrange(256))
        self.ng.append(randrange(256))
        self.nb.append(randrange(256))
        self.num_cells += 1
        self.changed = True
        
        
    def mouseMotion(self, buttons, pos, rel):
        pass
        
        
    def draw(self):
        if self.changed :
                self.screen.fill((255, 255, 255))
                print("Shit")
                print(self.nx)
                print("-------------------")
                print(self.ny)
                
                for y in range(self.h):
                        for x in range(self.w):
                                dmin = math.hypot(self.w-1, self.h-1)
                                j = -1
                                for i in range(self.num_cells):
                                        # d = math.hypot(self.nx[i]-x, self.ny[i]-y)
                                        d = math.fabs(self.nx[i]-x) + math.fabs(self.ny[i]-y)
                                        if d < dmin:
                                                dmin = d
                                                j = i
                                self.screen.set_at((x, y), (self.nr[j], self.ng[j], self.nb[j]))
                for i in range(self.num_cells):
                        self.screen.set_at((self.nx[i], self.ny[i]), (255, 255, 255))
                self.changed = False

s = Starter()
s.mainLoop(40)
