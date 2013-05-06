bzglados
========

AI scripts for bzrflag game.

In order to make it useful you need bzrflag package.  Inside of a common directory clone
the bzglados package, as well as bzrflag (git clone git://aml.cs.byu.edu/bzrflag.git)

Pull the bzagents directory out of bzrflag into the parent.

Make a rungame.sh script in the parent directory.  Starting settings:

./bzrflag/bin/bzrflag --world=bzrflag/maps/four_ls.bzw --friendly-fire --red-port=50100 --green-port=50101 --purple-port=50102 --blue-port=50103 $@ &
sleep 2
python bzagents/agent0.py localhost 50100 &
python bzagents/agent0.py localhost 50101 &
python bzagents/agent0.py localhost 50102 &
python bzagents/agent0.py localhost 50103 &


Changing the lines with the agents with change what script will govern that team.

Maps can be changed by selecting different maps from bzrflag/mapss
