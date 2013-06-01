#!/usr/bin/env python

import OpenGL
import time
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from numpy import zeros, transpose
class MapBuilder:
    
    def __init__(self,h,w):
        self.init_window(h,w)
        
    def draw_grid(self):
        # This assumes you are using a numpy array for your grid
        self.width, self.height = self.grid.shape
        glRasterPos2f(-1, -1)
        glDrawPixels(self.width, self.height, GL_LUMINANCE, GL_FLOAT, self.grid)
        glFlush()
        glutSwapBuffers()

    def update_grid(self,new_grid):
        self.grid = transpose(new_grid)

    def init_window(self, width, height):
        global window
        self.width=width
        self.height=height
        self.grid = zeros((self.width, self.height))
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

