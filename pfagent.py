#potential fields agent.  

import sys
import math
import time

from bzrc import BZRC, Command

class Agent(object):
    
    def __init__(self, bzrc):
        """Initialize the Agent"""
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        self.color = color
        
    def tick(self):
        """Some time has passed.  Do something."""
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        self.mytanks = mytanks
        self.othertanks = othertanks
        self.flags = flags
        self.shots = shots
        
        self.commands = []
        
        for tank in mytanks:
            """Once pfcalc is done we can finish this"""
            pass
        
        results = self.bzrc.do_commands(self.commands)
        
        
def main():
    # Process CLI arguments.
    try:
        execname, host, port, color = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port color' % execname
        sys.exit(-1)

    #connect
    bzrc = BZRC(host, int(port))
    
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
    
