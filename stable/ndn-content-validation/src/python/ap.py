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
import json,time
from threading import Thread
from app import App
from ndn import NDN

class AP():
    """I'm a router!!!"""
    def __init__(self,contract_address):
        # Global vars
        # UDP Socket
        self.emulation_time = 200
        self.sock_udp = socket(AF_INET,SOCK_DGRAM)
        self.sock_udp.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        self.contract = App()
        self.contract_address = contract_address
        # node PIT data structure
        self.this_PIT = dict()
        # General PIT
        self.PIT = dict()

        try:
            self.contract.initWeb3()
            self.contract.initContract(self.contract_address)
            self.contract.initContract(self.contract_address)
        except Exception as err:
            print (err)
            exit(-1)

    def onInterest(self):
        # Consumer side
        sock_udp = socket(AF_INET,SOCK_DGRAM)
        sock_udp.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        # Listen for requests from anywhere
        sock_udp.bind(("",2222))
        while 1:
            data, addr = sock_udp.recvfrom(1024)
            ndn_packet = json.loads(data.decode('utf-8'))
            pkt_type = ndn_packet['type']
            # Data Infos
            provider = ndn_packet['name'].split('/')[1]
            name = ndn_packet['name'].split('/')[2]

            # Here starts the attack <----
            if pkt_type == "VER":
                if self.PIT.get(name):
                    prefix = self.contract.getAnAccount(int(provider))
                    content_name = "/{0}/{1}".format(prefix,name)
                    try:
                        provider = self.contract.getAnAccount(int(ndn_packet['provider']))
                        print("[DEBUG-AP] AP verifying Content %s for provider %s" % (name,provider))
                        status = self.contract._verifyContent(content_name,provider)
                        print("[DEBUG-AP] Status ", status)

                        message = {'hop_count':15, 'type':'VER', 'name':ndn_packet['name'],'status':status}
                        message2json = str(json.dumps(message)).encode('ascii')
                        self.sock_udp.sendto(message2json,("10.0.0.255",2222)) # Using broadcast address of eth0
                    except Exception as err:
                        # print ("Error: {0} => {1}".format(err,ndn_packet))
                        pass

            elif pkt_type == "REG":
                # TODO: Finish this implementation
                provider = self.contract.getAnAccount(int(provider))
                content_name = "/{0}/{1}".format(provider,name)

                if not self.PIT.get(name):
                    # print("[DEBUG-AP] AP registering content %s" % (content_name))
                    self.contract._registerContent(content_name,provider)
                    self.writeRegisteredContents(ndn_packet['name'])
                    self.PIT[name] = True

            # TODO: Finish this implementation
            # elif data_2_json['type'] == "AUT":
            #     self.contract._registerProvider(name,provider)

    def writeRegisteredContents(self,content_name):
        content_list = open("/tmp/content_list.txt","a+")
        content_list.write(content_name+"\n")
        content_list.close()

    def StopEmulation(self):
        time.sleep(self.emulation_time+2)
        output_file = open("/tmp/emulation_output.txt","a+")
        output_file.write(self.contract.getStatistics())
        output_file.close()
        os.system("killall python3.7")


# Main Function
def main():
    contract_address = sys.argv[1]
    ap = AP(contract_address)

    s = Thread(None,target=ap.StopEmulation)
    s.start()

    t = Thread(None, target=ap.onInterest)
    t.start()


if __name__ == '__main__':
    main()
