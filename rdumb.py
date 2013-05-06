# Really Dumb Agent

import sys
import math
import time

from bzrc import BZRC, Command

class Agent(object):
    """This agent is really dumb"""
    
    def __init__(self, bzrc, n):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = [] #?
        self.time_passed = 0
        self.tank = n
        
    def tick(self, time_diff):
        """ If enough time has passed, turn."""
        
        
        
if __name__ == '__main__':
    try: 
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)
        
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

