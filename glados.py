# GLaDOS: Genetic Lifeform and Disk Operating System:
# (aka our final agent for bzrflag game)

# Ike Ellsworth and Josh Lepinski

import sys
import math
import time
import threading
import Queue

from numpy import zeros
from utilities.bzrc import BZRC, Command
from utilities.kalman import KalmanFilter as Filter
from utilities.search import Searcher

###########################################################
#  constants

# what is the posnoise?
NOISE = 3

#
###########################################################

class State:
    Running, Searching, Returning, Shadowing = range(4)
    
class myThread(threading.Thread:
    def __init__(self,grid,queue,worldSize,start,end,queueLock):
        threading.Thread.__init__(self)
        self.grid=copy.copy(grid)
        self.queue=queue
        self.worldSize=worldSize
        self.start=start
        self.end=end
        self.queueLock=queueLock
        
    def run():
        self.search=Searcher(self.worldSize)
        self.search.descretize_grid(self.grid)
        self.search.get_path(self.queue,self.queueLock,self.start,self.end)
        
        
    

class Controller(object):
    
    def __init__(self, bzrc):
        # bzrc connections
        self.bzrc = bzrc
        self.constants = self.bzrc.get_constants()
        self.commands = []
        
        # game details
        self.world_size = int(self.constants['worldsize'])
        self.offset = self.world_size/2
        self.grid = zeros((self.world_size, self.world_size))
        self.team = self.constants['team']
        
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        
        self.states = []
        self.paths = []
        self.threadQ = []
        self.QLocks=[]
        for tank in mytanks:
            self.states.append(State.Running)
            self.paths.append([])
            self.threadQ.append(Queue())
            self.QLocks.append(threading.Lock())
        
        self.filters = []
        

    # every tick:
    def tick(self, time_diff):
        mytanks, othertanks, flags, shots = self.bzrc.get_lots_o_stuff()
        target = flags[0] 
        if target.color == self.team:
            target = flags[1]
        for tank in mytanks:
            self.tank_control(tank, target, othertanks, shots)

 
    # Main tank control methods:       
    def tank_control(self, tank, target, othertanks, shots):
        index = tank.index
        if self.states[index] == State.Running:
            if len(self.paths[index]) <= 2:
                self.searcher.descretize_grid(self.grid) # maybe?
                # spawn a search thread, and change state
                self.states[index] = State.Searching
                return
            
            t = self.paths[index][1]
            if self.is_occupied(t):
                # spawn a search thread, and change state
                
                thread=myThread(self.grid,self.threadQ[index],self.world_size,(tank.x, tank.y),(target.x,target.y),QLocks[index])
                thread.start()
                self.states[index] = State.Searching
                return
            self.update_grid(tank)
            self.move_to_position(tank, self.to_world_space(t))
            if self.distance((tank.x, tank.y), self.to_world_space(t)) < HEREYET:
                self.paths[index] = self.paths[index][1:]
            
            
        elif self.states[index] == State.Searching:
            # check to see if the thread is finished
            QLocks[index].acquire()
            if not threadQ[index].empty():
            # if it is, then set that path and change state to running/returning
                self.paths[index]=threadQ[index].get()
                self.states[index] = State.Running
                QLocks[index].release()
            else:
                QLocks[index].release()
             # if it is not, find closest tank and target them
           
            
        elif self.states[index] == State.Returning:
            if len(self.paths[index]) <= 2:
                self.states[index] = State.Running
                return
            
            t = self.paths[index][1]
            self.move_to_position(tank, self.to_world_space(t))
            
        else:
            pass

    def update_grid(self, tank):
        """Gets the occgrid from the server for the current tank
           It then updates the world grid."""
        t_start, t_grid = self.bzrc.get_occgrid(tank.index)
        #print t_start
        g_x, g_y = self.to_grid_space(t_start)
        #print g_start
        for i in range(len(t_grid)):
            for j in range(len(t_grid[i])):
                x = g_x + i
                y = g_y + j
                self.grid[x][y] = t_grid[i][j]
                
        
    # Utility methods:
    def to_world_space(self, n):
        x, y = n
        return (x - self.offset, y - self.offset)
        
    def to_grid_space(self, n):
        x, y = n
        return (int(self.offset + x), int(self.offset + y))
        
    def distance(self, a , b):
        return math.sqrt((b[1]-a[1])**2+(b[0]-a[0])**2)

    def is_occupied( self, p ):
        x, y = p
        if self.is_outside_bounds(p):
            return True
        else:
            return self.grid[x][y] >= 1

    def is_outside_bounds(self, node ):
        return (node[0] < 0 or node[1] < 0 or
                node[0] > self.worldsize - 1 or
                node[1] > self.worldsize - 1)
        
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
    
    agent = Controller(bzrc)
    
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
