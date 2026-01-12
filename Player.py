import pygame
import random
import math
from Snake import Snake
from Segment import Segment


START_SCORE = 30


class Player(Snake):

    def __init__(self, x, y, w, h, filePath, winDims, Mapsize):
        super().__init__(x,y,w,h,filePath, Mapsize)
        pygame.font.init()
        self.winDims = winDims

    def update(self, food, snakes):
        self.calculateDirection()
        return super().update(snakes)
         
    def draw(self, window, camera):
        super().draw(window, camera)
        font = pygame.font.Font(None, 20)
        score_text = font.render(f'Score: {self.score}', True, (15, 15, 15))
        window.blit(score_text, (10, 10))
    
    
    def calculateDirection(self):
          mousePos = pygame.mouse.get_pos()
          worldPos = (mousePos[0] - self.winDims[0]/2 + self.rect.x, mousePos[1] - self.winDims[1]/2 + self.rect.y)
          self.direction = [worldPos[0] - self.rect.x, worldPos[1] - self.rect.y ]
          length = (self.direction[0]**2 + self.direction[1]**2)**(1/2)
          self.direction = [self.direction[0]/length, self.direction[1]/length]
         
        
        