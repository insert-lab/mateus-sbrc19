#!/usr/bin/env python3.7
# This script ilustrates the server side of the application.
# Alice will:
#           provide and register data,
#           also she can perform bad actions like provide false contents
#           or unauthorized ones.
# Author: Mateus Sousa
# Location: UFBA, Brazil
# Date: 09/14/18
from socket import *
import sys,os
import random
import json
from threading import Thread

class Router():
    """I'm a router!!!"""
    def __init__(self):
        # Global vars
        # UDP Socket
        self.sock_udp = socket(AF_INET,SOCK_DGRAM)
        self.sock_udp.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        # Data packet structure
        self.Data = dict()
        # node PIT data structure
        self.this_PIT = dict()
        # General PIT
        self.PIT = dict()

    def onInterest(self):
        # Consumer side
        sock_udp = socket(AF_INET,SOCK_DGRAM)
        sock_udp.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        # Listen for requests from anywhere
        sock_udp.bind(("",2222))
        while 1:
            data, addr = sock_udp.recvfrom(1024)
            ndn_packet = json.loads(data.decode('utf-8'))
            # Data Infos
            producer = str(ndn_packet['name']).split('/')[1]
            name = ndn_packet['name']

            if ndn_packet['hop_count'] > 0:
                try:
                    # Here starts the attack <----
                    if self.PIT.get(name): # Is a data packet?
                        # print("[DEBUG-R] Router forwarding DATA packet %s" % (name))
                        # Send
                        self.sock_udp.sendto(data,('<broadcast>',2222))
                        # Delete entry
                        del(self.PIT[name])

                    elif ndn_packet['type'] == "interest": # Forward?
                        # print("[DEBUG-R] Router forwarding INTEREST packet %s" % (name))
                        # Decrement hop count
                        ndn_packet['hop_count'] = ndn_packet['hop_count']-1
                        # Forward interest packet
                        message = str(json.dumps(ndn_packet)).encode('ascii')
                        self.sock_udp.sendto(message,('<broadcast>',2222))
                        # Add on PIT
                        self.PIT[name] = True

                    else:
                        # print("[DEBUG-R] Forwarding message {}".format(ndn_packet['type']))
                        # Decrement hop count
                        ndn_packet['hop_count'] = ndn_packet['hop_count']-1
                        # Forward interest packet
                        message = str(json.dumps(ndn_packet)).encode('ascii')
                        self.sock_udp.sendto(message,('<broadcast>',2222))
                except Exception as err:
                    print ("[DEBUG-R] Router error: ",err, " on packet {}".format(ndn_packet))
                    exit(-1)

# Main Function
def main():
    router = Router()
    t = Thread(None, target=router.onInterest)
    t.start()


if __name__ == '__main__':
    main()
