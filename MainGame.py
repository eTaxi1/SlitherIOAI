#Generic Libraries
import pygame
import random
import math
from enum import Enum
#Game Classes
from Player import Player
from Food import Food
from AI import AI
from Snake import Snake
from Camera import Camera
from FreeCam import FreeCam
from Spectator import Spectator
from Grid import Grid


PLAYER_TEXTURE = "textures/head.png"
SCREEN_W = 1000
SCREEN_H = 600
START_H = 10
START_W = 10
FPS = 60
NUM_ORBS = 400
NUM_AI = 0
MapSize = int(SCREEN_W*4)
NUM_PLAYERS = 8


class cameraMode(Enum):
    PLAYER = 1,
    FREE = 2


class MainGame:
    def __init__(self):
        self.dims = (SCREEN_W, SCREEN_H)
        self.window = None #pygame.display.set_mode(self.dims)
        self.winColour= (255,255,255)
        self.end = False
        self.range = MapSize
        PLAYER_START_POS = polarCoord()
        CAMERA_START_POS = PLAYER_START_POS
        pygame.font.init()
        self.players = [] ################### MULTICAM
        self.cameras = []
        self.freeCamera = FreeCam(-MapSize/2, 0, self.dims, MapSize, START_W, START_H)
        self.current_Camind = 0
        self.spectate = Spectator(0,0)
        self.grid = Grid(150, MapSize*2)
        self.clock = pygame.time.Clock()
        self.food = []
        self.snakes = []
        self.cameraMode = cameraMode.PLAYER
        self.textures = ["textures/blue_food.png", "textures/green_food.png", "textures/orange_food.png", "textures/green_food.png", "textures/red_food.png", "textures/yellow_food.png", "textures/purple_food.png", "textures/lyellow_food.png", "textures/indigo_food.png"]
        self.init()
    def get_players(self):
        return self.players

    def get_food_states(self):
        return self.food
    
    def get_grid(self):
        return self.grid
    
    def reset(self):
        self.food = []
        self.grid = Grid(150, MapSize*2)
        for player in self.players:
            player.reset()
            self.grid.addToCell(player)
            for seg in player.segments:
                self.grid.addToCell(seg)
        for i in range(NUM_ORBS):
            randR = random.randint(10, 20) ## size of orb
            randTexture = random.choice(self.textures)
            randXY = polarCoord()
            newFood = Food(randXY[0], randXY[1], randR, randTexture)
            self.food.append(newFood)
            self.grid.addToCell(self.food[i])
            
        
    def init(self):
        self.food = []
        self.snakes = []
        self.grid = Grid(150, MapSize*2)
        #Adding food to game
        for i in range(NUM_ORBS):
            randR = random.randint(10, 20) ## size of orb
            randTexture = random.choice(self.textures)
            randXY = polarCoord()
            newFood = Food(randXY[0], randXY[1], randR, randTexture)
            self.food.append(newFood)
            self.grid.addToCell(self.food[i])
        #adding players to game
        for i in range(NUM_PLAYERS):
            randTexture = random.choice(self.textures)
            randXY = polarCoord()
            newPlayer = Snake(randXY[0], randXY[1], START_W, START_H, randTexture, MapSize)
            newCamera = Camera(randXY[0], randXY[1], (newPlayer.rect.w, newPlayer.rect.h), (SCREEN_W, SCREEN_H))
            self.players.append(newPlayer)
            self.cameras.append(newCamera)
            self.grid.addToCell(newPlayer)
            for seg in newPlayer.segments:
                self.grid.addToCell(seg)
        ##self.play() ###DISABLE

    def play(self):
        while self.end == False:
            self.update()
            self.render()

    def update(self):
        self.clock.tick(FPS)
        #Window events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.end = True
            elif event.type == pygame.KEYDOWN: #################### MULTI CAMERA
                if event.key == pygame.K_3:
                    self.cameraMode = cameraMode.PLAYER
                    self.current_Camind -= 1
                elif event.key == pygame.K_4:
                    self.cameraMode = cameraMode.PLAYER
                    self.current_Camind += 1
                elif event.key == pygame.K_f:
                    self.cameraMode = cameraMode.FREE
                    self.current_Camind = 0
            elif(event.type == pygame.MOUSEBUTTONDOWN):
                if(event.button == 4):
                    self.freeCamera.applyZoom(1.1)
                elif(event.button == 5):
                    self.freeCamera.applyZoom(0.9)
        #Food events
        for f in self.food:
            if(f.update(self.snakes)):                                                  ########################### TODO: SNAKE CELL ADDING/DELETING 
                self.food.remove(f)
                self.grid.deleteFromCell(f)
            if(f.update(self.players)):
                self.food.remove(f)
                self.grid.deleteFromCell(f)
        #print(len(self.food))
        
        if(len(self.food) < NUM_ORBS):
            randR = random.randint(10, 20) ## size of orb
            randTexture = random.choice(self.textures)
            randXY = polarCoord()
            newFood = Food(randXY[0], randXY[1], randR, randTexture)
            self.food.append(newFood)
            self.grid.addToCell(newFood)
        #AI update
        for snake in self.players:# Loop through every snake in the game
             snake.calculateDirection(self.grid, self.food) # Calculate the direction the snake moves
             self.grid.deleteFromCell(snake) # Delete current snake from grid
             if(snake.update(self.players) == True): #### Move the snake in that direction, if they collide with something return True
                     self.grid.addToCell(snake) # Add modified snake back to grid
                     self.dropFood(snake) # Drops food on snake death
                     self.grid.deleteFromCell(snake)                                               ######################## NEEDS ADDED
                     snake.reset()
                     self.grid.addToCell(snake)
             elif((snake.rect.x**2) + (snake.rect.y)**2 >= snake.Mapsize**2):
                 snake.reset()
                 self.grid.addToCell(snake)
             else:
                 self.grid.addToCell(snake)
        ############################################################################################################
        #Camera Movement
        if(self.cameraMode == cameraMode.PLAYER):################ MULTICAMERA
            player = self.players[self.current_Camind]
            camera = self.cameras[self.current_Camind]
            camera.update(player.rect.x, player.rect.y)
        elif(self.cameraMode == cameraMode.FREE):
            self.spectate.update()
            self.freeCamera.update(self.spectate.x, self.spectate.y)
        return 

    def render(self):
        self.window.fill(self.winColour)
        if self.cameraMode == cameraMode.FREE:
            camera = self.freeCamera
            transform = camera.translate(0,0)
            pygame.draw.circle(self.window, (75,75,75), (transform[0], transform[1]), transform[2], width=0)
        else:
            camera = self.cameras[self.current_Camind]
            pygame.draw.circle(self.window, (75,75,75), camera.translate(0,0), MapSize, width=0)
            font = pygame.font.Font(None, 20)
            score_text = font.render(f'Score: {self.players[self.current_Camind].score}', True, (15, 15, 15))
            self.window.blit(score_text, (10, 10))
            
        for f in self.food:
            f.draw(self.window, camera) #### MULTI CAM 
        
       # for snake in self.snakes:
        #    snake.draw(self.window, camera)
        for player in self.players:
            player.draw(self.window, camera)
        #pygame.draw.circle()
        ##multicam
        if(self.cameraMode == cameraMode.FREE):
             self.spectate.draw(self.window, self.freeCamera)

        pygame.display.update()
    
    
    
    def stableFood(self):
        randR = random.randint(10, 20)
        randTexture = random.choice(self.textures)
        randXY = polarCoord()
        newFood = Food(randXY[0], randXY[1], randR, randTexture)
        return newFood
    
    
    def dropFood(self, snake):
        startX = snake.rect.x ##Line 141 to 168 is dropping food where snake was after death
        startY = snake.rect.y
        size = 3
        texture = snake.filePath
        agentFood = []
        for i in range(size):
             p = polarCoord1(int(snake.rect.w/2))
             centreX = snake.rect.x + snake.rect.w/2
             centreY = snake.rect.y + snake.rect.h/2
             offset_x = p[0]
             offset_y = p[1]
             newFood = Food(centreX+offset_x, centreY+offset_y, (snake.rect.w * 0.66)/size, texture)
             self.food.append(newFood)
             agentFood.append(newFood)
             self.grid.addToCell(newFood)
        
        #newFood = Food(startX, startY, size, texture)
        #self.food.append(newFood)
        for segment in snake.segments:
             for i in range(size):
                 chance = random.randint(1,100)
                 if(chance <= 30):
                     p = polarCoord1(int(segment.rect.w/2))
                     centreX = segment.rect.x + segment.rect.w/2
                     centreY = + segment.rect.y + segment.rect.h/2
                     offset_x = + p[0]
                     offset_y =  p[1]
                     newFood = Food(centreX+offset_x, centreY+offset_y, segment.rect.w/size, texture)
                     self.food.append(newFood)
                     agentFood.append(newFood)
                     self.grid.addToCell(newFood)
        return agentFood

def polarCoord():
    r = random.randint(-MapSize, MapSize)
    alpha = 2 * math.pi * random.random()
    randX = r * math.cos(alpha)
    randY = r * math.sin(alpha)
    return (randX, randY)

def polarCoord1(area):
    r = random.randint(-area, area)
    alpha = 2 * math.pi * random.random()
    randX = r * math.cos(alpha)
    randY = r * math.sin(alpha)
    return (randX, randY)