from Food import Food
from Snake import Snake
from Segment import Segment
import math
class Grid:
    def __init__(self, cellsize, mapSize):
        self.cellsize = cellsize
        self.mapSize = mapSize
        self.grid = [[[] for _ in range(mapSize // cellsize)] for _ in range(mapSize // cellsize)]
    
    def cell_location(self, x, y):
        grid_x = int((x + self.mapSize // 2) // self.cellsize)
        grid_y = int((y + self.mapSize // 2) // self.cellsize)
        return min(grid_x, 9), min(grid_y, 9)
    
    def addToCell(self, obj):
        x,y = self.cell_location(obj.rect.x, obj.rect.y)
        #print(f'gridX: {y}, gridY: {x}')
        self.grid[y][x].append(obj)

    def deleteFromCell(self, obj):
        x,y = self.cell_location(obj.rect.x, obj.rect.y)
        #print(f'Deleting obj: {obj}   | X: {y}, Y: {x}')
        #print(self.grid)
        #print(f'Cell: {self.grid[y][x]}')
        self.grid[y][x].remove(obj)

    def moveCell(self, obj):
        currentX, currentY = self.cell_location(obj.rect.x, obj.rect.y)
        #if obj == self.grid[y][x]
    
    def getCellPopulation(self, obj):
        x,y = self.cell_location(obj.rect.x, obj.rect.y)
        population = self.grid[y][x].copy()
        if obj in population: ### If the snake is in the cell remove it 
            population.remove(obj)
        for seg in obj.segments: ### If any of the segments are in the population remove them
            if seg in population:
                population.remove(seg)
        return population
    
    def getNearByCellPopulation(self, obj):
        x,y = self.cell_location(obj.rect.x, obj.rect.y)
        min = 0
        max = (self.mapSize // self.cellsize)-1
        my_cell_population = self.grid[y][x].copy()
        if obj in my_cell_population:
            my_cell_population.remove(obj)            
        middle = my_cell_population
        #print(self.grid)
        #print(f'X: {y}, Y: {x}')
        if(y != min):
            top = self.grid[y-1][x].copy()
        if y != max:
            bottom = self.grid[y+1][x].copy()
        if x != min:
            left = self.grid[y][x-1].copy()
        if x != max:
            right = self.grid[y][x+1].copy()
        if y != min and x != max:
            top_right = self.grid[y-1][x+1].copy()
        if y != min and x != min:
            top_left = self.grid[y-1][x-1].copy()
        if y != max and x != max:
            bottom_right = self.grid[y+1][x+1].copy()
        if y != max and x != min:
            bottom_left = self.grid[y+1][x-1].copy()
        population = middle

        #print(f'Middle: {middle}  |  Top: {top}  |  Bottom: {bottom}  | Left: {left}  |  Right: {right}  | Top-Right: {top_right}  | Top_Left: {top_left}  |  Bottom_Right: {bottom_right}  |  Bottom_Left: {bottom_left}')
        if(y == min and x == min):
            population += right + bottom_right + bottom
        if(y == max and x == max):
            population += left + top_left + top
        if(y == max and x == min):
            population += top + top_right + right
        if(y == min and x == max):
            population += bottom + bottom_left + left
        if(y == min and x != min):
            population += right + bottom_right + bottom + bottom_left + left
        if(x == min and y != min):
            population += top + top_right + right + bottom_right + bottom
        if(y == max and x != max):
            population += left + top_left + top + top_right + right
        if(x == max and y != max):
            population += bottom + bottom_left + left + top_left + top
        if(y != min and y != max and x != min and x != max):
            population += top + top_right + right + bottom_right + bottom + bottom_left + left + top_left
        nearbySnake = []
        nearbyFood = []
        nearbySegment = []
        max_w = 100
        for seg in obj.segments:
            if seg in population:
                population.remove(seg)
        for pop in population:
            direction = [pop.rect.x - obj.rect.x, pop.rect.y-obj.rect.y]
            dist = (direction[0]**2 + direction[1]**2) ** (1/2)
            if dist == 0:
                continue
            #direction[0] /= dist 
            #direction[1] /= dist 
            size = pop.rect.w
            if(type(pop) is Food): 
                nearbyFood.append([direction[0]/dist, direction[1]/dist, dist/self.mapSize, size/max_w, pop.rect.x/self.mapSize, pop.rect.y/self.mapSize])
            if(type(pop) is Snake):
                nearbySnake.append([direction[0]/dist, direction[1]/dist, dist/self.mapSize, size/max_w, pop.rect.x/self.mapSize, pop.rect.y/self.mapSize, pop.direction[0], pop.direction[1]])
                for seg in pop.segments:
                    sizeSeg = seg.rect.w
                    directionSeg = [seg.rect.x - obj.rect.x, seg.rect.y - obj.rect.y]
                    distSeg = (directionSeg[0]**2 + directionSeg[1]**2) ** (1/2)
                    #directionSeg[0] /= distSeg 
                    #directionSeg[1] /= distSeg
                    nearbySegment.append([directionSeg[0]/distSeg, directionSeg[1]/distSeg, distSeg/self.mapSize, sizeSeg/max_w, seg.rect.x/self.mapSize, seg.rect.y/self.mapSize, seg.direction[0], seg.direction[1]])
        
        return nearbyFood, nearbySnake, nearbySegment
    
    def searchForClosestNeighbour(self, obj):
        x,y = self.cell_location(obj.rect.x, obj.rect.y)
        population = self.getCellPopulation(obj)
        nearestDist = math.inf
        nearestFood = None
        for food in population:
            if(type(food) is Food):
                direction = [food.rect.x - obj.rect.x, food.rect.y-obj.rect.y]
                dist = (direction[0]**2 + direction[1]**2) ** (1/2)
                if dist < nearestDist:
                    nearestDist = dist
                    nearestFood = food
        return nearestFood




