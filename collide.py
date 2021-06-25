def collide_actor_wall(_actor, _wall):
    _actor.bump()
    return 1
    
def collide_actor_actor(_a1, _a2):
    "Default collision - do nothing"
    return 1

def collide_actor_mine(_actor, _mine):
    _actor.bump(damage=25)
    _mine.die()
    return 1

def collide_bullet_actor(_bullet, _actor):
    _actor.bump(damage=_bullet.damage)
    if _actor.hitpoints==0:
        _bullet.shooter.killed_actor(_actor)
    _bullet.die()
    return 1

def collide_bullet_world(_bullet, _world, where):
    _bullet.die()
    return 1

def collide_mine_world(_mine, _world, where):
    "If a mine is layed outside the world boundaries - erase it"
    _mine.die()
    
def collide_actor_world(_actor, _world, where):
    _actor.bump()
    
def collide_mobile_actors(actor1, actor2):
    actor1.bump(damage=25)
    actor2.bump(damage=25)

def collide_mines(mine1, mine2):
    from misc import Explosion
    mine1.die()
    mine2.die()
    Explosion(center=mine1.rect.center, angle=mine1.angle, world=mine1.world)

def rev_args(_method):
    return lambda x,y: _method(y,x)

def get_dispatcher():
    "imports here (not at top of module) to avoid collision with World imports"
    from multimethods import Dispatch
    from world import World
    from actor import Actor
    from basicrobot import *
    from misc import *
    dispatch= Dispatch()
    #collide.add_rule((PlayerRobot, Collectible), collect)
    dispatch.add_rule((Actor, Actor), collide_actor_actor)

    #ImmobileActor to allow catching dropped Mine
    dispatch.add_rule((ImmobileActor, Wall), collide_actor_wall) 
    dispatch.add_rule((Wall, ImmobileActor), rev_args(collide_actor_wall))

    dispatch.add_rule((MobileActor, Mine), collide_actor_mine)    
    dispatch.add_rule((Mine, MobileActor), rev_args(collide_actor_mine))

    dispatch.add_rule((Mine, World, tuple), collide_mine_world)

    dispatch.add_rule((MobileActor, World, tuple), collide_actor_world)

    dispatch.add_rule((MobileActor, MobileActor), collide_mobile_actors)
    dispatch.add_rule((Mine, Mine), collide_mines)

    dispatch.add_rule((Bullet, World, tuple), collide_bullet_world)

    dispatch.add_rule((Bullet, BasicRobot), collide_bullet_actor)
    dispatch.add_rule((BasicRobot, Bullet), rev_args(collide_bullet_actor))
    
    return dispatch

