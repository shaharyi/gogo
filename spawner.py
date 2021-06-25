import random, time
from basicrobot import *
from minedropperrobot import *

class Spawner(ImmobileActor):
    def __init__(self,location=(0,0),world=None,**props):
        ImmobileActor.__init__(self,**props)
        self.location= location
        self.time= 0.0
        self.world= world
        self.angle= 0
        self.velocity= 0
        self.height= 32.0
        self.width= 32.0
        self.hitpoints= 1
        self.physical= False
        self.robots = []
        for name,klass in globals().iteritems():
            if name.endswith("Robot"):
                self.robots.append(klass)
        self.world.send((self.id,"JOIN"))

    def tick(self, updateRate):    
        if self.time == 0.0:
            self.time = time.time() + 0.5 # wait 1/2 second on start
        elif time.time() >= self.time: # every five seconds
            self.time = time.time() + 5.0
            angle = random.random() * 360.0
            velocity = random.random() * 100.0 + 1
            newRobot = random.choice(self.robots)
            newRobot(location=self.location,angle=angle,velocity=velocity,world=self.world)

