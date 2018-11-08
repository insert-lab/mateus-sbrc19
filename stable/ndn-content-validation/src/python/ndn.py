#!/usr/bin/env python3.7
import time
import os,json

class NDN():
    def __init__(self):
        self.interestLifetime = 4 # default interest lifetime
        # General PIT
        self.PIT = dict()
        # node PIT data structure
        self.this_PIT = dict()

    def onTimeOut(self,PIT,sock_udp):
        while 1:
            if len(self.this_PIT) > 0:
                for k in self.this_PIT:
                    now = time.time()
                    if self.this_PIT[k] >= self.interestLifetime:
                        # Resend
                        overhead = {"hop_count":15,"type":"interest","name":k, "payload": [hex(x) for x in range(100)]} # use sys.getsizeof(arr) to get the array size in bytes
                        interest = str(json.dumps(overhead)).encode('ascii')
            if len(self.PIT) > 0:
                for k in self.PIT:
                    now = time.time()
                    if self.PIT[k] >= self.interestLifetime:
                        # Remove from PIT
                        del(self.PIT[k])

    def sendInterest(self):
        overhead = {"hop_count":15,"type":"interest","name":name, "payload": [hex(x) for x in range(10)]}
        interest = str(json.dumps(overhead)).encode('ascii')
        # Send interest
        self.sock_udp.sendto(interest,('<broadcast>',2222))
        # Add on PIT
        self.this_PIT[name] = True
        # count
