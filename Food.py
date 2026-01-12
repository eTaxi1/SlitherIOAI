import pygame
import math
from Object import Object


class Food(Object):
    def __init__(self, x, y, r, filePath):
        super().__init__(x,y,r,r,filePath)
        self.score = r

    def update(self, snakes):
        for snake in snakes:
            if self.rect.colliderect(snake.rect):
                print(f'Snake Score Before: {snake.score}    |    Food Size: {self.score}           Size B: {snake.rect.w}')
                snake.score += round(self.score*(1/10))
                print(f'Snake Score After: {snake.score}           |  Size A: {snake.rect.w}')
                return True
        return False
    
    
    
        