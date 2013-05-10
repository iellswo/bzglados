
#!/usr/bin/env python
'''This is a demo on how to use Gnuplot for potential fields.  We've
intentionally avoided "giving it all away."
'''


from __future__ import division 
from itertools import cycle
import math

try:
    from numpy import linspace
except ImportError:
    # This is stolen from numpy.  If numpy is installed, you don't
    # need this:
    def linspace(start, stop, num=50, endpoint=True, retstep=False):
        """Return evenly spaced numbers.

        Return num evenly spaced samples from start to stop.  If
        endpoint is True, the last sample is stop. If retstep is
        True then return the step value used.
        """
        num = int(num)
        if num <= 0:
            return []
        if endpoint:
            if num == 1:
                return [float(start)]
            step = (stop-start)/float((num-1))
            y = [x * step + start for x in xrange(0, num - 1)]
            y.append(stop)
        else:
            step = (stop-start)/float(num)
            y = [x * step + start for x in xrange(0, num)]
        if retstep:
            return y, step
        else:
            return y


########################################################################
# Constants

# Output file:
FILENAME = 'fields.gpi'
# Size of the world (one of the "constants" in bzflag):
WORLDSIZE = 800
# How many samples to take along each dimension:
SAMPLES = 25
# Change spacing by changing the relative length of the vectors.  It looks
# like scaling by 0.75 is pretty good, but this is adjustable:
VEC_LEN = 0.75 * WORLDSIZE / SAMPLES
# Animation parameters:
ANIMATION_MIN = 0
ANIMATION_MAX = 500
ANIMATION_FRAMES = 50
SPREAD=30


########################################################################
# Field and Obstacle Definitions


    #this determines our arrow at the point x y I've added the attractive field case
   
