import sys
from util import Util
from client import Client

class RanBot():
    def __init__(self, keys=None):
        self.util = Util()
        self.keys = keys

        if self.keys == None:
            self.util.log("entry", "No keys provided")
            sys.exit(1)
        else:
            self.util.log("entry", "Starting server")
            self.client = Client(self.util, keys)
    
    def run(self):
        self.util.log("entry", "Executing Server")
        self.client.run()