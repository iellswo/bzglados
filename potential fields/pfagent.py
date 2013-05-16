#potential fields agent.  

import sys
import math
import time

from pfgen import PFGEN
from bzrc import BZRC, Command

class Agent(object):
    
    def __init__(self, bzrc):
        """Initialize the Agent"""
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        
        self.flags = self.bzrc.get_flags()
        target_flag = (0,0)
        self.target_color = self.constants['team']
        for flag in self.flags:
            if flag.color != self.constants['team']:
                target_flag = (flag.x, flag.y)
                self.target_color = flag.color
        # these change the initialization
        spread = 10
        obstacle_scale = .6
        self.flag_scale = .75
        
        self.pfg = PFGEN(self.constants['worldsize'], spread, self.bzrc.get_obstacles(), 
                         obstacle_scale, target_flag, self.constants['flagradius'], self.flag_scale)
                         
        self.capture_state = False
        
    def tick(self):
        """Some time has passed.  Do something."""
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.mytanks = mytanks
        self.othertanks = othertanks
        old_flags = self.flags
        self.flags = flags
        self.shots = shots
        
        
        #if self.flags_moved(old_flags):
        #    flag = [flag for flag in self.flags if flag.color == self.target_color][0]
        #    self.pfg.update((flag.x, flag.y), self.constants['flagradius'], self.flag_scale)

        self.commands = []
        if self.capture_state == True:
            my_base = [base for base in self.bzrc.get_bases() if base.color == self.constants['team']][0]
            base_center_x = float(my_base.corner1_x + my_base.corner3_x)/2
            base_center_y = float(my_base.corner1_y + my_base.corner3_y)/2
            self.pfg.update((base_center_x, base_center_y), 50, self.flag_scale)
        else:
            target_flag = [flag for flag in self.flags if flag.color == self.target_color][0]
            #print target_flag.color
            #print "flag", target_flag.x, target_flag.y
            self.pfg.update((float(target_flag.x), float(target_flag.y)), self.constants['flagradius'], self.flag_scale)
            
        self.capture_state = False
        
        for tank in mytanks:
            if tank.flag != '-':
                self.capture_state = True
            self.move_tank(tank)
        
        results = self.bzrc.do_commands(self.commands)
        
    def move_tank(self, tank):
        target_vector = self.pfg.generate_fields(tank.x, tank.y)
        #print "tank", tank.x, tank.y
        #print "target", target_vector[0], target_vector[1]
        self.move_to_position(tank, target_vector[0], target_vector[1])
        
    def move_to_position(self, tank, target_x, target_y):
        """Set command to move to given coordinates."""
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        command = Command(tank.index, 1, relative_angle, True)
        self.commands.append(command)
        
        
    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle
        
        
def main():
    # Process CLI arguments.
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        #print >>sys.stderr, '%s: incorrect number of arguments' % execname
        #print >>sys.stderr, 'usage: %s hostname port' % execname
        sys.exit(-1)

    #connect
    bzrc = BZRC(host, int(port))
    
    agent = Agent(bzrc)
    
    # Run the agent
    try:
        while True:
            agent.tick()
    except KeyboardInterrupt:
        #print "Exiting due to keyboard interrupt."
        bzrc.close()
        
if __name__ == '__main__':
    main()
    
