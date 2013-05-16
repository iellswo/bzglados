# searching agent

import sys
import math

from bzrc import BZRC, Command

class State(object):
    """A state keeps track of things used by the various searches."""
    pass

class Agent(object):
    
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.mytank = self.bzrc.get_mytanks()[0]
        start, grid = self.bzrc.get_occgrid(0)
        self.grid = []
        self.offset = int(self.constants['worldsize'])/2
        #print self.constants
        for i in range(int(self.constants['worldsize'])):
            row = []
            for j in range(int(self.constants['worldsize'])):
                row.append( [start[0] + i, start[1] + j, grid[i][j]] )
            self.grid.append(row)
        self.othertanks = self.bzrc.get_othertanks();
        for tank in self.othertanks:
            self.grid[int(tank.x)+self.offset][int(tank.y)+self.offset][2] = 1
            #print self.grid[int(tank.x)+self.offset][int(tank.y)+self.offset]
        self.goal = [flag for flag in self.bzrc.get_flags() if flag.color == 'green'][0]
        #print self.goal.color, self.goal.x, self.goal.y 
        
    def search(self, algorithm):
        if algorithm == 'depthfirst' or algorithm == 'dfs':
            pass
        elif algorithm == 'breadthfirst' or algorithm == 'bfs':
            pass
        elif algorithm == 'idastar':
            pass
        elif algorithm == 'uniformcost' or algorithm == 'ucs':
            pass
        elif algorithm == 'astar':
            pass
        else:
            raise Exception(algorithm)
    
    def depthFirstSearch(self):
        """Returns a list of tuples, being x, y coordinates on the grid
           being the path to the goal found via a depth first search"""
        
        
        
def main():
    # Process CLI arguments.
    try:
        execname, host, port, algorithm = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port algorithm' % execname
        sys.exit(-1)

    #connect
    bzrc = BZRC(host, int(port))
    
    agent = Agent(bzrc)
    
    try:
        agent.search(algorithm)
    except Exception as e:
        print 'Error: unrecognized algorithm: %s' % str(e)
        print 'valid options: dfs, bfs, idastar, ucs, astar'

if __name__ == '__main__':
    main()
