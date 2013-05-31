# Grid Exploration Agent

import sys
import math
import time

from numpy import zeros

from bzrc import BZRC, Command
#from mapBuilder import MapBuilder

# constants change behaviour:

# We assume that this much percent of the map is occupied
AOR = 0

class GridAgent(object):
    
    def __init__ (self, bzrc):
        # bzrc connections
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        
        # world details
        self.world_size = int(self.constants['worldsize'])
        self.offset = self.world_size/2
        self.grid = []
        for i in range(self.world_size):
            row = []
            for j in range(self.world_size):
                row.append(AOR)
        tanks = self.bzrc.get_mytanks()
        t_n = len(tanks)
        self.targets = []
        for i in t_n:
            self.targets.append( None )
                
        self.explored = zeros((self.world_size, self.world_size))
        
        # map builder components
        # self.builder = MapBuilder(self.world_size, self.world_size)
        
    def tick(self):
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        
        for tank in mytanks:
            update_grid(tank)
            #move_tank(tank)
            
        results = self.bzrc.do_commands(self.commands)

    # Main tank methods:
    
    def update_grid(self, tank):
        t_start, t_grid = self.bzrc.get_occgrid(tank.index)
        g_start = self.to_grid_space(t_start)
        for i in len(t_grid):
            for j in len(t_grid[i]):
                # Bayesian stuff happens here
                self.grid[g_start+i][g_start+j] = t_grid[i][j]

    # Utility methods:
    
    def to_world_space(self, n):
        x, y = n
        return (self.offset + x, self.offset + y)
    def to_world_space(self, x, y):
        return self.to_world_space((x, y))
        
    def to_grid_space(self, n):
        x, y = n
        return (x - self.offset, y - self.offset)
    def to_grid_space(self, x, y):
        return self.to_grid_space((x, y))


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
    
    agent = GridAgent(bzrc)
    
    # Run the agent
    try:
        while True:
            agent.tick()
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()
