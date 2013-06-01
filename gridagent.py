# Grid Exploration Agent

import sys
import math
import time
import random
import curses

from numpy import zeros
from Queue import PriorityQueue
from collections import deque

from bzrc import BZRC, Command
from mapBuilder import MapBuilder

########################################################################
# constants change behaviour:

# We assume that this much percent of the map is occupied
AOR = .4

# If the percentage is higher than this we assume it's an occupied square
TH = .9

# If the percentage is lower than this we assume it's unoccupied
THL = .1

# The range of the search space for new target
RANGE = 200

# How many steps we look fowards when traversing our A* path
LOOKAHEAD = 2

########################################################################

class State(object):
    pass
    
class Failure(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class GridAgent(object):
    
    def __init__ (self, bzrc):
        # bzrc connections
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        
        # world details
        self.world_size = int(self.constants['worldsize'])
        self.offset = self.world_size/2
        self.grid = zeros((self.world_size, self.world_size))
        for i in range(self.world_size):
            for j in range(self.world_size):
                self.grid[i][j] = AOR
                
        # tank control elements
        tanks = self.bzrc.get_mytanks()
        t_n = len(tanks)
        self.targets = []
        for i in range(t_n):
            self.targets.append( None )
                
        self.explored = zeros((self.world_size, self.world_size))
        
        # map builder components
        self.builder = MapBuilder(self.world_size, self.world_size)
        
        # important bayesian components
        self.true_positive = float(self.constants['truepositive'])
        self.true_negative = float(self.constants['truenegative'])
        
    def tick(self):
        #print 'tick'
        self.commands = []
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        
        for tank in mytanks:
            self.update_grid(tank)
            self.move_tank(tank)
            
        results = self.bzrc.do_commands(self.commands)
        self.builder.draw_grid()
        

    # Main tank methods:
    
    def update_grid(self, tank):
        """Gets the occgrid from the server for the current tank
           It then updates the world grid using bayesian reasoning."""
        t_start, t_grid = self.bzrc.get_occgrid(tank.index)
        #print t_start
        g_x, g_y = self.to_grid_space(t_start)
        #print g_start
        for i in range(len(t_grid)):
            for j in range(len(t_grid[i])):
                observed = t_grid[i][j]
                x = g_x + i
                y = g_y + j
                
                # the current probability that this space is occupied
                p_state = self.grid[x][y]
                
                if p_state == 0 or p_state == 1:
                    continue
                
                # the probability that the sensor says it's occupied when it is occupied
                p_sensor = self.true_positive if observed == 1 else 1-self.true_negative
                
                
                # find p_observed, which is the probability that the sensor would observe
                # what it observed taking everything into consideration
                p_sensor_not = 1-self.true_positive if observed == 1 else self.true_negative
                p_observed = p_state*p_sensor + (1-p_state) * p_sensor_not
                
                p_new = p_sensor * p_state / p_observed
                
                if p_new >= TH:
                    self.grid[x][y] = 1
                elif p_new <= THL:
                    self.grid[x][y] = 0
                else:
                    self.grid[x][y] = p_new
                
                self.grid[x][y] = p_new
                
                if self.explored[g_x+i][g_y+j] == 0:
                    self.explored[g_x+i][g_y+j] = 1
                    
        self.builder.update_grid(self.grid)

    def move_tank(self, tank):
        
        if self.targets[tank.index] is not None and self.is_occupied(self.to_grid_space(self.targets[tank.index])):
            self.targets[tank.index] = None
        
        look_ahead = (int(tank.x + tank.vx), int(tank.y + tank.vy))
        if self.is_occupied(self.to_grid_space(look_ahead)):
            self.targets[tank.index] = None
        
        
        if self.targets[tank.index] is None:
            self.stop_all_tanks()
            print 'current location:', tank.x, tank.y
            t = raw_input('Enter a target location >- ')
            t = t.split(',')
            if len(t) != 2:
                print 'invalid'
                return
            t[0] = int(t[0].strip())
            t[1] = int(t[1].strip())
            t = (t[0], t[1])
            print 'target:', t
            self.targets[tank.index] = t
        self.move_to_position(tank, self.targets[tank.index])
        if self.is_at_target(tank):
            self.targets[tank.index] = None
        
    def stop_all_tanks(self):
        tanks = self.bzrc.get_mytanks()
        com = []
        for tank in tanks:
            command = Command(tank.index, 0, 0, False)
            com.append(command)
        self.bzrc.do_commands(com)
        
    def stop_tank(self, tank):
        command = Command(tank.index, 0, 0, False)
        self.commands.append(command)
        
    def is_at_target(self, tank):
        target = self.targets[tank.index]
        pos = (tank.x, tank.y)
        return self.distance(target, pos)**2 < 2
        
    def move_to_position(self, tank, target):
        """Set command to move to given coordinates."""
        target_x, target_y = target
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        relative_angle = relative_angle
        command = Command(tank.index, max(0, .4-abs(relative_angle)), relative_angle, False)
        self.commands.append(command)
        
    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle
    
    
    # Getting the path the tank is supposed to follow
    
    
    

    # Utility methods:
    def to_world_space(self, n):
        x, y = n
        return (x - self.offset, y - self.offset)
        
    def to_grid_space(self, n):
        x, y = n
        return (self.offset + x, self.offset + y)
        
    def distance(self, a , b):
        return math.sqrt((b[1]-a[1])**2+(b[0]-a[0])**2)
        
    def is_occupied( self, p ):
        return self.grid[p[0]][p[1]] >= TH
        
    def get_new_target(self, p):
        p_x, p_y = self.to_grid_space(p)
        #print max(0, p_x - RANGE), min(self.world_size - 1, p_x + RANGE)
        x = random.randint(max(0, p_x - RANGE), min(self.world_size - 1, p_x + RANGE))
        y = random.randint(max(0, p_y - RANGE), min(self.world_size - 1, p_y + RANGE))
        if self.explored[x][y]:
            return None
        elif self.is_occupied((x, y)):
            return None
        else:
            return (x, y)

def main():
    # Process CLI arguments.
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % execname
        sys.exit(-1)
        
    #connect
    bzrc = BZRC(host, int(port))
    
    agent = GridAgent(bzrc)
    
    # Run the agent
    #while True:
    #    agent.tick()
    try:
        while True:
            agent.tick()
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()
