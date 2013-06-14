import sys
import math
import random

from bzrc import BZRC, Command

class Agent(object):
    
    def __init__(self, bzrc, target):
        # bzrc connections
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        
        self.target = target
        
    def tick(self):
        #print 'tick'
        self.commands = []
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        
        for tank in mytanks:
            self.move_tank(tank)
            
        results = self.bzrc.do_commands(self.commands)
        
    def move_tank(self, tank):
        if self.distance((tank.x, tank.y), self.target) < 20:
            self.spin_randomly(tank)
        else:
            x, y = self.target
            #print 'tank at', tank.x, tank.y, 'target:', x, y
            self.move_to_position(tank, x, y)
            
    def spin_randomly(self, tank):
        cur_speed = tank.angvel
        new_speed = tank.angvel + random.uniform(-.7, .7)
        command = Command(tank.index, 0, new_speed, False)
        self.commands.append(command)
            
    def move_to_position(self, tank, target_x, target_y):
        """Set command to move to given coordinates."""
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        command = Command(tank.index, max(-.05, .7-abs(relative_angle)), relative_angle, False)
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
        execname, host, port, x, y = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    target = (int(x), int(y))
    # Connect.
    #bzrc = BZRC(host, int(port), debug=True)
    bzrc = BZRC(host, int(port))

    agent = Agent(bzrc, target)



    # Run the agent
    try:
        while True:
            agent.tick()
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()
