
class Camera:
    def __init__(self, x, y, playerDims, windowDims):
        self.x = x
        self.y = y
        self.playerDims = playerDims
        self.windowDims = windowDims
        self.zoom = 1

    def update(self, playerX, playerY):
        self.x = playerX
        self.y = playerY
        

    def translate(self,x,y):
        return (x-self.x + self.windowDims[0]/2 - self.playerDims[0]/2, y-self.y + self.windowDims[1]/2 - self.playerDims[1]/2)
    