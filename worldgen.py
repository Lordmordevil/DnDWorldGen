from pygamehelper import *
from pygame import *
from world import WorldMap 




class Starter(PygameHelper):
    def __init__(self):
        self.w, self.h = 1600, 900
        self.offset = [0,0]
        self.viewProps = {"ShowPoints" : False , "DrawMode" : 0}
        self.zoom = 1
        PygameHelper.__init__(self, size=(self.w, self.h), fill=((255,255,255)))

        self.showVerts = True;
        self.showTesl = False;

        self.map = WorldMap(123, (self.w, self.h))
        self.map.generate()

        self.tileIdx = 0

    def getOffset(self):
        return [int(self.offset[0] * self.zoom), int(self.offset[1] * self.zoom)]
        
    def update(self):
        pass
            
        
    def keyUp(self, key):
        if key == 118: #pressed V
            self.map.generateLandmass()
            print("Generating Land")
        elif key == 98:  #pressed B
            self.map.generateRivers()
            print("Generate rivers")
        elif key == 114: #pressed R
            self.map.reset()
            self.tileIdx = 0
            print("Reset Elevation")
        elif key == 112: #pressed P
            self.viewProps["ShowPoints"] = not self.viewProps["ShowPoints"]
            print("Show points")
        elif key == 109: #pressed M
            self.viewProps["DrawMode"] += 1
            if self.viewProps["DrawMode"] == 3:
                self.viewProps["DrawMode"] = 0
            print("Map mode")
        elif key == 110: #pressed N
            print("Next site: ", self.tileIdx)
            self.tileIdx += 1
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
        
        
    def mouseMotion(self, buttons, pos, rel):
        pass
        
        
    def draw(self):
        if self.viewProps["DrawMode"] == 0:
            self.screen.fill((39, 50, 64))
            self.map.draw(self.screen, self.getOffset(), self.zoom, self.viewProps)
        elif self.viewProps["DrawMode"] == 1:
            self.screen.fill((0, 0, 0))
            self.map.drawSite(self.screen, self.viewProps, self.tileIdx)
        elif self.viewProps["DrawMode"] == 2:
            self.screen.fill((0, 0, 0))
            self.map.drawRiver(self.screen, self.viewProps, self.tileIdx)
            

s = Starter()
s.mainLoop(40)
