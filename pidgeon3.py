import sys
import math
import time
import random

from bzrc import BZRC, Command


class Agent(object):
    """Class handles all command and control logic for a teams tanks."""

    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        mytanks=bzrc.get_mytanks()
        self.target_by_tank_num=[]
        for tank in mytanks:
            self.target_by_tank_num.append((int(self.constants['worldsize'])/2)-50)
       

    def tick(self, time_diff):
        """Some time has passed; decide what to do next."""
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.mytanks = mytanks
        self.othertanks = othertanks
        self.flags = flags
        self.shots = shots
        self.enemies = [tank for tank in othertanks if tank.color !=
                        self.constants['team']]

        self.commands = []

        for tank in mytanks:
            if tank.y-(self.target_by_tank_num[tank.index])==0:
                self.target_by_tank_num[tank.index]=-1*self.target_by_tank_num[tank.index]
                #print "switching target"
                
            self.move_to_position(tank,(0,self.target_by_tank_num[tank.index]))

        results = self.bzrc.do_commands(self.commands)

    

    def move_to_position(self, tank, target):
        """Set command to move to given coordinates."""
        target_x, target_y = target
        target_angle = math.atan2(target_y - tank.y,
                                  target_x - tank.x)
        relative_angle = self.normalize_angle(target_angle - tank.angle)
        wiggle = random.uniform(-.1, .1)
        command = Command(tank.index, max(-.03, random.uniform(.3, 1)-abs(relative_angle)), relative_angle+wiggle, False)
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
            time_diff = time.time() - prev_time
            agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()
