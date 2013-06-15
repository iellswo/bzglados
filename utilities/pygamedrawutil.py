import pygame
import time

BGCOLOR = (0, 0, 0)
MECOLOR = (255, 0, 0)
ENCOLOR = (0, 255, 0)
TACOLOR = (0, 0, 255)
OLCOLOR = (0, 255, 255)

# how long do we leave the trail?
MTL = 10

class DrawUtil:
    
    def __init__(self, worldsize):
        pygame.init()
        self.screen = pygame.display.set_mode((worldsize, worldsize))
        self.screen.fill(BGCOLOR)
        pygame.display.set_caption('Kalman Filter Agent')
        self.screensize = worldsize
        self.enemy = self.point_display((0, 0))
        self.target = self.point_display((0, 0))
        self.trail = []

    # convert a point, (x, y) tuple, to a PyGame coordinate
    def point_display(self, p):
        x, y = p
        return (int(self.screensize/2 + x), int(self.screensize/2 - y))

    def change_tank_pos(self, tank_pos):
        self.me = self.point_display(tank_pos)
        
    def change_enemy_position(self, tank_pos):
        self.enemy = self.point_display(tank_pos)
        
    def change_target(self, tank_pos):
        self.target = self.point_display(tank_pos)
        
    def add_observed(self, tank_pos):
        self.trail.append(self.point_display(tank_pos))
        if len(self.trail) >= MTL:
            self.trail = self.trail[1:]
            
    def update_display(self):
        self.screen.fill(BGCOLOR)
        #pygame.draw.circle(self.screen, MECOLOR, self.me, 4)
        pygame.draw.circle(self.screen, ENCOLOR, self.enemy, 4)
        #pygame.draw.circle(self.screen, TACOLOR, self.target, 4)
        
        for p in self.trail:
            pygame.draw.circle(self.screen, OLCOLOR, p, 1)
            
        pygame.display.update()
