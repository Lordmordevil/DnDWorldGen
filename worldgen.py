from pygamehelper import *
from pygame import *
from world import WorldMap 




class Starter(PygameHelper):
    def __init__(self):
        self.w, self.h = 1200, 700
        self.offset = [0,0]
        self.zoom = 1
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))

        self.showVerts = True;
        self.showTesl = False;

        self.map = WorldMap(123, (self.w, self.h))

    def getOffset(self):
        return [int(self.offset[0] * self.zoom), int(self.offset[1] * self.zoom)]
        
    def update(self):
        pass
            
        
    def keyUp(self, key):
        print(key)
        if key == 118: #pressed V
            self.map.generateLandmass()
            print("Generating Land")
        elif key == 98:  #pressed B
            self.map.blurMap()
            print("Blur")
        elif key == 114: #pressed R
            self.map.reset()
            print("Reset Elevation")
        if key == 269:
            self.zoom *= 0.66
        if key == 270:
            self.zoom *= 1.5
        if key == 273:
            self.offset[1] += 10/self.zoom
        if key == 274:
            self.offset[1] -= 10/self.zoom
        if key == 275:
            self.offset[0] -= 10/self.zoom
        if key == 276:
            self.offset[0] += 10/self.zoom

        
    def mouseUp(self, button, pos):
        pass
        # self.points.append(Point(pos[0], pos[1]))
        # self.initTriangulation()
        
        
    def mouseMotion(self, buttons, pos, rel):
        pass
        
        
    def draw(self):
        self.screen.fill((39, 50, 64))
        
        self.map.draw(self.screen, self.getOffset(), self.zoom)
            

s = Starter()
s.mainLoop(40)
