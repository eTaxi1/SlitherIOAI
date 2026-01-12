import pygame

class FreeCam:
    def __init__(self, x, y, windowDims, mapSize, w, h):
        self.x = x
        self.y = y
        self.windowDims = windowDims
        self.zoom = 0.3
        self.mapSize = mapSize
        self.offset = -mapSize/2

    def update(self, specX, specY):
        self.x = specX
        self.y = specY
        
    def applyZoom(self, scale_factor,):
        self.zoom *= scale_factor
        self.zoom = max(0.05, min(self.zoom, 5))
         
    
    def translate(self,x,y):#, w, h):
        return ((x-self.x - self.offset - 600 + self.windowDims[0]/2)*self.zoom, (y-self.y - self.offset + self.windowDims[1]/2)*self.zoom, self.mapSize*self.zoom)#, self.w*self.zoom, self.h*self.zoom)