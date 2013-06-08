import OpenGL
import time
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from numpy import zeros, transpose
class drawUtil:
    
    def __init__(self,h,w):
        self.init_window(h,w)
        self.blank=[0.0,0.0,0.0]
        self.path=[]
        self.height=h
        self.width=w
        self.nofollow=None
        
        self.previous=None
        self.friendly=None
        self.target=None
    
    def to_canvas_space(self, coord):
        x,y=coord
        x=int(x)
        y=int(y)
        
        return x+(self.width/2), y+(self.height/2)
    
    def draw_block(self, coord,color,previous_coord):
        for i in range(y-4,y+3):
            if i>self.height:
                break
            if i<-1*self.height:
                i=-1*self.height
            for j in range(x-4,x+3):
                if j>self.width:
                    break
                if j<-1*self.width:
                    i=-1*self.width
                self.grid[i][j]=color
        if previous_coord:
            x,y=self.to_canvas_space(previous_coord)
            for i in range(y-4,y+3):
                if i>self.height:
                    break
                if i<-1*self.height:
                    i=-1*self.height
                for j in range(x-4,x+3):
                    if j>self.width:
                        break
                    if j<-1*self.width:
                        i=-1*self.width
                        self.grid[i][j]=self.blank
            
    def add_enemy_tank(self, coord):
        enemy_color=[1.0,0.0,0.0]
        enemy_previous=[0.6,0.0,0.5]
        x,y=self.to_canvas_space(coord)
        for i in range(y-4,y+3):
            if i>self.height:
                break
            if i<-1*self.height:
                i=-1*self.height
            for j in range(x-4,x+3):
                if j>self.width:
                    break
                if j<-1*self.width:
                    i=-1*self.width
                self.grid[i][j]=enemy_color
        if self.previous:
            x,y=self.to_canvas_space(self.previous)
            for i in range(y-4,y+3):
                if i>=self.height:
                    break
                if i<-1*self.height:
                    i=-1*self.height
                for j in range(x-4,x+3):
                    if j>=self.width:
                        break
                    if j<-1*self.width:
                        i=-1*self.width
                    if (y-2)<i<(y+2) and (x-2)<j<(x+2):
                        self.grid[i][j]=enemy_previous
                    else:
                        self.grid[i][j]=self.blank
        self.path.append(coord)
        if len(self.path)>10:
            x,y=self.to_canvas_space(self.path[0])
            for i in range(y-4,y+3):
                if i>=self.height:
                    break
                if i<-1*self.height:
                    i=-1*self.height
                for j in range(x-4,x+3):
                    if j>=self.width:
                        break
                    if j<-1*self.width:
                        i=-1*self.width
                    self.grid[i][j]=self.blank
            self.path=self.path[1:]
            
        self.previous=coord
        
        
    def add_shooting_tank(self, coord):
        friendly_color=[0,0,1]
        x,y=self.to_canvas_space(coord)
        draw_block(coord,friendly_color,self.friendly)
        self.friendly=coord
    
    def add_nofollow_tank(self, coord):
        nofollow_color=[1,1,1]
        x,y=self.to_canvas_space(coord)
        for i in range(y-4,y+3):
            if i>=self.height:
                break
            if i<-1*self.height:
                i=-1*self.height
            for j in range(x-4,x+3):
                if j>=self.width:
                    break
                if j<-1*self.width:
                    i=-1*self.width
                self.grid[i][j]=nofollow_color
        if self.nofollow:
            x,y=self.to_canvas_space(self.nofollow)
            for i in range(y-4,y+3):
                for j in range(x-4,x+3):
                    self.grid[i][j]=self.blank
        self.nofollow=coord
        
    def add_shot(self, coord):
        shot_color=[0,1,0]
        x,y=self.to_canvas_space(coord)
        print coord, "coord"
        
        
        x=int(x)
        y=int(y)
        print (x,y), "changed"
        
        for i in range(y-3,y+4):
            if i>=self.height:
                break
            if i<-1*self.height:
                i=-1*self.height
        
            self.grid[i][x]=shot_color
        for j in range(x-3,x+4):
            if j>=self.width:
                break
            if j<-1*self.width:
                j=-1*self.width
            self.grid[y][j]=shot_color
        if self.target:
            x,y=self.to_canvas_space(self.target)
            for i in range(y-3,y+4):
                if i>=self.height:
                    break
                if i<-1*self.height:
                    i=-1*self.height
                
                    i=-1*self.width
                self.grid[i][x]=self.blank
            for j in range(x-3,x+4):
                if j>=self.width:
                    break
                if j<-1*self.width:
                    j=-1*self.width
                self.grid[y][j]=self.blank
        self.target=coord
            
        
                
            
        
    def draw_grid(self):
        # This assumes you are using a numpy array for your grid
        self.width = len(self.grid)
        self.height = len(self.grid)
        glRasterPos2f(-1, -1)
        glDrawPixels(self.width, self.height, GL_RGB, GL_FLOAT, self.grid)
        glFlush()
        glutSwapBuffers()

    def update_grid(self,new_grid):
        self.grid = new_grid

    def init_window(self, width, height):
        global window
        self.width=width
        self.height=height
        c=[0.0,0.0,0.0]
        a=[]
        for i in range(0,self.height):
            a.append([])
            for j in range(0,self.width):
                a[i].append(c)
        
        self.grid = a
        glutInit(())
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(20, 20)
        window = glutCreateWindow("Grid filter")
        glutDisplayFunc(self.draw_grid)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def hang(self):
        glutMainLoop()

