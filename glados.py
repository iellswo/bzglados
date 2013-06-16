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
    Runner, Captor, Hunter, Shadow, Dead = range(5)
    
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
        
        self.mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.enemies = [tank for tank in othertanks if tank.color != self.team]
        self.states = []
        self.flag = find(lambda flag: flag.color != self.team, flags)
        
        self.base = find(lambda base: base.color == self.team, self.bzrc.get_bases())

        self.painter=DrawUtil(self.world_size) #painter

        for tank in mytanks:
            self.states.append(State.Runner)
        self.states[-1] = State.Hunter
        
        self.filters = []
        for tank in self.enemies:
            self.filters.append(Filter(NOISE))
            
        self.compass = Generator(self.world_size, SPREAD, SCALE)
        

    # every tick:
    def tick(self, time_diff):
        self.mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.enemies = [tank for tank in othertanks if tank.color !=
                        self.constants['team']]
        self.flag = find(lambda flag: flag.color != self.team, flags)

        for enemigo in self.enemies:
            color = enemigo.callsign[:-1]
            ilen = len(enemigo.callsign) - len(enemigo.color)
            index = int(enemigo.callsign[-ilen:])
            enemigo.index = index
            #print index
            if enemigo.status != 'alive':
                continue
                
            self.painter.add_observed((enemigo.x,enemigo.y)) # painter
            
            self.filters[index].update((enemigo.x, enemigo.y), time_diff)
            # painter
            if index == 0:
                x, y = self.filters[0].get_enemy_position()
                
                self.painter.change_enemy_position((x, y)) # /painter
            
        self.painter.update_display() # painter
            
        for tank, state in zip(self.mytanks, self.states):
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
        index = tank.index
        if state == State.Runner:
            goal = (self.flag.x, self.flag.y)
            mode = FireMode.Safety
        
        elif state == State.Hunter:
            best_enemy = None
            best_dist = 2.0 * self.world_size
            for enemy in self.enemies:
                if enemy.status != 'alive':
                    continue
                dist = self.distance((tank.x, tank.y), (enemy.x, enemy.y))
                if dist < best_dist:
                    best_dist = dist
                    best_enemy = enemy
            if best_enemy is None:
                self.states[index] = State.Runner
                command = Command(index, 0, 0, False)
                self.commands.append(command)
                return
            goal = self.filters[best_enemy.index].get_enemy_position()
            #print goal
            mode = FireMode.Auto
        
        elif state == State.Captor:
            base_center_x = float(self.base.corner1_x + self.base.corner3_x)/2
            base_center_y = float(self.base.corner1_y + self.base.corner3_y)/2
            goal = (base_center_x, base_center_y)
            mode = FireMode.Semi
            
        elif state == State.Shadow:
            best_ally = None
            best_dist = 2.0 * self.world_size
            for ally in self.mytanks:
                if ally.status != 'alive':
                    continue
                dist = self.distance((tank.x, tank.y), (ally.x, ally.y))
                if dist < best_dist:
                    best_dist = dist
                    best_ally = ally
            if best_ally is None:
                self.states[index] = State.Runner
                command = Command(index, 0, 0, False)
                self.commands.append(command)
                return
            goal = (ally.x, ally.y)
            mode = FireMode.Semi
        
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
