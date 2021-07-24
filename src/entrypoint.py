import os
import sys
import json
from ran import RanBot

def entry():
    # parse secrets json from path env var
    with open(os.environ.get("SECRETS_PATH"), 'r') as f:
        secrets = json.load(f)
    
    # create ran bot
    bot = RanBot(keys=secrets)
    bot.run()

    return 0

if __name__ == "__main__":
    sys.exit(entry())
