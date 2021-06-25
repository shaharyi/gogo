import stackless

import util

class Actor(object):
    """Abstract class for an actor.

    Noticable Services:
    a stackless-channel msg pump;
    List of all actors as the static dict "actors";
    """
    actors={}
    next_id=0

    def __init__(self, **props):
        self.world = None
        self.public = True
        self.physical = True
        self.id = Actor.next_id
        Actor.next_id += 1
        klass= self.__class__.__name__
        self.name = "%s#%d" %(klass, self.id)
        Actor.actors[self.id] = self
        self.channel = stackless.channel()
        for n,v in props.items():
            setattr(self, n, v)
        print 'loading', vars(self)
        self.processMessageMethod = self.defaultMessageAction
        stackless.tasklet(self.processMessage)()
  
    def processMessage(self):
        while 1:
            self.processMessageMethod(self.channel.receive())

    def defaultMessageAction(self,args):
        method_name= 'handle_'+args[1]
        method= getattr(self, method_name, None)
        if method is None:
            util.log('Unknown msg=%s for %s' % (args[1], self.name))
        else:
            method(args)

    def tick(self, *args):
        pass
        
    def die(self):
        self.world.send( (self.id,"KILLME") )
