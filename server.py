import sys,time,cPickle,struct
import stackless

import stacklesssocket as socket

from util import myvars
import world
from actor import Actor
from playeractor import PlayerActor
from basicrobot import BasicRobot
from spawner import Spawner
from misc import *
import display

class Server(Actor):
    """Server app.

    Respon:
    Create World.
    Create initial actors eg Spawner and Walls.
    
    Collab:
    Forward Client packets (eg INPUT) to World, which dispatches them (eg to PlayerActor)
    Forward WORLD_STATE msgs (sent from World) to Clients, which forwards them to Display.
    """
    def __init__(self, conn, udp_port, use_mcast=False):
        Actor.__init__(self)
        self.public= False
        self.clients = {}
        # Create an INET, STREAMing socket
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to an addres, and a port
        self.serversocket.bind(conn)
        # Become a server socket
        self.serversocket.listen(5)
        stackless.tasklet(self.acceptConn)()

        self.playerIDs = {}
        self.name = 'server' # gethostbyname(gethostname())  #name=IP
        self.mcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.mcast_port = udp_port
        if use_mcast:
            self.mcast_group = '225.0.0.250'
            ttl = struct.pack('b', 1)               # Time-to-live
            self.mcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        self.worldChannel = world.World._singleton.channel
        self.disp = display.Display(self.worldChannel)
        """        
        HWall(location=(168,120), world=self.worldChannel) # 32x8 wall
        HWall(location=(200,120), world=self.worldChannel) # 32x8 wall
        HWall(location=(232,120), world=self.worldChannel) # 32x8 wall
        HWall(location=(264,120), world=self.worldChannel) # 32x8 wall
        VWall(location=(168,88), world=self.worldChannel)
        VWall(location=(288,88), world=self.worldChannel)

        HWall(location=(168,370), world=self.worldChannel)
        HWall(location=(200,370), world=self.worldChannel)
        HWall(location=(232,370), world=self.worldChannel)
        HWall(location=(264,370), world=self.worldChannel)
        VWall(location=(168,378), world=self.worldChannel)
        VWall(location=(288,378), world=self.worldChannel)
        """

        VWall(location=(370,200), world=self.worldChannel)
        VWall(location=(370,232), world=self.worldChannel)
        VWall(location=(370,264), world=self.worldChannel)
        VWall(location=(370,296), world=self.worldChannel)
        HWall(location=(378,200), world=self.worldChannel)
        HWall(location=(378,320), world=self.worldChannel)

        VWall(location=(100,200), world=self.worldChannel)
        VWall(location=(100,232), world=self.worldChannel)
        VWall(location=(100,264), world=self.worldChannel)
        VWall(location=(100,296), world=self.worldChannel)
        HWall(location=(76,192), world=self.worldChannel)
        HWall(location=(76,328), world=self.worldChannel)
        Spawner( (232,232),world=self.worldChannel)
        
        #player = PlayerActor((50,250), angle=298, velocity=5, world=self.worldChannel)
        #player2 = PlayerActor((450,250), angle=298, velocity=5, world=self.worldChannel)
        #BasicRobot(location=(100,100),world=self.worldChannel)        
        self.worldChannel.send((self.id,"JOIN", myvars(self)))

    def acceptConn(self):
        while self.serversocket.accepting:
            # Accept connections from outside
            (clientSocket, address) = self.serversocket.accept()
            # Now do something with the clientSocket
            # In this case, each client is managed in a tasklet
            stackless.tasklet(self.manageSocket)(clientSocket, address)
            stackless.schedule()

    def manageSocket(self, clientSocket, address):
        # Record the client data in a dict
        self.clients[clientSocket] = address
        print "Client %s:%s connected..." % (address[0],address[1])
        # For each send we expect the socket returns 1, if its 0 an error ocurred
        if not clientSocket.send('Connection OK\n\rType q! to quit.\n\r>'):
            clientSocket.close()
            return
        data = ''
        while clientSocket.connected:
            l = clientSocket.recv(4)
            if len(l)==0:
                continue
            ln = struct.unpack('i',l)[0]
            #print "len: %d" % ln
            r = 0
            data = ""
            while r<ln:
                data += clientSocket.recv(ln-r)
                r = len(data)
            args = cPickle.loads(data)
            print "server got (%d): %s " % (r,str(args))
            sentFrom, msg, msgArgs = args[0],args[1],args[2:]
            if msg=='JOIN' or msg=='NEW_PLAYER': # JOIN = a Display joined, create a player for it
                playerID= server.playerIDs.get(clientSocket, None)
                if playerID:
                    actor=Actor.actors.get(playerID, None)
                    if actor: actor.die()
                player = PlayerActor(world = server.worldChannel)
                server.playerIDs[clientSocket] = player.id
            elif msg=='INPUT' and Actor.actors.has_key(server.playerIDs[clientSocket]):
                msg_fwd = (server.playerIDs[clientSocket], msg) + msgArgs
                server.worldChannel.send(msg_fwd)
            elif msg=='KILLME':
                print 'Server: KILLME'
                if Actor.actors.has_key(server.playerIDs[clientSocket]):
                    msg_fwd = (server.playerIDs[clientSocket], msg) + msgArgs
                    server.worldChannel.send(msg_fwd)
                print "Closed connection for %s:%s" % (address[0],address[1])
                del self.clients[clientSocket]
                break  #>>> and hence CLOSE the clientSocket
            else:
                punk = cPickle.dumps((server.name, "Unknown command",None),-1)
                l= struct.pack('i',len(punk))
                s= clientSocket.sendall(l + punk)
                #if s<len(l)+len(punk): raise Exception("send didn't send all data")
            stackless.schedule()
        clientSocket.close()

    def defaultMessageAction(self,args):
        "Fwd msg to all network Clients"
        sentFrom, msg, msgArgs = args[0],args[1],args[2:]
        if msg!="WORLD_STATE":
            print "Unexpected msg: %s" % msg
            return
        cp = msgArgs[1]
        #if cp: print "Server Forwarding", time.time() - cp
        fwd_msg = (self.name, msg) + msgArgs
        #print type(msgArgs[0].actors[0][1]._Sprite__g)
        buf = cPickle.dumps(fwd_msg, -1) #-1 for highest protocol
        ln= len(buf)
        l= struct.pack('i',ln)
        s= l+buf
        if use_mcast:
            bytes_sent= self.mcast_sock.sendto(s, (self.mcast_group, self.mcast_port))
        else:
            for clientIP, clientPort in self.clients.values():
                #print "sending to %s (%d): %s" %(clientAddress,len(buf), str(fwd_msg))
                bytes_sent= self.mcast_sock.sendto(s, (clientIP, self.mcast_port))
                #s= clientSocket.sendall(l + buf)
                #if s<len(l)+len(buf): raise Exception("send didn't send all data")
                #print "just sent %d bytes" % s


if __name__ == "__main__":
    host = ''
    tcp_port= 3000
    udp_port= 3001
    use_mcast= '-m' in sys.argv

    print sys.argv
    print "Starting up server on IP:port %s:%s,%s (mcast=%s)" % (host, tcp_port, udp_port,use_mcast)
    world.World()
    server = Server((host,tcp_port),udp_port,use_mcast)
    stackless.run()
    server.serversocket.close()
    server.mcast_sock.close()
    print "Server: EXIT"

