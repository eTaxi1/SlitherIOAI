import pygame
from Object import Object
import math

class Segment(Object):
    def __init__(self, x, y, w, h, filePath, speed):
        super().__init__(x, y, w, h, filePath)
        self.speed = speed + int(speed * 0.4)
        self.dspeed = speed
        self.angle = 0
        self.turnSpeed = 15
        self.dturnspeed = 15
        self.direction = [1,1]

    def update(self, targetPos):
        direction = [targetPos[0]-self.rect.x, targetPos[1]-self.rect.y]
        
        length = (direction[0]**2 + direction[1]**2)**(1/2)
        if length == 0:
            return
        elif length < self.rect.w*(1/2):
            self.speed = int(self.dspeed / 2)
        elif length > self.rect.w:
            self.speed = int(self.dspeed * 4)
            self.turnSpeed = int(self.dturnspeed * 6)
        else:
            self.speed = self.dspeed
            self.turnSpeed = self.dturnspeed
        direction[0] /= length
        direction[1] /= length
        desired_angle = math.degrees(math.atan2(direction[1], direction[0]))
        self.direction = direction
        angle_difference = (desired_angle - self.angle + 180) % 360 - 180
        if abs(angle_difference) > self.turnSpeed:
            self.angle += self.turnSpeed if angle_difference > 0 else -self.turnSpeed
        else:
            self.angle = desired_angle
        self.angle = math.radians(self.angle)
        
        self.rect.x += math.cos(self.angle) * self.speed
        self.rect.y += math.sin(self.angle) * self.speed
        self.angle = math.degrees(self.angle)
        #self.rect.x += direction[0] * self.speed
        #self.rect.y += direction[1] * self.speed
