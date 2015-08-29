from pygamehelper import *
from pygame import *

from world import WorldMap 
from camera import Camera
        

class Starter(PygameHelper):
    def __init__(self):
        
        self.w, self.h = 1600, 1200

        self.camera = Camera()
        
        PygameHelper.__init__(self, size=(self.camera.view_w, self.camera.view_h), fill=((255,255,255)))

        self.showVerts = True;
        self.showTesl = False;

        self.map = WorldMap(123, (self.w, self.h))

        self.tileIdx = 0
        
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
            self.camera.viewProps["ShowPoints"] = not self.camera.viewProps["ShowPoints"]
            print("Show points")
        elif key == 109: #pressed M
            self.camera.viewProps["DrawMode"] += 1
            if self.camera.viewProps["DrawMode"] == 3:
                self.camera.viewProps["DrawMode"] = 0
            print("Map mode")
        elif key == 110: #pressed N
            print("Next site: ", self.tileIdx)
            self.tileIdx += 1
        if key == 269:
            self.camera.zoom *= 0.66
        if key == 270:
            self.camera.zoom *= 1.5
        if key == 273:
            self.camera.offset[1] -= 10/self.camera.zoom
        if key == 274:
            self.camera.offset[1] += 10/self.camera.zoom
        if key == 275:
            self.camera.offset[0] += 10/self.camera.zoom
        if key == 276:
            self.camera.offset[0] -= 10/self.camera.zoom

        
    def mouseUp(self, button, pos):
        pass
        
        
    def mouseMotion(self, buttons, pos, rel):
        pass
        
        
    def draw(self):
        if self.camera.viewProps["DrawMode"] == 0:
            self.screen.fill((39, 50, 64))
            self.map.draw(self.screen, self.camera)
            

s = Starter()
s.mainLoop(40)