def getObsVectors(x,y):
    '''User-defined field function.'''
        fx=0.0
        fy=0.0
        
        for fg in fieldGenerators:
            distance = (((fg['center'][0]-x) ** 2 + (fg['center'][1]-y) ** 2) ** 0.5)//2
            if abs(fg['center'][0]-x)>abs(fg['center'][1]-y): 
                    
                theta= math.atan((fg['center'][0]-x)//(fg['center'][1]-y))   
            else: 
                theta= math.atan((fg['center'][1]-y)//(fg['center'][0]-x))
             
                    
            if fg['type']=="push":
                if distance<fg['radius']:
                    if fg['center'][0]==x and y>fg['center'][1]:
       	   				fx+=0
       	   				fy+=-1
                    elif fg['center'][0]==x and y<fg['center'][1]:
        				fx+=0
        				fy+=1
                    elif fg['center'][1]==y and x<fg['center'][0]:
        				fx+=1
        				fy+=0
                    elif fg['center'][1]==y and x>fg['center'][0]:
                        fx+=-1
                        fy+=0
                    #elif abs(fg['center'][0]-x)>abs(fg['center'][1]-y):
                    elif x>fg['center'][0]:
                        fx+=math.cos(theta)
                        fy+=math.sin(theta)    
                    else:
                        fx+=math.cos(theta)*-1
                        fy+=math.sin(theta)*-1
                if fg['radius']<=distance<=(SPREAD+fg['radius']):
                    if fg['center'][0]==x and y>fg['center'][1]:
       	   				fx+=0
       	   				fy+=fg['scale']*(SPREAD+fg['radius']-distance)*-1
                    elif fg['center'][0]==x and y<fg['center'][1]:
        				fx+=0
        				fy+=fg['scale']*(SPREAD+fg['radius']-distance)**1
                    elif fg['center'][1]==y and x<fg['center'][0]:
        				fx+=fg['scale']*(SPREAD+fg['radius']-distance)**1
        				fy+=0
                    elif fg['center'][1]==y and x>fg['center'][0]:
                        fx+=fg['scale']*(SPREAD+fg['radius']-distance)**-1
                        fy+=0
                    elif abs(fg['center'][0]-x)>abs(fg['center'][1]-y):
                        fy+=fg['scale']*(SPREAD+fg['radius']-distance)*math.cos(theta)
                        fx+=fg['scale']*(SPREAD+fg['radius']-distance)*math.sin(theta)
                        if y<fg['center'][1]:
                            fy+=fg['scale']*(SPREAD+fg['radius']-distance)*math.cos(theta)*-2
                            fx+=fg['scale']*(SPREAD+fg['radius']-distance)*math.sin(theta)*-2
                    elif x>fg['center'][0]:
                        fx+=fg['scale']*(SPREAD+fg['radius']-distance)*math.cos(theta)
                        fy+=fg['scale']*(SPREAD+fg['radius']-distance)*math.sin(theta)
                    else:
                        fx+=fg['scale']*(SPREAD+fg['radius']-distance)*math.cos(theta)*-1
                        fy+=fg['scale']*(SPREAD+fg['radius']-distance)*math.sin(theta)*-1
                if distance>(SPREAD+fg['radius']):
					fx+=0.0
					fy+=0.0
                    
        
        return fx, fy
def getGoalVector(x, y):
    distance = (((fg['center'][0]-x) ** 2 + (fg['center'][1]-y) ** 2) ** 0.5)//2
            if abs(fg['center'][0]-x)>abs(fg['center'][1]-y): 
                    
                theta= math.atan((fg['center'][0]-x)//(fg['center'][1]-y))   
            else: 
                theta= math.atan((fg['center'][1]-y)//(fg['center'][0]-x))
             
    if fg['type']=="pull":
                if distance<fg['radius']:
                    fx=0.0
                    fy=0.0
                    
                elif fg['radius']<=distance<=(SPREAD+fg['radius']):
                   if fg['center'][0]==x and y>fg['center'][1]:
       	   				fx=0
       	   				fy=fg['scale']*(distance-fg['radius'])*-1
                   elif fg['center'][0]==x and y<fg['center'][1]:
        				fx=0
        				fy=fg['scale']*(distance-fg['radius'])*1
                   elif fg['center'][1]==y and x<fg['center'][0]:
        				fx=fg['scale']*(distance-fg['radius'])*1
        				fy=0
                   elif fg['center'][1]==y and x>fg['center'][0]:
                        fx=fg['scale']*(distance-fg['radius'])*-1
                        fy=0 
                    
                   elif ((fg['center'][0]-x)==(fg['center'][1]-y)or(fg['center'][0]-x)==(fg['center'][1]-abs(y))) and x>fg['center'][0]:
                           fy=fg['scale']*(distance-fg['radius'])*math.cos(theta)*-1
                           fx=fg['scale']*(distance-fg['radius'])*math.sin(theta)*-1
                       
                   elif abs(fg['center'][0]-x)>abs(fg['center'][1]-y):
                        
                        fy=fg['scale']*(distance-fg['radius'])*math.cos(theta)
                        fx=fg['scale']*(distance-fg['radius'])*math.sin(theta)
                        if y>fg['center'][1]:
                            fy*=-1
                            fx*=-1
                   else:
                         
                        if x>fg['center'][0]and abs(fg['center'][0]-x)<abs(fg['center'][1]-y):
                            fx=fg['scale']*(distance-fg['radius'])*math.cos(theta)*-1
                            fy=fg['scale']*(distance-fg['radius'])*math.sin(theta)*-1
                        else:
                            fx=fg['scale']*(distance-fg['radius'])*math.cos(theta)
                            fy=fg['scale']*(distance-fg['radius'])*math.sin(theta)
                        
                    
                elif distance>(SPREAD+fg['radius']):
                    if fg['center'][0]==x and y>fg['center'][1]:
       	   				fx=0
       	   				fy=fg['scale']*-1
                    elif fg['center'][0]==x and y<fg['center'][1]:
                        fx=0
                        fy=fg['scale']*1
                    elif fg['center'][1]==y and x<fg['center'][0]:
                        fx=fg['scale']*1
                        fy=0
                    elif fg['center'][1]==y and x>fg['center'][0]:
                        fx=fg['scale']*-1
                        fy=0                    
                    
                    elif abs(fg['center'][0]-x)>abs(fg['center'][1]-y): 
                        if y>fg['center'][0]:
                            fy=fg['scale']*math.cos(theta)*-1
                            fx=fg['scale']*math.sin(theta)*-1
                    
                        else:
                            fy=fg['scale']*math.cos(theta)
                            fx=fg['scale']*math.sin(theta)
                    else:
                        if x>fg['center'][0]:
                            fx=fg['scale']*math.cos(theta)*-1
                            fy=fg['scale']*math.sin(theta)*-1
                    
                        else:
                            fx=fg['scale']*math.cos(theta)
                            fy=fg['scale']*math.sin(theta)
    return fx,fy
            
def getDirections(x,y):
    return getGoalVector(x,y)+getObsVectors(x,y)               
OBSTACLES = [((150.0, 150.0), (150.0, 90.0), (90.0, 90.0), (90.0, 150.0))]
'''((150.0, 210.0), (150.0, 150.0), (90.0, 150.0), (90.0, 210.0)),
  ((210.0, 150.0), (210.0, 90.0), (150.0, 90.0), (150.0, 150.0)),
   ((150.0, -90.0), (150.0, -150.0), (90.0, -150.0), (90.0, -90.0)),

    ((210.0, -90.0), (210.0, -150.0), (150.0, -150.0), (150.0, -90.0)), 
    ((150.0, -150.0), (150.0, -210.0), (90.0, -210.0), (90.0, -150.0)),
     ((-90.0, -90.0), (-90.0, -150.0), (-150.0, -150.0), (-150.0, -90.0)),
      ((-90.0, -150.0), (-90.0, -210.0), (-150.0, -210.0), (-150.0, -150.0)),
       ((-150.0, -90.0), (-150.0, -150.0), (-210.0, -150.0), (-210.0, -90.0)),
        ((-90.0, 150.0), (-90.0, 90.0), (-150.0, 90.0), (-150.0, 150.0)), 
        ((-90.0, 210.0), (-90.0, 150.0), (-150.0, 150.0), (-150.0, 210.0)), 
        ((-150.0, 150.0), (-150.0, 90.0), (-210.0, 90.0), (-210.0, 150.0)),
         ((10.0, 60.0), (10.0, -60.0), (-10.0, -60.0), (-10.0, 60.0))]
'''

OBSTACLESCALE=.1
GOALSCALE=.9        
FLAGS=[(-370,0),(0,-370),(370,0),(0,370)]
GOAL={'radius' : 2.5,'center' : (0,0), 'type' : "pull", 'scale' : .9} 

fieldGenerators = [flg1]

########################################################################
# Helper Functions

def initialize(WS,SP,OB,OS,GL,GR,GS,):
    OBSTACLES=OB
    SPREAD=SP
    WORLDSIZE=WS
    OBJECTSCALE=OS
    GOALSCALE=GS
    GOAL={'radius' : GR,'center' : GL, 'type' : "pull", 'scale' : GOALSCALE}
    obsRadiusAndCenter(OBSTACLES)

def obsRadiusAndCenter(tup):
    xmin=float("inf")
    xmax=float("-inf")
    ymin=float("inf")
    ymax=float("-inf")
    for pairs in tup:
        if pairs[0]>xmax:
            xmax=pairs[0]
        if pairs[0]<xmin:
            xmin=pairs[0]
        if pairs[1]>ymax:
            ymax=pairs[0]
        if pairs[1]<ymin:
            ymin=pairs[0]
    temp=((((xmax-xmin)**2+(ymax-ymin)**2)**.5)/2,((xmax-xmin)//2+xmin,(ymax-ymin)//2+ymin),"push")
    fg={'radius' : temp[0],'center' : temp[1], 'type' : temp[2], 'scale' : .01}
    print(fg)
    fieldGenerators.append(fg)
    return temp
        
      






    


