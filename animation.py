
#!/usr/bin/env python
'''This is a demo on how to use Gnuplot for potential fields.  We've
intentionally avoided "giving it all away."
'''


from __future__ import division 
from itertools import cycle
import math

class ANIMATION:
    
    
    def __init__(self, WS, OB):
        """Initialize variables"""
        self.worldSize=WS
        
        self.obstacles=OB
        self.counter=0
        try:
            from Gnuplot import GnuplotProcess
        except ImportError:
            print "Sorry.  You don't have the Gnuplot module installed."
            import sys
            sys.exit(-1)
        self.gp = GnuplotProcess(persist=True)
        self.gp.write(self.draw_obstacles(self.obstacles)) 
   
        
    def animate(self,orderedVisits, color):
        
        self.gp.write(self.gnuplot_header(-self.worldSize / 2, self.worldSize / 2))
        self.gp.write(self.draw_nodes(orderedVisits,color))
    
    def animateTuples(self,orderedVisits, color):
        
        self.gp.write(self.gnuplot_header(-self.worldSize / 2, self.worldSize / 2))
        self.gp.write(self.draw_node_tuples(orderedVisits,color))
       
        


    def draw_nodes(self,nodes,color):
        '''Return a string which tells Gnuplot to draw all of the obstacles.'''
        #s = 'unset arrow\n'
        s = ''

       
        last_point = nodes[0]
        for cur_point in nodes[1:]:
            s += self.draw_line_pause(last_point, cur_point, color)
            last_point = cur_point
        
        
           
        return s
    
    def draw_node_tuples(self,nodes,color):
        '''Return a string which tells Gnuplot to draw all of the obstacles.'''
        #s = 'unset arrow\n'
        s = ''

        for cur_point in nodes:
            s += self.draw_line_pause(cur_point[0], cur_point[1], color)
           
        
        
           
        return s    
        
    def gnuplot_header(self,minimum, maximum):
        '''Return a string that has all of the gnuplot sets and unsets.'''
        s = ''
        s += 'set xrange [%s: %s]\n' % (minimum, maximum)
        s += 'set yrange [%s: %s]\n' % (minimum, maximum)
        # The key is just clutter.  Get rid of it:
        s += 'unset key\n'
        # Make sure the figure is square since the world is square:
        s += 'set size square\n'
        # Add a pretty title (optional):
        #s += "set title 'Potential Fields'\n"
        return s
    
    def draw_obstacles(self,obstacles):
        '''Return a string which tells Gnuplot to draw all of the obstacles.'''
        s = 'unset arrow\n'
        brown=3
        for obs in obstacles:
            last_point = obs[0]
            for cur_point in obs[1:]:
                s += self.draw_line(last_point, cur_point, brown)
                last_point = cur_point
            s += self.draw_line(last_point, obs[0], brown)
        
        return s
                  
    def draw_line(self,p1, p2,color):
        '''Return a string to tell Gnuplot to draw a line from point p1 to
        point p2 in the form of a set command.'''
        x1 = p1[0]
        y1 = p1[1]
        x2 = p2[0]
        y2 = p2[1]
        s='set arrow from %s, %s to %s, %s nohead lt %d\n' % (x1, y1, x2, y2 ,color)
        
        return s
        
    def draw_line_pause(self, p1, p2, color):
        '''Return a string to tell Gnuplot to draw a line from point p1 to
        point p2 in the form of a set command.'''
        x1 = p1[0]
        y1 = p1[1]
        x2 = p2[0]
        y2 = p2[1]
        s='set arrow from %s, %s to %s, %s nohead lt %d\n' % (x1, y1, x2, y2 ,color)
        
        s+="\nplot '-' with lines\n0 0 0 0\ne\npause %f\n" % (0)

        return s
       
   






        


