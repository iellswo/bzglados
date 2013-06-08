# The Kalman Filter

import math
from numpy import matrix, identity

#######################################

# friction coeffient
C = 0.1

#######################################

class KalmanFilter():
    
    def __init__(self, noise):
        # starting values:
        self.mu_t = matrix('0; 0; 0; 0; 0; 0')
        self.E_t = matrix([[100, 0,   0,   0,   0,   0],
                          [0,   0.1, 0,   0,   0,   0],
                          [0,   0,   0.1, 0,   0,   0],
                          [0,   0,   0,   100, 0,   0],
                          [0,   0,   0,   0,   0.1, 0],
                          [0,   0,   0,   0,   0,   0.1]])
                              
        # constants:
        self.E_x = matrix([[0.1, 0,   0,   0,   0,   0],
                          [0,   0.1, 0,   0,   0,   0],
                          [0,   0,   80,  0,   0,   0],
                          [0,   0,   0,   0.1, 0,   0],
                          [0,   0,   0,   0,   0.1, 0],
                          [0,   0,   0,   0,   0,   80]])
        self.H = matrix([[1.0, 0, 0, 0, 0, 0], [0, 0, 0, 1.0, 0, 0]])
        self.E_z = matrix([[noise**2, 0], [0, noise**2]])

    def update(self, Z_next, D_t):
        F = matrix([[1, D_t, D_t**2/2, 0, 0, 0],
                   [0, 1,   D_t,       0, 0, 0],
                   [0, -C,  1,         0, 0, 0],
                   [0, 0, 0, 1, D_t, D_t**2/2],
                   [0,  0,  0,       0, 1, D_t],
                   [0, 0, 0, 0, -C, 1]])
                   
        thrice = (F * self.E_t * F.getT()) + self.E_x
        swap = self.H * thrice * self.H.getT() + self.E_z
        K_next = thrice * self.H.getT() * swap.getI()
        
        mu_next = F*self.mu_t + K_next * (Z_next - self.H * F * self.mu_t)
        
        minus = K_next * self.H
        s = int(math.sqrt(minus.size))
        E_next = (identity(s) - minus)*thrice
        
        self.mu_t = mu_next
        self.E_t = E_next
        
    def get_enemy_position(self):
        m = self.H * self.mu_t
        pos = (m[0, 0], m[0, 1])
        return pos
