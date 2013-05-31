
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
SAMPLES = 30
# Change spacing by changing the relative length of the vectors.  It looks
# like scaling by 0.75 is pretty good, but this is adjustable:
VEC_LEN = 0.75 * WORLDSIZE / SAMPLES
# Animation parameters:
ANIMATION_MIN = 0
ANIMATION_MAX = 500
ANIMATION_FRAMES = 50

SPREAD=10


########################################################################
# Field and Obstacle Definitions

def generate_fields(x, y):
    att = [fg for fg in fieldGenerators if fg['type'] == "pull"]
    x1, y1 = generate_attractive_fields(x, y, att[0])
    x2, y2 = generate_repulsive_fields(x, y)
    x3, y3 = generate_tangental_fields(x, y)
    return (x1+x2+x3), (y1+y2+y3)
    #return (x1,y1)
    #return (x2,y2)
    #return (x3,y3)

def generate_attractive_fields(x, y, fg):
    
    fx = 0.0
    fy = 0.0
    
    # return the vector for this location
    distance = math.sqrt( (fg['center'][0] - x)**2 +  (fg['center'][1] - y)**2 )
    theta=math.atan2((fg['center'][1] - y), (fg['center'][0] - x))
    if distance<fg['radius']:
        fx = 0
        fx = 0
    elif fg['radius'] <= distance <= (SPREAD + fg['radius']):
        fx = fg['scale'] * (distance-fg['radius']) * math.cos(theta)
        fy = fg['scale'] * (distance-fg['radius']) * math.sin(theta)
    elif distance>(SPREAD+fg['radius']):
        fx = fg['scale'] * math.cos(theta)
        fy = fg['scale'] * math.sin(theta)
    
    return fx, fy
    
def generate_repulsive_fields(x, y):
    
    fx = 0.0
    fy = 0.0
    
    for fg in fieldGenerators:
        if fg['type'] == 'push':
            #print fg
            distance = math.sqrt( (fg['center'][0] - x)**2 +  (fg['center'][1] - y)**2 )
            theta=math.atan2((fg['center'][1] - y), (fg['center'][0] - x))
        
            if distance<fg['radius']:
                fx += -math.copysign(1000, math.cos(theta))
                fy += -math.copysign(1000, math.sin(theta))
            elif fg['radius'] <= distance <= (SPREAD + fg['radius']):
                fx += -fg['scale'] * (SPREAD + fg['radius'] - distance) * math.cos(theta)
                fy += -fg['scale'] * (SPREAD + fg['radius'] - distance) * math.sin(theta)
            elif distance>(SPREAD+fg['radius']):
                fx += 0.0
                fy += 0.0
            
    return fx, fy
    
def generate_tangental_fields(x, y):
    
    fx = 0.0
    fy = 0.0
    
    for fg in fieldGenerators:
        if fg['type'] == 'push':
            #print fg
            distance = math.sqrt( (fg['center'][0] - x)**2 +  (fg['center'][1] - y)**2 )
            theta=math.atan2((fg['center'][1] - y), (fg['center'][0] - x)) + math.pi/4
        
            if distance<fg['radius']:
                fx += -math.copysign(1000, math.cos(theta))
                fy += -math.copysign(1000, math.sin(theta))
            elif fg['radius'] <= distance <= (SPREAD + fg['radius']):
                fx += -fg['scale'] * (SPREAD + fg['radius'] - distance) * math.cos(theta)
                fy += -fg['scale'] * (SPREAD + fg['radius'] - distance) * math.sin(theta)
            elif distance>(SPREAD+fg['radius']):
                fx += 0.0
                fy += 0.0
            
    return fx, fy
    

'''
OBSTACLES=[((100.0, 42.4264068712), (142.426406871, 0.0), (100.0, -42.4264068712), (57.5735931288, 5.19573633741e-15)), ((-100.0, 42.4264068712), (-57.5735931288, 0.0), (-100.0, -42.4264068712), (-142.426406871, 5.19573633741e-15)), ((2.59786816871e-15, 142.426406871), (42.4264068712, 100.0), (2.59786816871e-15, 57.5735931288), (-42.4264068712, 100.0)), ((2.59786816871e-15, -57.5735931288), (42.4264068712, -100.0), (2.59786816871e-15, -142.426406871), (-42.4264068712, -100.0))]            
'''
OBSTACLES = [((150.0, 150.0), (150.0, 90.0), (90.0, 90.0), (90.0, 150.0)), ((150.0, 210.0), (150.0, 150.0), (90.0, 150.0), (90.0, 210.0)), ((210.0, 150.0), (210.0, 90.0), (150.0, 90.0), (150.0, 150.0)), ((150.0, -90.0), (150.0, -150.0), (90.0, -150.0), (90.0, -90.0)), ((210.0, -90.0), (210.0, -150.0), (150.0, -150.0), (150.0, -90.0)), ((150.0, -150.0), (150.0, -210.0), (90.0, -210.0), (90.0, -150.0)), ((-90.0, -90.0), (-90.0, -150.0), (-150.0, -150.0), (-150.0, -90.0)), ((-90.0, -150.0), (-90.0, -210.0), (-150.0, -210.0), (-150.0, -150.0)), ((-150.0, -90.0), (-150.0, -150.0), (-210.0, -150.0), (-210.0, -90.0)), ((-90.0, 150.0), (-90.0, 90.0), (-150.0, 90.0), (-150.0, 150.0)), ((-90.0, 210.0), (-90.0, 150.0), (-150.0, 150.0), (-150.0, 210.0)), ((-150.0, 150.0), (-150.0, 90.0), (-210.0, 90.0), (-210.0, 150.0)), ((10.0, 60.0), (10.0, -60.0), (-10.0, -60.0), (-10.0, 60.0))]


         
FLAGS=[(-370,0),(0,-370),(370,0),(0,370)]
flg1={'radius' : 2.5,'center' : (0,370), 'type' : "pull", 'scale' : 1}  
flg2={'radius' : 2.5,'center' : (0,-370), 'type' : "pull", 'scale' : .5}  
flg3={'radius' : 2.5,'center' : (370,0), 'type' : "pull", 'scale' : .5}  
flg4={'radius' : 2.5,'center' : (0,370), 'type' : "pull", 'scale' : .5}         

