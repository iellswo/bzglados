from bzrc import BZRC

bzrc = BZRC('localhost', 50100)

constants = bzrc.get_constants()

print 'constants', constants

obstacles = bzrc.get_obstacles()

print 'obstacles', obstacles

bzrc.close()
