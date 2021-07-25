from discord import channel
import time
import parse
import discord
from ratelimiter import AsyncRateLimiter
from util import Util

# Import the pipelines
from pipeline import TranslationPipeline
from pipeline import QnAPipeline
from pipeline import DanbooruPipeline
from pipeline import YoutubePipeline
from pipeline import WikipediaPipeline

class Client():
    def __init__(self, util, keys=None):
        self.util = util
        self.client = discord.Client()
        self.token = keys["discord_token"]
        self.tl_pipeline = TranslationPipeline(self.util, keys)
        self.qna_pipeline = QnAPipeline(self.util, keys)
        self.db_pipeline = DanbooruPipeline(self.util, keys)
        self.yt_pipeline = YoutubePipeline(self.util, keys)
        self.wiki_pipeline = WikipediaPipeline(self.util, keys)
        self.last_message = None
        self.until = None
        self.rate_limited = False
        # Limit generation to 6 messages per minute.
        self.rate_limiter = AsyncRateLimiter(max_calls=2, period=10, callback=self.limited)

    def log(self, message):
        if self.util is not None:
            self.util.log(self.__class__.__name__, message)
    
    async def limited(self, until):
        duration = int(round(until - time.time()))
        self.until = until
        self.rate_limited = True
        await self.last_message.channel.send('Please wait for {0} seconds to use this command again.'.format(duration))

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
        
        self.last_message = message
        
        # Check if rate limited, if so, return
        if self.until != None:
            if self.until > time.time():
                duration = int(round(self.until - time.time()))
                await message.channel.send('Please wait for {0} seconds to use this command again.'.format(duration))
                return
        
        async with self.rate_limiter:
            if self.rate_limited:
                self.rate_limited = False
                await self.rate_limiter.pop_call()
                return
            else:
                await self.message_handler(message)
    
    async def message_handler(self, message):
        if message.content.startswith('r!t'):
            msg = parse.parse('r!tl {0} {1} {2}', message.content.replace('\n', ''))
            from_lang = msg[0]
            to_lang = msg[1]
            text = msg[2]
            await message.channel.send(self.tl_pipeline.generate(text, from_lang, to_lang))
        
        # danbooru
        if message.content.startswith('r!d'):
            msg = parse.parse('r!d {0}', message.content.replace('\n', ''))
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
        
        if message.content.startswith('r!q'):
            msg = parse.parse('r!q {0}', message.content.replace('\n', ''))
            await message.channel.send(self.qna_pipeline.generate(msg[0]))