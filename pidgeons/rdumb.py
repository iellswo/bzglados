# Really Dumb Agent

import sys
import math
import time
import random

from bzrc import BZRC, Command

class Agent(object):
    """This agent is really dumb"""
    
    def __init__(self, bzrc, n):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.time_passed = 0
        self.reload_passed = 0
        self.tank = n
        self.wait = random.uniform(3, 8)
        self.reload_wait = random.uniform(1.5, 2.5)
        self.state = 'stopped'
        self.target_angle = 0
        
        
    def tick(self, time_diff):
        """ If enough time has passed, turn."""
        self.reload_passed += time_diff
        if self.reload_passed >= self.reload_wait:
            self.bzrc.shoot(self.tank)
            self.reload_wait = random.uniform(1.5, 2.5)
        self.control_tank(time_diff)
        self.bzrc.do_commands(self.commands)
        
    def control_tank(self, time_diff):
        if self.state == 'stopped':
            self.state = 'moving'
            self.time_passed = 0
            self.move_tank(self.tank, 0)
        elif self.state == 'moving':
            self.move_tank(self.tank, time_diff)
        elif self.state == 'turning':
            self.turn_tank(self.tank)
        
    def move_tank(self, tank, time_diff):
        self.time_passed += time_diff
        if self.time_passed >= self.wait:
            self.commands.append(Command(self.tank, 0, 0, False))
            self.state = 'turning'
            tanks = self.bzrc.get_mytanks()
            current_angle = tanks[self.tank].angle
            self.target_angle = self.normalize_angle(current_angle + (math.pi/3.0))
            self.wait = random.uniform(3, 8)
        else:
            self.commands.append(Command(self.tank, 1, 0, False))
            
    def turn_tank(self, tank):
        tanks = self.bzrc.get_mytanks()
        current_angle = tanks[self.tank].angle
        relative_angle = self.normalize_angle(self.target_angle - current_angle)
        #print "turning", relative_angle
        command = Command(self.tank, 0, relative_angle, False)
        self.commands.append(command)
        if relative_angle ** 2 <= 0.005:
            self.commands.append(Command(self.tank, 0, 0, False))
            self.state = 'stopped'
            
    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle
        
if __name__ == '__main__':
    try: 
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)
        
    bzrc = BZRC(host, int(port))
    
    agents = []
    for i in range(10):
        agents.append(Agent(bzrc, i))
        
    
    prev_time = time.time()
    
    # Run the agent
    try:
        while True:
            time_diff = time.time() - prev_time
            prev_time = time.time()
            for agent in agents:
                agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()

