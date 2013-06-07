import sys
import math
import random

from bzrc import BZRC, Command

class States:
    Ahead, Turn, Backup, Circle = range(4)
    
times = {1.0, .3, 2.0, 2.3}

class Agent(object):
    
    def __init__(self, bzrc):
        # bzrc connections
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        
        self.step = 0
        self.state = States.Ahead
        
    def tick(self, time_diff):
        self.step += time_diff
        
    
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
