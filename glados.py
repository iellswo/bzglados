# GLaDOS: Genetic Lifeform and Disk Operating System:
# (aka our final agent for bzrflag game)

# Ike Ellsworth and Josh Lepinski

import sys
import math
import time
import threading
import Queue
import copy

from random import randint
from numpy import zeros
from utilities.bzrc import BZRC, Command
from utilities.kalman import KalmanFilter as Filter
from utilities.localpfgen import PFGEN as Generator
from utilities.pygamedrawutil import DrawUtil # painter

###########################################################
#  constants

# what is the posnoise?
NOISE = 3

# What is the spread used by the potential fields?
SPREAD = 26

# What is the Obstacle Scale?
SCALE = 3

#
###########################################################

def find(f, seq):
    """Return first item in sequence where f(item) == True."""
    for item in seq:
        if f(item):
            return item

class State:
    Runner, Captor, Hunter, Guard, Shadow, Dead = range(6)
    
class FireMode:
    Safety, Semi, Auto = range(3)


class Controller(object):
    
    def __init__(self, bzrc):
        # bzrc connections
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        
        # game details
        self.world_size = int(self.constants['worldsize'])
        self.offset = self.world_size/2

        self.team = self.constants['team']
        
        self.shot_speed = float(self.constants['shotspeed'])
        
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.enemies = [tank for tank in othertanks if tank.color != self.team]
        self.states = []
        self.flag = find(lambda flag: flag.color != self.team, flags)
        
        self.base = find(lambda base: base.color == self.team, self.bzrc.get_bases())

        self.painter=DrawUtil(self.world_size) #painter

        for tank in mytanks:
            self.states.append(State.Runner)
        
        self.filters = []
        for tank in self.enemies:
            self.filters.append(Filter(NOISE))
            
        self.compass = Generator(self.world_size, SPREAD, SCALE)
        

    # every tick:
    def tick(self, time_diff):
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.enemies = [tank for tank in othertanks if tank.color !=
                        self.constants['team']]
        self.flag = find(lambda flag: flag.color != self.team, flags)

        for enemigo in self.enemies:
            color = enemigo.callsign[:-1]
            index = int(enemigo.callsign[-1])
            if enemigo.status != 'alive':
                continue
                
            self.painter.add_observed((enemigo.x,enemigo.y)) # painter
            
            self.filters[index].update((enemigo.x, enemigo.y), time_diff)
            # painter
            if index == 0:
                x, y = self.filters[0].get_enemy_position()
                
                self.painter.change_enemy_position((x, y)) # /painter
            
        self.painter.update_display() # painter
            
        for tank, state in zip(mytanks, self.states):
            if state == State.Dead:
                continue
            if tank.status != 'alive':
                self.states[tank.index] == State.Dead
                continue
            self.tank_control(tank, state)
        
        results = self.bzrc.do_commands(self.commands)


    # Main tank control methods:       
    def tank_control(self, tank, state):
        goal = None
        mode = None
        if state == State.Runner:
            goal = (self.flag.x, self.flag.y)
            mode = FireMode.Safety
        else:
            goal = (self.flag.x, self.flag.y)
            mode = FireMode.Safety
        g_x, g_y = goal
        try:
            start, grid = self.bzrc.get_occgrid(tank.index)
            m0veto = self.compass.use_grid(grid, tank.x, tank.y, g_x, g_y, 1)
            self.move_to_position(tank, m0veto)
        except Exception:
            print 'crisis averted'
            return
        # targeting code here.
        

                
    def move_to_position(self, tank, target):
        """Set command to move to given coordinates."""
        target_x, target_y = target
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        relative_angle = relative_angle
        command = Command(tank.index, max(-.05, .8-abs(relative_angle)), relative_angle, False)
        self.commands.append(command)
        
    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle
        
    # Utility methods:
    def to_world_space(self, n):
        x, y = n
        return (x - self.offset, y - self.offset)
        
    def to_grid_space(self, n):
        x, y = n
        return (int(self.offset + x), int(self.offset + y))
        
    def distance(self, a , b):
        return math.sqrt((b[1]-a[1])**2+(b[0]-a[0])**2)

    def is_occupied( self, p ):
        x, y = p
        if self.is_outside_bounds(p):
            return True
        else:
            return self.grid[x][y] >= 1

    def is_outside_bounds(self, node ):
        return (node[0] < 0 or node[1] < 0 or
                node[0] > self.worldsize - 1 or
                node[1] > self.worldsize - 1)
        
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
    
    agent = Controller(bzrc)
    
    prev_time = time.time()
  
    # Run the agent
    try:
        while True:
            
            now = time.time()
            time_diff = now - prev_time
            prev_time = now
            
            agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()
