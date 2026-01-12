from Snake import Snake
import math
import random
import numpy as np
from scipy.spatial.distance import cdist


class AI(Snake):
    def __init__(self, x, y, w, h, filePath, Mapsize):
        super().__init__(x, y, w, h, filePath, Mapsize)

    def update(self, snakes):
        return super().update(snakes)
# A function that takes in observables and predicts the x,y point to move to 
    def calculateDirection(self, grid, food):
        if len(food)==0:
            return
        #closestDist = math.inf
        #closestFood = food[0]
        closestFood = grid.searchForClosestNeighbour(self)
        
        if(closestFood == None):
            direction = [1,1]
        else:
            direction = [closestFood.rect.x - self.rect.x, closestFood.rect.y - self.rect.y]
        #print(closestFood)
        
        l = (direction[0]**2 + direction[1]**2) ** (1/2)
        if(l == 0):
            return
        direction[0] /= l
        direction[1] /= l
        desired_angle = math.degrees(math.atan2(direction[1], direction[0]))
        #gradual turn towards target
        angle_difference = (desired_angle - self.angle + 180) % 360 - 180
        
        if abs(angle_difference) > self.turnSpeed:
            self.angle += self.turnSpeed if angle_difference > 0 else -self.turnSpeed
        else:
            self.angle = desired_angle
        self.angle = math.radians(self.angle)
        self.direction=direction
   ## def calculateDirection(self):
        #Define inputs

        
        #Create Model structure


        #Handle Outputs
       # pass
