bzglados
========

AI scripts for bzrflag game.

In order to make it useful you need bzrflag package.  Inside of a common directory clone the bzglados package, as well as bzrflag (git clone git://aml.cs.byu.edu/bzrflag.git)

The command line options for bzrflag can be found using the -h flag.

The pidgeons folder contains a few 'clay pidgeons', which can be used as target practice.

The utilities folder contains all of the utility code used by the various agents and at other stages in development and testing.

The agents:

glados.py:  Our final agent.  This is the competitive agent that will play a game of capture the flag.

gridagent.py: This agent uses a bayesian filter to filter out noise and explore the map to discover obstacles.

kalmanagent.py: Uses a kalman filter to filter out position noise given by the server for a tank.  The agent itself stands still and attempts to shoot a moving (or possibly still) target.  The pidgeons are great for testing this agent.

pfagent.py: Uses potential fields only to navigate the world and capture the flag.  Server must report obstacles for this agent to run.

searchagent.py: Uses various searches to find a path to the enemy flag.  Does not control tanks, just prints to the screen using gnuplot library.
