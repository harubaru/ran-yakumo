import parse
import discord
from util import Util
from pipeline import TranslationPipeline

class Client():
    def __init__(self, util, keys=None):
        self.util = util
        self.client = discord.Client()
        self.token = keys["discord_token"]
        self.pipeline = TranslationPipeline(self.util, keys)

    def log(self, message):
        if self.util is not None:
            self.util.log('client', message)
    
    def run(self):
        self.log('Starting Discord Client')
        # Setup events
        self.on_ready = self.client.event(self.on_ready)
        self.on_message = self.client.event(self.on_message)
        self.client.run(self.token)
    
    async def on_ready(self):
        self.log('Connected to Discord Servers.')
    
    async def on_message(self, message):
        if not message.content.startswith('r!'):
            return
        
        # parse message
        msg = parse.parse('r!tl {0} {1} {2}', message.content)
        from_lang = msg[0]
        to_lang = msg[1]
        text = msg[2]
        await message.channel.send(self.pipeline.generate(text, from_lang, to_lang))
