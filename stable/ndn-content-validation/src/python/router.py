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
import sys,os,time
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
        self.interestLifetime = 4
        # node PIT data structure
        self.this_PIT = dict()
        # General PIT
        self.PIT = dict()

    def onTimeOut(self):
        # XXX: PIT structure is: {name:(start_time, type)}
        while 1:
            # iterates for PIT
            if len(self.PIT) > 0:
                temp_PIT = self.PIT.copy()
                for k in temp_PIT:
                    now = time.time()
                    if now - self.PIT[k] >= self.interestLifetime:
                        # Remove from PIT
                        del(self.PIT[k])
            time.sleep(0.3)

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
            pkt_type = ndn_packet['type']

            if ndn_packet['hop_count'] > 0:
                try:
                    # Here starts the attack <----
                    if self.PIT.get(name): # Is a data packet?
                        # print("[DEBUG-R] Router forwarding DATA packet %s" % (name))
                        # Delete entry
                        del(self.PIT[name])
                        # Send
                        ndn_packet['hop_count'] = ndn_packet['hop_count']-1
                        # Forward interest packet
                        message = str(json.dumps(ndn_packet)).encode('ascii')
                        self.sock_udp.sendto(message,('<broadcast>',2222))

                    elif (pkt_type == "interest" or pkt_type == "VER" or pkt_type == "REG"):
                        # print("[DEBUG-R] Forwarding message {}".format(ndn_packet))
                        # Decrement hop count
                        ndn_packet['hop_count'] = ndn_packet['hop_count']-1
                        # Forward interest packet
                        message = str(json.dumps(ndn_packet)).encode('ascii')
                        # Add on PIT
                        self.PIT[name] = time.time()
                        self.sock_udp.sendto(message,('<broadcast>',2222))

                except Exception as err:
                    print ("[DEBUG-R] Router error: ",err, " on packet {}".format(ndn_packet))
                    exit(-1)

# Main Function
def main():
    router = Router()
    t = Thread(None, target=router.onInterest)
    t.start()
    p = Thread(None,target=router.onTimeOut)
    p.start()



if __name__ == '__main__':
    main()
