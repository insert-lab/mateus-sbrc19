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
import json,time,os
from threading import Thread

class Producer():
    """Producer class"""
    def __init__(self, contract_address, emulation_time,my_id):
        # Global vars
        self.contract = App()
        self.content_file_write = open("/tmp/contents.txt","a+")
        self.num_provided_contents = 20 # maximum number of provided contents
        self.emulation_time = float(emulation_time) # this node index for
        self.my_id = int(my_id)
        self.contract_address = contract_address
        # UDP Socket
        self.sock_udp = socket(AF_INET,SOCK_DGRAM)
        self.sock_udp.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        # Data packet structure
        self.Data = dict()
        # node PIT data structure
        self.this_PIT = dict()
        # General PIT
        self.PIT = dict()

    def register_contents(self):
        print("[DEBUG-PR] Registering contents")
        for i in range(self.num_provided_contents):
            # Random content's name
            rand = str(random.randint(0,1000)).encode('ascii')
            content = hashlib.sha256(rand).hexdigest()
            # Content with producer ID (e.g., /1/foobar)
            name = "/{0}/{1}".format(str(self.my_id),str(content))
            # Write contetns names in an file for consumer usage
            self.content_file_write.write(name+"\n")
            # register my content on Blockchain
            ndn_packet = {"hop_count":15,"type":"REG","name":name,'provider':str(self.my_id) ,"payload": [hex(x) for x in range(100)]}
            interest = str(json.dumps(ndn_packet)).encode('ascii')
            self.sock_udp.sendto(interest,('<broadcast>',2222))

        self.content_file_write.close()

    def onInterest(self):
        # Consumer side
        sock_udp = socket(AF_INET,SOCK_DGRAM)
        sock_udp.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        # Listen for requests from anywhere
        sock_udp.bind(("",2222))
        print("[DEBUG-PR] Server is on")

        while 1:
            data, addr = sock_udp.recvfrom(1024)
            ndn_packet = json.loads(data.decode('utf-8'))
            # Extracting packet informations
            producer = str(ndn_packet['name']).split('/')[1]
            name = ndn_packet['name']

            if ndn_packet['hop_count'] > 0:
                if str(producer) == str(self.my_id) and ndn_packet['type'] == "interest":
                    # print("[DEBUG-PR] Node {0} received an interest for {1}".format(self.my_id, name))
                    # Now return a data packet
                    data_pkt = {'hop_count':15,'type':'data','name':name, 'provider': str(self.my_id), 'payload': [hex(x) for x in range(40)]}
                    message = str(json.dumps(data_pkt)).encode('ascii')
                    self.sock_udp.sendto(message,('<broadcast>',2222))

                elif self.PIT.get(name): # return data to origin
                    self.sock_udp.sendto(data,('<broadcast>',2222))
                    del(self.PIT[name])

                elif ndn_packet['type'] == "interest":
                    # Decrement hop count
                    ndn_packet['hop_count'] = ndn_packet['hop_count']-1
                    # Forward interest packet
                    message = str(json.dumps(ndn_packet)).encode('ascii')
                    # Send
                    self.sock_udp.sendto(message,('<broadcast>',2222))
                    # Add on PIT
                    self.PIT[name] = True

    def StopEmulation(self):
        time.sleep(self.emulation_time+2)
        os.system("killall python3.7")

if len(sys.argv) < 2:
    print("[!] Usage: {0} <contract_address> <emulation_time> ".format(sys.argv[0]))
    exit(-1)

# Main Function
def main():
    contract_address = sys.argv[1]
    my_id = None
    # BUG: my_id is receiving a INVALID string on inicialization
    try:
        my_id = int(sys.argv[2])
    except:
        my_id = 0
    emulation_time = 200.0

    producer = Producer(contract_address,emulation_time,my_id)
    s = Thread(None, target=producer.StopEmulation) # Start emulation
    s.start()
    producer.register_contents()
    t = Thread(None, target=producer.onInterest)
    t.start()


if __name__ == '__main__':
    main()
