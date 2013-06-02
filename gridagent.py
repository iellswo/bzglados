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
TH = .99999

# If the percentage is lower than this we assume it's unoccupied
THL = .1

# If the percentage is higher tanks will avoid
THT = .999

# The range of the search space for new target
RANGE = 450

# At what ratio (of the current speed) do we look ahead for obstacles
LOOKAHEAD = 2.5

# How much berth do we give obstacles?
RAD = 90

# How many times to we try to find an unoccupied square? (affects speed)
TRYAGAIN = 30

# How close until we say we have reached our target (distance squared)
TARGETRADIUS = 150

# How many times to we try and go around an obstacle before we back up
# and set a new target
BACKUP = 6

# For how many ticks to we back up?
BUTICKS = 2

# Wiggle Variance: how wide is our wiggle?
WV = .02

# How far apart do tanks have to be before we tell them to back up and try 
# somewhere else (distance squared)
TANKRADIUS = 10

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
        self.targets = [(-self.offset+20, -self.offset+20), (20, -self.offset+20), (self.offset-20, 20),
                        (20, self.offset-20), (-self.offset+20, self.offset-20)]
        self.temptargets = []
        self.attempts = []
        self.ticks = []
        for i in range(t_n):
            self.attempts.append(0)
            self.ticks.append(0)
            self.temptargets.append( None )
            self.targets.append((0, 0))
            print 'tank', i, 'begins with target', self.targets[i]
        
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
                
                # the probability that the sensor says it's occupied when it is occupied
                p_sensor = self.true_positive if observed == 1 else 1-self.true_negative
                
                # find p_observed, which is the probability that the sensor would observe
                # what it observed taking everything into consideration
                p_sensor_not = 1-self.true_positive if observed == 1 else self.true_negative
                p_observed = p_state*p_sensor + (1-p_state)*p_sensor_not
                
                p_new = p_sensor * p_state / p_observed
                
                self.grid[x][y] = p_new
                    
        self.builder.update_grid(self.grid)


    def move_tank(self, tank):
        
        if self.tank_collision(tank.index):
            self.backup(tank)
            return
        
        if self.targets[tank.index] is not None and self.is_occupied(self.to_grid_space(self.targets[tank.index])):
            self.targets[tank.index] = None
            
        if self.targets[tank.index] is None:
            t = self.get_new_target((tank.x, tank.y))
            print 'target for tank', tank.index, 'is now', t
            self.targets[tank.index] = t
        
        look_ahead = (int(tank.x + (LOOKAHEAD*tank.vx)), int(tank.y + (LOOKAHEAD*tank.vy)))
        if self.is_occupied(self.to_grid_space(look_ahead)) or self.attempts[tank.index] >= BACKUP:
            if self.attempts[tank.index] < BACKUP:
                o_x, o_y = self.get_orientation(int(tank.vx), int(tank.vy))
                d_x, d_y = self.get_dominant_direction(int(tank.vx), int(tank.vy))
                t = self.contain((tank.x + (RAD * o_y * d_y), tank.y + (RAD * o_x * d_x)))
                print 'tank', tank.index, 'is blocked, setting temporary target', t
                self.temptargets[tank.index] = t
                self.attempts[tank.index] += 1
            else:
                print 'tank', tank.index, 'is backing up...'
                self.backup(tank)
                self.ticks[tank.index] += 1
                if self.ticks[tank.index] > BUTICKS:
                    self.ticks[tank.index] = 0
                    self.attempts[tank.index] = 0
                    o_x, o_y = self.get_orientation(-int(tank.vx), -int(tank.vy))
                    d_x, d_y = self.get_dominant_direction(-int(tank.vx), -int(tank.vy))
                    self.temptargets[tank.index] = (tank.x + (2 * RAD * o_y * d_y), tank.y + (2 * RAD * o_x * d_x))
                return
        
        if self.temptargets[tank.index] is None:
            self.move_to_position(tank, self.targets[tank.index])
        else:
            self.move_to_position(tank, self.temptargets[tank.index])
        if self.is_at_target(tank):
            self.ticks[tank.index] = 0
            self.attempts[tank.index] = 0
            if self.temptargets[tank.index] is None:
                self.targets[tank.index] = None
            else:
                self.temptargets[tank.index] = None
        
    def backup(self, tank):
        command = Command(tank.index, -1, 0, False)
        self.commands.append(command)

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
        target = (0, 0)
        if self.temptargets[tank.index] is None:
            target = self.targets[tank.index]
        else:
            target = self.temptargets[tank.index]
        pos = (tank.x, tank.y)
        return self.distance(target, pos)**2 < TARGETRADIUS
        
    def move_to_position(self, tank, target):
        """Set command to move to given coordinates."""
        target_x, target_y = target
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        relative_angle = relative_angle
        wiggle = random.uniform(-WV, WV)
        command = Command(tank.index, max(0, .4-abs(relative_angle)), relative_angle+wiggle, False)
        self.commands.append(command)
        
    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle
    
    def tank_collision(self, index):
        tanks = self.bzrc.get_mytanks()
        cur_tank = [tank for tank in tanks if tank.index == index][0]
        for tank in tanks:
            if tank.index == index:
                continue
            if self.distance((cur_tank.x, cur_tank.y), (tank.x, tank.y))** 2 < TANKRADIUS:
                return True
    
    
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
        if self.is_outside_bounds(p):
            return True
        else:
            return self.grid[p[0]][p[1]] >= THT

    def is_outside_bounds(self, node ):
        return (node[0] < 0 or node[1] < 0 or
                node[0] > int(self.constants['worldsize']) - 1 or
                node[1] > int(self.constants['worldsize']) - 1)
        
    def get_new_target(self, p):
        p_x, p_y = self.to_grid_space(p)
        #print max(0, p_x - RANGE), min(self.world_size - 1, p_x + RANGE)
        x = random.randint(max(0, p_x - RANGE), min(self.world_size - 1, p_x + RANGE))
        y = random.randint(max(0, p_y - RANGE), min(self.world_size - 1, p_y + RANGE))
        
        for i in range(TRYAGAIN):
            if self.is_decided((x, y)):
                x = random.randint(max(0, p_x - RANGE), min(self.world_size - 1, p_x + RANGE))
                y = random.randint(max(0, p_y - RANGE), min(self.world_size - 1, p_y + RANGE))
            else:
                break

        return self.to_world_space((x, y))
            
    def is_decided(self, p):
        # assumes p is in grid space
        x, y = p
        g = self.grid[x][y]
        return g < THL or g > TH
        
    def get_orientation(self, vx, vy):
        dirx = 0
        diry = 0
        if vx != 0:
            dirx = vx/abs(vx)
        if vy != 0:
            diry = vy/abs(vy)
        return (dirx, diry)
        
    def get_dominant_direction(self, vx, vy):
        if abs(vx) > abs(vy):
            return (1, 0)
        elif abs(vy) > abs(vx):
            return (0, 1)
        else:
            return (1, 1)
            
    def contain(self, p):
        x, y = p
        x = max(x, -self.offset+1)
        x = min(x, self.offset-1)
        y = max(y, -self.offset+1)
        y = min(y, self.offset-1)
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
