import sys, time
import pygame
import pygame.locals
import stackless

from actor import Actor
from util_pygame import *
from util  import myvars
from renderer import *

class Display(Actor):
    """Use Pygame to show the graphics and get input.

    Respon:
    Whenever a WORLD_STATE msg is received, refresh the screen to render the actors anew.
    
    Collab:
    Display only communicate with its world.
    Its world is World in Server-app, or Client in Client-app.   
    Forward Pygame input to World.
    """    
    def __init__(self,world):
        Actor.__init__(self)
        self.public= False
        self.world = world
        self.sprite_group = pygame.sprite.RenderPlain()
        pygame.init()
        Renderers()
        self.screen= pygame.display.set_mode((496,496))
        #self.screen = pygame.display.get_surface()        
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((200, 200, 200))        
        pygame.display.set_caption("Actor Demo")
        self.world.send((self.id,"JOIN",myvars(self)))
        
    def defaultMessageAction(self,args):
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg == "WORLD_STATE":
            cp = msgArgs[1]
            if cp:
                print "Display WORLD_STATE", time.time() - cp
            self.updateDisplay(msgArgs)
        else:
            print "DISPLAY UNKNOWN MESSAGE", args
            
    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                self.world.send((self.id, "KILLME"))
                sys.exit(0)
            elif (event.type==pygame.KEYDOWN and event.key==pygame.K_RETURN):
                self.world.send((self.id, 'NEW_PLAYER', myvars(self)))
            elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                self.world.send((self.id, "INPUT", event.type, event.key, time.time()))

    def updateDisplay(self,msgArgs):
        self.process_input()
        self.screen.blit(self.background, (0,0))
        worldState = msgArgs[0]
        self.sprite_group.empty()
        for id, props in worldState.actors:
            sprite= SpriteActor.get_sprite(props)
            self.sprite_group.add(sprite)
        self.sprite_group.update()
        self.sprite_group.draw(self.screen)
        pygame.display.flip()


