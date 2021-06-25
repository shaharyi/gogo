import time , math
from basicrobot import MobileActor
from misc import Mine,Explosion

class MinedropperRobot(MobileActor):
    def __init__(self,location=(0,0),angle=135,velocity=1,
                 hitpoints=20,world=None, **props):
        MobileActor.__init__(self, **props)
        self.location = location
        self.angle = angle
        self.delta = 0.0
        self.height=32.0
        self.width=32.0
        self.deltaDirection = "up"
        self.nextMine = 0.0
        self.velocity = velocity
        self.hitpoints = hitpoints
        self.world = world
        self.world.send((self.id,"JOIN"))

    def tick(self,updateRate):
        MobileActor.tick(self, updateRate)
        if self.deltaDirection == "up":
            self.delta += 60.0 * (1.0 / updateRate)
            if self.delta > 15.0:
                self.delta = 15.0
                self.deltaDirection = "down"
        else:
            self.delta -= 60.0 * (1.0 / updateRate)
            if self.delta < -15.0:
                self.delta = -15.0
                self.deltaDirection = "up"
        if self.nextMine <= time.time():
            self.nextMine = time.time() + 1.0
            mineX,mineY = (self.location[0] + (self.width / 2.0) ,
                            self.location[1] + (self.width / 2.0))

            mineDistance = (self.width / 2.0 ) ** 2
            mineDistance += (self.height / 2.0) ** 2
            mineDistance = math.sqrt(mineDistance)

            VectorX,VectorY = (math.sin(math.radians(self.angle + self.delta)),
                                math.cos(math.radians(self.angle + self.delta)))
            VectorX,VectorY = VectorX * mineDistance,VectorY * mineDistance
            x,y = self.location
            x += self.width / 2.0
            y += self.height / 2.0
            x -= VectorX
            y += VectorY
            Mine( center=(x,y), world=self.world)            
        self.angle += self.delta
        
    def bump(self, damage=0):
        self.angle += 73.0
        if self.angle >= 360:
            self.angle -= 360
        self.take_damage(damage)
            
    def take_damage(self, damage):
        self.hitpoints -= damage
        if self.hitpoints <= 0:
            Explosion(center=self.rect.center,angle=self.angle,world=self.world)
            self.die()

