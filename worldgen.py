from pygamehelper import *
from pygame import *
from world import WorldMap 




class Starter(PygameHelper):
    def __init__(self):
        self.w, self.h = 1200, 700
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))

        self.showVerts = True;
        self.showTesl = False;

        self.map = WorldMap(123, (self.w, self.h))

        
    def update(self):
        pass
        
    def keyUp(self, key):
        if key == 118: #pressed V
            self.map.generateLandmass()
            print("Generating Ocean")

        
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
