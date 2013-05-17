# searching agent

import sys
import math

from animation import ANIMATION as Animation

from collections import deque

from bzrc import BZRC, Command
    
class State(object):
    pass

class Problem(object):
    pass

class Agent(object):
    
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.mytank = self.bzrc.get_mytanks()[0]
        #print self.mytank.x, self.mytank.y
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
        self.ani = Animation(int(self.constants['worldsize']), self.bzrc.get_obstacles())
        
    def search(self, algorithm):
        if algorithm == 'depthfirst' or algorithm == 'dfs':
            return self.depthFirstSearch()
        elif algorithm == 'breadthfirst' or algorithm == 'bfs':
            problem = Problem()
            problem.starting = (int(self.mytank.x + self.offset), int(self.mytank.y + self.offset))
            problem.goal = (int(self.goal.x + self.offset), int(self.goal.y + self.offset))
            #problem.goal = (int(self.mytank.x + self.offset + 10), int(self.mytank.y + self.offset))
            self.breadthFirstSearch(problem)
        elif algorithm == 'idastar':
            pass
        elif algorithm == 'uniformcost' or algorithm == 'ucs':
            pass
        elif algorithm == 'astar':
            pass
        else:
            raise Exception('Unknown algorithm %d' % algorithm)
    
    def depthFirstSearch(self):
        """Returns a list of tuples, being x, y coordinates on the grid
           being the path to the goal found via a depth first search"""
     
    def breadthFirstSearch(self, problem):
        """Returns a list of tuples, being x, y coordinates on the grid
           being the path to the goal found via a depth first search"""
        frontier=deque([])
        if problem.starting == problem.goal:
            return [problem.starting]
        node = State()
        node.coord = problem.starting
        node.parent = None
        frontier.append( node )
        explored=[]
        while True:
            if len(frontier) == 0:
                raise Exception('failure')
            node = frontier.popleft()
            explored.append(node)
            for n in self.get_neighbors(node.coord):
                fc = [f.coord for f in frontier]
                ec = [e.coord for e in explored]
                if n not in fc and n not in ec:
                    if self.grid[n[0]][n[1]][2] == 1:
                        continue
                    #print n
                    newnode = State()
                    newnode.coord = n
                    newnode.parent = node
                    if n == problem.goal:
                        s = self.make_solution(newnode)
                        self.ani.animate(s, [self.adjust(e.coord) for e in explored])
                        return s
                    frontier.append(newnode)
    
    def get_neighbors(self, node):
        l = []
        if not self.is_outside_bounds( (node[0]-1, node[1]) ):
            l.append( (node[0]-1, node[1]) )
        if not self.is_outside_bounds( (node[0]+1, node[1]) ):
            l.append( (node[0]+1, node[1]) )
        if not self.is_outside_bounds( (node[0], node[1]+1) ):
            l.append( (node[0], node[1]+1) )
        if not self.is_outside_bounds( (node[0], node[1]-1) ):
            l.append( (node[0], node[1]-1) )
        if not self.is_outside_bounds( (node[0]-1, node[1]+1) ):
            l.append( (node[0]-1, node[1]+1) )
        if not self.is_outside_bounds( (node[0]+1, node[1]+1) ):
            l.append( (node[0]+1, node[1]+1) )
        if not self.is_outside_bounds( (node[0]-1, node[1]-1) ):
            l.append( (node[0]-1, node[1]-1) )
        if not self.is_outside_bounds( (node[0]+1, node[1]-1) ):
            l.append( (node[0]+1, node[1]-1) )
        return l
        
    def is_outside_bounds(self, node):
        return (node[0] < 0 or node[1] < 0 or
                node[0] > int(self.constants['worldsize']) - 1 or
                node[1] > int(self.constants['worldsize']) - 1)
                
    def make_solution(self, node):
        a = []
        while node.parent != None:
            a.append( self.adjust(node.coord) )
            node = node.parent
        a.append( self.adjust(node.coord) )
        a.reverse()
        return a
        
    def adjust(self, coord):
        return (self.grid[coord[0]][coord[1]][0], self.grid[coord[0]][coord[1]][1])
    
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
    
    agent.search(algorithm)


if __name__ == '__main__':
    main()
