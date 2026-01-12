import pygame


class Object:
    def __init__(self, x, y, w, h, filePath):
        self.rect = pygame.Rect(x,y,w,h)
        image= pygame.image.load(filePath)
        self.texture = pygame.transform.scale(image, (w, h))
        self.w = w
        self.h = h

    def draw(self, window, camera):
        pos = camera.translate(self.rect.x, self.rect.y)
        zoom = camera.zoom
        scaledTexture = pygame.transform.scale(self.texture, (int(self.rect.width * zoom), int(self.rect.height*zoom)))
        window.blit(scaledTexture, (pos[0], pos[1]))