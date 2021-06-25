import sys, time, os
import socket as stdsocket
from socket import gethostbyname, gethostname
import stacklesssocket as socket

DATA_TYPES = [bool,int,long,float,str,unicode,complex,list,tuple,set,dict,None]

IMAGE_EXT  = '.png'
DEBUG = True

logfile=open('../logs/%s.txt' % time.strftime('%Y%m%d_%H%M%S'), 'wt')

def log(s):
    if not DEBUG: return
    logfile.write(s+'\n')    #logfile.write(os.linesep)
    logfile.flush()

"""
class Properties:
    "Sets its instance attributes to be the target ones, excluding class instances"
    def __init__(self, obj):
        items_holder= type(obj)==dict  and  obj or vars(obj)
        [setattr(self,n,v) for n,v in items_holder.items() if type(v) in DATA_TYPES and not n.startswith('_')]
"""

def myvars(obj):
    return dict([(n,v) for (n,v) in vars(obj).items() if type(v) in DATA_TYPES  and not n.startswith('_')])

def sign(x):
    return cmp(x,0)

def log(s):
    print s

def exit(s):
    print 'exit:', s
    sys.exit(0)

def roundtup(tup):
    return map(round, tup)

# Open a UDP socket, bind it to a port and select a multicast group
def openmcastsock(group, port):
    # Import modules used only here
    import string
    import struct
    #
    # Create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #
    # Allow multiple copies of this program on one machine
    # (not strictly needed)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #
    # Bind it to the port
    s.bind(('', port))
    #
    # Look up multicast group address in name server
    # (doesn't hurt if it is already in ddd.ddd.ddd.ddd format)
    group = gethostbyname(group)
    #
    # Construct binary group address
    bytes = map(int, string.split(group, "."))
    grpaddr = 0
    for byte in bytes: grpaddr = (grpaddr << 8) | byte
    #
    # Construct struct mreq from grpaddr and ifaddr
    ifaddr = socket.INADDR_ANY
    mreq = struct.pack('ll', socket.htonl(grpaddr), socket.htonl(ifaddr))
    #
    # Add group membership
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    #
    return s

def openucastsock(port):
    listenSocket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind it to the port
    listenSocket.bind(('', port))
    return listenSocket
    
