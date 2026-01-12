import pygame
from Object import Object
from Segment import Segment
import random
import math
from Food import Food


maxDistance = 500
START_SCORE = 10
START_WIDTH = 10
class Snake(Object):

    def __init__(self, x, y, w, h, filePath, MapSize):
        super().__init__(x,y,w,h,filePath)
        self.speed = 5
        self.dspeed = self.speed
        self.score = START_SCORE
        self.prevScore = 0
        self.filePath = filePath
        self.segments = []
        self.direction = [1,1]
        self.angle = 0
        self.turnSpeed = 5
        self.Mapsize = MapSize
        self.begin = True
        self.boost = False
        self.startSegments()
        self.startSize = 10
        self.startTurnSpeed = 5

    def update(self, snakes):
        # Calculating new position
        self.rect.x += math.cos(self.angle) * self.speed
        self.rect.y += math.sin(self.angle) * self.speed
        self.angle = math.degrees(self.angle)

        if self.begin == True:
            self.startSegments()
        #Adding segments
        if(self.score - 10 - self.prevScore >= 10):
            self.prevScore = self.score - 10
            self.addSegment()
        self.updateSegments()
        if(self.collide_with_snake(snakes)):
            return True
        
        return False            

    def collide_with_snake(self, snakes):
        for snake in snakes:
             direction = [snake.rect.x - self.rect.x, snake.rect.y - self.rect.y]
             dist = (direction[0]**2 + direction[1]**2)**(1/2)

             if dist > maxDistance or dist == 0:
                  continue
             
             for segment in snake.segments:
                 if self.rect.colliderect(segment.rect):
                     return True
                 
    def draw(self, window, camera):
        super().draw(window, camera)
        #font = pygame.font.Font(None, 20)
        #score_text = font.render(f'Score: {self.score}', True, (15, 15, 15))
        #window.blit(score_text, (10, 10))
        zoom = camera.zoom
        for segment in self.segments:
             pos = camera.translate(segment.rect.x, segment.rect.y)
             scaledTexture = pygame.transform.scale(segment.texture, (int(segment.rect.width * zoom), int(segment.rect.height * zoom)))
             window.blit(scaledTexture, (pos[0], pos[1]))
    
    def reset(self):
        randXY = self.polarCoord(self.Mapsize)
        self.rect.x = randXY[0]
        self.rect.y = randXY[1]
        self.score=START_SCORE
        self.rect.w = START_WIDTH
        self.rect.h = START_WIDTH
        self.speed = self.dspeed
        self.prevScore = 0
        self.turnSpeed = 5
        self.segments = []
        self.startSegments()
        self.begin = True
    
    def polarCoord(self, MapSize):
            r = random.randint(-MapSize, MapSize)
            alpha = 2 * math.pi * random.random()
            randX = r * math.cos(alpha)
            randY = r * math.sin(alpha)
            return (randX, randY)
    
    def startSegments(self):
            for i in range(8):
                 self.addSegment()
            self.begin = False
    def adjustSize(self):
        seg = None
        if(self.score < 100):
            additional_segments = (self.score - 10) // 5
            length = 9 + additional_segments
        else:
            additional_segments = 0.5 * math.sqrt(self.score-100)
            length = min(17 + additional_segments, 50)
        if(length // 1 > len(self.segments)):
            seg = self.addSegment()
        self.rect.w = min(self.startSize + 0.3 * math.log(self.score, 2), 100)
        self.rect.h = min(self.startSize + 0.3 * math.log(self.score, 2), 100)
        self.turnSpeed = self.startTurnSpeed - 0.12 * math.log(self.score, 2)
        for segment in self.segments:
            segment.rect.w = self.rect.w
            segment.rect.h = self.rect.h
        
        return seg
            
    def addSegment(self):
        startX = self.direction[0] * -1 * self.rect.w * (1/2)
        startY = self.direction[1] * -1 * self.rect.h * (1/2)
        if(len(self.segments)==0):
            startX += self.rect.x
            startY += self.rect.y
        else:
            startX += self.segments[-1].rect.x
            startY += self.segments[-1].rect.y
        if(self.begin == True):      
            self.rect.w *= 1.1
            self.rect.h *= 1.1
            self.turnSpeed *= 0.99
            self.startTurnSpeed = self.turnSpeed
            self.startSize = self.rect.w
        for segment in self.segments:
            if self.begin == True: 
                segment.rect.w = self.rect.w
                segment.rect.h = self.rect.h
                   
        newSegment = Segment(startX, startY, self.rect.w, self.rect.h, self.filePath, self.speed)
              #newSegment.update()
        self.segments.append(newSegment)
        return newSegment
        
     
    def updateSegments(self):
         for i in range(len(self.segments)):
             if i == 0:
                 self.segments[i].update((self.rect.x, self.rect.y))
             else:
                 self.segments[i].update((self.segments[i-1].rect.x, self.segments[i-1].rect.y))
              
    def boostSnake(self):
         ## If NN returns value > X turn boost is true
         if self.boost == True and self.score > 11:
              self.score -= 2
              self.adjustSize()
              self.speed = self.dspeed * 2
              location = [self.segments[-1].rect.x + self.segments[-1].rect.w,
                           self.segments[-1].rect.y + self.segments[-1].rect.h/2]
              newFood = Food(location[0], location[1], 10, self.filePath)
              return newFood 
         else:
              self.speed = self.dspeed 
             
    
        