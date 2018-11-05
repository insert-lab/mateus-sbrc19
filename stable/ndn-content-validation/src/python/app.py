#!/usr/bin/env python3.7
from web3 import Web3, HTTPProvider
import json
import sys,random,time

class App():
    def __init__(self):
        self.w3 = None
        self.accounts = list()
        self.this_account = None
        self.contract_instance = None
        self.verification_fail_counter = 0
        self.verification_sucess_counter = 0
        self.successfully_registered_contents = 0
        self.registered_providers = 0
        self.backoff_delay = 0.0
        self.used_accounts = list()

    def initWeb3(self):
        while 1:
            try:
                w3Provider = HTTPProvider('http://10.0.1.20:7545')
                # w3Provider = HTTPProvider('http://127.0.0.1:7545') # For local tests
                self.w3 = Web3(w3Provider)
                self.accounts = self.w3.eth.accounts
                # self.this_account = self.getAnAccount() # Pick an random account for this process
                break
            except Exception as err:
                print(err)
                self.backoff_delay+=1
                time.sleep(1)

    def initContract(self,address):
        try:
            abi_file = open("/tmp/ContentValidation.json","r")
            abi_file = json.loads(abi_file.read())

            contract_address = self.w3.toChecksumAddress(address) # Here goes the contract address
            self.contract_instance = self.w3.eth.contract(address=contract_address,abi=abi_file['abi'])
        except Exception as err:
            print (err)
            exit(-1)

    def _verifyContent(self,content_name, provider_account):
        try:
            self.contract_instance.functions.verifyContent(content_name,provider_account).transact({'from':self.accounts[0],'gas':410000})
            status = self.contract_instance.functions.verifyContent(content_name,provider_account).call()
            if (bool(status)):
                # print("Provider '{0}' is ALLOWED to provide content '{1}'!".format(provider_account,content_name))
                # Count
                self.verification_sucess_counter+=1
                return True
            else:
                self.verification_fail_counter+=1
                # print("node '{0}' is an INVALID provider for content '{1}'! Call the cops.".format(provider_account,content_name))
                return False
        except Exception as err:
            print(err)

    def _registerProvider(self,content_name,provider_account):
        try:
            self.contract_instance.functions.registerAllowedProviders(content_name,provider_account).transact({'from':provider_account, 'gas': 410000})
            # print("New provider for content '{0}' registered successfully!".format(content_name))
            self.registered_providers+=1
        except Exception as err:
            print(err)

    def _registerContent(self,content_name,producer_account):
        # print(self.contract_instance.functions.myFunction().call())
        try:
            self.contract_instance.functions.registerContent(content_name,producer_account).transact({'from':producer_account, 'gas': 410000})
            status = self.contract_instance.functions.checkContentStatus(content_name).call()
            if (bool(status)):
                # print("Content '{0}' belonging to {1} registered successfully!".format(content_name,producer_account))
                # LOG
                # Counter
                self.successfully_registered_contents+=1
                return True
            else:
                print("Error on register content! Try again later.")
                return False
        except Exception as err:
            print(err)

    def getAnAccounts(self):
        return self.accounts

    def getAnAccount(self, id):
        if id < len(self.accounts):# and self.accounts[id] not in self.used_accounts:
            # self.used_accounts.append(self.accounts[id])
            self.this_account = self.accounts[id]
            return self.accounts[id]
        else:
            print("This account is currently being used. Exiting to avoid execution errors...")
            exit(-1)

    def getStatistics(self):
            return("RC: {0}\nRP:{1}\nVS: {2}\nVF: {3}\nBD: {4}\n".format(self.successfully_registered_contents,
            self.registered_providers,
            self.verification_sucess_counter,
            self.verification_fail_counter,
            self.backoff_delay))


# For debugging purposes
# address = self.w3.toChecksumAddress("0x85e20912ed9cab54e5712e5d1b39b77e593b9067")
# if __name__ == '__main__':
#     initWeb3()
#     initContract()
#
#     address = self.this_account
#     fake = self.accounts[3]
#
#     _registerContent("data1",address)
#     _verifyContent("data1",fake)
#     _registerProvider("data1",fake)
#     _verifyContent("data1",fake)
