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
from app import App
import sys
import hashlib
import random
import json
from threading import Thread

class FakeProducer():
    """I'm BAD!!!"""
    def __init__(self, contract_address,my_id):
        # Global vars
        self.contract = App()
        self.content_file_write = open("/tmp/contents.txt","a+")
        self.content_file_read = open("/tmp/contents.txt","r")
        self.num_provided_contents = 20 # maximum number of provided contents
        self.this_account = None
        self.my_id = int(my_id)
        self.contract_address = contract_address
        # UDP Socket
        self.sock_udp = socket(AF_INET,SOCK_DGRAM)
        self.sock_udp.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        # Data packet structure
        self.Data = dict()
        # General PIT
        self.PIT = dict()

    def onInterest(self):
        # Consumer side
        sock_udp = socket(AF_INET,SOCK_DGRAM)
        sock_udp.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        # Listen for requests from anywhere
        sock_udp.bind(("",2222))
        print("[DEBUG-UP] Malicious Server is on")

        while 1:
            data, addr = sock_udp.recvfrom(1024)
            ndn_packet = json.loads(data.decode('utf-8'))
            # Data Infos
            producer = str(ndn_packet['name']).split('/')[1]
            name = str(ndn_packet['name'])
            # Here starts the attack <----
            # if self.PIT.get(name): # Is a data packet?
            #     ndn_packet['provider'] = self.this_account # Modify content
            #     # Encode
            #     message = str(json.dumps(ndn_packet)).encode('ascii')
            #     # Send
            #     self.sock_udp.sendto(message,('<broadcast>',2222))
            #     # Delete entry
            #     del(self.PIT[name])

            # IF it's a interest packet then Forward it
            if ndn_packet['type'] == "interest":
                # Decrement hop count
                ndn_packet['hop_count'] = ndn_packet['hop_count']-1
                # Forward interest packet
                # interest = str(json.dumps(ndn_packet)).encode('ascii')
                # self.sock_udp.sendto(interest,('<broadcast>',2222))

                # Mode Furious
                data_pkt = {'hop_count':15 ,'type':'data','name':name, 'provider': str(self.my_id), 'payload': [hex(x) for x in range(100)]}
                message = str(json.dumps(data_pkt)).encode('ascii')
                self.sock_udp.sendto(message,('<broadcast>',2222))

            # if ndn_packet['type'] == "interest" or ndn_packet['type'] == "data": # Forward?
            elif ndn_packet['type'] == "data":
                # if self.PIT.get(name):
                    # del(self.PIT[name])
                # print("[DEBUG-UP] Attacking packet {0}".format(name))
                # Fake data packet
                data_pkt = {'hop_count':15 ,'type':'data','name':name, 'provider': str(self.my_id), 'payload': [hex(x) for x in range(100)]}
                message = str(json.dumps(data_pkt)).encode('ascii')
                self.sock_udp.sendto(message,('<broadcast>',2222))


if len(sys.argv) < 2:
    print("[!] Usage: {0} <contract_address> <account_index> ".format(sys.argv[0]))
    exit(-1)

# Main Function
def main():
    contract_address = sys.argv[1]
    my_id = sys.argv[2]

    fakeproducer = FakeProducer(contract_address,my_id)
    t = Thread(None, target=fakeproducer.onInterest)
    t.start()


if __name__ == '__main__':
    main()
