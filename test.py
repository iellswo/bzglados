import math

def normalize_angle(angle):
    """Make any angle be between +/- pi."""
    angle -= 2 * math.pi * int (angle / (2 * math.pi))
    if angle <= -math.pi:
        angle += 2 * math.pi
    elif angle > math.pi:
        angle -= 2 * math.pi
    return angle
    
print normalize_angle(3*math.pi)
