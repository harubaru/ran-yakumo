import sys
from util import Util
from client import Client

class Bot():
    def __init__(self, keys=None):
        self.util = Util()
        self.keys = keys
    
    def log(self, message):
        if self.util:
            self.util.log(self.__class__.__name__, message)

class RanBot(Bot):
    def __init__(self, keys=None):
        super().__init__(keys)

        if self.keys == None:
            self.log("No keys provided")
            sys.exit(1)
        else:
            self.log("Starting server")
            self.client = Client(self.util, keys)
    
    def run(self):
        self.log("Executing Server")
        self.client.run()