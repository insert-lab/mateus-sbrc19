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

contract = App()

if not len(sys.argv[:-1]):
    print("[!] Usage: {0} <contract_address>".format(sys.argv[0]))
    exit(-1)


try:
    contract.initWeb3()
    contract.initContract(sys.argv[1])
    realAddr = contract.getAnAccount(1)
    fakeAddr = contract.getAnAccount(2)

    contract._registerProvider("data1",fakeAddr)

except Exception as err:
    print (err)
