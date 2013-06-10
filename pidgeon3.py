import sys
import math
import random
import time

from bzrc import BZRC, Command

def ahead(tank):
    print 'ahead'
    command = Command(tank.index, .8, 0, False)
    return command
    
def backup(tank):
    print 'backup'
    command = Command(tank.index, -.8, 0, False)
    return command
    
def sharp_turn(tank):
    print 'sharp turn'
    command = Command(tank.index, .9, random.choice([-1, 1]), False)
    return command
    
def wide_turn(tank):
    print 'wide turn'
    an = tank.angvel if tank.angvel**2 > .05 else random.choice([-.5, .5])
    command = Command(tank.index, .7, an, False)
    return command
    
def stop(tank):
    return Command(tank.index, 0, 0, True)
    
STATES = [ahead, backup, sharp_turn, wide_turn]
    
times = [2.0, 2.7, 2.5, 2.3]

class Agent(object):
    
    def __init__(self, bzrc):
        # bzrc connections
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        
        self.step = 0
        self.state = 0
        
    def tick(self, time_diff):
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.step += time_diff
        if self.step > times[self.state]:
            #self.commands.append(stop(mytanks[0]))
            self.step = 0.0
            self.state = random.randint(0, 3)
            for tank in mytanks:
                self.commands.append(STATES[self.state](tank))
                self.bzrc.do_commands(self.commands)
        
        
            
        
        
    
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
