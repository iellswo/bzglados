
#!/usr/bin/env python
'''This is a demo on how to use Gnuplot for potential fields.  We've
intentionally avoided "giving it all away."
'''


from __future__ import division 
from itertools import cycle
import math

class PFGEN:
    
    
    def __init__(self, WS, SP, OS, ):
        """Initialize variables"""
        self.spread=SP
        self.worldSize=WS
        self.obsScale=OS
        
        
        self.fieldGenerators = []
        

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
                  
    
   

    ########################################################################
    # Helper Functions

  
    
    def use_grid(self, grid,x,y,gx,gy,ocupiedVal):
         #print x
        if x < (-self.worldSize/2)+50 or y < (-self.worldSize/2)+50 or x > (self.worldSize/2-51) or y > (self.worldSize/2-51):
            #print "x in function="+str(x)+"y in function="+str(y)+""
            return 0,0

        ocupiedVal=.9
        spread=10
       
        goalRadius=2.5
        goalScale=1
        fx = 0.0
        fy = 0.0
        
        
        distance = math.sqrt( (gx - x)**2  +  (gy - y)**2 )
        theta = math.atan2((gy - y), (gx - x))
        if distance < goalRadius:
            fx = 0
            fx = 0
        elif goalRadius <= distance <= (spread + goalRadius):
            fx = goalScale * (distance-goalRadius) * math.cos(theta)
            fy = goalScale * (distance-goalRadius) * math.sin(theta)
        elif distance>(spread+goalRadius):
            fx = goalScale * math.cos(theta)
            fy = goalScale * math.sin(theta)
        
        #the array containing the number of occupied in each quadrant
        quadrant=[0,0,0,0,0,0,0,0,0]
        #the array containing the aproximate center point of each quadrant
        center=[
        [x-(len(grid)/3),y+(len(grid)/3)],[x,y+(len(grid)/3)],[x+(len(grid)/3),y+(len(grid)/3)],
        [x-(len(grid)/3),y]              ,[x,y]              ,[x+(len(grid)/3),y],
        [x-(len(grid)/3),y-(len(grid)/3)],[x,y-(len(grid)/3)],[x+(len(grid)/3),y-(len(grid)/3)]
        ]
        tallie=0
        #this loop populates the array 'quadrant' with number of occupied cells
        for i in range(0,len(grid)):
            for j in range(0,len(grid)):
                tallie+=1
                if j < len(grid)/3:
                    if i < len(grid)/3:
                        #print("xy:"+str(i)+" , "+str(j)+"\n")
                        if grid[j][i]>=ocupiedVal:
                            quadrant[0]+=1
                
                    elif i < 2*(len(grid)/3):
                        if grid[j][i]>=ocupiedVal:
                            quadrant[1]+=1
                    
                    else:
                        if grid[j][i]>=ocupiedVal:
                            quadrant[2]+=1
                        
                elif j < 2*(len(grid)/3):
                    if i < len(grid)/3:
                        if grid[j][i]>=ocupiedVal:
                            quadrant[3]+=1
                        
                    elif i < 2*(len(grid)/3):
                        if grid[j][i]>=ocupiedVal:
                            quadrant[4]+=1
                    
                    else:
                        if grid[j][i]>=ocupiedVal:
                            quadrant[5]+=1
                    
                elif j<(len(grid)): 
                    if i < len(grid)/3:
                        if grid[j][i]>=ocupiedVal:
                            quadrant[6]+=1
                            
                    elif i < 2*(len(grid)/3):
                        if grid[j][i]>=ocupiedVal:
                            quadrant[7]+=1
                        
                    else:
                        if grid[j][i]>=ocupiedVal:
                            quadrant[8]+=1
            q=0
            rfx=0
            rfy=0
            objScale=.75
            # we might be able use shrinkCase if we can verify that we have 2 strong quadrands surounding a weaker one in the direction we should go.
            # this would scale rfx or rxy based on wether we can deduce the likely hood of a path
            shrinkCase=1;
            
            
            for q in range(0,len(quadrant)):
                if not q==4:
                    distance = math.sqrt( (center[q][0] - x)**2 +  (center[q][1] - y)**2 )
                    theta = math.atan2((center[q][1] - y), (center[q][0] - x)) + math.pi/4
            # i'm thinking since this is tangential
               
                #if q%2==1:
                
                    rfx += -math.copysign(50, math.cos(theta))*  (float(quadrant[q])/(float(len(grid))/float(3))**2)
                    rfy += -math.copysign(50, math.sin(theta))*  (float(quadrant[q])/(float(len(grid))/float(3))**2)
                #else:
                '''
                rfx += -objScale * 2 * (spread + (((len(grid)/3)/2)**2+((len(grid)/3)/2)**2)**.5  - distance) * math.cos(theta) *  (float(quadrant[q])/(float(len(grid))/float(3)))
                rfy += -objScale * 2 * (spread + (((len(grid)/3)/2)**2+((len(grid)/3)/2)**2)**.5  - distance) * math.sin(theta) *  (float(quadrant[q])/(float(len(grid))/float(3)))
                '''

           
    #print "returning: "+str(fx+rfx*shrinkCase)+" "+str(fx+rfx*shrinkCase)+" "+str(quadrant)+" "
        return fx+rfx*shrinkCase, fy+rfy*shrinkCase
                            
                            
                        

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
          






        


