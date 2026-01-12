import pygame

class Map:
    def __init__(self, x, y, scale, MapSize):
        self.scale = scale
        self.x = x
        self.y = y
        self.MapSize = MapSize/self.scale #radius




    def update(self, playerX, playerY):
            playerX = (playerX/self.scale) 
            playerY = (playerY/self.scale)

    def draw(self, window):
         pygame.draw.circle(self.window, (85,85,85), self.x,self.y, self.MapSize, width=0)
         pygame.draw.circle(self.window, (85,85,85), self.x,self.y, self.MapSize, width=0)