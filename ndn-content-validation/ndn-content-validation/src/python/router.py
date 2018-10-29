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
import sys
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
            data_2_json = json.loads(data.decode('utf-8'))
            # Data Infos
            producer = str(data_2_json['name']).split('/')[1]
            name = data_2_json['name']

            # Here starts the attack <----
            if self.PIT.get(name) and data_2_json['type'] == "data": # Is a data packet?
                # print("[DEBUG] Router forwarding DATA packet %s" % (name))
                # Send
                self.sock_udp.sendto(data,('<broadcast>',2222))
                # Delete entry
                del(self.PIT[name])

            elif data_2_json['type'] == "interest": # Forward?
                hop_count = data_2_json['hop_count']
                # print("[DEBUG] Router forwarding INTEREST packet %s" % (name))
                if hop_count >= 1:
                    # Decrement hop count
                    data_2_json['hop_count'] = data_2_json['hop_count']-1
                    # Forward interest packet
                    message = str(json.dumps(data_2_json)).encode('ascii')
                    self.sock_udp.sendto(message,('<broadcast>',2222))
                    # Add on PIT
                    self.PIT[name] = True

# Main Function
def main():
    router = Router()
    t = Thread(None, target=router.onInterest)
    t.start()


if __name__ == '__main__':
    main()
