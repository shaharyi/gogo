import cPickle, struct, time, sys
import stackless
import socket as stdsocket
from socket import gethostbyname, gethostname
import stacklesssocket as socket

import actor
import display
from util import *

class Client(actor.Actor):
    """Client app.
    
    Can use either TCP or UDP multicast.
    For UDP use -m.
    Specify host using -h, or it defaults to the local host.
    
    Respon:
    Create the World and Display.
    Register at Server.
    
    Collab:
    Forward msgs (eg WORLD_STATE, sent from World to Server to Client) to Display.
    """
    def __init__(self, server_addr, tcp_port, udp_port, use_mcast=False):
        actor.Actor.__init__(self)
        self.name = gethostbyname(gethostname())  #name=IP
        self.sock = socket.socket()
        self.sock.connect((server_addr, tcp_port))
        if use_mcast:
            self.bcast_sock= openmcastsock('225.0.0.250', udp_port)
        else:
            self.bcast_sock= openucastsock(udp_port)
        self.disp = display.Display(self.channel)
        stackless.tasklet(self.netAction)()

    def defaultMessageAction(self,args):
        "Forward all msgs to Server"
        #sentFrom = args[0]
        fwd_msg = (self.name, args[1]) + args[2:]
        pfwd_msg = cPickle.dumps(fwd_msg, -1) #-1 for highest protocol
        ln= len(pfwd_msg)
        #print "sending (%d) bytes" % (ln+4)
        l= struct.pack('i',ln)
        s= self.sock.sendall(l + pfwd_msg)
        #print 'Sent %d bytes' % s
        #if s<len(l)+len(pfwd_msg): raise Exception("send didn't send all data")
        

    def netAction(self):
        "Forward msgs to Display"
        while 1:#self.bcast_sock.connected:
            l=self.bcast_sock.recvfrom(4)[0]
            #l=self.bcast_sock.recv(4)
            ln = struct.unpack('i',l[:4])[0]
            data = self.bcast_sock.recvfrom(ln)[0]
            #data = self.bcast_sock.recv(ln)
            if len(data)<ln:
                print 'got less data than expected: %d / %d' % (len(data),ln)
                continue
            #print "got %d/%d bytes" % (len(data), ln)
            args = cPickle.loads(data)
            #print "got %s" % str(args)
            sentFrom, msg, msgArgs = args[0],args[1],args[2:]
            cp=msgArgs[1]
            if cp:
                print "Client Forwarding", time.time()-cp
            fwd_msg = (self.id, msg) + msgArgs
            #print "forwarding %s" % str(fwd_msg)
            self.disp.channel.send(fwd_msg)

        
    def netAction_buf(self):
        "Buffered version of netAction"
        buf = ''
        ISIZE= struct.calcsize('i')
        while self.sock.connected:
            #print "client connection", 1, "waiting to recv"
            data, address = self.bcast_sock.recvfrom(1024)
            buf += data
            while 1:
                l= buf[0:4]
                if len(l)<ISIZE:
                    break
                ln= struct.unpack('i',l)[0]
                #print "len: %d" % ln
                ldata=len(buf[4:ln+4])
                if ldata < ln:
                    break
                #print "got %d bytes" % ldata
                args = cPickle.loads(buf[4:ln+4])
                buf=buf[4+ldata:]
                #print "got %s" % str(args)
                sentFrom, msg, msgArgs = args[0],args[1],args[2:]
                cp=msgArgs[1]
                if cp:
                    print "Client Forwarding", time.time()-cp
                fwd_msg = (self.id, msg) + msgArgs
                #print "forwarding %s" % str(fwd_msg)
                self.disp.channel.send(fwd_msg)
                 
if '-h' not in sys.argv:
    server_addr = '127.0.0.1'
else:
    server_addr= sys.argv[sys.argv.index('-h')+1]
mcast= '-m' in sys.argv
print 'argv=',sys.argv
print "Connecting mcast=", mcast,", server=",server_addr, "..."
import world
world.World()
client = Client(server_addr, 3000, 3001, mcast)
print "Connected"
stackless.run()
client.bcast_sock.close()
client.sock.close()
print 'Client: EXIT'

