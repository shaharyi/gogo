import pygame.font

class SpriteActorRenderer:
    """Generic Sprite pre-renderer    
    Doesn't do any real rendering but prepares the sprite for it.
    """
    def render(self, _sprite, *args):
        if _sprite.angle != 0:
            _sprite.image= pygame.transform.rotate(_sprite.orig_image,-_sprite.angle)
        loc=offs=[0,0]
        for d in (0,1):
            offs[d]= _sprite.image.get_rect().center[d] - _sprite.orig_image.get_rect().center[d]
            loc[d] = int(_sprite.location[d]-offs[d])
        #_sprite.rect = _sprite.image.get_rect()
        _sprite.rect.topleft = loc
        _sprite.collide_rect = pygame.Rect(_sprite.image.get_rect())
        _sprite.collide_rect.topleft = loc  #_sprite.location
   
class ScoreRenderer(SpriteActorRenderer):
  """Renders the Score text for a player on the Score-sprite image Surface.
  Warning: can't instanciate before pygame.init (or specifically font.init)
  """
  def __init__(self):
      self.showing=None
      self.font = pygame.font.SysFont('serif', 24)
  def render(self, _score, *args):
      _score.rect.topleft = _score.location
      if _score.value != self.showing:
          #render(text, antialias, color (RGBA), background=None): return Surface
          text = self.font.render("%5d" % _score.value, 1, (0,0,0,0),(200, 200, 200))
          _score.image.blit(text, (0,0)) #in location (0,0) 
          self.showing = _score.value
      
class Renderers:
    """Holds the dict of Renderers Singletons.       
    Instanciated only after pygame.init in Display, so that Font gets init()ed.
    """
    renderers={}
    def __init__(self):
       for name,klass in globals().iteritems():
            if name.endswith("Renderer"):
                Renderers.renderers[name] = eval(name+'()')                
    @staticmethod
    def get(name):        
        return Renderers.renderers.get(name, None)
        
