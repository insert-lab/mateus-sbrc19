#!/usr/bin/env python3.7
# This script ilustrates the client side of the application.
# Bob will:
#           request data,
#           verifyContent
#
# Author: Mateus Sousa
# Location: UFBA, Brazil
# Date: 09/14/18
from socket import *
from app import App
import sys
import time
import json
import random,os
from threading import Thread

random.seed(2018)

class Consumer():
    """docstring for Consumer."""
    def __init__(self, contract_address,emulation_time,my_id):
        self.emulation_time = float(emulation_time)
        self.contract = App()
        self.contract_address = contract_address
        # File with content names TODO: remove '\n' chars
        self.content_file_array = ""
        # According to the emulation time
        self.maximum_request = random.randint(20,500)
        self.requests_per_second = 5
        # UDP Socket
        self.sock_udp = socket(AF_INET,SOCK_DGRAM)
        self.sock_udp.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        self.sock_udp.bind(('',2222))
        # node PIT data structure
        self.this_PIT = dict()
        # General PIT
        self.PIT = dict()

        # Metrics
        self.interests_sent = 0.0
        self.data_received = 0.0
        #

        try:
            self.contract.initWeb3()
            self.contract.getAnAccount(int(my_id))
            self.contract.initContract(self.contract_address)
            # realAddr = self.contract.getAnAccount(1)
            # fakeAddr = self.contract.getAnAccount(2)

            # Problemas de DoS realizados pelo consumidor que tenta inundar a BC
            # com falsas requisicoes ou incriminar algum produtor autentico
            # self.contract._verifyContent("data1",fakeAddr)
            # self.contract._verifyContent("data1",fakeAddr)
        except Exception as err:
            print (err)
            exit(-1)

    def setFile(self):
        self.content_file_array = list(open("/tmp/contents.txt","r").readlines())

    def sendInterest(self):
        if (self.maximum_request > 0):
            file_size = len(self.content_file_array)
            try:
                for c in range(self.requests_per_second):
                    name = self.content_file_array[random.randint(0,file_size-1)].replace('\n','')
                    # interest packet format
                    data_2_json = {"hop_count":15,"type":"interest","name":name, "payload": [hex(x) for x in range(10)]}
                    interest = str(json.dumps(data_2_json)).encode('ascii')
                    # Send interest
                    self.sock_udp.sendto(interest,('<broadcast>',2222))
                    # Add on PIT
                    self.this_PIT[name] = True
                    # count
                    self.interests_sent += 1.0
                    self.maximum_request-=1
            except:
                pass
            # Interval
            time.sleep(1)
            # Loop
            self.sendInterest()

    # On consumer, onData works for both Interests and Data packets
    def onData(self):
        while 1:
            data, addr = self.sock_udp.recvfrom(1024)
            data_2_json = json.loads(data.decode('utf-8'))
            name = data_2_json['name']
            # Is pending?
            if self.this_PIT.get(name) and data_2_json['type'] == "data":
                provider = data_2_json['account']
                status = self.contract._verifyContent(name,provider)
                if status:
                    # count
                    self.data_received += 1
                # Delete entry
                del(self.this_PIT[name])

            elif self.PIT.get(name) and data_2_json['type'] == "data": # Did I Forward it?
                # Forward data packet
                self.sock_udp.sendto(data,('<broadcast>',2222))
                del(self.PIT[name])

            elif data_2_json['type'] == "interest" and not (self.this_PIT.get(name) or  self.PIT.get(name)): # Forward it
                # Decrement hop count
                data_2_json['hop_count'] = data_2_json['hop_count']-1
                # Forward interest packet
                message = str(json.dumps(data_2_json)).encode('ascii')
                self.sock_udp.sendto(message,('<broadcast>',2222))
                # Add on PIT
                self.PIT[name] = True

            # else: #drop it
            #     print (data_2_json)

    def StopEmulation(self):
        time.sleep(self.emulation_time)
        output_file = open("/tmp/emulation_output","a+")
        output_file.write(self.contract.getStatistics())
        try:
            output_file.write("ISR:{0}\n".format(self.data_received/self.interests_sent))
        except:
            output_file.write("ISR: 0")
        output_file.close()
        os.system("killall python3.7")

if len(sys.argv[:-1]) < 1:
    print("[!] Usage: {0} <contract_address> <emulation_time>".format(sys.argv[0]))
    exit(-1)


def main():
    contract_address = sys.argv[1]
    emulation_time = sys.argv[2]
    my_id = sys.argv[3]

    consumer = Consumer(contract_address, emulation_time,my_id)
    # Wait for producers register their contents
    time.sleep(6)
    consumer.setFile()
    s = Thread(None,target=consumer.StopEmulation)
    s.start()
    t = Thread(None,target=consumer.onData)
    t.start()
    # Begin requests
    consumer.sendInterest()


if __name__ == '__main__':
    main()
