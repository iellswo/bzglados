
#!/usr/bin/env python
'''This is a demo on how to use Gnuplot for potential fields.  We've
intentionally avoided "giving it all away."
'''


from __future__ import division 
from itertools import cycle
import math

class ANIMATION:
    
    
    def __init__(self, WS, SP, OB, OS, GL, GR, GS):
        """Initialize variables"""
        self.spread=SP
        self.worldSize=WS
        self.obsScale=OS
        self.goal={'radius' : float(GR), 'center' : GL, 'type' : "pull", 'scale' : float(GS)}
        self.obstacles=OB
        self.fieldGenerators = []
        for ob in OB:
            self.obsRadiusAndCenter(ob)
            

    def update(self, GL, GR, GS):
        self.goal={'radius' : float(GR),'center' : GL, 'type' : "pull", 'scale' : float(GS)}
        
   
    ########################################################################
    # Field and Obstacle Definitions


        #this determines our arrow at the point x y I've added the attractive field case
     
       
    def generate_repulsive_fields(self, x, y):
        
        fx = 0.0
        fy = 0.0
        
        for fg in self.fieldGenerators:
            if fg['type'] == 'push':
                #print fg
                distance = math.sqrt( (fg['center'][0] - x)**2 +  (fg['center'][1] - y)**2 )
                theta=math.atan2((fg['center'][1] - y), (fg['center'][0] - x))
            
                if distance<fg['radius']:
                    fx += -math.copysign(10, math.cos(theta))
                    fy += -math.copysign(10, math.sin(theta))
                elif fg['radius'] <= distance <= (self.spread + fg['radius']):
                    fx += -fg['scale'] * (self.spread + fg['radius'] - distance) * math.cos(theta)
                    fy += -fg['scale'] * (self.spread + fg['radius'] - distance) * math.sin(theta)
                elif distance>(self.spread+fg['radius']):
                    fx += 0.0
                    fy += 0.0
                
        return fx, fy
    
    def generate_attractive_fields(self, x, y, fg):
        
        fx = 0.0
        fy = 0.0
        # return the vector for this location
        distance = math.sqrt( (fg['center'][0] - x)**2  +  (fg['center'][1] - y)**2 )
        theta = math.atan2((fg['center'][1] - y), (fg['center'][0] - x))
        if distance < fg['radius']:
            fx = 0
            fx = 0
        elif fg['radius'] <= distance <= (self.spread + fg['radius']):
            fx = fg['scale'] * (distance-fg['radius']) * math.cos(theta)
            fy = fg['scale'] * (distance-fg['radius']) * math.sin(theta)
        elif distance>(self.spread+fg['radius']):
            fx = fg['scale'] * math.cos(theta)
            fy = fg['scale'] * math.sin(theta)
        
        return fx, fy
        
    def generate_tangental_fields(self,x, y):
        
        fx = 0.0
        fy = 0.0
        
        for fg in self.fieldGenerators:
            if fg['type'] == 'push':
                #print fg
                distance = math.sqrt( (fg['center'][0] - x)**2 +  (fg['center'][1] - y)**2 )
                theta = math.atan2((fg['center'][1] - y), (fg['center'][0] - x)) + math.pi/4
            
                if distance<fg['radius']:
                    fx += -math.copysign(50, math.cos(theta))
                    fy += -math.copysign(50, math.sin(theta))
                elif fg['radius'] <= distance <= (self.spread + fg['radius']):
                    fx += -fg['scale']*2 * (self.spread + fg['radius'] - distance) * math.cos(theta)
                    fy += -fg['scale']*2 * (self.spread + fg['radius'] - distance) * math.sin(theta)
                elif distance>(self.spread+fg['radius']):
                    fx += 0.0
                    fy += 0.0
                
        return fx, fy

    def generate_fields(self, x, y):
        
        x1, y1 = self.generate_attractive_fields(x, y, self.goal)
        #print "attractive", x1, y1
        x2, y2 = self.generate_repulsive_fields(x, y)
        #print "repulsive", x2, y2
        x3, y3 = self.generate_tangental_fields(x, y)
        #print "tangental", x3, y3
        return (x+x1+x2+x3), (y+y1+y2+y3)
        
    def animate(self,path,orderedVisits):
        try:
            from Gnuplot import GnuplotProcess
        except ImportError:
            print "Sorry.  You don't have the Gnuplot module installed."
            import sys
            sys.exit(-1)
        gp = GnuplotProcess(persist=True)
        gp.write(gnuplot_header(-self.worldsize / 2, self.worldsize / 2))
        gp.write(draw_obstacles(self.obstacles)) 
        gp.write(draw_nodes(orderedVisits))
        gp.write(draw_path(path))
        
    def draw_path(self,path):
        '''Return a string which tells Gnuplot to draw all of the obstacles.'''
        s = 'unset arrow\n'

        for p in path:
            red=1
            last_point = p[0]
            for cur_point in p[1:]:
                s += draw_line(last_point, cur_point, red)
                last_point = cur_point
        return s

    def draw_nodes(self,nodes):
        '''Return a string which tells Gnuplot to draw all of the obstacles.'''
        s = 'unset arrow\n'

        for n in nodes:
            green=2
            last_point = n[0]
            for cur_point in n[1:]:
                s += draw_line(last_point, cur_point, green)
                last_point = cur_point
            
            s+="\nplot '-' with lines\n0 0 0 0\ne\npause %f\n" % (1.0)
           
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
        brown=6
        for obs in obstacles:
            last_point = obs[0]
            for cur_point in obs[1:]:
                s += draw_line(last_point, cur_point, brown)
                last_point = cur_point
            s += draw_line(last_point, obs[0], brown)
           
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
   

    ########################################################################
    # Helper Functions

   

    def obsRadiusAndCenter(self, tup):
        xmin=float("inf")
        xmax=float("-inf")
        ymin=float("inf")
        ymax=float("-inf")
        for pairs in tup:
            if float(pairs[0])>xmax:
                xmax=float(pairs[0])
            if float(pairs[0])<xmin:
                xmin=float(pairs[0])
            if float(pairs[1])>ymax:
                ymax=float(pairs[1])
            if float(pairs[1])<ymin:
                ymin=float(pairs[1])
        temp = ( ( math.sqrt( float(xmax-xmin)**2 + float(ymax-ymin)**2)/2 ), 
        (float(xmax-xmin)/2 + xmin, float(ymax-ymin)/2 + ymin), 
        "push")
        fg = {'radius' : temp[0], 'center' : temp[1], 'type' : temp[2], 'scale' : .5}
        self.fieldGenerators.append(fg)
        
        return temp
          






        


