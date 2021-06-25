import math

from world import World
from util import *
from util_pygame import *

class ImmobileActor(SpriteActor):
    """A Immobile sprite class

    Can have a nonzero angle but better not, since zero angle won't cause rotate.
    """
    def __init__(self, location=(0,0), world=None, **props):
        props['angle'] = props.get('angle', 90)
        SpriteActor.__init__(self, location=location,
                             world=world, **props)

class MobileActor(ImmobileActor):
    """A sprite with angle and velocity that can move
    
    The undo step_back() is not accurate if updateRate changes
    updateRate is frame-rate, about 25 frame/sec depending on main loop idle-time.
    """
    def __init__(self, location=(0,0), velocity=50,
                 world=None, **props):
        ImmobileActor.__init__(self, location=location,
                             velocity = velocity, world=world, **props)
        self.updateRate=25 #in case a bump() precedes first tick()
        self.old_location = location

    def next_location(self, updateRate):
        VectorX,VectorY = (math.sin(math.radians(self.angle)) * self.velocity,
                           math.cos(math.radians(self.angle)) * self.velocity)
        x,y = self.location
        x += VectorX / updateRate
        y -= VectorY / updateRate
        return x,y

    def step_back(self):
        self.location= self.old_location
        """self.angle += 180
        self.location = self.next_location(self.updateRate)
        self.angle -= 180
        """
        
    def tick(self, updateRate):
        self.updateRate = updateRate
        self.old_location = self.location
        self.location= self.next_location(updateRate)

from misc import Explosion

class BasicRobot(MobileActor):
    """A dumb robot that goes in circles
    
    Can take damage of bump() until hitpoints is down to zero.
    """
    MAX_VELOCITY=100
    def __init__(self, location=(0,0), hitpoints=1, world=None, **props):
        MobileActor.__init__(self, location=location,
                             hitpoints = hitpoints, world=world, **props)
        self.world.send((self.id,"JOIN"))

    def take_damage(self, damage):
        self.hitpoints -= damage
        if self.hitpoints <= 0:
            Explosion(center=self.rect.center,angle=self.angle,world=self.world)
            self.die()

    def bump(self, damage=0):
        MobileActor.step_back(self)
        self.angle += 73.0
        if self.angle >= 360:
            self.angle -= 360
        if damage: self.take_damage(damage)

    def tick(self, updateRate):
        self.angle += 30.0 * (1.0 / updateRate)
        if self.angle >= 360:
            self.angle -= 360
        MobileActor.tick(self, updateRate)