fieldGenerators = [flg1]

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
            ymax=pairs[1]
        if pairs[1]<ymin:
            ymin=pairs[1]
    temp=((float(((xmax-xmin)**2+(ymax-ymin)**2)**.5))/2,(float(xmax-xmin)/2+xmin,float(ymax-ymin)/2+ymin),"push")
    fg={'radius' : temp[0], 'center' : temp[1], 'type' : temp[2], 'scale' : .1}
    fieldGenerators.append(fg)
    #print fg

    return temp
        
      

def gpi_point(x, y, vec_x, vec_y):
    '''Create the centered gpi data point (4-tuple) for a position and
    vector.  The vectors are expected to be less than 1 in magnitude,
    and larger values will be scaled down.'''
    r = (vec_x ** 2 + vec_y ** 2) ** 0.5
    if r > 1:
        vec_x /= r
        vec_y /= r
    return (x - vec_x * VEC_LEN / 2, y - vec_y * VEC_LEN / 2,
            vec_x * VEC_LEN, vec_y * VEC_LEN)

def gnuplot_header(minimum, maximum):
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

def draw_line(p1, p2):
    '''Return a string to tell Gnuplot to draw a line from point p1 to
    point p2 in the form of a set command.'''
    x1, y1 = p1
    x2, y2 = p2
    return 'set arrow from %s, %s to %s, %s nohead lt 3\n' % (x1, y1, x2, y2)
    


def draw_obstacles(obstacles,flgs):
    '''Return a string which tells Gnuplot to draw all of the obstacles.'''
    s = 'unset arrow\n'

    for obs in obstacles:
        last_point = obs[0]
        for cur_point in obs[1:]:
            s += draw_line(last_point, cur_point)
            last_point = cur_point
        s += draw_line(last_point, obs[0])
        for flg in flgs:
            temp=(flg[0]+3,flg[1])
            temp2=(flg[0]-3,flg[1])
            s += draw_line(temp2, temp,)
            temp=(flg[0],flg[1]+3)
            temp2=(flg[0],flg[1]-3)
            s += draw_line(temp2, temp,)
    return s
    

    
def plot_field(function):
    '''Return a Gnuplot command to plot a field.'''
    s = "plot '-' with vectors head\n"

    separation = WORLDSIZE / SAMPLES
    end = WORLDSIZE / 2 - separation / 2
    start = -end

    points = ((x, y) for x in linspace(start, end, SAMPLES)
                for y in linspace(start, end, SAMPLES))

    for x, y in points:
        f_x, f_y = function(x, y)
        plotvalues = gpi_point(x, y, f_x, f_y)
        if plotvalues is not None:
            x1, y1, x2, y2 = plotvalues
            s += '%s %s %s %s\n' % (x1, y1, x2, y2)
    s += 'e\n'
    return s


########################################################################
# Plot the potential fields to a file

outfile = open(FILENAME, 'w')
print >>outfile, gnuplot_header(-WORLDSIZE / 2, WORLDSIZE / 2)
print >>outfile, draw_obstacles(OBSTACLES,FLAGS)

print >>outfile, plot_field(generate_fields)



########################################################################
# Animate a changing field, if the Python Gnuplot library is present

try:
    from Gnuplot import GnuplotProcess
except ImportError:
    print "Sorry.  You don't have the Gnuplot module installed."
    import sys
    sys.exit(-1)
    
    #this for loop populates the list of fieldGenerators -Josh
for obs in OBSTACLES:
    obsRadiusAndCenter(obs)
    

    
forward_list = list(linspace(ANIMATION_MIN, ANIMATION_MAX, ANIMATION_FRAMES/2))
backward_list = list(linspace(ANIMATION_MAX, ANIMATION_MIN, ANIMATION_FRAMES/2))
anim_points = forward_list + backward_list

gp = GnuplotProcess(persist=True)#this starts the GP process and makes it a persistent file so it doesn't close automatically
gp.write(gnuplot_header(-WORLDSIZE / 2, WORLDSIZE / 2))#sets up the initialization
gp.write(draw_obstacles(OBSTACLES,FLAGS))#draws the obstacles and now flags -josh


gp.write(plot_field(generate_fields))


