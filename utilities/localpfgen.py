
#!/usr/bin/env python
'''This is a demo on how to use Gnuplot for potential fields.  We've
intentionally avoided "giving it all away."
'''


from __future__ import division 
from itertools import cycle
import math

class PFGEN:
    
    
    def __init__(self, WS, SP, OS ):
        """Initialize variables"""
        self.spread=SP
        self.worldSize=float(WS)
        self.obsScale=OS
        
        
        self.fieldGenerators = []
        

    def update(self, GL, GR, GS):
        self.goal={'radius' : float(GR),'center' : GL, 'type' : "pull", 'scale' : float(GS)}
        
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


    def generate_fields(self, x, y, grid):
        
        x1, y1 = self.generate_attractive_fields(x, y, self.goal)
        
        x2, y2 =self.use_grid(grid,x,y)
        
        return (x+x1+x2), (y+y1+y2)


    def use_grid(self, grid, x, y):
         
        if x < (-self.worldSize/2)+50 or y < (-self.worldSize/2)+50 or x > (self.worldSize/2-51) or y > (self.worldSize/2-51):
           
            return 0,0

        #the array containing the number of occupied in each quadrant
        
        quadrant=[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        
        #the array containing the aproximate center point of each quadrant
        
        center=[
        [x-(len(grid)/3),y+(len(grid)/3)],[x,y+(len(grid)/3)],[x+(len(grid)/3),y+(len(grid)/3)],
        [x-(len(grid)/3),y]              ,[x,y]              ,[x+(len(grid)/3),y],
        [x-(len(grid)/3),y-(len(grid)/3)],[x,y-(len(grid)/3)],[x+(len(grid)/3),y-(len(grid)/3)]
        ]

        ocupiedVal = 1
        #this loop populates the array 'quadrant' with number of occupied cells
        for i in range(0,len(grid)):
            for j in range(0,len(grid)):
                
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

        for q in range(0,len(quadrant)):
            if not q==4:
                distance = math.sqrt( (center[q][0] - x)**2 +  (center[q][1] - y)**2 )
                theta = math.atan2((center[q][1] - y), (center[q][0] - x))
                #rfx += -math.copysign(50, math.cos(theta))*  (float(quadrant[q])/(float(len(grid))/float(3))**2)
                #rfy += -math.copysign(50, math.sin(theta))*  (float(quadrant[q])/(float(len(grid))/float(3))**2)
                rfx += -self.obsScale * (float(quadrant[q])/(len(grid)**2/9.0)) * (len(grid)*math.sqrt(2)/2 - distance) * math.cos(theta)
                rfy += -self.obsScale * (float(quadrant[q])/(len(grid)**2/9.0)) * (len(grid)*math.sqrt(2)/2 - distance) * math.sin(theta)
        return rfx, rfy





        


