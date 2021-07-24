from discord import channel
import parse
import discord
from util import Util

# Import the pipelines
from pipeline import TranslationPipeline
from pipeline import DanbooruPipeline
from pipeline import YoutubePipeline
from pipeline import WikipediaPipeline

class Client():
    def __init__(self, util, keys=None):
        self.util = util
        self.client = discord.Client()
        self.token = keys["discord_token"]
        self.tl_pipeline = TranslationPipeline(self.util, keys)
        self.db_pipeline = DanbooruPipeline(self.util, keys)
        self.yt_pipeline = YoutubePipeline(self.util, keys)
        self.wiki_pipeline = WikipediaPipeline(self.util, keys)

    def log(self, message):
        if self.util is not None:
            self.util.log(self.__class__.__name__, message)
    
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
        
        # translation
        if message.content.startswith('r!t'):
            msg = parse.parse('r!tl {0} {1} {2}', message.content)
            from_lang = msg[0]
            to_lang = msg[1]
            text = msg[2]
            await message.channel.send(self.tl_pipeline.generate(text, from_lang, to_lang))
        
        # danbooru
        if message.content.startswith('r!d'):
            msg = parse.parse('r!d {0}', message.content)
            if message.channel.is_nsfw():
                await message.channel.send(self.db_pipeline.generate(msg[0], True))
            else:
                await message.channel.send(self.db_pipeline.generate(msg[0], False))
        
        if message.content.startswith('r!yt'):
            msg = parse.parse('r!yt {0}', message.content)
            await message.channel.send(self.yt_pipeline.generate(msg[0]))

        if message.content.startswith('r!wiki'):
            msg = parse.parse('r!wiki {0}', message.content)
            await message.channel.send(self.wiki_pipeline.generate(msg[0]))