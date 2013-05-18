# searching agent

import sys
import math
import thread

from Queue import PriorityQueue

from animation import ANIMATION as Animation

from collections import deque

from bzrc import BZRC, Command
    
class State(object):
    pass

class Problem(object):
    pass
    
class Failure(Exception):
    
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

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
        self.step = 1000
        
        self.path = []
        
    def search(self, algorithm):
        problem = Problem()
        problem.starting = (int(self.mytank.x + self.offset), int(self.mytank.y + self.offset))
        problem.goal = (int(self.goal.x + self.offset), int(self.goal.y + self.offset))
        if algorithm == 'depthfirstP' or algorithm == 'dfs':
            problem.penalized=True
            return self.depthFirstSearch(problem)
        elif algorithm == 'depthfirst' or algorithm == 'dfs':
            problem.penalized=False
            return self.depthFirstSearch(problem)
        elif algorithm == 'breadthfirstP' or algorithm == 'bfs':
            problem.penalized=True
            #problem.goal = (int(self.mytank.x + self.offset + 10), int(self.mytank.y + self.offset))
            return self.breadthFirstSearch(problem)
        elif algorithm == 'breadthfirst' or algorithm == 'bfs':
            problem.penalized=False
            #problem.goal = (int(self.mytank.x + self.offset + 10), int(self.mytank.y + self.offset))
            return self.breadthFirstSearch(problem)
        elif algorithm == 'iterativedeepeningP' or algorithm == 'ids':
            #problem.goal = (int(self.mytank.x + self.offset + 10), int(self.mytank.y + self.offset))
            problem.penalized=True
            return self.iterativeDeepening(problem)
        elif algorithm == 'iterativedeepening' or algorithm == 'ids':
            #problem.goal = (int(self.mytank.x + self.offset + 10), int(self.mytank.y + self.offset))
            problem.penalized=False
            return self.iterativeDeepening(problem)
        elif algorithm == 'uniformcostP' or algorithm == 'ucs':
            #problem.goal = (int(self.mytank.x + self.offset + 10), int(self.mytank.y + self.offset))
            problem.penalized=True
            return self.uniformCost(problem)
        elif algorithm == 'uniformcost' or algorithm == 'ucs':
            #problem.goal = (int(self.mytank.x + self.offset + 10), int(self.mytank.y + self.offset))
            problem.penalized=False
            return self.uniformCost(problem)
        elif algorithm == 'astarP':
            #problem.goal = (int(self.mytank.x + self.offset + 50), int(self.mytank.y + self.offset-10))
            problem.penalized=True
            return self.aStar(problem)
        elif algorithm == 'astar':
            #problem.goal = (int(self.mytank.x + self.offset + 50), int(self.mytank.y + self.offset-10))
            problem.penalized=False
            return self.aStar(problem)
        
        else:
            raise Failure('Unknown algorithm %d' % algorithm)
            
    def aStar(self, problem):
        node = State()
        node.coord = problem.starting
        node.parent = None
        nexplored=1
        node.gscore=0
        node.cost = 0
        node.fscore=0 + self.aStarCostEstimate(node.coord,problem.goal)
        openNodes = PriorityQueue(maxsize=0)
        openNodes.put((node.fscore,node))
        openList=[node.coord]
        closedNodes=[]
        self.path=[]
        while True:
            
           
            if openNodes.empty():
                 raise Exception('failure')
            node=openNodes.get()[1]
            openList.remove(node.coord)
            if self.grid[node.coord[0]][node.coord[1]][2] == 1:
                continue
            if node.coord== problem.goal:
                s, l, c = self.make_solution(node)
                self.ani.animate(s, 1)
                print " nodes visited:", nexplored
                print "length of path:", l
                print "  cost of path:", c
                return s
            closedNodes.append(node.coord)
            if node.parent:
                self.path.append((self.adjust(node.parent.coord),self.adjust(node.coord)))
                
            if len(self.path) > self.step:
                #print "new command"
                self.ani.animateTuples(self.path, 2 ) 
                self.path = []
            neighbors=self.get_neighbors_with_weight(node.coord)
            for n in neighbors:
                nexplored += 1
                costOfTravel=n[2]
                if problem.penalized:
                    if self.nextToObject(node.coord) and self.nextToObject((n[0],n[1])):
                        costOfTravel=n[2]*1.5
                    elif self.nextToObject(node.coord): 
                        costOfTravel=n[2]*1.1
                    elif self.nextToObject((n[0],n[1])):
                        costOfTravel=n[2]*1.3
                    
                tenativeGScore = node.gscore + costOfTravel
                
                if (n[0],n[1]) in closedNodes:
                    
                    if tenativeGScore>=n[2]:
                        continue
               
                        
                if (n[0],n[1]) not in openList or tenativeGScore < n[2]:
                    newNode=State()
                    newNode.coord=(n[0],n[1])
                    newNode.parent=node
                    newNode.gscore=tenativeGScore
                    newNode.cost = costOfTravel
                    newNode.fscore=newNode.gscore + self.aStarCostEstimate(newNode.coord,problem.goal)
                    if newNode.coord not in openList:
                       # print n
                        openNodes.put((newNode.fscore,newNode))
                        openList.append(newNode.coord)
                       # print openNodes.qsize()
     
                     
    def aStarCostEstimate(self, a , b):
        #return 1
        return ((b[1]-a[1])**2+(b[0]-a[0])**2)**.5
        
    def nextToObject(self, node):
        if self.is_occupied( (node[0]-1, node[1]) ):
            return True
        if self.is_occupied( (node[0]+1, node[1]) ):
            return True
        if self.is_occupied( (node[0], node[1]+1) ):
            return True
        if self.is_occupied( (node[0], node[1]-1) ):
            return True
        if self.is_occupied( (node[0]-1, node[1]+1) ):
            return True
        if self.is_occupied( (node[0]+1, node[1]+1) ):
            return True
        if self.is_occupied( (node[0]-1, node[1]-1) ):
            return True
        if self.is_occupied( (node[0]+1, node[1]-1) ):
            return True
        return False
            
    def is_occupied( self, p ):
        return self.grid[p[0]][p[1]][2] == 1
            
    def uniformCost(self, problem):
        node = State()
        node.coord = problem.starting
        node.parent = None
        node.weight=0
        explored=[problem.starting]
        self.path=[]
        if problem.starting == problem.goal:
            return [self.adjust(problem.starting)]
        frontier = PriorityQueue(maxsize=0)
        frontier.put((node.weight,node))
        while True:
            if frontier.empty():
                raise Exception('failure')
            node = frontier.get()[1]
            
            if node.parent:
                self.path.append((self.adjust(node.parent.coord),self.adjust(node.coord)))
            if len(self.path) > self.step:
                #pass path to self.ani somehow
                self.ani.animateTuples(self.path, 2)
                self.path = []
            for x, y, c in self.get_neighbors_with_weight(node.coord):
                n = (x, y)
                if n not in explored:
                    if self.grid[n[0]][n[1]][2] == 1:
                        continue
                    #print n
                    explored.append(n)
                    newnode = State()
                    newnode.coord = n
                    newnode.weight = node.weight + c
                    newnode.parent = node
                    if n == problem.goal:
                        s = self.make_solution(newnode)
                        self.ani.animate(s, 1)
                        return s
                    frontier.put((newnode.weight, newnode))
    
    def iterativeDeepening(self, problem):
        cutoff = 1
        while True:
            try:
                result = self.depthLimitedSearch(problem, cutoff)
                self.ani.animate(result, 1)
                return result
            except Failure:
                self.ani.animateTuples(self.path, 2)
                cutoff += 1
                
    def depthLimitedSearch(self, problem, cutoff):
        node = State()
        node.coord = problem.starting
        node.parent = None
        node.cost = 0
        return self.recursiveDLS(node, problem, cutoff, [])
        
    def recursiveDLS(self, node, problem, cutoff, visited):
        if node.parent:
            self.path.append((self.adjust(node.parent.coord),self.adjust(node.coord)))
        visited.append(node.coord)
        if len(self.path) > self.step:
            self.ani.animateTuples(self.path, 2)
            self.path = []
        if node.coord == problem.goal:
            s, l, c = self.make_solution(newnode)
            self.ani.animate(s, 1)
            print " nodes visited: tl;dr"
            print "length of path:", l
            print "  cost of path:", c
            return self.make_solution(node)
        elif cutoff == 0:
            raise Failure('Limit Reached')
        else:
            neighbors = self.get_neighbors_with_weight(node.coord)
            for x, y, w in neighbors:
                n = (x, y)
                if self.grid[n[0]][n[1]][2] == 1:
                    continue
                elif n in visited:
                    continue
                newnode = State()
                newnode.coord = n
                newnode.parent = node
                newnode.cost = w
                try:
                    return self.recursiveDLS(newnode, problem, cutoff-1, visited)
                except Failure:
                    continue
            raise Failure('No solution with that limit')
 

    def depthFirstSearch(self, problem):
        """Returns a list of tuples, being x, y coordinates on the grid
           being the path to the goal found via a depth first search"""
        stack = []
        explored = [problem.starting]
        nexplored = 1
        recent = [problem.starting]
        if problem.starting == problem.goal:
            return [self.adjust(problem.starting)]
        node = State()
        node.coord = problem.starting
        path = [ (self.adjust(node.coord), self.adjust(node.coord)) ]
        node.parent = None
        node.cost = 0
        stack.append(node)
        while True:
            if len(stack) == 0:
                raise Failure('Depth First Search')
            node = stack.pop()
            if len(path) > self.step:
                #pass path to self.ani somehow
                self.ani.animateTuples(path, 2)
                path = []
            neighbors = self.get_neighbors_with_weight(node.coord)
            #neighbors.reverse()
            for x, y, w in neighbors:
                n = (x, y)
                if n in recent:
                    continue
                elif n in explored:
                    continue
                if self.grid[n[0]][n[1]][2] == 1:
                    continue
                explored.append(n)
                recent.append(n)
                nexplored += 1
                path.append( (self.adjust(node.coord), self.adjust(n)) )
                newnode = State()
                newnode.coord = n
                newnode.parent = node
                newnode.cost = w
                if n == problem.goal:
                    s, l, c = self.make_solution(newnode)
                    self.ani.animate(s, 1)
                    print " nodes visited:", nexplored
                    print "length of path:", l
                    print "  cost of path:", c
                    return s
                stack.append(newnode)
     
    def breadthFirstSearch(self, problem):
        """Returns a list of tuples, being x, y coordinates on the grid
           being the path to the goal found via a depth first search"""
        frontier=deque([])
        if problem.starting == problem.goal:
            return [self.adjust(problem.starting)]
        node = State()
        node.coord = problem.starting
        node.parent = None
        node.cost = 0
        frontier.append( node )
        explored=[node.coord]
        nexplored = 1
        recent=[node.coord]
        path = [ (self.adjust(node.coord), self.adjust(node.coord) ) ]
        while True:
            if len(frontier) == 0:
                raise Failure('Breadth First Search')
            node = frontier.popleft()
            if len(path) > self.step:
                #pass path to self.ani somehow
                self.ani.animateTuples(path, 2)
                path = []
            for x, y, w in self.get_neighbors_with_weight(node.coord):
                n = (x, y)
                if n  in recent:
                    continue
                elif n in explored:
                    continue
                if self.grid[n[0]][n[1]][2] == 1:
                    continue
                #print n
                explored.append(n)
                recent.append(n)
                nexplored += 1
                if len(recent) > 1000:
                    recent = recent[-300:]
                path.append( (self.adjust(node.coord), self.adjust(n)) )
                newnode = State()
                newnode.coord = n
                newnode.parent = node
                newnode.cost = w
                if n == problem.goal:
                    s, l, c = self.make_solution(newnode)
                    self.ani.animate(s, 1)
                    print " nodes visited:", nexplored
                    print "length of path:", l
                    print "  cost of path:", c
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
        
    def get_neighbors_with_weight(self, node):
        l = []
        if not self.is_outside_bounds( (node[0]-1, node[1]) ):
            l.append( (node[0]-1, node[1], 1) )
        if not self.is_outside_bounds( (node[0]+1, node[1]) ):
            l.append( (node[0]+1, node[1], 1) )
        if not self.is_outside_bounds( (node[0], node[1]+1) ):
            l.append( (node[0], node[1]+1, 1) )
        if not self.is_outside_bounds( (node[0], node[1]-1) ):
            l.append( (node[0], node[1]-1, 1) )
        if not self.is_outside_bounds( (node[0]-1, node[1]+1) ):
            l.append( (node[0]-1, node[1]+1, math.sqrt(2)) )
        if not self.is_outside_bounds( (node[0]+1, node[1]+1) ):
            l.append( (node[0]+1, node[1]+1, math.sqrt(2)) )
        if not self.is_outside_bounds( (node[0]-1, node[1]-1) ):
            l.append( (node[0]-1, node[1]-1, math.sqrt(2)) )
        if not self.is_outside_bounds( (node[0]+1, node[1]-1) ):
            l.append( (node[0]+1, node[1]-1, math.sqrt(2)) )
        return l
        
    def is_outside_bounds(self, node):
        return (node[0] < 0 or node[1] < 0 or
                node[0] > int(self.constants['worldsize']) - 1 or
                node[1] > int(self.constants['worldsize']) - 1)
                
    def make_solution(self, node):
        a = []
        c = 0
        l = 0
        while node.parent != None:
            a.append( self.adjust(node.coord) )
            c += node.cost
            l += 1
            node = node.parent
        a.append( self.adjust(node.coord) )
        a.reverse()
        return a, l, c
        
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
    
    try:
        agent.search(algorithm)
    except Failure as f:
        print f


if __name__ == '__main__':
    main()
