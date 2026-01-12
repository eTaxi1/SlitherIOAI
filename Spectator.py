import pygame

class Spectator:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x,self.y,0,0)
        image= pygame.image.load('textures/part.png')
        self.texture = pygame.transform.scale(image, (0, 0))

    def update(self):
        keys = pygame.key.get_pressed()
            
        if(keys[pygame.K_a]):
            self.x -= 100
        if(keys[pygame.K_d]):
            self.x += 100
        if(keys[pygame.K_w]):
            self.y -= 100
        if(keys[pygame.K_s]):
            self.y += 100

    def draw(self, window, camera):
        pos = camera.translate(self.x, self.y)
        window.blit(self.texture, (pos[0], pos[1]))