import math

from numpy import zeros
from Queue import PriorityQueue

# what fraction do we descretize?
FACTOR = 16
OCCRATIO = .7

class Failure(Exception):
    
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
class Problem():
    
    def __init__(self, starting, goal):
        self.starting = starting
        self.goal = goal

class Searcher():
    
    def __init__(self, world_size):
        self.grid_size = world_size/FACTOR
        #print self.grid_size
        self.grid = self.init_grid()
        
    def init_grid(self):
        return zeros((self.grid_size, self.grid_size))
        
    def descretize_grid(self, grid):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                ave = 0.0
                for x in range(FACTOR):
                    for y in range(FACTOR):
                        #print (i*FACTOR)+x, (j*FACTOR)+y
                        ave += grid[(i*FACTOR)+x][(j*FACTOR)+y]
                ave = ave / (FACTOR**2)
                self.grid[i][j] = ave
                
    def descretize_point(self, p):
        x, y = p
        return (x/FACTOR, y/FACTOR)
        
    def expand_point(self, p):
        x, y = p
        return (x*FACTOR + (FACTOR/2), y*FACTOR + (FACTOR/2))
                
    def print_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                print self.grid[i][j],
            print ''
            
    def get_path(self, start, end):
        problem = Problem(self.descretize_point(start), self.descretize_point(end))
        return self.a_star(problem)
    
    def a_star(self, problem):
        node = {}
        node['coord'] = problem.starting
        node['parent'] = None
        node['gscore']=0
        node['cost'] = 0
        node['fscore']=0 + self.distance(node['coord'],problem.goal)
        openNodes = PriorityQueue(maxsize=0)
        openNodes.put((node['fscore'],node))
        openList=[node['coord']]
        closedList=[]
        nodes = []
        size = self.grid_size
        for i in range(size):
            row = []
            for j in range(size):
                row.append( None )
            nodes.append(row)
        while True:
            
            if openNodes.empty():
                 raise Failure('A*')
            node=openNodes.get()[1]
            c = node['coord']
            openList.remove(c)
            if self.grid[c[0]][c[1]] >= OCCRATIO:
                continue
            if c == problem.goal:
                s = self.make_solution(node)
                return s
            closedList.append(c)
                
            neighbors=self.get_neighbors_with_weight(c)
            for x, y, w in neighbors:
                costOfTravel = w
                
                if self.nextToObject(node['coord']) and self.nextToObject((x,y)):
                    costOfTravel=w*2.5
                elif self.nextToObject(node['coord']): 
                    costOfTravel=w*.7
                elif self.nextToObject((x,y)):
                    costOfTravel=w*2.1
                    
                tenativeGScore = node['gscore'] + costOfTravel
                
                if (x,y) in closedList:
                    
                    if tenativeGScore>=costOfTravel:
                        continue
                        
                yes = False
                if nodes[x][y] != None:
                    if tenativeGScore < nodes[x][y]['gscore']:
                        yes = True
                        
                if (x,y) not in openList or yes:
                    newNode={}
                    if nodes[x][y]!=None:
                        newNode = nodes[x][y]
                    newNode['coord']=(x,y)
                    newNode['parent']=node
                    newNode['gscore']=tenativeGScore
                    newNode['cost'] = costOfTravel
                    newNode['fscore']=tenativeGScore + self.distance((x,y), problem.goal)
                    nodes[x][y] = newNode
                    if newNode['coord'] not in openList:
                        openNodes.put((newNode['fscore'],newNode))
                        openList.append(newNode['coord'])
                        
    def distance(self, a , b):
        return math.sqrt((b[1]-a[1])**2+(b[0]-a[0])**2)
        
    def make_solution(self, node):
        a = []

        while node['parent'] != None:
            a.append( self.expand_point(node['coord']) )

            node = node['parent']
        a.append( self.expand_point(node['coord']) )
        a.reverse()
        return a
        
    def get_neighbors_with_weight(self, node):
        x, y = node
        l = []
        if not self.is_outside_bounds( (x-1, y) ):
            l.append( (x-1, y, 1) )
        if not self.is_outside_bounds( (x+1, y) ):
            l.append( (x+1, y, 1) )
        if not self.is_outside_bounds( (x, y+1) ):
            l.append( (x, y+1, 1) )
        if not self.is_outside_bounds( (x, y-1) ):
            l.append( (x, y-1, 1) )
        if not self.is_outside_bounds( (x-1, y+1) ):
            l.append( (x-1, y+1, math.sqrt(2)) )
        if not self.is_outside_bounds( (x+1, y+1) ):
            l.append( (x+1, y+1, math.sqrt(2)) )
        if not self.is_outside_bounds( (x-1, y-1) ):
            l.append( (x-1, y-1, math.sqrt(2)) )
        if not self.is_outside_bounds( (x+1, y-1) ):
            l.append( (x+1, y-1, math.sqrt(2)) )
        return l
        
    def nextToObject(self, node):
        x, y = node
        if self.is_occupied( (x-1, y) ):
            return True
        if self.is_occupied( (x+1, y) ):
            return True
        if self.is_occupied( (x, y+1) ):
            return True
        if self.is_occupied( (x, y-1) ):
            return True
        if self.is_occupied( (x-1, y+1) ):
            return True
        if self.is_occupied( (x+1, y+1) ):
            return True
        if self.is_occupied( (x-1, y-1) ):
            return True
        if self.is_occupied( (x+1, y-1) ):
            return True
        return False
        
    def is_occupied( self, p ):
        if self.is_outside_bounds(p):
            return True
        return self.grid[p[0]][p[1]] >= OCCRATIO
        
    def is_outside_bounds(self, node):
        x, y = node
        return (x < 0 or y < 0 or
                x > int(self.grid_size) - 1 or
                y > int(self.grid_size) - 1)
