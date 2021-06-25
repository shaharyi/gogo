import time
from basicrobot import ImmobileActor, MobileActor

class Explosion(ImmobileActor):
    def __init__(self, **props):
        ImmobileActor.__init__(self, time=0.0, physical=False, **props)
        self.location = self.center[0]-self.rect.w/2, self.center[1]-self.rect.h/2
        self.world.send((self.id,"JOIN"))
    def tick(self, updateRate):
        self.time = self.time or time.time()   #init if zero
        if time.time() >= self.time + 3.0:
            self.die()

class Score(ImmobileActor):
    def __init__(self,world=None,**props):
        ImmobileActor.__init__(self, world=world, value=0, renderer_name='ScoreRenderer', **props)
        self.world.send((self.id,"JOIN"))

class Mine(ImmobileActor):
    def __init__(self,**props):
        ImmobileActor.__init__(self, hitpoints=1, **props)
        self.location = self.center[0]-self.rect.w/2, self.center[1]-self.rect.h/2
        self.world.send((self.id,"JOIN"))        
    def bump(self): #dropped over a wall
        self.die()

class Bullet(MobileActor):
    def __init__(self,**props):
        MobileActor.__init__(self, damage=1, hitpoints=1,velocity=150, **props)
        self.location = self.center[0]-self.rect.w/2, self.center[1]-self.rect.h/2
        self.world.send((self.id,"JOIN"))
    def bump(self, damage=0): #hit a mine or a wall
        self.die()

class Wall(ImmobileActor):
    def __init__(self, angle=0, **props):
        ImmobileActor.__init__(self, angle=angle, **props)
        self.world.send((self.id,"JOIN"))        
class VWall(Wall):
    def __init__(self, angle=0, **props):
        Wall.__init__(self, angle=angle, **props)        
class HWall(Wall):
    def __init__(self, angle=0, **props):
        Wall.__init__(self, angle=angle, **props)

