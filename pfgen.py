
#!/usr/bin/env python
'''This is a demo on how to use Gnuplot for potential fields.  We've
intentionally avoided "giving it all away."
'''


from __future__ import division 
from itertools import cycle
import math

class PFGEN:
    
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
    def __init__(self,WS,SP,OB,OS,GL,GR,GS,):
        self.spread=SP
        self.worldSize=WS
        self.obsScale=OS
        self.goal={'radius' : GR,'center' : GL, 'type' : "pull", 'scale' : GS}
        self.obstacles=OB
        self.fieldGenerators = []
        self.obsRadiusAndCenter(OB)

    def update(SP,OS,GS,GL,GR,GO):
        self.spread=SP
        self.obsScale=OS
        elf.goal={'radius' : GR,'center' : GL, 'type' : "pull", 'scale' : GS}
        
   
    # Size of the world (one of the "constants" in bzflag):
    WORLDSIZE = 800
    # How many samples to take along each dimension:
    SAMPLES = 25
    # Change spacing by changing the relative length of the vectors.  It looks
    # like scaling by 0.75 is pretty good, but this is adjustable:
    VEC_LEN = 0.75 * WORLDSIZE / SAMPLES

    spread=30


    ########################################################################
    # Field and Obstacle Definitions


        #this determines our arrow at the point x y I've added the attractive field case
     
       
    def generate_repulsive_fields(x, y):
        
        fx = 0.0
        fy = 0.0
        
        for fg in self.fieldGenerators:
            if fg['type'] == 'push':
                #print fg
                distance = math.sqrt( (fg['center'][0] - x)**2 +  (fg['center'][1] - y)**2 )
                theta=math.atan2((fg['center'][1] - y), (fg['center'][0] - x))
            
                if distance<fg['radius']:
                    fx += -math.copysign(1000, math.cos(theta))
                    fy += -math.copysign(1000, math.sin(theta))
                elif fg['radius'] <= distance <= (spread + fg['radius']):
                    fx += -fg['scale'] * (spread + fg['radius'] - distance) * math.cos(theta)
                    fy += -fg['scale'] * (spread + fg['radius'] - distance) * math.sin(theta)
                elif distance>(spread+fg['radius']):
                    fx += 0.0
                    fy += 0.0
                
        return fx, fy
    def generate_attractive_fields(x, y, fg):
        
        fx = 0.0
        fy = 0.0
        
        # return the vector for this location
        distance = math.sqrt( (fg['center'][0] - x)**2 +  (fg['center'][1] - y)**2 )
        theta=math.atan2((fg['center'][1] - y), (fg['center'][0] - x))
        if distance<fg['radius']:
            fx = 0
            fx = 0
        elif fg['radius'] <= distance <= (spread + fg['radius']):
            fx = fg['scale'] * (distance-fg['radius']) * math.cos(theta)
            fy = fg['scale'] * (distance-fg['radius']) * math.sin(theta)
        elif distance>(spread+fg['radius']):
            fx = fg['scale'] * math.cos(theta)
            fy = fg['scale'] * math.sin(theta)
        
        return fx, fy

    def generate_fields(x, y):
        att = [fg for fg in self.fieldGenerators if fg['type'] == "pull"]
        x1, y1 = generate_attractive_fields(x, y, att[0])
        x2, y2 = generate_repulsive_fields(x, y)
        return (x1+x2), (y1+y2)
                  
    
    '''((150.0, 150.0), (150.0, 90.0), (90.0, 90.0), (90.0, 150.0)),
    ((150.0, 210.0), (150.0, 150.0), (90.0, 150.0), (90.0, 210.0)),
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

    

    ########################################################################
    # Helper Functions

   

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
        self.fieldGenerators.append(fg)
        return temp
            
          






        


