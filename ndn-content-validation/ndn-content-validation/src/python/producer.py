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

random.seed(2018)

class Producer():
    """Producer class"""
    def __init__(self, contract_address, emulation_time,my_id):
        # Global vars
        self.contract = App()
        self.content_file_write = open("/tmp/contents.txt","a+")
        self.num_provided_contents = 20 # maximum number of provided contents
        self.emulation_time = float(emulation_time) # this node index for
        self.my_id = int(my_id)
        self.this_account = None
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

        try:
            self.contract.initWeb3()
            self.this_account = self.contract.getAnAccount(self.my_id)
            # self.this_account = self.contract.getAnAccount()
            self.contract.initContract(self.contract_address)
        except Exception as err:
            print (err)
            exit(-1)

    def register_contents(self):
        print("[DEBUG] Registering contents")
        for i in range(self.num_provided_contents):
            # Random content's name
            rand = str(random.randint(0,1000)).encode('ascii')
            content = hashlib.sha256(rand).hexdigest()
            # Content with producer ID (e.g., /1/foobar)
            name = "/{0}/{1}".format(str(self.this_account),str(content))
            # Write contetns names in an file for consumer usage
            self.content_file_write.write(name+"\n")
            # register my content on Blockchain
            status = self.contract._registerContent(name,self.this_account)
            if not status: # Try to register again
                i-=1
        self.content_file_write.close()

    def onInterest(self):
        # Consumer side
        sock_udp = socket(AF_INET,SOCK_DGRAM)
        sock_udp.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        # Listen for requests from anywhere
        sock_udp.bind(("",2222))
        print("[DEBUG] Server is on")

        while 1:
            data, addr = sock_udp.recvfrom(1024)
            data_2_json = json.loads(data.decode('utf-8'))
            # Data Infos
            producer = str(data_2_json['name']).split('/')[1]
            name = data_2_json['name']

            if str(producer) == str(self.this_account) and data_2_json['type'] == "interest":
                # Now return a data packet
                data_pkt = {'type':'data','name':name, 'account': str(self.this_account), 'payload': [hex(x) for x in range(40)]}
                message = str(json.dumps(data_pkt)).encode('ascii')
                self.sock_udp.sendto(message,('<broadcast>',2222))

            elif self.PIT.get(name): # return data to origin
                self.sock_udp.sendto(data,('<broadcast>',2222))
                del(self.PIT[name])

            elif data_2_json['type'] == "interest":
                # Decrement hop count
                data_2_json['hop_count'] = data_2_json['hop_count']-1
                # Forward interest packet
                message = str(json.dumps(data_2_json)).encode('ascii')
                # Send
                self.sock_udp.sendto(message,('<broadcast>',2222))
                # Add on PIT
                self.PIT[name] = True

    def StopEmulation(self):
        time.sleep(self.emulation_time+2)
        output_file = open("/tmp/emulation_output","a+")
        output_file.write(self.contract.getStatistics())
        output_file.close()
        self.contract.getStatistics()
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
