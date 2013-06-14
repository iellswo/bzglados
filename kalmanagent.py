# Kalman filter agent

import sys
import math
import time
#import random

from bzrc import BZRC, Command
from utilities.kalman import KalmanFilter as Filter
from utilities.pygameDrawUtil import DrawUtil

###########################################################
#  constants

# How long do we wait between kalman filter calculations?
WAIT = .2

# What is the posnoise?
NOISE = 3

# We adjust this to make change:
FUDGE = 5.35

###########################################################

class Agent(object):
    
    def __init__ (self, bzrc):
        # bzrc connections
        self.bzrc = bzrc
       
        self.constants = self.bzrc.get_constants()
        #print self.constants
        self.commands = []
        
        # world details
        self.world_size = int(self.constants['worldsize'])
        self.shot_speed = float(self.constants['shotspeed'])
        
        self.target = (0,0, False)
        self.delta = 0.0
        self.painter=DrawUtil(self.world_size)
        self.kfilter = Filter(NOISE)

    def tick(self, time_diff):
        
        #print time_diff
        self.delta += time_diff
        
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        target = othertanks[0]
        me = mytanks[0]
        #self.kfilter.update((target.x, target.y), time_diff)
        if self.delta >= WAIT:
            
            #print 'update', random.uniform(-.5, .5)
            self.get_new_target(target, me)
            self.painter.update_display()
            self.delta = 0.0
            
        for tank in mytanks:
            self.painter.change_tank_pos((tank.x, tank.y))
            self.tank_controller(tank)
            
        results = self.bzrc.do_commands(self.commands)
        
        
    def get_new_target(self, tank, me):
        # Insert kalman filter here
        if tank.status=='alive':
            #print 'alive'
            self.painter.add_observed((tank.x,tank.y))
            self.kfilter.update((tank.x, tank.y), self.delta)
            x, y = self.kfilter.get_enemy_position()
            self.painter.change_enemy_position((x, y))
            d_t = FUDGE * self.shot_speed / self.distance((me.x, me.y), (x, y))
            #print d_t
            x, y = self.kfilter.get_target(d_t)
            self.painter.change_target((x, y))
            self.target = (x, y, True)
        else:
            #self.painter.add_nofollow_tank(x,y)
            x, y, t = self.target
            self.kfilter.reset()
            #print 'dead'
            self.target = (x, y, False)
        
    def tank_controller(self, tank):
        target_x, target_y, alive = self.target
        distance = self.distance(self.target, (tank.x, tank.y))
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        if abs(relative_angle) <= .005 and alive:
            self.bzrc.shoot(tank.index)
        command = Command(tank.index, 0, relative_angle*(distance/50), False)
        self.commands.append(command)
        
    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle
        
    def distance(self, a , b):
        return math.sqrt((b[1]-a[1])**2+(b[0]-a[0])**2)


def main():
    # Process CLI arguments.
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    #bzrc = BZRC(host, int(port), debug=True)
    bzrc = BZRC(host, int(port))

    agent = Agent(bzrc)

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
