import os, sys

import pygame
from pygame.locals import *
if not pygame.font:  print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

import actor
import util
from renderer import *

def spritecollide(sprite, group, dokill):
    """util_pygame.spritecollide(sprite, group, dokill) -> list
       collision detection between sprite and group

       A rewrite of pygame.sprite.spritecollide by Shahar 
       in order to collide with collide_rect vs rect.
       Given a sprite and a group of sprites, this will
       return a list of all the sprites that intersect
       the given sprite.
       all sprites must have a "collide_rect" value, which is a
       rectangle of the sprite area. if the dokill argument
       is true, the sprites that do collide will be
       automatically removed from all groups."""
    crashed = []
    if dokill:
        for s in group.sprites():
            if sprite.rect.colliderect(s.collide_rect):
                s.kill()
                crashed.append(s)
    else:
        for s in group:
            if sprite.rect.colliderect(s.collide_rect):
                crashed.append(s)
    return crashed

class SpriteActor(actor.Actor, pygame.sprite.Sprite):
    """A special Actor that does not JOIN the World.
    Thus, it's tick() isn't called by World.
    It is inherited by normal actors who are active on the Server.
    On the Client, this is the only type of actor;
    It can only be rendered, it isn't not really alive.
    """
    sprite_group= pygame.sprite.Group()
    sprites={}

    def __init__(self, **props):
        pygame.sprite.Sprite.__init__(self)
        actor.Actor.__init__(self, **props)
        if not hasattr(self, 'image_file'):
            self.image_file = self.__class__.__name__ + util.IMAGE_EXT            
        if not hasattr(self, 'renderer_name'):
            self.renderer_name = 'SpriteActorRenderer'
        self.renderer =  Renderers.get(self.renderer_name)
        self.add(SpriteActor.sprite_group)
        SpriteActor.sprites[self.id] = self
        #call without transparenct colorkey, since the image defines one
        self.orig_image, self.rect = load_image(self.image_file)#,-1)#(0xf3,0x0a,0x0a))
        self.image = self.orig_image
        self.collide_rect= pygame.Rect(self.rect)

    @staticmethod
    def get_sprite(actorProps):
        if SpriteActor.sprites.has_key(actorProps['id']):
            sprite= SpriteActor.sprites[actorProps['id']]
            #print actorProps.items()
            for n,v in actorProps.items():
                setattr(sprite, n, v)  #actually for updating location,angle, image-frame#
        else:
            sprite= SpriteActor(**actorProps)
        return sprite

    def update(self, *args):
        """Called by Group.update(args)
        Calls the specific actor-renderer. Usually SpriteActorRenderer.
        """
        self.renderer.render(self, *args)

images={}

def load_image(name, colorkey=None):
    "colorkey is the tranparency color"
    if images.has_key(name):
        return images[name], images[name].get_rect()
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        #RLEACCEL= slower to modify - problem to rotate. faster to blit on non-accel display
        image.set_colorkey(colorkey)#, RLEACCEL)
        print 'colorkey on'
    images[name]= image
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', wav
        raise SystemExit, message
    return sound
